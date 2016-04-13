## Exported with zipline2quantopian (c) Florent chandelier - https://github.com/florentchandelier/zipline2quantopian ##
 

 #### File: global_import/quantopian_import.py ###
import math
import pandas as pd
import numpy as np
from scipy import stats as scistats
import operator
import itertools
#import sys, os

from datetime import datetime
import pytz


#from zipline.api import get_environment  

'''
For security reasons, algorithms can only import the following modules:
bisect
brokers
cmath
collections
copy
datetime
functools
heapq
itertools
math
numpy
operator
pandas
pykalman
pytz
QSTK
Queue
random
re
scipy
sklearn
statsmodels
talib
time
zipline
zlib
'''
 

 #### Next File ###
 

 #### File: TradingSystemArchitecture/0_quantopianAnalyticsManager.py ###

'''
AnalyticsManager compatible with the Quantopian log (from logBook) constraint
'''    

class AnalyticsManager ():
    '''
    this class manages logs and analytics
    '''
    def __init__(self, analytics_name, analytics_debug=False):
        
        self.analytics_name = analytics_name
        self.analytics_dump_dir = None
        
        self.__analyticsdump = False
        
        self.__log_state = False
        # create logger object
        self.__logger = log
        
        self.analytics = dict()
        return
        
    def set_log (self, status):
        self.__log_state = status
        
        if status:
            self.set_log_option()
        return
        
    def get_log (self):
        return self.__log_state
        
    def set_log_console (self, level):        
        msg = "logging activated in console"
        self.add_log('info',msg)
        return True
        
    def set_log_file (self, level):
        pass
        return True
        
    def set_log_option(self, logconsole=False, logfile=False, level=3):              
        # create logger with 'spam_application'
        self.__logger.level = level
        
        self.__log_state = logconsole or logfile
                   
        if logfile:
            self.set_log_file(level)            
        if logconsole:        
            self.set_log_console(level)

        return
        
    def add_log(self, logtype, msg):
        if not self.get_log():
            return

        # no critical in Quantopian logbook
        if logtype == 'critical':
            self.__logger.error(msg)        
        elif logtype == 'error':
            self.__logger.error(msg)
        elif logtype == 'warning':
            self.__logger.warning(msg)
        elif logtype == 'info':
            self.__logger.info(msg)
        elif logtype == 'debug':
            self.__logger.debug(msg)
        return
        
    def set_dumpanalytics (self, status):
        pass
        
    def get_dumpanalytics (self):
        pass
        
    def create_analytics (self, name, columns):
        pass
        return
        
    def insert_analyticsdata (self, name, row):
        pass      
        return
        
    def create_dir (self, outdir):
        pass
        
    def write_analytics_tocsv (self, output_directory):
        pass
            
         

 #### Next File ###
 

 #### File: TradingSystemArchitecture/OrderManager.py ###

'''
To Dos:
    1. Convert all target percent positions in a number of instruments in order to be 
    able to exit the specific position of a specific strategy
'''

