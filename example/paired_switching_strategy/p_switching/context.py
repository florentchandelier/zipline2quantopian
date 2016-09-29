from necessary_import import *

def init_zip (context):
    context.performance_analysis = zp_performance_summary.performance()
    context.startDate = datetime(2004, 1, 1, 0, 0, 0, 0, pytz.utc)
    context.endDate = datetime(2015, 1, 1, 0, 0, 0, 0, pytz.utc) 
    return

def set_init_common (context):
    init_zip (context)
    
    set_symbol_lookup_date('2015-1-1')
    set_commission(commission.PerShare(cost=0.005, min_trade_cost=1.00)) 
              
    for strategy in context.portfolio_manager.strategies:
        sched_params_list = strategy.get_schedule_function()
        for params in sched_params_list:
            context.schedule_function(params['func'], params['date_rule'],
            params['time_rule'], params['half_days'])

    '''
        OrderManager
    '''
    
    context.schedule_function(context.order_manager.unfilled_store,
                  date_rule=date_rules.every_day(),
                  time_rule=time_rules.market_close(hours=0, minutes=15))
   
    context.schedule_function(context.order_manager.unfilled_restore,
                  date_rule=date_rules.every_day(),
                  time_rule=time_rules.market_open(hours=0, minutes=45))
    
    # execute order_book every 30 minutes
    for minute in range(60, 390, 30):  
        schedule_function(context.order_manager.update, date_rules.every_day(), time_rules.market_open(minutes = minute))
        
    '''
        EndOf OrderManager
    ''' 
                  
    context.schedule_function(get_cagr,
                  date_rule=date_rules.month_start(days_offset=5),
                  time_rule=time_rules.market_open(hours=4, minutes=0))
    
    context.schedule_function(check_cash_status, 
                  date_rule=date_rules.every_day(),
                  time_rule=time_rules.market_open(hours=2, minutes=3))
    
    context.schedule_function(record_func, 
                  date_rule=date_rules.every_day(),
                  time_rule=time_rules.market_open(hours=1, minutes=7)) 
                  
    return