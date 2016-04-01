from necessary_import import *; from context import *; from pswitching import *; 

def handle_data(context, data):
    
    context.portfolio_manager.handle_data(data)
    
    # visually check for accidental "borrowing of cash
    check_cash_status(context) 
    record(leverage=context.account.leverage)

    context.performance_analysis.update_ds(data.items()[0][1]['dt'].date(), context.portfolio.portfolio_value)
    return
              
   
def initialize(context):
    name = 'pswitching'
    context.portfolio_manager = PortfolioManager(context, name)
    
    s1 = pswitching(context, name='pair switching strategy 1')
    context.portfolio_manager.add_strategy(s1, allocation=0.9)
           
    context.global_fund_managed = context.portfolio_manager.get_portf_allocation()                                             
    context.instrument = context.portfolio_manager.get_instruments()  
        
    # store portfolio_value when fast_backtest is activated    
    context.performance_analysis = []
        
    context.cagr_period = 0
    context.env = get_environment('platform')
    set_init_common (context)
    
    return
    


    
    