class OrderManager(AnalyticsManager):
    def __init__ (self, context, name = "OrderManager"):
        
        # by default, the Portfolio logger is set to output to the console
        # at a level sufficient to report problems.
        AnalyticsManager.__init__(self, analytics_name=name)
        self.set_log_option(logconsole=True, logfile=False, level=3)
        
        self.context = context
        self.instruments = dict()
        
        # used to manage expected orders, making sure cash is freed by closing positions
        # before opening any new orders if necessary
        self.order_queue_open = dict()
        self.order_queue_close = dict()
        
        '''
        Analytics Manager
        '''
        self.create_analytics (name='pct_assets', columns=['timestamp', 'symbol', 'sell/target', 'buy/target'])
        self.create_analytics (name='position_size_tracking', columns=['timestamp', 'symbol', 'size'])

        return
    
    def add_instruments(self, values):
        self.instruments = combine_dicts(self.instruments,
                                         values,
                                         op=operator.add)
        return
    
    def send_order_through(self, data, instrument, dollar_value=0, style=MarketOrder()):
        '''
        MarketOrder()
        LimitOrder()
        '''
        nb_shares = int(np.floor(dollar_value /float(data[instrument].price) ))
        order(instrument, nb_shares, style=style)
        return
        
    def add_percent_orders(self, data, input_dict):
        # get current positions percentage of portfolio
        # to determine is the input_dict percentage of a position
        # corresponds to selling or buying said position
        self.update_current_positions(data)
        
        # distribute new percentage according to current position percentage
        for position in input_dict:
            if input_dict[position] > self.current_positions[position]:
                self.order_queue_open = combine_dicts({position:input_dict[position]},
                                         self.order_queue_open,
                                         op=operator.add)
            else:
                self.order_queue_close = combine_dicts({position:input_dict[position]},
                                         self.order_queue_close,
                                         op=operator.add)
        return
        
    def add_orders(self, input_dict):
        # loop through orders in dict and queue as close/open
        for mkt_order in input_dict:
            if input_dict[mkt_order] > 0:
                self.order_queue_open = combine_dicts({mkt_order:input_dict[mkt_order]},
                                         self.order_queue_open,
                                         op=operator.add)
            elif input_dict[mkt_order] < 0:
                self.order_queue_close = combine_dicts({mkt_order:input_dict[mkt_order]},
                                         self.order_queue_close,
                                         op=operator.add)                    
    
    def exit_positions (self, data):
        if len(self.order_queue_close)<1:
            return
            
        for k in self.order_queue_close:
            self.send_order_through(data, k, self.order_queue_close[k])
            
            msg = "\n\t"+str(get_datetime().date()) + " - exit_positions() order target in $: " +str(k) +" positions: " +str(self.order_queue_close[k])
            self.add_log('info',msg)
            
            if self.get_dumpanalytics():
                # columns=['timestamp', 'symbol', 'exit', 'enter']
                row = [get_datetime().date(), k, self.order_queue_close[k], '-']
                self.insert_analyticsdata('pct_assets',row)            
            
        self.order_queue_close = dict()
        return
        
    def enter_positions(self, data):
        '''
            Objective: Prevent "not enough funds available"
                
            we do not buy new positions if:
                (1) no orders, 
                (2) need to sell some and free some cash, 
                (3) some new positions are not yet filled and unfilled positions may free some cash
    
        
            Consideration: 
            this logic does not work on daily data (because of the pending 'closing transactions'
            the objective is to have a daily mode that is as close as possible to a minute mode            
            Consequently:
            >> daily mode: should allow every orders at once as all orders will be submitted at same time (EOD closing)
            >> minute mode: first close orders (sell long and close shorts), then move to buy more of current positions
        ''' 
        data_freq = get_environment(field='data_frequency')
        if data_freq == 'minute' and (len(self.order_queue_open) <1 or len(self.order_queue_close)>1 or len(get_open_orders()) > 0):
            if len(self.order_queue_close)>1:
                msg = "long position status: wait to fill all position_exit"
                print(msg)
            elif len(get_open_orders()) > 0:
                msg = "long positions status: waiting for unfilled orders to get through"
                print(msg)
            return
            
        for k in self.order_queue_open:
            self.send_order_through(data, k, self.order_queue_open[k])
            
            msg = "\n\t"+str(get_datetime().date()) + " - enter_positions() order target in $: " +str(k) +" positions: " +str(self.order_queue_open[k])
            self.add_log('info',msg)
            
            if self.get_dumpanalytics():
                # columns=['timestamp', 'symbol', 'exit', 'enter']
                row = [get_datetime().date(), k, '-', self.order_queue_open[k]]
                self.insert_analyticsdata('pct_assets',row) 
                
        self.order_queue_open = dict()
        return
        
    def update (self, data):
        '''
        NOTE
        In backtests, orders are submitted in one bar, and are filled in the 
        next bar. In daily mode your algorithm receives data once per day, at 
        market close; so an order submitted on Monday at 4PM will get filled 
        on Tuesday at 4PM. In minute mode, an order submitted at 10:00AM Monday
        will get filled at 10:01AM that same Monday, where there is much less 
        movement in the price. 
        '''
        self.exit_positions(data)
        self.enter_positions(data)
        
        if self.get_dumpanalytics():
            # loop through all current holdings
            for inst in self.context.portfolio.positions:
                # columns=['timestamp', 'symbol', 'size']
                row = [get_datetime().date(), inst, self.context.portfolio.positions[inst].amount]
                self.insert_analyticsdata('position_size_tracking',row)  
        return

    def update_current_positions(self, data):
        self.current_positions = dict()
        for k in self.instruments.values():
                self.current_positions[k] = (data[k].price*self.context.portfolio.positions[k].amount) / self.context.portfolio.portfolio_value
        return
        
