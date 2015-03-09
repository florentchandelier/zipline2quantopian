'''

NOTE from  John Fawcett
------------------------
https://www.quantopian.com/posts/how-can-i-use-fetch-csv%60-to-load-my-data-and-make-it-available-to-the-history%60-function

---> history() only accumulates data for trade bars from Q, so you have to build your own frame of data on fetcher fields



OBJECTIVE
----------
> to compare the diference between the rate of return of an instrument from yahoo prices, adjusted for splits and dividends, compared to the rate of return of quantopian prices that is adjusted for splits only.
> the period for determining the rate of return is derived from a global variable: RoR_period



INSTRUMENTS TO TEST WITH
------------------------

only dividend -> DIFFERENCE should be noticed when calculating rate of return for any period
-------------
TLT: only dividends, no split: so the expected difference in return should be meaningful as time goes by
EAD : wells-Fargo .. lots of dividends

only splits -> NO DIFFERENCE should be noticed when calculating rate of return for any period
-----------
Berkshire Hathaway Inc. (NYSE:BRK.B) : No dividends, only 1 split (Jan 21 2010) so the difference should be 0
NASDAQ:EBAY
YHOO

No splits, no dividend -> NO DIFFERENCE should be noticed when calculating rate of return for any period
----------------------
Exar Corporation (NYSE:EXAR)
RedHat RHT
'''

import pandas as pd
import datetime

RoR_period = 12

def initialize(context):
    context.stock = symbol('BRK_B')
    context.yinstrument = context.stock.symbol
    # replacing '_' in Q by '.' for yahoo
    context.yinstrument = context.yinstrument.replace("_", ".");
    # marking yahoo instrument by 'y_' for further identification
    context.yinstrument = 'y_'+context.yinstrument
    
    context.date = None
    context.lookback = RoR_period*21
    
    context.periodCount = 0
    today_year = str(datetime.date.today().year)
    back_year = '2002'
    url_start = 'http://ichart.finance.yahoo.com/table.csv?s='
    url_end = '&d=1&e=1&f=' + today_year+ '&g=d&a=0&b=29&c=' +back_year+ '&ignore=.csv'
    url = url_start+ context.yinstrument.split('y_')[1] +url_end
    print(url)
    
    fetch_csv(url, 
        date_column='Date',date_format='%Y-%m-%d',symbol=context.yinstrument,usecols=['Adj Close'],post_func=rename_col)

def rename_col(df):
    adj = df['Adj Close']
    
    df = df.rename(columns={'Adj Close': 'price'})
    df = df.fillna(method='ffill')
    df = df[['price', 'sid']]
    
    rateReturn = adj.pct_change(periods=RoR_period*21)
    df['ror_adj'] = rateReturn
    
    # further examples
    fastMA = pd.rolling_mean(adj, 10)
    slowMA = pd.rolling_mean(adj, 100)
    macd = fastMA - slowMA
    
    return df

def handle_data(context, data):
    date = get_datetime().date()

    if date == context.date: 
        return
    
    context.date = date
    if 'ror_adj' not in data[context.yinstrument]:
       return
    
    prices = history(context.lookback, '1d', 'price')
    rateReturn = (prices.ix[-1] - prices.ix[0]) / prices.ix[0]
    ror = data[context.yinstrument]['ror_adj']
    diff_rorYrorQ = ror - rateReturn[context.stock]

    record(RoR_4mth_YminusQ=100*(diff_rorYrorQ))   


