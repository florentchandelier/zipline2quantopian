from necessary_import import *; from AnalyticsManager import *;

'''
To Dos:
    1. Convert all target percent positions in a number of instruments in order to be 
    able to exit the specific position of a specific strategy
'''

class OrderManager(object, AnalyticsManager):
    def __init__ (self, context, name = "OrderManager"):
        
        # by default, the Portfolio logger is set to output to the console
        # at a level sufficient to report problems.
        AnalyticsManager.__init__(self, analytics_name=name)
        self.set_log_option(logconsole=True, logfile=False, level=4)
        
        self.context = context
        self.instruments = dict()
        
        # used to manage expected orders, making sure cash is freed by closing positions
        # before opening any new orders if necessary
        self.order_queue_open = dict()
        self.order_queue_close = dict()
        
        self.orderbook = dict()
        
        # store positions in $ value
        self.unfilled_orders = dict()
        
        self.columns = ['instrument', 'pos']
        self.orders = pd.DataFrame(columns=self.columns)
        
        '''
        Analytics Manager
        '''
        self.create_analytics (name='pct_assets', columns=['timestamp', 'symbol', 'sell/target', 'buy/target'])
        self.create_analytics (name='position_size_tracking', columns=['timestamp', 'symbol', 'size'])

        return

    def create_empty_pos_dict (self):
        return pd.DataFrame(columns=self.columns)
        
    def get_pos(self, data, inst, dollar_value):
        return int(np.floor(dollar_value /float(data.current(symbol(inst),'price')) ))
        
    def submit_dollarvalue (self, data, inst, dollar=0):
        pos_orderid = self.send_order_through(data, inst, dollar=dollar, order_style = 'limit')        
        msg = "pos_orderid: "+str(pos_orderid)
        self.add_log('warning',msg)
        return pos_orderid
        
    def submit_orderposition (self, data, inst, pos=0):
        pos_orderid = self.send_order_through(data, inst, pos=pos, order_type = 'size', order_style = 'limit')        
        msg = "pos_orderid: "+str(pos_orderid)
        self.add_log('warning',msg)        
        return pos_orderid
        
    def get_order_status (self, orderid):
        status = get_order(orderid)
        if status is not None:        
            return status.filled
        else:
            return False
        
    def get_strategies_orderstatus (self, context, data):
        
        for strategy in context.portfolio_manager.strategies:
            for orderid in strategy.portfolio.get_orders():
                status = self.get_order_status(orderid)
                if status is not 0:
                    strategy.portfolio.orderfilled (orderid, status)
#                print ('Order Status: ' +str(self.get_order_status(orderid)))
                
        return

    def add_position (self, inst, pos):
        """
        add orders to the order book; only limit orders are used
        """

        if inst in self.orders['instrument'].values:
            current_pos = self.orders[self.orders['instrument']==inst]['pos']
            current_pos = float(current_pos)
            index = self.orders.index[self.orders.instrument == inst][0]
            self.orders.pos.set_value(index,current_pos+pos)
        else:
            update = pd.DataFrame(np.array([[inst,pos]]), columns=self.columns)
            self.orders = self.orders.append(update, ignore_index=True)
            
        return
        
    def unfilled_store (self, context, data):
        """
        catch unfilled orders at end of day, and convert positions into $
        value to update self.unfilled_orders
        
        Args:
            None
            
        Kwarg:
                
        Returns:
            None
        """
        data_freq = get_environment(field='data_frequency')
        if data_freq == 'daily': return
                
        # reset unfilled
        self.unfilled_orders = dict()
        
        # retrieve all the open (unfilled) orders
        open_orders = get_open_orders()
        
        if open_orders:
            msg = "\nUnfilled:Store"
            for _inst in open_orders:
                inst = open_orders[_inst][0]
                unfilled_positions = inst.amount-inst.filled
                msg = msg + "\n["+str(_inst.symbol)+"] - target order: "+str(inst.amount)+" - filled pos: "+str(inst.filled)+ " - unfilled orders: " +str(unfilled_positions)
                
                # store position in $ value
                if inst.limit is None:
                    self.unfilled_orders = combine_dicts(
                    {_inst: np.floor(unfilled_positions*data.current(inst.sid,'price')) },
                    self.unfilled_orders,op=operator.add)
                else:                       
                    self.unfilled_orders = combine_dicts(
                    {_inst: np.floor(unfilled_positions*inst.limit) },
                    self.unfilled_orders,op=operator.add)
                
            '''
            cancelling all open orders
            https://www.quantopian.com/posts/how-do-you-cancel-all-open-orders-on-a-friday-afternoon
            '''
            for sec in open_orders:               # Each security object has a list  
                for order in open_orders[sec]:     # Each order in the list  
                    cancel_order(order.id)          # The order id  
            
            self.add_log('warning',msg)
        return
        
    def unfilled_restore (self, context, data):
        """
        update the orderbook with the unfilled orders from the previous day
        
        Args:
            None
            
        Kwarg:
                
        Returns:
            None
        """
        
        if len(self.unfilled_orders) > 0:
            msg = "\nUnfilled:Restore"
            for unfill in self.unfilled_orders:
                msg = msg + "\n["+str(unfill.symbol)+"] - target order $$: "+str(self.unfilled_orders[unfill])
                
            self.add_log('warning',msg)            
            self.orderbook_consolidator(self.unfilled_orders)
            
        self.unfilled_orders = dict()    
        return
        
    def orderbook_consolidator (self, dollar_dic):
        """
        agregate all orders in $ value for condolidated batch order submission
        to update self.orderbook accordingly
        
        Args:
            dictionary of form {symbol:$value}
            
        Kwarg:
                
        Returns:
            None
        """
        for mkt_order in dollar_dic:
            self.orderbook = combine_dicts({mkt_order:dollar_dic[mkt_order]},
                                         self.orderbook,
                                         op=operator.add)
        return
        
    def orderbook_submit (self):
        """
        sort orders prior submission to exit positions and free cash first, 
        and enter new positions ; update order_queue_open/close accordingly
        
        Args:
            none (use self.orderbook)
            
        Kwarg:
                
        Returns:
            True/False is there anything to be submitted
        """
                
        if len (self.orderbook) == 0:
            return False
            
        self.order_queue_close = combine_dicts( {k: v for k, v in self.orderbook.items() if v<0},
                                                 self.order_queue_close,
                                                 op=operator.add)
        self.order_queue_open = combine_dicts( {k: v for k, v in self.orderbook.items() if v>0},
                                                self.order_queue_open,
                                                op=operator.add)

        self.orderbook = dict()
            
        return True
    
    def add_instruments(self, values):
        self.instruments = combine_dicts(self.instruments,
                                         values,
                                         op=operator.add)
        return
    
    def send_order_through(self, data, instrument, dollar=0, pos=0, order_type = 'dollar', order_style='limit'):
        '''
        order_type:
                dollar
                size
        order_styles:
            MarketOrder()
            LimitOrder()
        '''
        
        # zipline
        data_freq = get_environment(field='data_frequency')
        if data_freq == 'daily': order_style = 'market'
        # endof zipline        
        
        if order_type == 'dollar':
            pos = int(np.floor(dollar /float(data.current(instrument,'price')) ))
        
