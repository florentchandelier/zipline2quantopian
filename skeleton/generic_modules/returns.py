from necessary_import import *

class returns ():
    '''
    http://orfe.princeton.edu/~jqfan/fan/FinEcon/chap1.pdf
    '''
    def init (self):
        return
        
    def simple_return (self):
        '''
        named one-period simple return
        It is the profit rate of holding the asset from time t-1 to t; 
        percentage of the gain with respect to the initial capital P(t−1)
        '''
        return
        
    def simple_gross_return (self):
        '''
        P(t)/P(t−1)=R(t)+ 1. 
        It is the ratio of the new market value at the end of the holding 
        period over the initial market value
        '''
        return
        
    def log_return (self):
        '''
        r(t)=ln(Pt/Pt−1), with t is the period, Annualized: R =year_in_t * r(t)
        Note that a log return is the logarithm (with the natural base) of a 
        gross return;
        One immediate convenience in using log returns is that the additivity 
        in multiperiod log returns
        
        The moral is that it may be better to look at the log-returns if you 
        are a buy-and-hold type of investor, because log-returns cancel out 
        when prices fluctuate, whereas percentage changes in price do not.
        
         The mean of a set of returns calculated using logarithmic returns is 
         less than the mean calculated using simple returns by an amount 
         related to the variance of the set of returns.
        '''
        return
    
    def relative_return (self):
        '''
        also named excess return, excess yield (for bonds to US Treas.bill)
        The term "relative returns" refers to returns as compared to a 
        benchmark index, or between (inter) different instruments
        '''
        return
        
    def geomtric_avg_returns (self):
        '''
        used to calculate average rate per period on investments that are 
        compounded over multiple periods.
        g(n) = [(1+rc)^(1/n)] - 1, with rc cumulative returns
        
        geometric growth rate rg = exp( 1/n * Sum(i->n) [log(1+ri)])-1 

        1. First add 1 to each number in the sequence. This is to avoid 
        problems with negative numbers.

        2. Multiple each number in the sequence.

        3. Raise the answer to the power of one divided by the count of the 
        numbers in the sequence.
        4. Subtract one from the result.
        
        The return numbers from year two to year five are simply not 
        independent events and depend on the amount of capital invested at 
        the beginning. In fact, most returns in finance are correlated, 
        including yields on bonds, stock returns and market risk premiums. 
        The longer the time horizon, the more important compounding becomes 
        and the more appropriate the use of geometric mean.

        '''
        return
