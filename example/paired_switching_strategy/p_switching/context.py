from necessary_import import *

def init_zip (context):
    context.performance_analysis = zp_performance_summary.performance()
    context.startDate = datetime(2004, 1, 1, 0, 0, 0, 0, pytz.utc)
    context.endDate = datetime(2015, 1, 1, 0, 0, 0, 0, pytz.utc) 
    return
    
def set_init_common (context):
    init_zip (context)
    
    context.set_commission(commission.PerTrade(cost=4.0))
    context.set_slippage(slippage.FixedSlippage(spread=0.00))
                  
    for strategy in context.portf.list_strategies:
        strategy.get_schedule_function()
                  
    context.schedule_function(get_cagr,
                  date_rule=date_rules.month_start(),
                  time_rule=time_rules.market_open(hours=5, minutes=0))
                  
    return