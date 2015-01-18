import os, sys
lib_path = os.path.abspath('../generic_modules/')
sys.path.append(lib_path)

from zipline.api import order_target, record, symbol, order_target_percent, history, symbols
from zipline.algorithm import TradingAlgorithm
from zipline.finance import trading, commission, slippage
import zipline.utils.events
from zipline.utils.events import (EventManager, make_eventrule, DateRuleFactory, TimeRuleFactory)
from zipline.utils.events import DateRuleFactory as date_rules
from zipline.utils.events import TimeRuleFactory as time_rules
from zipline.utils.factory import load_from_yahoo

import pylab as pl
import matplotlib.pyplot as plt
from zp_plot import *

from quantopian_import import *

from generic_modules.perf_analysis import *
from generic_modules.stock_metrics import *