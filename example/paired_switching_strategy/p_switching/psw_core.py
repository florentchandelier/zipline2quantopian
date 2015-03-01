from necessary_import import *

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

class paired_switching():
    
    def __init__(self, context):
        self.context = context
                      
    def ordering_logic(self, context, data):
        
        self.context.periodCount += 1
        
        # execute modulo context.Periodicity
        if self.context.periodCount % self.context.Periodicity == 0:
            ror = get_ratereturn (self.context,data, self.context.lookback)
            NbNan = np.count_nonzero(np.isnan(ror))
            if NbNan > 0:
                return -1
                
            index = self.context.instrument.values().index(ror.idxmax())
            self.allin(self.context.instrument.keys()[index])
        
        return
        
    def allin (self, inst):
        status = self.context.portfolio.positions[self.context.instrument[inst]].amount
        if status > 0:
            # do nothing, we are already invested
            pass
        
        else:
            self.context.nbSwitch +=1
    #        print("Date "+ str(data[context.stocks[0]].datetime) +"   Switch Nb: " +str(context.nbSwitch))

            up = self.context.instrument[inst]
            if (inst == 'treasury'):
                dwn = self.context.instrument['equity']
            else:
                dwn = self.context.instrument['treasury']
            
            order_target_percent(up, 1 *self.context.portf_allocation)
            order_target_percent(dwn, 0)                  
        
        return