#    def get_number_shares(self, data, percent_dict):
#        for position in input_dict:
#            target = input_dict[position]
#            # Sum value of all open positions and ending cash balance.
#            portfolio_totalvalue = self.context.portfolio.portfolio_value
#        return 

 #### Next File ###
 

 #### File: TradingSystemArchitecture/PortfolioManager.py ###

'''
 PortfolioManager manages the strategies of the portfolio and their allocation.

1.It verifies that total fund allocated does not exceed 100%, 
2. it may dynamically adjust strategies allocation based on market behavior.
''' 

#class Strategy(object):
#    def __init__ (self, name):
#        self.name = name        
#        return
 
class PortfolioManager(object, AnalyticsManager):

    def __init__(self, context, name):
        self.context = context # currently only required for get_portf_allocation       
        self.portf_name = name
        
        # by default, the Portfolio logger is set to output to the console
        # at a level sufficient to report problems.
        AnalyticsManager.__init__(self, analytics_name=name)
        self.set_log_option(logconsole=True, logfile=False, level=3)
        
        # list of strategies
        self.list_strategies = []
        self.portf_allocation = 0
        self.instruments = dict()
        self.strategies = list()
        
        self.order_manager = OrderManager(context, name = "OrderManager")
        
        return
        
    def add_strategy(self, value, allocation):
        if (self.portf_allocation + allocation > 1):
            msg = '\n\t Strategy named**'+str(value.name) +' ** cannot be added to portfolio. Total allocation exceeds 100%'
            self.add_log('error',msg)
            return
            
        if value.name in self.list_strategies:
            msg = '\n\t Strategy named ' +str(value.name) +' already exists and cannot be added to portfolio'
            self.add_log('error',msg)
            return
            
        value.portfolio.set_allocation(allocation)
        self.portf_allocation += allocation
        
        self.list_strategies.append(value.name)
        self.strategies.append(value)
        
        # Registrating with third-party methods
        #
#        value.set_send_percent_orders(self.order_manager.add_percent_orders)
#        value.set_send_order_through(self.order_manager.send_order_through)
#        value.set_add_orders(self.order_manager.add_orders)
#        value.portfolio.set_portf_allocation(self.get_portf_allocation)
        #
        # End of registration
        
        self.set_instruments(value.get_instruments())
        self.order_manager.add_instruments(value.get_instruments())
        
        return
        
    def get_portf_allocation(self):
        return self.portf_allocation
            
    def get_total_portfolio_value (self):
        return self.context.portfolio.portfolio_value
        
    def set_instruments(self, value):
        self.instruments = merge_dicts(self.instruments, value)
        return
        
    def get_instruments(self):
        return self.instruments
        
    def analytics_save (self, outdir):
        savepath = outdir+self.portf_name+'/'
        
        for strat in self.strategies:
            if strat.get_dumpanalytics():
                strat.write_analytics_tocsv(output_directory=savepath)
                
        if self.order_manager.get_dumpanalytics():
            self.order_manager.write_analytics_tocsv(output_directory=savepath)
            
    def sendorder_to_ordermanager (self, target_dollar_value):
        #
        # target_dollar_value: dictionary of positions target in dollar value
        # dict{inst; dollarvalue}
        #
        self.order_manager.add_orders (target_dollar_value)
        return
        
    def handle_data (self, data):
        self.order_manager.update(data)
        return
 

 #### Next File ###
 

 #### File: TradingSystemArchitecture/StrategyDesign.py ###

'''

to dos:


StrategyDesign is responsible for the basic strategy interactions. 
0. It receives fund allocation from the PortfolioManager

1. It registers with OrderManagement through the PortfolioManager, specifically
 to the method for executing orders.

2. It receives a strategy order and apply the allocation of funds set by the
 PortfolioManager.

3. It holds all the required schedule_functions to add in Initialize()
'''

