from necessary_import import *

def get_cagr(context, data):
''' in [def initialize(context)] add 
	- context.cagr_period = 0
	- in Z & Q: context.schedule_function(get_cagr,
                      date_rule=date_rules.month_start(days_offset=5),
                      time_rule=time_rules.market_open(hours=1, minutes=0))
'''
    context.cagr_period += 1
    if (context.cagr_period % 12 == 0):
        # portf_value: Sum value of all open positions and ending cash balance. 
        cagr = np.power(context.portfolio.portfolio_value/float(context.portfolio.starting_cash), 1/float(context.cagr_period/12) )-1
        print("CAGR = " +str(cagr))
    return
