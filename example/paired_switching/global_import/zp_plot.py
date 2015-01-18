from necessary_import import *

def plot_portfolio (results):
    fig = pl.figure(1, figsize=(8, 10))
    ax1 = plt.subplot(211)
    results.portfolio_value.plot(ax=ax1)
    ax1.set_ylabel('portfolio value')
    pl.show()
    
    return