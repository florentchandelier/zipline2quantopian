from necessary_import import *; from StrategyPortfolio import *; from AnalyticsManager import *;

'''

to dos:


StrategyDesign is responsible for the basic strategy interactions. 
0. It receives fund allocation from the PortfolioManager

1. It registers with OrderManagement through the PortfolioManager, specifically
 to the method for executing orders.

2. It receives a strategy order and apply the allocation of funds set by the
 PortfolioManager.

3. It holds all the required schedule_functions to add in Initialize()
'''

class StrategyDesign(object, AnalyticsManager):

    def __init__(self, context, name):      
        self.name = name
        self.context = context
        
        # by default, the Portfolio logger is set to output to the console
        # at a level sufficient to report problems.
        AnalyticsManager.__init__(self, analytics_name=name)
        self.set_log_option(logconsole=True, logfile=False, level=logging.WARNING)
        
        # These are registered by the PortfolioManager with OrderManager
        #
        self.order_management_send_orders = None
        self.order_management_send_order_through = None
        self.order_management_send_percent_orders = None
        #
        # End of order_management
        
        self.schedule_func_list = []
        self.instruments = dict()
        
        self.portfolio = StrategyPortfolio()
        self.portfolio.set_allocation(0)
        return
        
#        def compute_target(self, context, data):
#            raise NotImplementedError()
        
    def set_send_percent_orders(self, value):
        # Used in registration with OrderManager in the PortfolioManager
        #
        self.order_management_send_percent_orders = value
        return
        
    def send_percent_orders(self, data, target_percent_dict, precision=3):
        if self.portfolio.get_allocation() == 0:
            return
            
        '''
        to do: must be a more pythonic way
        '''
        for i in target_percent_dict:
            target_percent_dict[i] = round(target_percent_dict[i] * self.portfolio.get_allocation(), precision)
            
#        self.order_management_send_percent_orders(data, target_percent_dict)
        msg = ' line #66: send_percent_orders has been commented out while testing market order positions'
        self.add_log('warning', msg)
        
        self.convert_percent_to_shares(data, target_percent_dict)
        return
    
    def convert_percent_to_shares (self, data, pct):
        allocated_value = self.portfolio.portf_management_allocation(dollar=True)
        
        # convert each instrument pct into a number of shares
        for inst in pct:
            # inherently takes into account strategy allocation in portfolio
            dollar_value = pct[inst] *allocated_value
            # to prevent problem, submit an 'int' to the market.
            nb = int(np.floor(dollar_value / float(data[inst].price)))
            # update desired strategy targeted allocation
            self.portfolio.assets[inst] = nb
            
        # determine market orders to reach targeted number of shares
        market_orders = dict()
        for inst in self.portfolio.assets:
            # current instrument nb_shares
            current_nb = self.context.portfolio.positions[symbol(inst)].amount
            # negative is short, positive is long
            nb_shares = int(self.portfolio.assets[inst] - current_nb)
            if nb_shares != int(0):
#                market_orders = merge_dicts(market_orders, {inst:nb_shares})
                self.send_order_through(inst, nb_shares)
                
#        print('target: ' +str(self.portfolio.assets))
#        print('market order: ' +str(market_orders))
        return
    
    def set_send_order_through(self, value):
        self.order_management_send_order_through = value
        return
        
    def send_order_through(self, instrument, nb_shares=0, style=MarketOrder()):
        self.order_management_send_order_through(instrument, nb_shares, style=MarketOrder())
        return
        
    def set_name(self, value):
        self.name = value
        return
        
    def add_schedule_function(self, func):
        self.schedule_func_list.append(func)
        return
        
    def get_schedule_function(self):
        return self.schedule_func_list
        
    def get_instruments(self):
        return self.instruments
        
    def add_instruments (self, instrument_dict):
        self.instruments = merge_dicts(self.instruments, instrument_dict)
        
        for inst in instrument_dict:
            if instrument_dict[inst] not in self.portfolio.assets:
                self.portfolio.assets = merge_dicts(self.portfolio.assets, {instrument_dict[inst]:0})
        return
