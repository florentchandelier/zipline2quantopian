
class StrategyPortfolio (object):
    def __init__ (self):
        self.total_value = 0
        # instrument:nb_share
        self.assets = dict()
        
        self.allocation = 0
        # These are registered by the PortfolioManager with PortfolioManager
        #
        self.portf_management_allocation = None
        #
        # End of portf_management
        
        return
    def set_portf_allocation(self, value):
        self.portf_management_allocation = value
        return
        
    def get_total_assets_value (self):
        return
        
    def set_allocation(self, val):
        self.allocation = val
        return
        
    def get_allocation (self):
        return self.allocation
        
    def update_asset (self, inst, amount):
        if inst in self.assets:
            self.assets[inst] += amount    
        return