class StrategyDesign(object, AnalyticsManager):

    def __init__(self, context, name):      
        self.name = name
        self.context = context
        
        # by default, the Portfolio logger is set to output to the console
        # at a level sufficient to report problems.
        AnalyticsManager.__init__(self, analytics_name=name)
        self.set_log_option(logconsole=True, logfile=False, level=3)
        
        self.schedule_func_list = []
        self.instruments = dict()
        
        self.portfolio = StrategyPortfolio(context.portfolio_manager)
        self.portfolio.set_allocation(0)
        return
    
    def send_order (self, data, signal_type, value):
        # handling a dictionary of percent order(s)
        #
        if signal_type == 'pct':
            self._send_percent_order (data, value)
        return
    
    def _send_percent_order (self, data, pct):
        # for a strategy, what makes sense is the dollar value for a position
        # it should be the job of the OrderManager to get proper position size
        # based on market value when order will be filled (there might be 
        # priorities for orders to be filled, thus last time position sizing
        # is a good practice)
        target_dollar_value = dict()
        
        allocated_value = self.portfolio.get_allocation(allocation_type='dollar')
        # convert each instrument pct into a dollar value position
        for inst in pct:
            # inherently takes into account strategy allocation in portfolio
            dollar_value = pct[inst] *allocated_value
            # update desired strategy targeted allocation
            self.portfolio.assets[inst] = dollar_value
            
            current_value = self.context.portfolio.positions[inst].amount *data[inst].price
            tgt_dollar_value = self.portfolio.assets[inst] - current_value
            target_dollar_value = merge_dicts(target_dollar_value, {inst:tgt_dollar_value})
            
        self.context.portfolio_manager.sendorder_to_ordermanager (target_dollar_value)
        return
        
    def set_name(self, value):
        self.name = value
        return
        
    def add_schedule_function(self, func):
        self.schedule_func_list.append(func)
        return
        
    def get_schedule_function(self):
        return self.schedule_func_list
        
    def get_instruments(self):
        return self.instruments
        
    def add_instruments (self, instrument_dict):
        self.instruments = merge_dicts(self.instruments, instrument_dict)
        
        for inst in instrument_dict:
            if instrument_dict[inst] not in self.portfolio.assets:
                self.portfolio.assets = merge_dicts(self.portfolio.assets, {instrument_dict[inst]:0})
        return
 

 #### Next File ###
 

 #### File: TradingSystemArchitecture/StrategyPortfolio.py ###

class StrategyPortfolio (object):
    def __init__ (self, portfolio_manager):
        self.total_value = 0
        # instrument:dollar_value (dollar is more robust than nb shares as 
        # order_fill can be delayed by OrderManager)
        self.assets = dict()
        
        self.allocation = 0
        self.portfolio_manager = portfolio_manager
        
        return
        
#    def get_total_assets_value (self):
#        return
        
    def set_allocation(self, val):
        self.allocation = val
        return
        
    def get_allocation (self, allocation_type=None):
        if allocation_type == 'pct':
            return self.allocation
        if allocation_type == 'dollar':            
            return self.allocation * self.portfolio_manager.get_total_portfolio_value()
        
#    def update_asset (self, inst, amount):
#        if inst in self.assets:
#            self.assets[inst] += amount    
#        return 

 #### Next File ###
 

 #### File Auto Generated from Zipline: multi_strategy/context.py ###
def set_init_common (context):
    # init_zip (context) is removed for Quantopian
    
    set_commission(commission.PerTrade(cost=4.0))
    set_slippage(slippage.FixedSlippage(spread=0.00))
                  
    for strategy in context.portfolio_manager.strategies:
        strategy.get_schedule_function()
                  
    schedule_function(get_cagr,
                  date_rule=date_rules.month_start(),
                  time_rule=time_rules.market_open(hours=5, minutes=0))
                  
    return
 

 #### Next File ###
 

 #### File: multi_strategy/main.py ###

def handle_data(context, data):
    
    context.portfolio_manager.handle_data(data)
    
    # visually check for accidental "borrowing of cash
    check_cash_status(context) 
    record(leverage=context.account.leverage)

    return
              
   
def initialize(context):
    name = "multi-strat"
    context.portfolio_manager = PortfolioManager(context, name)
    allocation = 0.9/2    
    
    s1 = strat1(context, name='tlt strategy')
    context.portfolio_manager.add_strategy(s1, allocation=allocation)
    
    s2 = strat2(context, name='spy strategy')
    context.portfolio_manager.add_strategy(s2, allocation=allocation)
           
    context.global_fund_managed = context.portfolio_manager.get_portf_allocation()                                             
    context.instrument = context.portfolio_manager.get_instruments()  
        
    # store portfolio_value when fast_backtest is activated    
    context.performance_analysis = []
        
    context.cagr_period = 0
    context.env = get_environment('platform')
    set_init_common (context)

    return
 

 #### Next File ###
 

 #### File: multi_strategy/strat1/strat1_core.py ###

