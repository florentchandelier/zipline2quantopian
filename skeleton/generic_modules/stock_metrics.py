from necessary_import import *

def get_ratereturn (context, data, lookback):
    rateReturn = 0
    # Request history from the last period days
    prices = history(lookback, '1d', 'price')
    # compute returns over the period
    rateReturn = (prices.ix[-1] - prices.ix[0]) / prices.ix[0]
    return(rateReturn)
    
def get_std (context, lookback):
    std=0
    # Request history from the last period days
    prices = history(lookback, '1d', 'price')
    # compute standard deviation over period
    std = prices.std()
    return (std)
