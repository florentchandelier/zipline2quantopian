from necessary_import import *

def handle_data(context, data):
    # visually check for tapping in the margin
    check_cash_status(context) 
    record(leverage=context.account.leverage)
    
    context.performance_analysis.update_ds(data.items()[0][1]['dt'].date(), context.portfolio.portfolio_value)
    return


def initialize(context):
    
    context.global_fund_managed = 0.9
    
    weight1 = 0.5
    weight2 = 1-weight1
    start1_portf_allocation = weight1 *context.global_fund_managed
    start2_portf_allocation = weight2 *context.global_fund_managed
    
    context.s1 = strat1(context, start1_portf_allocation)
    context.s2 = strat2(context, start2_portf_allocation)
    
    # store portfolio_value when fast_backtest is activated    
    context.performance_analysis = []
    
    context.instrument = context.s1.instrument
    context.instrument += context.s2.instrument
    
    context.cagr_period = 0
    
    set_init_common (context)  
    return
