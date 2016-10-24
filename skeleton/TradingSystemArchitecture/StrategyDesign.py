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
        self.set_log_option(logconsole=True, logfile=False, level=3)
        
        self.schedule_func_list = []
        self.instruments = dict()
        
        self.portfolio = StrategyPortfolio(context, name)
        self.portfolio.set_allocation(0)
        return
    
    def send_order (self, data, signal_type, value):
        # handling a dictionary of percent order(s)
        #
        if signal_type == 'pct':
            self._send_percent_order (data, value)
        return
    
#    def _send_percent_order (self, data, pct):
#        # for a strategy, what makes sense is the dollar value for a position
#        # it should be the job of the OrderManager to get proper position size
#        # based on market value when order will be filled (there might be 
#        # priorities for orders to be filled, thus last time position sizing
#        # is a good practice)
#        target_dollar_value = dict()
#        
#        allocated_value = self.portfolio.get_allocation(allocation_type='dollar')
#        # convert each instrument pct into a dollar value position
#        for inst in pct:
#            # inherently takes into account strategy allocation in portfolio
#            dollar_value = pct[inst] *allocated_value
#            # update desired strategy targeted allocation
##            self.portfolio.assets[inst] = dollar_value
##            tgt_dollar_value = self.portfolio.update_asset(inst.symbol, dollar_value)
#            self.portfolio.update_asset(data, inst.symbol, dollar_value)
#            
#            current_value = self.context.portfolio.positions[inst].amount *data[inst].price
#            
##            current_value = self.portfolio.get_instrument_current_value(inst)            
#            
#            msg = " StrategyDesign: Price consolidation should not happen inside Strategy, but Global OderManager level"
#            self.add_log('warning',msg)
#            
#            current_value = self.context.portfolio.positions[inst].amount *data.current(inst, 'price')
#            tgt_dollar_value = dollar_value - current_value
#            target_dollar_value = merge_dicts(target_dollar_value, {inst:tgt_dollar_value})
#            
##            print("SD - inst: " + str(inst.symbol) + " desired %: " + str(pct[inst]) + " desired $: " +str(dollar_value) + " current $: " + str(current_value) + " target $: " + str(tgt_dollar_value))
#        
#        #
#        # target_dollar_value: dictionary of positions target in dollar value
#        # dict{inst; dollarvalue}
#        #
#        self.context.order_manager.orderbook_consolidator (target_dollar_value)
#        return
    
    def _send_percent_order (self, data, pct):
        # for a strategy, what makes sense is the dollar value for a position
        # it should be the job of the OrderManager to get proper position size
        # based on market value when order will be filled (there might be 
        # priorities for orders to be filled, thus last time position sizing
        # is a good practice)
        
        allocated_value = self.portfolio.get_allocation(allocation_type='dollar')
        # convert each instrument pct into a dollar value position
        for inst in pct:
            # inherently takes into account strategy allocation in portfolio
                
            dollar_value = pct[inst] *allocated_value
            # update desired strategy targeted allocation
#            self.portfolio.assets[inst] = dollar_value
#            tgt_dollar_value = self.portfolio.update_asset(inst.symbol, dollar_value)
            self.portfolio.update_asset(data, inst.symbol, dollar_value)
        return
        
    def set_name(self, value):
        self.name = value
        return
        
    def add_schedule_function(self, func, date_rule, time_rule, half_days=True):
        sched_param_dict = {'func':func, 'date_rule':date_rule, 'time_rule':time_rule, 'half_days':half_days}
        self.schedule_func_list.append(sched_param_dict)
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
