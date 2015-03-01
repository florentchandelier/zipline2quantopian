## Exported with zipline2quantopian (c) Florent chandelier - https://github.com/florentchandelier/zipline2quantopian ##
 

 #### File: ./global_import/quantopian_import.py ###
import math
import pandas as pd
import numpy as np
from scipy import stats as scistats

from datetime import datetime
import pytz
from zipline.api import get_environment
 

 #### Next File ###
 

 #### File: ./p_switching/psw_main.py ###

def handle_data(context, data):
    # visually check for tapping in the margin
    check_cash_status(context) 
    record(leverage=context.account.leverage)
    return


def initialize(context): 
    psw = paired_switching(context)
    
    context.instrument = {'equity':symbol('SPY'), 'treasury':symbol('TLT')} 
    context.nbSwitch = 0
       
    context.lookback = 3*21 # 4 months period, 21 trading days per month
    
    context.Periodicity = 1 # every x period ; 1 means every period
    context.periodCount = 0
    
    context.cagr_period = 0
    context.portf_allocation = 0.9
    
    context.max_priceslippage = (float(0.5)/100)     
    
    '''
    get_environment(field='platform')
    Returns information about the environment in which the backtest or live algorithm is running.
    If no parameter is passed, the platform value is returned. Pass * to get all the values returned in a dictionary.
    To use this method when running Zipline standalone, import get_environment from the zipline.api library.

    Parameters
    arena: Returns IB, live (paper trading), or backtest.
    data_frequency: Returns minute or daily.
    start: Returns the UTC datetime for start of backtest. In IB and live arenas, this is when the live algorithm was deployed.
    end: Returns the UTC datetime for end of backtest. In IB and live arenas, this is the trading day's close datetime.
    capital_base: Returns the float of the original capital in USD.
    platform: Returns the platform running the algorithm: quantopian or zipline.   
    '''    
    context.env = get_environment('platform')    
    if context.env is 'quantopian' or get_environment('arena') == 'live' or get_environment('arena') == 'IB': 

    	set_commission(commission.PerTrade(cost=4.0))
    	set_slippage(slippage.FixedSlippage(spread=0.00))
    	schedule_function(psw.ordering_logic,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=1, minutes=0))
                      
	schedule_function(get_cagr,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=5, minutes=0))
                      
    elif context.env == 'zipline':
        
    	context.set_commission(commission.PerTrade(cost=4.0))
    	context.set_slippage(slippage.FixedSlippage(spread=0.00))
     
    	context.schedule_function(psw.ordering_logic,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=1, minutes=0))
                      
	context.schedule_function(get_cagr,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=5, minutes=0))
                      
        context.startDate = datetime(2004, 1, 1, 0, 0, 0, 0, pytz.utc)
        context.endDate = datetime(2015, 1, 1, 0, 0, 0, 0, pytz.utc)
    
    return 

 #### Next File ###
 

 #### File: ./p_switching/psw_core.py ###

'''
OBJECTIVE
---------
Have a code that is fully compatible between Zipline and Quantopian, and that can be debug under Linux/Spyder.

-> To investigate Zip & Quant results : significative discrepencies on returns and the number of switches between pairs.


STRATEGY
--------
Lit.rev
    http://papers.ssrn.com/sol3/papers.cfm?abstract_id=1917044
    Paired-switching for tactical portfolio allocation
    Perf: 2003-2011: CAGR=15.0% (std=7.6%, min=6.7%)
    
Starting from the end of the first full week of the year, we look at the performance of the two equities
over the prior thirteen weeks (the ranking period), and buy the equity that has the higher return during
the ranking period. The position is held for thirteen weeks (the investment period). At the end of the
investment period the cycle is repeated.

Obviously, the number of weeks in the ranking period and the investment period can be varied
(independently) to optimize the strategy for a given pair of equities. Although the inevitable concerns
on over-fitting associated with such an optimization can be addressed by means of an
appropriate cross-validation methodology


IMPLEMENTATION
--------------
-> FROM http://www.portfolio123.com/mvnforum/viewthread_thread,6472
-> http://www.alphaarchitect.com/blog/2014/09/20/are-uber-simple-asset-allocation-systems-robust/

SPY / TLT
rebalance period: 1st day of month
ranking period: 4months
investment period: 1 month

-> http://seekingalpha.com/article/2714185-the-spy-tlt-universal-investment-strategy
The first is a switching strategy, which always switches to the ETF that had the best performance during the previous 3 months. 
This really simple switching strategy between TLT and SPY gave you a 14.8% return during the last 10 years, with twice 
the Sharpe ratio (return to risk) ratio of a simple SPY investment.
[2004-2011] CAGR=14.8%

'''

class paired_switching():
    
    def __init__(self, context):
        self.context = context
                      
    def ordering_logic(self, context, data):
        
        self.context.periodCount += 1
        
        # execute modulo context.Periodicity
        if self.context.periodCount % self.context.Periodicity == 0:
            ror = get_ratereturn (self.context,data, self.context.lookback)
            NbNan = np.count_nonzero(np.isnan(ror))
            if NbNan > 0:
                return -1
                
            index = self.context.instrument.values().index(ror.idxmax())
            self.allin(self.context.instrument.keys()[index])
        
        return
        
    def allin (self, inst):
        status = self.context.portfolio.positions[self.context.instrument[inst]].amount
        if status > 0:
            # do nothing, we are already invested
            pass
        
        else:
            self.context.nbSwitch +=1
    #        print("Date "+ str(data[context.stocks[0]].datetime) +"   Switch Nb: " +str(context.nbSwitch))

            up = self.context.instrument[inst]
            if (inst == 'treasury'):
                dwn = self.context.instrument['equity']
            else:
                dwn = self.context.instrument['treasury']
            
            order_target_percent(up, 1 *self.context.portf_allocation)
            order_target_percent(dwn, 0)                  
        
        return 

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
        initial_value = float(context.portf_allocation*context.portfolio.starting_cash)
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
