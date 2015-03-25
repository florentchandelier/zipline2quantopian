
from global_import.zipline_import import *
from p_switching.psw_main import *

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

    if not fast_backtest and results is not None:    
        plot_portfolio(results, algo)
        
        print("\n RISK METRICS \n")
        print(algo.perf_tracker.cumulative_risk_metrics)
        dd = from_trough_to_depth_trough(results, -7)
    
    elif results is not None:
        print('Do something')
