from necessary_import import *

def plot_portfolio (results, algo):
    
    fig = pl.figure(1, figsize=(8, 10))
    pl.subplots_adjust(left=0.2, right=0.98, bottom=0, top=0.96)
    #fig, axes = plt.subplots(nrows=4, ncols=4)    

    ax1 = fig.add_subplot(311)
    results.portfolio_value.plot(ax=ax1)
    ax1.set_ylabel('portfolio value ($)')
    
    ax2 = fig.add_subplot(312)
    (results.pnl).plot(ax=ax2, color='red')
    ax2.set_ylabel('PnL ($)')
    
    ax3 = fig.add_subplot(313)
    results.leverage.plot(ax=ax3)
    ax3.set_ylabel('leverage')
    
    fig.tight_layout()
    pl.show()
    
    br = trading.environment.benchmark_returns
    bm_returns = br[(br.index >= algo.startDate) & (br.index <= algo.endDate)]
    results['benchmark_returns'] = (1 + bm_returns).cumprod().values
    results['algorithm_returns'] = (1 + results.returns).cumprod()
    
    fig = pl.figure(2, figsize=(8, 10))
    pl.subplots_adjust(left=0.2, right=0.98, bottom=0, top=0.96)

    ax1 = fig.add_subplot(311, ylabel='Cumulative Returns')
    results[['algorithm_returns', 'benchmark_returns']].plot(ax=ax1, sharex=True)
    pl.legend(loc=0)    
    
    ax2 = fig.add_subplot(312, ylabel='Drawdowns')
    results['drawdowns'] = -100*algo.perf_tracker.cumulative_risk_metrics.drawdowns.values
    results['drawdowns'].plot(ax=ax2, color='blue')
    #pl.legend(loc=0)  
    
    # 21 trading days per month, 12*21=252 trading days a year ... approx
    ax3 = fig.add_subplot(313, ylabel='252-days rolling returns')
    results['rolling_ret'] = 100*results.portfolio_value.pct_change(12*21)
    results['rolling_ret'].plot(ax=ax3, color='blue')
    #pl.legend(loc=0)    
    
    #results.portfolio_value
    fig.tight_layout()
    pl.show()
    
    return
