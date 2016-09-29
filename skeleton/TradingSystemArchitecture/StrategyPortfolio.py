from necessary_import import *; from AnalyticsManager import *;

'''
    StrategyPortfolio is reponsible for monitoring each strategy.
    - position size
    - strategy pnl
    - strategy cash & open positions
'''

class StrategyPortfolio (object, AnalyticsManager):
    def __init__ (self, portfolio_manager):
        # by default, the Portfolio logger is set to output to the console
        # at a level sufficient to report problems.
        name = ''
        AnalyticsManager.__init__(self, analytics_name=name)
        self.set_log_option(logconsole=True, logfile=False, level=3)
        
        self.total_value = 0
        # instrument:dollar_value:orderid (dollar is more robust than nb shares as 
        # order_fill can be delayed by OrderManager)
        self.assets = dict()

        self.columns = ['instrument','current_dollar', 'orderid', 'past_dollar']
        self.position_tracking = pd.DataFrame(columns=self.columns)
    
        self.allocation = 0
        self.portfolio_manager = portfolio_manager
        
        return
        
#    def get_total_assets_value (self):
#        return
        
    def set_allocation(self, val):
        self.allocation = val
        return
        
    def get_allocation (self, allocation_type=None):
        if allocation_type == 'pct':
            return self.allocation
        if allocation_type == 'dollar': 
#            print("StrategyPortfolio: get_total_portfolio_value = " +str(self.portfolio_manager.get_total_portfolio_value()))
            return self.allocation * self.portfolio_manager.get_total_portfolio_value()
        
    def update_asset (self, inst, current_value, orderid=0):
        #
        # update the amount of dollars to be hold by a strategy,
        # for a given instrument, and monitor order fill/unfill;
        #
        #
        df = self.position_tracking 
        
        if inst in df['instrument'].values:
            past_dollar = df[df['instrument']==inst]['current_dollar']
            index = df.index[df.instrument == inst][0]
            df.current_dollar.set_value(index,current_value)
            df.orderid.set_value(index,orderid)
            df.past_dollar.set_value(index,past_dollar)
        else:
            '''
            ignore_index will ignore the old ongoing index in your dataframe and 
            ensure that the first row actually starts with index 1 instead of 
            restarting with index 0.
            '''
            update = pd.DataFrame(np.array([[inst,current_value,orderid,0]]), columns=self.columns)
            self.position_tracking = df.append(update, ignore_index=True)
            
        msg = " position_tracking \n" +str(df)
        self.add_log('warning',msg)
        return