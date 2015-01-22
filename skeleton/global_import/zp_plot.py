from necessary_import import *

def plot_portfolio (results, algo):
    fig = pl.figure(1, figsize=(8, 10))
    ax1 = plt.subplot(211)
    results.portfolio_value.plot(ax=ax1)
    ax1.set_ylabel('portfolio value')
    pl.show()
    
    br = trading.environment.benchmark_returns
    bm_returns = br[(br.index >= algo.startDate) & (br.index <= algo.endDate)]
    results['benchmark_returns'] = (1 + bm_returns).cumprod().values
    results['algorithm_returns'] = (1 + results.returns).cumprod()
    
    fig = pl.figure(2, figsize=(8, 10))
    pl.subplots_adjust(left=0.1, right=0.98, bottom=0.0, top=0.96)

    ax1 = fig.add_subplot(211, ylabel='Cumulative Returns')
    results[['algorithm_returns', 'benchmark_returns']].plot(ax=ax1, sharex=True)
#    pl.setp(ax1.get_xticklabels(), visible=False)
    pl.legend(loc=0)    
    
    ax2 = fig.add_subplot(212, ylabel='Drawdowns')
    results['drawdowns'] = -100*algo.perf_tracker.cumulative_risk_metrics.drawdowns.values
    results['drawdowns'].plot(ax=ax2, color='blue')
    #results.trade_price.plot(ax=ax2, color='red')
#    pl.setp(ax2.get_xticklabels(), visible=False)
    pl.legend(loc=0)
    
    pl.show()
    
    return
