from necessary_import import *;

class StrategyDesign(object):
    '''
    StrategyDesign is responsible for the basic strategy interactions. 
    0. It receives fund allocation from the PortfolioManager
    1. It registers with OrderManagement through the PortfolioManager, specifically to the method
    for executing orders.
    2. It receives a strategy order and apply the allocation of funds set by the PortfolioManager.
    3. It holds all the required schedule_functions to add in Initialize()
    '''
    def __init__(self, name):      
        self.name = name
        self.allocation = 0
        self.order_management_send_orders = None
        self.schedule_func_list = []
        return
        
#        def compute_target(self, context, data):
#            raise NotImplementedError()
        
    def set_send_orders(self, value):
        self.order_management_send_orders = value
        return
        
    def send_orders(self, data, target_percent_dict):
        if self.allocation == 0:
            return
            
        '''
        to do: must be a more pythonic way
        '''
        for i in target_percent_dict:
            target_percent_dict[i] = target_percent_dict[i] * self.allocation
            
        self.order_management_send_orders(data, target_percent_dict)
        return
        
    def set_allocation(self, value):
        self.allocation = value
        return
        
    def get_allocation(self):
        return self.allocation
        
    def set_name(self, value):
        self.name = value
        return
        
    def add_schedule_function(self, func):
        self.schedule_func_list.append(func)
        return
        
    def get_schedule_function(self):
        return self.schedule_func_list
