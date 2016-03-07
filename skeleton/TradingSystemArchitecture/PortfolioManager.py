from necessary_import import *; from OrderManager import *; from StrategyDesign import *;

'''
 PortfolioManager manages the strategies of the portfolio and their allocation.

1.It verifies that total fund allocated does not exceed 100%, 
2. it may dynamically adjust strategies allocation based on market behavior.
''' 

#class Strategy(object):
#    def __init__ (self, name):
#        self.name = name        
#        return
    
class PortfolioManager(object):

    def __init__(self, context):
        # list of strategies
        self.list_strategies = []
        self.order_management = OrderManager(context)
        self.portf_allocation = 0
        self.instruments = dict()
        
        self.strategies = list()
        
    def add_strategy(self, value, allocation):
        if (self.portf_allocation + allocation > 1):
            print('Error: Strategy **'+str(value.name) +' ** cannot be added to portfolio. Total allocation exceeds 100%')
            return
            
        value.set_allocation(allocation)
        self.portf_allocation += allocation
        
        self.list_strategies.append(value)
        self.strategies.append(value)
        
        value.set_send_percent_orders(self.order_management.add_percent_orders)
        value.set_send_order_through(self.order_management.send_order_through)
        
        self.set_instruments(value.get_instruments())
        self.order_management.add_instruments(value.get_instruments())
        
        return
        
    def get_portf_allocation(self):
        return self.portf_allocation
        
    def set_instruments(self, value):
        self.instruments = merge_dicts(self.instruments, value)
        return
        
    def get_instruments(self):
        return self.instruments
