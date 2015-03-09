import os, sys
lib_path = os.path.abspath('../global_import/')
sys.path.append(lib_path)

from global_import.zipline_import import *
from strat1.strat1_core import *
from strat2.strat2_core import *