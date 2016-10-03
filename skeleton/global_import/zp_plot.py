from necessary_import import *

def plot_portfolio (results, algo, algo_name=None, bench_plot=True, bench_name=None, algo_color=None):
    
    fig = plt.figure(1, figsize=(8, 10))
    plt.subplots_adjust(left=0.2, right=0.98, bottom=0, top=0.96)
    #fig, axes = plt.subplots(nrows=4, ncols=4)    

    ax1 = fig.add_subplot(311, ylabel='portfolio value ($)')
    if algo_color is None:
        add_serie (ax1, results.portfolio_value, algo_name) 
    else:
        add_serie (ax1, results.portfolio_value, algo_name, color=algo_color)
    format_plot(ax1)
    
    ax2 = fig.add_subplot(312, ylabel='leverage')
    add_serie (ax2, results.leverage, algo_name)   
    format_plot(ax2, leg_location='lower left')
    
    ax3 = fig.add_subplot(313, ylabel='PnL ($)' )
    add_serie (ax3, results.pnl, algo_name)   
    format_plot(ax3)
    
    fig.tight_layout()
#    pl.show()
    
    br = results.benchmark_period_return
    bm_returns = br[(br.index >= algo.startDate) & (br.index <= algo.endDate + timedelta(days=1))]
#    results['benchmark_returns'] = (1 + bm_returns).cumprod().values
    results['benchmark_returns'] = (1 + bm_returns)
    results['algorithm_returns'] = (1 + results.returns).cumprod()
    
    fig = plt.figure(2, figsize=(8, 10))
    
    plt.subplots_adjust(left=0.2, right=0.98, bottom=0, top=0.96)

    ax1 = fig.add_subplot(311, ylabel='Cumulative Returns')
    if bench_plot:
        add_serie (ax1, results['benchmark_returns'], bench_name, color='black')
    
    if algo_color is None:
        add_serie (ax1, results['algorithm_returns'], algo_name)
    else:
        add_serie (ax1, results['algorithm_returns'], algo_name, color=algo_color)
    format_plot(ax1)
    
    ax2 = fig.add_subplot(312, ylabel='Drawdowns')
    results['drawdowns'] = -100*algo.perf_tracker.cumulative_risk_metrics.drawdowns
    add_serie (ax2, results['drawdowns'], algo_name)   
    format_plot(ax2, leg_location='lower left')
    
    # 21 trading days per month, 12*21=252 trading days a year ... approx
    ax3 = fig.add_subplot(313, ylabel='252-days rolling returns')
    results['rolling_ret'] = 100*results.portfolio_value.pct_change(12*21)
    add_serie (ax3, results['rolling_ret'], algo_name)   
    format_plot(ax3)
    
    fig.tight_layout()
    plt.show()
    
    return

def add_serie(ax, s, serie_name=None, style=None, color=None, alpha=0.5):
#    st = 'k'
#    if style is not None:
#        st=style
        
    if color is not None:
        if serie_name is None:
            s.plot(ax=ax, color=color, sharex=True, alpha=alpha)
        else:
            s.plot(ax=ax, label=serie_name, color=color, sharex=True, alpha=alpha)
    else:
        if serie_name is None:
            s.plot(ax=ax, sharex=True, alpha=alpha)
        else:
            s.plot(ax=ax, label=serie_name, sharex=True, alpha=alpha)
    
def format_plot(ax, leg_location=None):
    loc='upper left'
    if leg_location is not None:
        loc=leg_location
    # Now add the legend with some customizations.
    legend = ax.legend(loc=loc, shadow=False, labelspacing=0, frameon=False) 
    # Set the fontsize
    for label in legend.get_texts():
        label.set_fontsize('small')
    
    for label in legend.get_lines():
        label.set_linewidth(.5)  # the legend line width
    
def heat_map(df):
    """
    https://www.quantopian.com/posts/finding-the-best-moving-averages-now-with-2012-testing-period
    This creates our heatmap using our sharpe ratio dataframe
    """
    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(111)
    axim = ax.imshow(df.values,cmap = matplotlib.pyplot.get_cmap('RdYlGn'), interpolation = 'nearest')
    ax.set_xlabel(df.columns.name)
    ax.set_xticks(np.arange(len(df.columns)))
    ax.set_xticklabels(list(df.columns))
    ax.set_ylabel(df.index.name)
    ax.set_yticks(np.arange(len(df.index)))
    ax.set_yticklabels(list(df.index))
    ax.set_title("Sharpe Ratios")
    matplotlib.pyplot.colorbar(axim)