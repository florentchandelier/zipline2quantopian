from necessary_import import *

def handle_data(context, data):
    # visually check for tapping in the margin
    check_cash_status(context) 
    record(leverage=context.account.leverage)
    return


def initialize(context):
    
    context.portf_allocation = 0.9
    
    weight1 = 0.5
    weight2 = 1-weight1
    start1_portf_allocation = weight1 *context.portf_allocation
    start2_portf_allocation = weight2 *context.portf_allocation
    
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