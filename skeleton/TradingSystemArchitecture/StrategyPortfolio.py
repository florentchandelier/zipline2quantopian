
class StrategyPortfolio (object):
    def __init__ (self):
        self.total_value = 0
        # instrument:share_number
        self.assets = dict()
        
        self.allocation = 0
    
    def get_total_value(self):
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
        else:
            self.assets[inst] = amount    
        return