from necessary_import import *

def handle_data(context, data):
    # visually check for tapping in the margin
    check_cash_status(context) 
    record(leverage=context.account.leverage)
    record(equity_line=context.portfolio.portfolio_value)
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