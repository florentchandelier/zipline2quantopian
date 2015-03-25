## Exported with zipline2quantopian (c) Florent chandelier - https://github.com/florentchandelier/zipline2quantopian ##
 

 #### File: ./global_import/quantopian_import.py ###
import math
import pandas as pd
import numpy as np
from scipy import stats as scistats
import operator
import itertools

from datetime import datetime
import pytz
from zipline.api import get_environment
 

 #### Next File ###
 

 #### File: multi_strategy/strat2/strat2_core.py ###

class strat2():
    
    def __init__(self, context, portf_allocation):
        self.context = context
        self.lookback = 3*21
        self.instrument = symbols('EBAY')
        self.portf_allocation = portf_allocation
        
        return
        
    def abs_mom_up (self, data):
        inst = self.instrument[0]
        
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
        inst = self.instrument[0]
        
        mom = self.abs_mom_up(data)
        
        # mom = -1 if Nan values
        dic = self.create_dict()
        if mom == 1:
#             order_target_percent(inst, 1* self.portf_allocation)
             dic[inst] = 1* self.portf_allocation
        elif mom == 0:
#            order_target_percent(inst, 0)
            dic[inst] = 0
            
        return dic
            
    def create_dict(self): 
        default_values = np.zeros(len(self.instrument))
        return dict(zip(self.instrument,default_values)) 

 #### Next File ###
 

 #### File: multi_strategy/strat1/strat1_core.py ###

class strat1():
    
    def __init__(self, context, portf_allocation):
        self.context = context
        self.lookback = 3*21
        self.instrument = symbols('YHOO')
        self.portf_allocation = portf_allocation
        
        return
        
    def abs_mom_up (self, data):
        inst = self.instrument[0]
        
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
        inst = self.instrument[0]
        
        mom = self.abs_mom_up(data)
        
        # mom = -1 if Nan values
        dic = self.create_dict()
        if mom == 1:
#             order_target_percent(inst, 1* self.portf_allocation)
             dic[inst] = 1* self.portf_allocation
        elif mom == 0:
#            order_target_percent(inst, 0)
            dic[inst] = 0
        
        return dic
            
    def create_dict(self): 
        default_values = np.zeros(len(self.instrument))
        return dict(zip(self.instrument,default_values)) 

 #### Next File ###
 

 #### File: multi_strategy/strat_main.py ###

def handle_data(context, data):
    # visually check for tapping in the margin
    check_cash_status(context) 
    record(leverage=context.account.leverage)
    return


def initialize(context):
    
    context.global_fund_managed = 0.9
    
    weight1 = 0.5
    weight2 = 1-weight1
    start1_portf_allocation = weight1 *context.global_fund_managed
    start2_portf_allocation = weight2 *context.global_fund_managed
    
    context.s1 = strat1(context, start1_portf_allocation)
    context.s2 = strat2(context, start2_portf_allocation)
    
    context.instrument = context.s1.instrument
    context.instrument += context.s2.instrument
    
    context.cagr_period = 0
    
    context.env = get_environment('platform')    
    if context.env is 'quantopian' or get_environment('arena') == 'live' or get_environment('arena') == 'IB': 
    	set_commission(commission.PerTrade(cost=4.0))
    	set_slippage(slippage.FixedSlippage(spread=0.00))
    	schedule_function(rebalance,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=1, minutes=0))
                      
	schedule_function(get_cagr,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=5, minutes=0))
                      
    elif context.env == 'zipline':
        context.set_commission(commission.PerTrade(cost=4.0))
        context.set_slippage(slippage.FixedSlippage(spread=0.00))
        
        context.schedule_function(rebalance,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=1, minutes=0))
        context.schedule_function(get_cagr,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=5, minutes=0))
                      
        context.startDate = datetime(2004, 1, 1, 0, 0, 0, 0, pytz.utc)
        context.endDate = datetime(2015, 1, 1, 0, 0, 0, 0, pytz.utc)
    
    return
    
def rebalance(context, data):
    d1 = context.s1.rebalance(context, data)
    d2 = context.s2.rebalance(context, data)
    
    update_positions = combine_dicts(d1,d2,operator.add)
    
    for k in update_positions.keys():
        order_target_percent(k, update_positions[k])
            
    return
    
def combine_dicts(a, b, op=operator.add):
    return dict(a.items() + b.items() + [(k, op(a[k], b[k])) for k in set(b) & set(a)])
 

 #### Next File ###
 

 #### File: ./generic_modules/live_metrics.py ###

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
        initial_value = float(context.global_fund_managed*context.portfolio.starting_cash)
        current_value = float(context.portfolio.portfolio_value - (context.portfolio.starting_cash-initial_value) )
        
        cagr = np.power(current_value/initial_value, 1/float(context.cagr_period/12) )-1
        
        print( '['+str(data.items()[0][1].datetime.year) +'-'+str(data.items()[0][1].datetime.month)+'] > CAGR = ' +str(cagr))
    return
 

 #### Next File ###
 

 #### File: ./generic_modules/stock_metrics.py ###

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