class strat1(StrategyDesign):
    def __init__(self, context, name = 'stupid momentum strategy on TLT', instruments=None):
        StrategyDesign.__init__(self, context, name)

        self.context = context
        self.lookback = 3*21 # 4 months period, 21 trading days per month

        if instruments is None:        
            self.instruments = {'treasury':symbol('TLT')}
       
        self.add_schedule_function( schedule_function(self.rebalance,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=1, minutes=0))
        )

        '''
        Analytics Manager
        '''
        self.create_analytics (name='allocation', columns=['timestamp', 'treasury', 'mom'])
        
        return
        
    def abs_mom_up (self, data):
        inst = self.instruments.values()[0]
        
        prices = history(self.lookback, '1d', 'price')
        NbNan = np.count_nonzero(np.isnan(prices))
        if NbNan > 0:
            return -1
                
        mom = prices.mean()
        if data[inst].price > mom[inst]:
            return 1
        else:
            return 0
            
    def rebalance (self, context, data):
        inst = self.instruments.values()[0]        
        mom = self.abs_mom_up(data)
        if mom == -1:
            return
        # mom = -1 if Nan values
        target_percent_dict = dict()
        if mom == 1:
            target_percent_dict[inst] = 1
            msg = " TOY EXAMPLE MSG "+str(get_datetime().date()) + " - Long TLT: "
            self.add_log('info',msg)
        elif mom == 0:
            target_percent_dict[inst] = 0
            msg = " TOY EXAMPLE MSG "+str(get_datetime().date()) + " - Exit TLT: "
            self.add_log('info',msg)
        
        '''
        dumping anaytics: toy example as no value logging mom as-is
        '''
        if self.get_dumpanalytics():
            # columns=['timestamp', 'equity', 'treasury']
            row = [get_datetime().date(), target_percent_dict[self.instruments['treasury']],
                   mom]
            self.insert_analyticsdata('allocation',row)
            
        self.send_order(data, signal_type='pct', value=target_percent_dict) 
        return
 

 #### Next File ###
 

 #### File: multi_strategy/strat2/strat2_core.py ###

class strat2(StrategyDesign):        

    def __init__(self, context, name = 'stupid momentum strategy on SPY', instruments=None):
        StrategyDesign.__init__(self, context, name)

        self.context = context
        self.lookback = 3*21 # 4 months period, 21 trading days per month

        if instruments is None:        
            self.instruments = {'equity':symbol('SPY')}
       
        self.add_schedule_function( schedule_function(self.rebalance,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=1, minutes=0))
        )

        '''
        Analytics Manager
        '''
        self.create_analytics (name='allocation', columns=['timestamp', 'equity', 'mom'])
        return
        
    def abs_mom_up (self, data):
        inst = self.instruments.values()[0]
        
        prices = history(self.lookback, '1d', 'price')
        NbNan = np.count_nonzero(np.isnan(prices))
        if NbNan > 0:
            return -1
                
        mom = prices.mean()
        if data[inst].price > mom[inst]:
            return 1
        else:
            return 0
            
    def rebalance (self, context, data):
        inst = self.instruments.values()[0]        
        mom = self.abs_mom_up(data)
        if mom == -1:
            return
        
        # mom = -1 if Nan values
        target_percent_dict = dict()
        if mom == 1:
            target_percent_dict[inst] = 1
            msg = " TOY EXAMPLE MSG "+str(get_datetime().date()) + " - Long SPY: " 
            self.add_log('info',msg)
        elif mom == 0:
            target_percent_dict[inst] = 0
            msg = " TOY EXAMPLE MSG "+str(get_datetime().date()) + " - Exit SPY: "
            self.add_log('info',msg)
            
        '''
        dumping anaytics: toy example as no value logging mom as-is
        '''
        if self.get_dumpanalytics():
            # columns=['timestamp', 'equity', 'treasury']
            row = [get_datetime().date(), target_percent_dict[self.instruments['equity']],
                   mom]
            self.insert_analyticsdata('allocation',row)
        
        self.send_order(data, signal_type='pct', value=target_percent_dict) 
        return
 

 #### Next File ###
 

 #### File: generic_modules/stock_metrics.py ###

