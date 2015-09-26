
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

import cProfile
import pstats
import StringIO

import time

def do_cprofile(func):
    def profiled_func(*args, **kwargs):
        profile = cProfile.Profile()
        try:
            profile.enable()
            result = func(*args, **kwargs)
            profile.disable()
            return result
        finally:
            profile.print_stats()
    return profiled_func
    
@do_cprofile
def run_the_algo(algo, data):
	return algo.run(data)

def cp_run(fn_pro):
    return cProfile.run('run_the_algo(algo,data)', fn_pro)
	
if __name__ == '__main__':
    
    is_profiling = False
    profiling_output = False
    
    fast_backtest = True
    algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data, capital_base = 10000, fast_backtest=fast_backtest)
    
    instrument = [''.join(w) for w in algo.instrument.values()]
    data = load_from_yahoo(stocks=instrument, indexes={},start=algo.startDate, end=algo.endDate)
    data = data.dropna()
    #
    # End Of Fetch and Load
    #
    results = None
    
    if profiling_output:
        fn_pro = 'statsfile_original'
        cp_run(fn_pro)
        stream = StringIO.StringIO()
        stats = pstats.Stats(fn_pro, stream=stream)
        stats.print_stats()  
        print stream.getvalue()
        
    elif is_profiling:    
        results = run_the_algo(algo, data)
    else:
        start_time = time.time()
        results = algo.run(data)
        print(" --- algo.run completed in %s seconds ---" % (time.time() - start_time)) 
        algo.performance_analysis.render_get_gain_to_pain()        
        algo.performance_analysis.render_from_trough_to_depth_trough(-5)
        algo.performance_analysis.get_ds().plot()

    if not fast_backtest and results is not None:    
        plot_portfolio(results, algo)
        
        print("\n RISK METRICS \n")
        print(algo.perf_tracker.cumulative_risk_metrics)
        dd = from_trough_to_depth_trough(results, -7)
    
    elif results is not None:
        print('Not Implemented')
