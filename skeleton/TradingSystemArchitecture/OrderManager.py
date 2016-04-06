from necessary_import import *; from AnalyticsManager import *;

'''
To Dos:
    1. Convert all target percent positions in a number of instruments in order to be 
    able to exit the specific position of a specific strategy
'''

class OrderManager(AnalyticsManager):
    def __init__ (self, context, name = "OrderManager"):
        
        # by default, the Portfolio logger is set to output to the console
        # at a level sufficient to report problems.
        AnalyticsManager.__init__(self, analytics_name=name)
        self.set_log_option(logconsole=True, logfile=False, level=log.WARNING)
        
        self.context = context
        self.instruments = dict()
        
        # used to manage expected orders, making sure cash is freed by closing positions
        # before opening any new orders if necessary
        self.order_queue_open = dict()
        self.order_queue_close = dict()
        
        '''
        Analytics Manager
        '''
        self.create_analytics (name='pct_assets', columns=['timestamp', 'symbol', 'sell/target', 'buy/target'])
        self.create_analytics (name='position_size_tracking', columns=['timestamp', 'symbol', 'size'])

        return
    
    def add_instruments(self, values):
        self.instruments = combine_dicts(self.instruments,
                                         values,
                                         op=operator.add)
        return
    
    def send_order_through(self, data, instrument, dollar_value=0, style=MarketOrder()):
        '''
        MarketOrder()
        LimitOrder()
        '''
        nb_shares = int(np.floor(dollar_value /float(data[instrument].price) ))
        order(instrument, nb_shares, style=style)
        return
        
    def add_percent_orders(self, data, input_dict):
        # get current positions percentage of portfolio
        # to determine is the input_dict percentage of a position
        # corresponds to selling or buying said position
        self.update_current_positions(data)
        
        # distribute new percentage according to current position percentage
        for position in input_dict:
            if input_dict[position] > self.current_positions[position]:
                self.order_queue_open = combine_dicts({position:input_dict[position]},
                                         self.order_queue_open,
                                         op=operator.add)
            else:
                self.order_queue_close = combine_dicts({position:input_dict[position]},
                                         self.order_queue_close,
                                         op=operator.add)
        return
        
    def add_orders(self, input_dict):
        # loop through orders in dict and queue as close/open
        for mkt_order in input_dict:
            if input_dict[mkt_order] > 0:
                self.order_queue_open = combine_dicts({mkt_order:input_dict[mkt_order]},
                                         self.order_queue_open,
                                         op=operator.add)
            elif input_dict[mkt_order] < 0:
                self.order_queue_close = combine_dicts({mkt_order:input_dict[mkt_order]},
                                         self.order_queue_close,
                                         op=operator.add)                    
    
    def exit_positions (self, data):
        if len(self.order_queue_close)<1:
            return
            
        for k in self.order_queue_close:
            self.send_order_through(data, k, self.order_queue_close[k])
            
            msg = "\n\t"+str(get_datetime().date()) + " - exit_positions() order target in $: " +str(k) +" positions: " +str(self.order_queue_close[k])
            self.add_log('info',msg)
            
            if self.get_dumpanalytics():
                # columns=['timestamp', 'symbol', 'exit', 'enter']
                row = [get_datetime().date(), k, self.order_queue_close[k], '-']
                self.insert_analyticsdata('pct_assets',row)            
            
        self.order_queue_close = dict()
        return
        
    def enter_positions(self, data):
        '''
            Objective: Prevent "not enough funds available"
                
            we do not buy new positions if:
                (1) no orders, 
                (2) need to sell some and free some cash, 
                (3) some new positions are not yet filled and unfilled positions may free some cash
    
        
            Consideration: 
            this logic does not work on daily data (because of the pending 'closing transactions'
            the objective is to have a daily mode that is as close as possible to a minute mode            
            Consequently:
            >> daily mode: should allow every orders at once as all orders will be submitted at same time (EOD closing)
            >> minute mode: first close orders (sell long and close shorts), then move to buy more of current positions
        ''' 
        data_freq = get_environment(field='data_frequency')
        if data_freq == 'minute' and (len(self.order_queue_open) <1 or len(self.order_queue_close)>1 or len(get_open_orders()) > 0):
            if len(self.order_queue_close)>1:
                msg = "long position status: wait to fill all position_exit"
                print(msg)
            elif len(get_open_orders()) > 0:
                msg = "long positions status: waiting for unfilled orders to get through"
                print(msg)
            return
            
        for k in self.order_queue_open:
            self.send_order_through(data, k, self.order_queue_open[k])
            
            msg = "\n\t"+str(get_datetime().date()) + " - enter_positions() order target in $: " +str(k) +" positions: " +str(self.order_queue_open[k])
            self.add_log('info',msg)
            
            if self.get_dumpanalytics():
                # columns=['timestamp', 'symbol', 'exit', 'enter']
                row = [get_datetime().date(), k, '-', self.order_queue_open[k]]
                self.insert_analyticsdata('pct_assets',row) 
                
        self.order_queue_open = dict()
        return
        
    def update (self, data):
        '''
        NOTE
        In backtests, orders are submitted in one bar, and are filled in the 
        next bar. In daily mode your algorithm receives data once per day, at 
        market close; so an order submitted on Monday at 4PM will get filled 
        on Tuesday at 4PM. In minute mode, an order submitted at 10:00AM Monday
        will get filled at 10:01AM that same Monday, where there is much less 
        movement in the price. 
        '''
        self.exit_positions(data)
        self.enter_positions(data)
        
        if self.get_dumpanalytics():
            # loop through all current holdings
            for inst in self.context.portfolio.positions:
                # columns=['timestamp', 'symbol', 'size']
                row = [get_datetime().date(), inst, self.context.portfolio.positions[inst].amount]
                self.insert_analyticsdata('position_size_tracking',row)  
        return

    def update_current_positions(self, data):
        self.current_positions = dict()
        for k in self.instruments.values():
                self.current_positions[k] = (data[k].price*self.context.portfolio.positions[k].amount) / self.context.portfolio.portfolio_value
        return
        
    def get_number_shares(self, data, percent_dict):
        for position in input_dict:
            target = input_dict[position]
            # Sum value of all open positions and ending cash balance.
            portfolio_totalvalue = self.context.portfolio.portfolio_value
        return