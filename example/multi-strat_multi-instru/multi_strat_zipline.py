from multi_strategy.main import *

'''
SPY
TLT
[2004-12] > CAGR = 0.0177355555556
[2005-12] > CAGR = 0.0199389959971
[2006-12] > CAGR = 0.041403567331
[2007-12] > CAGR = 0.0243879689342
[2008-12] > CAGR = 0.015779432316
[2009-12] > CAGR = 0.0205408462794
[2010-12] > CAGR = 0.0164658404502
[2011-12] > CAGR = 0.0285847491249
[2012-12] > CAGR = 0.0340288522755
[2013-12] > CAGR = 0.0359042344244
[2014-12] > CAGR = 0.0393219808861
'''
	
if __name__ == '__main__':
    
    fast_backtest = True
    algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data, capital_base = 10000, fast_backtest=fast_backtest)
    
    instrument = [''.join(w) for w in algo.instrument.values()]

    data = load_from_yahoo(stocks=instrument, indexes={},start=algo.startDate, end=algo.endDate)
    data = data.dropna()
    
    '''
    Setting Analytics and Log System
    '''
    log_level = 2 # 2-INFO; 3=WARNING .... check AnalyticsManager module
    algo.portfolio_manager.order_manager.set_dumpanalytics(False)
    algo.portfolio_manager.order_manager.set_log_option(logconsole=False, logfile=False, level=log_level)    

    idx = algo.portfolio_manager.list_strategies.index('tlt strategy')
    algo.portfolio_manager.strategies[idx].set_log_option(logconsole=False, logfile=False, level=log_level)
    algo.portfolio_manager.strategies[idx].set_dumpanalytics(True) 
    
    idx = algo.portfolio_manager.list_strategies.index('spy strategy')
    algo.portfolio_manager.strategies[idx].set_log_option(logconsole=False, logfile=True, level=log_level)
    algo.portfolio_manager.strategies[idx].set_dumpanalytics(False) 
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
        
    '''
    Accessing Strategy(ies) analytics
    '''
    output_directory='analytics/'
    algo.portfolio_manager.analytics_save(output_directory)
        