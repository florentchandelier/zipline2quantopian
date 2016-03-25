import os, sys
import time

lib_path = os.path.abspath('../../global_import/')
sys.path.append(lib_path)
from global_import.zipline_import import *
from global_import.quantopian_import import *

lib_path = os.path.abspath('../../generic_modules/')
sys.path.append(lib_path)
from generic_modules.generic import *


