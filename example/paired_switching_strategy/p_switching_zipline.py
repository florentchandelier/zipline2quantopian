
from global_import.zipline_import import *
from p_switching.psw_core import *


if __name__ == '__main__':
 
    algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data, capital_base = 10000)
    
    #
    # Fetch and Load financial Instruments
    #
    # This process is required if you declare more than one list of instruments in your algorithm.
    # This is often the case if a strategy applies filters to a list of stocks, and
    # default to cash (or any other instrument) should none of the stocks satisfy
    # the criteria, or a cash-stop situation is reached.
    #
    new_data = [''.join(w) for w in algo.stocks]
    #new_data += [algo.cashETF]
    data = load_from_yahoo(stocks=new_data, indexes={},start=algo.startDate, end=algo.endDate)
    data = data.dropna()
    #
    # End Of Fetch and Load
    #
    
    results = algo.run(data)
    plot_portfolio(results, algo)
  
#    results.pnl ; results.returns
    algo.perf_tracker.cumulative_risk_metrics