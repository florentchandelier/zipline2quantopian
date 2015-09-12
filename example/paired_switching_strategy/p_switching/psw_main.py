from necessary_import import *

def handle_data(context, data):
    # visually check for tapping in the margin
    check_cash_status(context) 
    record(leverage=context.account.leverage)
    record(equity_line=context.portfolio.portfolio_value)
    
    context.performance_analysis.update_ds(data.items()[0][1]['dt'].date(), context.portfolio.portfolio_value)
    return


def initialize(context): 
    context.psw = paired_switching(context)
    # store portfolio_value when fast_backtest is activated    
    context.performance_analysis = []
    
    context.instrument = {'equity':symbol('SPY'), 'treasury':symbol('TLT')} 
    context.nbSwitch = 0
       
    context.lookback = 3*21 # 4 months period, 21 trading days per month
    
    context.Periodicity = 1 # every x period ; 1 means every period
    context.periodCount = 0
    
    context.cagr_period = 0
    context.global_fund_managed = 0.9
    
    context.max_priceslippage = (float(0.5)/100)

    set_init_common (context)     
    
    return