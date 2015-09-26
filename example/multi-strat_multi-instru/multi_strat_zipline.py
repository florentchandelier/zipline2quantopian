from multi_strategy.main import *
	
if __name__ == '__main__':
    
    fast_backtest = True
    algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data, capital_base = 10000, fast_backtest=fast_backtest)
    
    instrument = [''.join(w) for w in algo.instrument.values()]

    data = load_from_yahoo(stocks=instrument, indexes={},start=algo.startDate, end=algo.endDate)
    data = data.dropna()
    #
    # End Of Fetch and Load
    #

    results = algo.run(data)

    if not fast_backtest:
        algo_name = 'multi_mom_50%_strat1'
        benchmark_name = 'SPY'
        bench_plot = False
        plot_portfolio(results, algo, algo_name, bench_plot, benchmark_name)
        
        print("\n RISK METRICS \n")
        print(algo.perf_tracker.cumulative_risk_metrics)
        dd = from_trough_to_depth_trough(results, -7)
    else:
        
        algo.performance_analysis.render_get_gain_to_pain()        
        algo.performance_analysis.render_from_trough_to_depth_trough(-5)
        algo.performance_analysis.get_ds().plot()
        