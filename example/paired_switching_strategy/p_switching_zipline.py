from collections import defaultdict
import matplotlib.pylab as pl

from global_import.zipline_import import *
from p_switching.main import *

'''
SPY
TLT
[2004-12] > CAGR = -0.0217077777778
[2005-12] > CAGR = 0.0302265123101
[2006-12] > CAGR = 0.0511810008782
[2007-12] > CAGR = 0.0611904241916
[2008-12] > CAGR = 0.0636832451999
[2009-12] > CAGR = 0.0857415189302
[2010-12] > CAGR = 0.0947395494563
[2011-12] > CAGR = 0.128460466573
[2012-12] > CAGR = 0.11529851544
[2013-12] > CAGR = 0.126279075622
[2014-12] > CAGR = 0.127991632433
 --- algo.run completed in 6.11192798615 seconds ---
'''

def visu_robust_param (all_sharpes):
    test = parameters_robustness()
    for param in test.permutation:
        algo = TradingAlgorithm(initialize=initialize_optimizeparameters, handle_data=handle_data, capital_base=10000, parameters=param)
        start_time = time.time()
        results = algo.run(data)
        algo.performance_analysis.get_ds().plot(color='darkgrey', alpha=0.6)
        
        # Calculate the sharpe for this backtest
        sharpe = (results.returns.mean()*282)/(results.returns.std() * np.sqrt(282))
        all_sharpes[param] = sharpe
        
    return all_sharpes
    
def backtest (fast_backtest, color='darkgrey', bechmark = False):
    algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data, capital_base=10000)
    start_time = time.time()
    results = algo.run(data)
    
    if  fast_backtest:
        print(" --- algo.run completed in %s seconds ---" % (time.time() - start_time)) 
        algo.performance_analysis.render_get_gain_to_pain()        
#        algo.performance_analysis.render_from_trough_to_depth_trough(-5)
        algo.performance_analysis.get_ds().plot(color=color)
    else:    
        plot_portfolio(results, algo)
        print("\n RISK METRICS \n")
        print(algo.perf_tracker.cumulative_risk_metrics)
        dd = from_trough_to_depth_trough(results, -7)
    
    if bechmark:
        ( algo.capital_base*(1+results.benchmark_period_return) ).plot(color='black')    
    return
    
def get_data(start, end, instrument):
    #    data = load_from_yahoo(stocks=instrument, indexes={},start=algo.startDate, end=algo.endDate)
    data = load_from_yahoo(stocks=instrument, indexes={},start=start, end=end)
    data = data.dropna()
    return data

if __name__ == '__main__':
    
    fast_backtest = True
    robust_param = True
    bechmark = True   
    #: Create a dictionary to hold all the results of our algorithm run
    all_sharpes = defaultdict(dict)
         
    start = datetime(2004, 1, 1, 0, 0, 0, 0, pytz.utc)
    end = datetime(2015, 1, 1, 0, 0, 0, 0, pytz.utc)
    instrument = ['SPY', 'TLT']
    data = get_data(start, end, instrument)

    algo = None
    if robust_param:
       visu_robust_param (all_sharpes)
       # last run with the 'final' parameters, overlayed on all param
       backtest (fast_backtest=True, color='orangered', bechmark = True)
    else:
       algo.backtest (fast_backtest)
        
    '''
    Accessing Strategy(ies) analytics
    '''
    if algo is not None:
        output_directory='analytics/'
        algo.portfolio_manager.analytics_save(output_directory)

#    all_sharpes = pd.DataFrame(all_sharpes)
    all_sharpes = pd.DataFrame({"key": all_sharpes.keys(), "value": all_sharpes.values()})
    all_sharpes

    