def get_ratereturn (context, data, lookback):
    rateReturn = 0
    # Request history from the last period days
    prices = history(lookback, '1d', 'price')
    # compute returns over the period
    rateReturn = (prices.ix[-1] - prices.ix[0]) / prices.ix[0]
    return(rateReturn)
    
def get_std (context, lookback):
    std=0
    # Request history from the last period days
    prices = history(lookback, '1d', 'price')
    # compute standard deviation over period
    std = prices.std()
    return (std)
 

 #### Next File ###
 

 #### File: generic_modules/generic.py ###

def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result   

def close_all_positions(instruments):
    for inst in instruments:
        order_target_percent(inst, 0)
    
    return
    
#def close_all_hedge(context):
#    if context:
#        order_target_percent(context.instrument['hedge_treasury'], 0)    
#    return
    
def is_nan_price (price):
    NbNan = np.count_nonzero(np.isnan(price))
    if NbNan > 0:
        return True
    else:
        False
        
def get_weight_list(nb_list, start, finish, increment, precision=2):
    weights = np.arange(start, finish+increment,increment)
    lists = []
    lw = []
    lw = [round(x,2) for x in list(np.around(weights, precision))]
    
    for x in range(nb_list):
        lists.append(lw)
    return lists

def get_permutation(wl, op=operator.eq, condition_value=1, topn = 0):
    '''
    s: a list of weight
    op: operator conditioning the permutation validity (ex: summ weight is 100%)
    
    return: list of potential allocation weights
    '''
    ll=list(itertools.product(*wl))
    ll = ll[1:]
    
    if topn > 0:
        # get max number instrument (forcing a maximum nb of non-zero)
        sm_topn = [op(len(np.nonzero(np.asarray(it))[0]), topn) for it in ll]
        ind = [index for index,value in enumerate(sm_topn) if value==True]
        ll = [ll[i] for i in ind]
        # get min weight for each instrument
        sm_min = [max(it)<=0.6 for it in ll]
        ind = [index for index,value in enumerate(sm_min) if value==True]
        ll = [ll[i] for i in ind]
        
    sm=[op(sum(item), condition_value) for item in ll]
    indices=[index for index,value in enumerate(sm) if value==True]
    
    return [ll[i] for i in indices]
    
def combine_dicts(a, b=None, op=operator.add, force_absolute_values = False):
    if b == None:
        return a
    if force_absolute_values:
        return dict(a.items() + b.items() + [(k, op(abs(a[k]), abs(b[k]))) for k in set(b) & set(a)])
    else:
        return dict(a.items() + b.items() + [(k, op(a[k], b[k])) for k in set(b) & set(a)])
    
def create_zero_target_percent(inst): 
    default_values = np.zeros(len(inst))
    return dict(zip(inst,default_values))
 

 #### Next File ###
 

 #### File: generic_modules/live_metrics.py ###

def check_cash_status(context):
    
    if context.portfolio.cash < 0:
        if context.env == 'quantopian':
            log.info("Negative Cash Balance = %4.2f" % (context.portfolio.cash) )
        else:
            print("Negative Cash Balance = %4.2f" % (context.portfolio.cash))
    return
    
def get_cagr(context, data):
# in [def initialize(context)] add 
#	- context.cagr_period = 0
#	- in Z & Q: context.schedule_function(get_cagr,
#                      date_rule=date_rules.month_start(days_offset=5),
#                      time_rule=time_rules.market_open(hours=1, minutes=0))
	
    context.cagr_period += 1
    if (context.cagr_period % 12 == 0):
        # portf_value: Sum value of all open positions and ending cash balance. 
        # context.global_fund_managed: holds the weight factor allocated to the strategy (usually <1)
        initial_value = float(context.global_fund_managed*context.portfolio.starting_cash)
        initial_residual = float(context.portfolio.starting_cash - initial_value)
        current_value = float(context.portfolio.portfolio_value - initial_residual )
        
        cagr = np.power(current_value/initial_value, 1/float(context.cagr_period/12) )-1
        
        print( '['+str(data.items()[0][1].datetime.year) +'-'+str(data.items()[0][1].datetime.month)+'] > CAGR = ' +str(cagr))
    return
 

 #### Next File ###
