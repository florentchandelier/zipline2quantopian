from necessary_import import * ;

'''
OBJECTIVE
---------
Have a code that is fully compatible between Zipline and Quantopian, and that can be debug under Linux/Spyder.

-> To investigate Zip & Quant results : significative discrepencies on returns and the number of switches between pairs.


STRATEGY
--------
Lit.rev
    http://papers.ssrn.com/sol3/papers.cfm?abstract_id=1917044
    Paired-switching for tactical portfolio allocation
    Perf: 2003-2011: CAGR=15.0% (std=7.6%, min=6.7%)
    
Starting from the end of the first full week of the year, we look at the performance of the two equities
over the prior thirteen weeks (the ranking period), and buy the equity that has the higher return during
the ranking period. The position is held for thirteen weeks (the investment period). At the end of the
investment period the cycle is repeated.

Obviously, the number of weeks in the ranking period and the investment period can be varied
(independently) to optimize the strategy for a given pair of equities. Although the inevitable concerns
on over-fitting associated with such an optimization can be addressed by means of an
appropriate cross-validation methodology


IMPLEMENTATION
--------------
-> FROM http://www.portfolio123.com/mvnforum/viewthread_thread,6472
-> http://www.alphaarchitect.com/blog/2014/09/20/are-uber-simple-asset-allocation-systems-robust/

SPY / TLT
rebalance period: 1st day of month
ranking period: 4months
investment period: 1 month

-> http://seekingalpha.com/article/2714185-the-spy-tlt-universal-investment-strategy
The first is a switching strategy, which always switches to the ETF that had the best performance during the previous 3 months. 
This really simple switching strategy between TLT and SPY gave you a 14.8% return during the last 10 years, with twice 
the Sharpe ratio (return to risk) ratio of a simple SPY investment.
[2004-2011] CAGR=14.8%

'''
            
class pswitching(StrategyDesign):
    def __init__(self, context, instruments=None):
        name = 'pair switching strategy'
        StrategyDesign.__init__(self, name)

        self.nbSwitch = 0
        self.lookback = 3*21 # 4 months period, 21 trading days per month
        self.Periodicity = 1 # every x period ; 1 means every period
        self.periodCount = 0

        if instruments is None:        
            self.instruments = {'equity':symbol('SPY'), 'treasury':symbol('TLT')}
       
        self.add_schedule_function( context.schedule_function(self.order_logic,
                      date_rule=date_rules.month_start(),
                      time_rule=time_rules.market_open(hours=1, minutes=0))
        )
        return
        
    def set_configuration(self, param, value):
        self.config[param] = value           
        return
        
    def get_configuration(self):
        return self.config
        
    def order_logic(self, context, data):
        
        self.periodCount += 1
        
        # execute modulo context.Periodicity
        if self.periodCount % self.Periodicity == 0:
            ror = get_ratereturn (context,data, self.lookback)
            NbNan = np.count_nonzero(np.isnan(ror))
            if NbNan > 0:
                return -1
                
            index = self.instruments.values().index(ror.idxmax())
            self.allin(data, self.instruments.keys()[index])
        
        return
        
    def allin (self, data, inst):

        self.nbSwitch +=1

        up = self.instruments[inst]
        if (inst == 'treasury'):
            dwn = self.instruments['equity']
        else:
            dwn = self.instruments['treasury']
        
        target_percent_dict = dict() 
        target_percent_dict[up] = 1
        target_percent_dict[dwn] = 0
        
        self.send_orders(data, target_percent_dict)                   
        
        return      
