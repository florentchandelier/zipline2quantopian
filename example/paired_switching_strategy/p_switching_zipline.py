
from global_import.zipline_import import *
from p_switching.psw_main import *


if __name__ == '__main__':
 
    algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data, capital_base = 10000)
    
    instrument = [''.join(w) for w in algo.instrument.values()]
    data = load_from_yahoo(stocks=instrument, indexes={},start=algo.startDate, end=algo.endDate)
    data = data.dropna()
    #
    # End Of Fetch and Load
    #
    
    results = algo.run(data)
    plot_portfolio(results, algo)
  
    print("\n RISK METRICS \n")
    print(algo.perf_tracker.cumulative_risk_metrics)
    dd = from_trough_to_depth_trough(results, -7)