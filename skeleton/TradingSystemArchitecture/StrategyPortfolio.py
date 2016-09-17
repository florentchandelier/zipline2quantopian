
class StrategyPortfolio (object):
    def __init__ (self, portfolio_manager):
        self.total_value = 0
        # instrument:dollar_value (dollar is more robust than nb shares as 
        # order_fill can be delayed by OrderManager)
        self.assets = dict()
        
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
        
#    def update_asset (self, inst, amount):
#        if inst in self.assets:
#            self.assets[inst] += amount    
#        return