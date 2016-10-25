from necessary_import import *; from AnalyticsManager import *;

'''
    StrategyPortfolio is reponsible for monitoring each strategy.
    - position size
    - strategy pnl
    - strategy cash & open positions
'''

class StrategyPortfolio (object, AnalyticsManager):
    def __init__ (self, context, name):
        # by default, the Portfolio logger is set to output to the console
        # at a level sufficient to report problems.
        self.context = context
        self.name = name
        AnalyticsManager.__init__(self, analytics_name=name+'_StrategyPortfolio')
        self.set_log_option(logconsole=True, logfile=False, level=3)
        
        self.total_value = 0
        # instrument:dollar_value:orderid (dollar is more robust than nb shares as 
        # order_fill can be delayed by OrderManager)
        self.assets = dict()

#        self.columns = ['instrument','current_dollar', 'orderid', 'past_dollar', 'current_pos', 'past_pos']
        self.columns = ['instrument','pos', 'orderid', 'filled']
        self.position_tracking = pd.DataFrame(columns=self.columns)
    
        self.allocation = 0
        
        return
        
#    def get_total_assets_value (self):
#        return

    def create_empty_pos_dict (self):
        return pd.DataFrame(columns=self.columns)
        
    def set_allocation(self, val):
        self.allocation = val
        return
        
    def get_orders (self):
        orderid = []
        df = self.position_tracking
        
        dropouts = []
        for i in range(len(df)):
            order = df.iloc[i]
            
            if abs(float(order.pos)) - abs(float(order.filled)) > 0:
                orderid.append(order.orderid)
            elif order.pos == 0:
                '''
                clean up if instrument is not allocated
                '''
                dropouts.append(i)
                
        df = df.drop(df.index[dropouts])
        self.position_tracking = df
        return orderid
        
    def orderfilled (self, orderid, status):
        df = self.position_tracking
        
        index = df.index[df.orderid == orderid][0]
        df.filled.set_value(index, status)
        
        self.position_tracking = df
        return
        
    def get_allocation (self, allocation_type=None):
        if allocation_type == 'pct':
            return self.allocation
        if allocation_type == 'dollar': 
#            print("StrategyPortfolio: get_total_portfolio_value = " +str(self.portfolio_manager.get_total_portfolio_value()))
            return self.allocation * self.context.portfolio_manager.get_total_portfolio_value()
            
#    def get_instrument_current_value (self, inst):
#        return self.position_tracking.current_dollar[self.position_tracking.instrument==inst.symbol]
        
#    def update_asset (self, data, inst, current_value, orderid=0):
#        #
#        # update the amount of dollars to be hold by a strategy,
#        # for a given instrument, and monitor order fill/unfill;
#        #
#        #
#        df = self.position_tracking
#        
#        tgt_pos = self.context.order_manager.get_pos(data, inst, current_value)       
#        
#        past_dollar = 0.00
#        past_pos = 0.00
#        
#        if inst in df['instrument'].values:
#            past_dollar = df[df['instrument']==inst]['current_dollar']
#            past_pos = float(df[df['instrument']==inst]['current_pos'])
#            index = df.index[df.instrument == inst][0]
#
#            df.current_dollar.set_value(index,current_value)
#            df.orderid.set_value(index,orderid)
#            df.past_dollar.set_value(index,past_dollar)
#            df.past_pos = past_pos
#            df.current_pos = tgt_pos
#            
#        else:
#            '''
#            ignore_index will ignore the old ongoing index in your dataframe and 
#            ensure that the first row actually starts with index 1 instead of 
#            restarting with index 0.
#            '''
#            update = pd.DataFrame(np.array([[inst,current_value,orderid, past_dollar, tgt_pos, past_pos]]), columns=self.columns)
#            df = df.append(update, ignore_index=True)
#        
#        diff_pos = tgt_pos - past_pos
#        self.context.order_manager.add_position(inst, diff_pos)
#        self.position_tracking = df
#        
#        msg = " position_tracking \n" +str(self.position_tracking)
#        self.add_log('debug',msg)
#        
#        return
        
    def update_asset (self, data, inst, dollar, orderid=0):
        #
        # update the amount of dollars to be hold by a strategy,
        # for a given instrument, and monitor order fill/unfill;
        #
        #
        
        df = self.position_tracking
        
        current_value = 0
        current_pos = 0
        if inst in df['instrument'].values:
            current_pos = float(df[df['instrument']==inst]['pos'])
            current_value = current_pos * float(data.current(symbol(inst),'price'))
            
        new_pos = 0
        if dollar == 0 and current_pos > 0:
            [pos, orderid] = self.context.order_manager.submit_orderposition(data, symbol(inst), pos=-current_pos)
            new_pos = 0 
        else:
            diff_dollar = dollar - current_value        
            [pos, orderid] = self.context.order_manager.submit_dollarvalue(data, symbol(inst), dollar=diff_dollar)
            new_pos = current_pos+pos
          
        filled = 0
        if inst in df['instrument'].values:
#            past_dollar = df[df['instrument']==inst]['current_dollar']
#            past_pos = float(df[df['instrument']==inst]['current_pos'])
            index = df.index[df.instrument == inst][0]

            df.pos.set_value(index,new_pos)
            df.orderid.set_value(index,orderid)
            df.orderid.set_value(index,filled)
            
        else:
            '''
            ignore_index will ignore the old ongoing index in your dataframe and 
            ensure that the first row actually starts with index 1 instead of 
            restarting with index 0.
            '''
            update = pd.DataFrame(np.array([[inst,new_pos,orderid, filled]]), columns=self.columns)
            df = df.append(update, ignore_index=True)                    
        
        self.position_tracking = df
        return