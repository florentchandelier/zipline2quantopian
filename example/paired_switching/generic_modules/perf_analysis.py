from necessary_import import *

def get_cagr(context, data):
    context.cagr_period += 1
    if (context.cagr_period % 12 == 0):
        # portf_value: Sum value of all open positions and ending cash balance. 
        cagr = np.power(context.portfolio.portfolio_value/float(context.portfolio.starting_cash), 1/float(context.cagr_period/12) )-1
        print("CAGR = " +str(cagr))
    return
