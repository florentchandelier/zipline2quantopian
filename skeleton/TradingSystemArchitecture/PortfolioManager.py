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
 
class PortfolioManager(object, AnalyticsManager):

    def __init__(self, context, name):
        self.context = context # currently only required for get_portf_allocation       
        self.portf_name = name
        
        # by default, the Portfolio logger is set to output to the console
        # at a level sufficient to report problems.
        AnalyticsManager.__init__(self, analytics_name=name)
        self.set_log_option(logconsole=True, logfile=False, level=logging.WARNING)
        
        # list of strategies
        self.list_strategies = []
        self.portf_allocation = 0
        self.instruments = dict()
        self.strategies = list()
        
        self.order_management = OrderManager(context, name = "OrderManager")
        
        return
        
    def add_strategy(self, value, allocation):
        if (self.portf_allocation + allocation > 1):
            msg = '\n\t Strategy named**'+str(value.name) +' ** cannot be added to portfolio. Total allocation exceeds 100%'
            self.add_log('error',msg)
            return
            
        if value.name in self.list_strategies:
            msg = '\n\t Strategy named ' +str(value.name) +' already exists and cannot be added to portfolio'
            self.add_log('error',msg)
            return
            
        value.portfolio.set_allocation(allocation)
        self.portf_allocation += allocation
        
        self.list_strategies.append(value.name)
        self.strategies.append(value)
        
        # Registrating with third-party methods
        #
        value.set_send_percent_orders(self.order_management.add_percent_orders)
        value.set_send_order_through(self.order_management.send_order_through)
        value.portfolio.set_portf_allocation(self.get_portf_allocation)
        #
        # End of registration
        
        self.set_instruments(value.get_instruments())
        self.order_management.add_instruments(value.get_instruments())
        
        return
        
    def get_portf_allocation(self, dollar = False):
        if dollar:
            return self.portf_allocation * self.context.portfolio.portfolio_value
        else:
            return self.portf_allocation
        
    def set_instruments(self, value):
        self.instruments = merge_dicts(self.instruments, value)
        return
        
    def get_instruments(self):
        return self.instruments
        
    def analytics_save (self, outdir):
        savepath = outdir+self.portf_name+'/'
        
        for strat in self.strategies:
            if strat.get_dumpanalytics():
                strat.write_analytics_tocsv(output_directory=savepath)
                
        if self.order_management.get_dumpanalytics():
            self.order_management.write_analytics_tocsv(output_directory=savepath)