#        print("OM -  inst: " + str(instrument.symbol) + " $: " +str(dollar_value))
#        print ( str(get_datetime()) + " Order: inst = " +str(instrument.symbol) +" size = " +str(nb_shares) + " Price = " + str(data.current(instrument, 'price')))        

        pos = int(np.floor(pos))
        if order_style is 'limit':
            orderid = order(instrument, pos, style=LimitOrder(data.current(instrument, 'price')) )
        elif order_style is 'market':
            orderid = order(instrument, pos)
            
        return [pos, orderid]
        
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
        # target_dollar_value: dictionary of positions target in dollar value
        # dict{inst; dollarvalue}
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
        if len(self.order_queue_close) == 0:
            return
            
        for k in self.order_queue_close:
            self.send_order_through(data, k, self.order_queue_close[k], 'limit')
            
            msg = "\n\t" + " - exit_positions() order target in $: " +str(k) +" positions: " +str(self.order_queue_close[k])
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
        
        if len(self.order_queue_open) == 0:
            return
            
#        print("OrderManager: get_total_portfolio_value = " +str(self.context.portfolio.portfolio_value))
            
        data_freq = get_environment(field='data_frequency')
        if data_freq == 'minute' and (len(self.order_queue_open) <1 or len(self.order_queue_close)>1):
            if len(self.order_queue_close)>1:
                msg = "long position status: wait to fill all position_exit"
                self.add_log('info',msg)
            elif len(get_open_orders()) > 0:
                msg = "long positions status: waiting for unfilled closing positions"
                self.add_log('info',msg)
            return
        
        # mitigating for unfilled orders freeing cash
        wait_cashavailable = False
        
        for k in self.order_queue_open:
            # if not enough cash available, add the order to the order_book for next execution
            if self.order_queue_open[k] > self.context.portfolio.cash:
                wait_cashavailable = True
                msg = " Not enough cash to enter position. Wait for open orders to fill. [" + str(k.symbol) +"@ $"+str(self.order_queue_open[k])+"]"
                self.add_log('warning',msg)
                
            if wait_cashavailable:
                self.orderbook_consolidator ({k:self.order_queue_open[k]})
            else:
                self.send_order_through(data, k, self.order_queue_open[k], 'limit')    
                
                msg = "\n\t" + " - enter_positions() order target in $: " +str(k) +" positions: " +str(self.order_queue_open[k])
                self.add_log('info',msg)
                
                if self.get_dumpanalytics():
                    # columns=['timestamp', 'symbol', 'exit', 'enter']
                    row = [get_datetime().date(), k, '-', self.order_queue_open[k]]
                    self.insert_analyticsdata('pct_assets',row)
                    
        self.order_queue_open = dict()
        return                
        
    def update (self, context, data):
        '''
        NOTE
        In backtests, orders are submitted in one bar, and are filled in the 
        next bar. In daily mode your algorithm receives data once per day, at 
        market close; so an order submitted on Monday at 4PM will get filled 
        on Tuesday at 4PM. In minute mode, an order submitted at 10:00AM Monday
        will get filled at 10:01AM that same Monday, where there is much less 
        movement in the price. 
        '''
        
        if self.orderbook_submit():
            self.exit_positions(data)
            self.enter_positions(data)
            
            if self.get_dumpanalytics():
                # loop through all current holdings
                for inst in self.context.portfolio.positions:
                    # columns=['timestamp', 'symbol', 'size']
                    row = [get_datetime().date(), inst, self.context.portfolio.positions[inst].amount]
                    self.insert_analyticsdata('position_size_tracking',row)  
            return
        return

    def update_current_positions(self, data):
        self.current_positions = dict()
        for k in self.instruments.values():
                self.current_positions[k] = (data.current(k, 'price')*self.context.portfolio.positions[k].amount) / self.context.portfolio.portfolio_value
        return
        
#    def get_number_shares(self, data, percent_dict):
#        for position in input_dict:
#            target = input_dict[position]
#            # Sum value of all open positions and ending cash balance.
#            portfolio_totalvalue = self.context.portfolio.portfolio_value
#        return
