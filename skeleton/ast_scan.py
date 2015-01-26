#!/usr/bin/env python

from __future__ import print_function

from abc import ABCMeta, abstractmethod
from ast import NodeVisitor, Name, parse
from six import with_metaclass
import sys

import click


class Warning(with_metaclass(ABCMeta)):
    def __init__(self, node):
        self.node = node

    @property
    def header(self):
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
        raise NotImplementedError()


def create_warning(msg):
    """
    Create a new warning type that prints a message after a header.
    """
    str_ = '{{header}}: {msg}'.format(msg=msg)

    class _Warning(Warning):
        def __str__(self):
            return str_.format(header=self.header)

    return _Warning

# A warning the represents an `exec` statement.
ExecWarning = create_warning('`exec` statement found.')


def create_warning_from_function(fnname):
    """
    Construct a new warning type for a function.
    """
    return create_warning('`{fn}` function call found.'.format(fn=fnname))


# A mapping of illegal functions to warning types.
illegal_builtins_warnings = {
    fn: create_warning_from_function(fn)
    for fn in {
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
    def __init__(self, filename):
        self._filename = filename
        self._warnings = set()

    def visit_Exec(self, node):
        self._warnings.add(ExecWarning(node))
        return self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, Name):
            warning = illegal_builtins_warnings.get(node.func.id)
            if warning is not None:
                self._warnings.add(warning(node))

        return self.generic_visit(node)

    def validate(self):
        with open(self._filename) as f:
            code = f.read()

        self.visit(parse(code, self._filename))

        # Sort the warnings so that they are printed in the order the code
        # appears in the file.
        for warning in sorted(self._warnings):
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
