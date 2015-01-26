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
    
def from_through_to_depth_through(x, thresh_dd=0, first_n=0):
    '''
     query the table for all drawdowns that were more than thres_dd%, 
     or the first_n biggest drawdowns;
     # http://stackoverflow.com/questions/27060037/pandas-way-to-groupby-like-itertools-groupby
    '''

    if thresh_dd >0: thresh_dd = -thresh_dd

    if thresh_dd < 0:
        # this should return the max depth and length
        mask = x <= thresh_dd
        groupnum = mask.diff().fillna(method='bfill').cumsum()
        
#        if np.count_nonzero(x[groupnum==0]<=thresh_dd) == 0:
#            x = x[groupnum>0]            
#            groupnum = groupnum[groupnum>0]
#            
#        
#        max_num = max(groupnum)
#        if np.count_nonzero(x[groupnum==max_num]<=thresh_dd) == 0:
#            x = x[groupnum<max_num]
#            groupnum = groupnum[groupnum<max_num]
            
        print("\n DRAWDOWNS ANALYSIS \n")
#        print("Nb of periods where DD <= " +str(thresh_dd) +"% : " +str(max(groupnum)) )
        
        print("DD : Length   Depth")        
        for key,grp in x.groupby(groupnum):
#            print ("tet = " +str(grp.min()) )
#            print grp.date
#            print key
            if (max(grp) <= thresh_dd):
                print("       " +str(len(grp)) +"     " +str(round(grp.min(),2)))
            
    return x.groupby(groupnum)
    
#    if first_n > 0:
        
'''
Lastly, I wanted to know the proportion of the time that someone watching the 
strategy will be feeling the pain of watching the strategy go to those depths, 
so I took the sum of the "To Trough" column and divided it by the amount of 
days of the backtest
'''
