from necessary_import import *; 
import re; import os; import pandas as pd; import numpy as np

def load_from_dir(directory, stocks, start, end):
    benchmark = 'SPY'
    data_spy= pd.io.parsers.read_csv(directory+str(benchmark)+'.csv', index_col='Date')

    t = data_spy.index
    index = t
    df = pd.DataFrame()
    df.index.names = ['Date']
    
    df = pd.DataFrame(data_spy['Adj Close'].values, index=index, columns=['SPY'])
    
    bench = [benchmark]
    instruments = set(stocks)-set(bench)
    for inst in instruments:
        ref = pd.io.parsers.read_csv(directory+str(inst)+'.csv', index_col='Date')
        ref = pd.DataFrame(ref['Adj Close'].values, index=ref.index, columns=[inst])
        
        idx = set(df.index) & set(ref.index)
        length = ref.index[ref.index.isin( df.index)]
        ref = ref.ix[length]
        df = df.ix[length]
        df = pd.concat([df, ref], axis=1)

    df.index = df.index.to_datetime().tz_localize('UTC')
    # df will automatically adjust to the start:end as best as possible based on current df.index without complaining
    return df.ix[start:end]
    
def update_instruments (directory):
    return
    
def consolidate_instruments (directory):
    # list all content of the directory
    all_content = os.listdir(directory)
    csv_inst = [x for x in all_content if x.endswith(".csv")]
    # sort by name
    csv_inst.sort()
    
    while len(csv_inst) > 0: #for inst in csv_inst:
#        symbol = inst.split('-')[0]
        symbol = re.split(r'[-\.csv]\s*', csv_inst[0])[0]
        
        '''
        look for all elements starting with ....
        log index, load the files, and further use the logged index to remove them
        '''
        files = [filename for filename in csv_inst if filename.startswith(symbol)]
        
        consolidate = pd.DataFrame()
        i = files[0]
        file_path = directory+i
        csv = pd.io.parsers.read_csv(file_path, index_col='Date')
        consolidate = np.round (consolidate.append(csv), decimals=3)
        os.remove(file_path)
        files.remove(i)
        csv_inst = [x for x in csv_inst if not i in x]
            
        # consolidate
        for i in files:
            '''
            does append modify the original data ... can we only append new data ?
            '''
            file_path = directory+i
            csv = pd.io.parsers.read_csv(file_path, index_col='Date')
            
            idx = csv.index - consolidate.index
            new = np.round(csv.ix[idx], decimals=3)
            
            consolidate = new.append(consolidate)
            # when appended, index is messed up. Realigning chronologically
            consolidate = consolidate.sort_index()

            # remove files from csv_inst and from the directory ... keep only the consolidation
            os.remove(file_path)
            csv_inst = [x for x in csv_inst if not i in x]
    
        consolidate.to_csv(directory+symbol+'.csv', index=True, header=True) 
    return

if __name__ == '__main__':
    directory = "/home/flo/perso/zipline_strategies/data/"
    consolidate_instruments (directory)