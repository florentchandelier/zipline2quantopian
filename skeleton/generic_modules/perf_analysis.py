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
    
def from_trough_to_depth_trough(results, thresh_dd=0, first_n=0):
    '''
     query the table for all drawdowns that were more than thres_dd%, 
     or the first_n biggest drawdowns;
     # http://stackoverflow.com/questions/27060037/pandas-way-to-groupby-like-itertools-groupby
    '''
    
    x = results['drawdowns']

    if thresh_dd >0: thresh_dd = -thresh_dd

    # this should return the max depth and length
    mask = x <= thresh_dd
    groupnum = mask.diff().fillna(method='bfill').cumsum()
        
    print("\n DRAWDOWNS ANALYSIS \n")
    print(" DD period below the " +str(thresh_dd) +"% watermark" )
    
    if max(groupnum) == 0:
        print("No occurence of DD <= " +str(thresh_dd) +"%")
        return None
        
    col = ['From', 'maxDD', 'To', 'mDD', 'Length', 'To mDD', 'Recovery']
    df = pd.DataFrame(columns=col)
    
    for key,grp in x.groupby(groupnum):
        if (max(grp) <= thresh_dd):
            length = len(grp)-1
            df.loc[len(df)] = [ grp.index[0].strftime("%Y-%m-%d"), grp.idxmin().strftime("%Y-%m-%d") ,grp.index[length].strftime("%Y-%m-%d"), 
                   grp.min(), (grp.index[length]-grp.index[0]).days, (grp.argmin()-grp.index[0]).days, (grp.index[length]-grp.argmin()).days]
    
    tot_days = (results.portfolio_value.index[len(results.portfolio_value)-1] - results.portfolio_value.index[0]).days
    print(" %-time in High DD watermark: " +str(round(100*df['Length'].sum()/tot_days ,0) ) +"% \n")        
    print df
    return df
    
#    if first_n > 0:
        
'''
Lastly, I wanted to know the proportion of the time that someone watching the 
strategy will be feeling the pain of watching the strategy go to those depths, 
so I took the sum of the "To Trough" column and divided it by the amount of 
days of the backtest
'''
