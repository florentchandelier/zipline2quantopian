from necessary_import import *

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
        print( str(data[context.stocks[0]].datetime.year) +" CAGR = " +str(cagr))
    return
    
def check_cash_status(context):
    
    if context.portfolio.cash < 0:
        if context.env == 'quantopian':
            log.info("Negative Cash Balance = %4.2f" % (context.portfolio.cash) )
        else:
            print("Negative Cash Balance = %4.2f" % (context.portfolio.cash))
    return
