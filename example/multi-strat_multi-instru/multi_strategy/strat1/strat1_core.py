from necessary_import import *

class strat1():
    
    def __init__(self, context, portf_allocation):
        self.context = context
        self.lookback = 3*21
        self.instrument = symbols('YHOO')
        self.portf_allocation = portf_allocation
        
        return
        
    def abs_mom_up (self, data):
        inst = self.instrument[0]
        
        prices = history(self.lookback, '1d', 'price')
        NbNan = np.count_nonzero(np.isnan(prices))
        if NbNan > 0:
            return -1
                
        mom = prices.mean()
        if data[inst].price > mom[inst]:
            return 1
        else:
            return 0
            
    def rebalance (self, context, data):
        inst = self.instrument[0]
        
        mom = self.abs_mom_up(data)
        
        # mom = -1 if Nan values
        dic = self.create_dict()
        if mom == 1:
#             order_target_percent(inst, 1* self.portf_allocation)
             dic[inst] = 1* self.portf_allocation
        elif mom == 0:
#            order_target_percent(inst, 0)
            dic[inst] = 0
        
        return dic
            
    def create_dict(self): 
        default_values = np.zeros(len(self.instrument))
        return dict(zip(self.instrument,default_values))