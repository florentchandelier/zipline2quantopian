#!/usr/bin/env python

from __future__ import print_function

from abc import ABCMeta, abstractmethod
from ast import NodeVisitor, parse
from six import with_metaclass
import sys

import click


class Warning(with_metaclass(ABCMeta)):
    """
    A type that represents a warning that code will not work on the Quantopian
    platform.
    """
    def __init__(self, node):
        self.node = node

    @property
    def header(self):
        """
        The header for a warning message, this is used to prefix the message
        with the line and column the code that triggered the warning was
        found on.
        """
        node = self.node
        return '{lno}:{col}'.format(lno=node.lineno, col=node.col_offset)

    def __lt__(self, other):
        """
        Define a sort order based on the location of the node this is warning
        about.
        """
        s_node = self.node
        o_node = other.node
        return ((s_node.lineno, s_node.col_offset) <
                (o_node.lineno, o_node.col_offset))

    @abstractmethod
    def __str__(self):
        """
        The message for the warning.
        """
        raise NotImplementedError()


def create_warning(msg, base=Warning):
    """
    Create a new warning type that prints a message after a header.
    `base` is the base class to use for the new warning type.
    """
    str_ = '{{header}}: {msg}'.format(msg=msg)

    class _Warning(base):
        def __str__(self):
            return str_.format(header=self.header)

    return _Warning

# A warning the represents an `exec` statement.
ExecWarning = create_warning('`exec` statement found.')


class NameWarning(Warning):
    """
    A warning for a `Name` node.
    """
    pass


def create_warning_from_name(name):
    """
    Construct a new warning type for a function.
    """
    return create_warning(
        '`{name}` name found.'.format(name=name),
        base=NameWarning,
    )


# A mapping of illegal names to warning types.
illegal_name_warnings = {
    name: create_warning_from_name(name)
    for name in {
        '__import__',
        'compile',
        'delattr',
        'eval',
        'exec',
        'execfile',
        'file',
        'getattr',
        'globals',
        'help',
        'input',
        'intern',
        'locals',
        'memoryview',
        'raw_input',
        'reload',
        'setattr',
        'super',
        'intern',
    }
}


class SafetyCheck(NodeVisitor):
    """
    A visitor that scans for things that will not run on Quantopian.
    """
    def __init__(self, filename, filters=None):
        """
        Run the ast check on `filename`.

        `filters` is an optional iterable of warning types to filter from the
        validation step.
        """
        self._filename = filename
        self._warnings = set()
        self._filters = tuple(filters or ())

    def visit_Exec(self, node):
        self._warnings.add(ExecWarning(node))
        return self.generic_visit(node)

    def visit_Name(self, node):
        warning = illegal_name_warnings.get(node.id)
        if warning is not None:
            self._warnings.add(warning(node))

        return self.generic_visit(node)

    def validate(self):
        """
        Run the check.
        This prints out all the warnings in the order they occured in the
        code.
        """
        with open(self._filename) as f:
            code = f.read()

        self.visit(parse(code, self._filename))

        # Sort the warnings so that they are printed in the order the code
        # appears in the file.
        for warning in sorted(self._warnings):
            if isinstance(warning, self._filters):
                continue

            print(
                '{fl}:{warning}'.format(fl=self._filename, warning=warning),
                file=sys.stderr,
            )


@click.command()
@click.argument('filename', type=click.Path(exists=True))
def main(filename):
    SafetyCheck(filename).validate()


if __name__ == '__main__':
    main()
