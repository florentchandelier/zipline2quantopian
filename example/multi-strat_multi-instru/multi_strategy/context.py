from necessary_import import *

def init_zip (context):
    context.performance_analysis = zp_performance_summary.performance()
    context.startDate = datetime(2004, 1, 1, 0, 0, 0, 0, pytz.utc)
    context.endDate = datetime(2015, 9, 3, 0, 0, 0, 0, pytz.utc)
     
    return
    
def set_init_common (context):
    init_zip (context)
    
    context.set_commission(commission.PerTrade(cost=4.0))
    context.set_slippage(slippage.FixedSlippage(spread=0.00))
        
    context.schedule_function(rebalance,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=1, minutes=0))
    context.schedule_function(get_cagr,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=5, minutes=0))
                         
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