from necessary_import import *

def load_from_dir(directory, stocks, start, end):
    data_spy= pd.io.parsers.read_csv(directory+'SPY.csv', index_col='Date')

    t = data_spy.index
    index = t.to_datetime()    
    df = pd.DataFrame()
    df.index.names = ['Date']
    
    df = pd.DataFrame(data_spy.values, index=index, columns=['SPY'])    
    
    for inst in stocks:
        ref = pd.io.parsers.read_csv(directory+str(inst)+'.csv', index_col='Date')      
        df[inst]=ref.values

    
    return df