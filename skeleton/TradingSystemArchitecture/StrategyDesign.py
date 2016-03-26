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

    def __init__(self, name):      
        self.name = name
        
        # by default, the Portfolio logger is set to output to the console
        # at a level sufficient to report problems.
        AnalyticsManager.__init__(self, analytics_name=name)
        self.set_log_option(logconsole=True, logfile=False, level=logging.WARNING)
        
        self.order_management_send_orders = None
        self.order_management_send_order_through = None
        self.schedule_func_list = []
        self.instruments = dict()
        
        self.portfolio = StrategyPortfolio()
        self.portfolio.set_allocation(0)
        return
        
#        def compute_target(self, context, data):
#            raise NotImplementedError()
        
    def set_send_percent_orders(self, value):
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
            
        self.order_management_send_percent_orders(data, target_percent_dict)
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
