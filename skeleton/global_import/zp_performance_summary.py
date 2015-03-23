from necessary_import import *

class performance():
    
    def __init__ (self):
        self.ds = pd.Series()
        self.df = pd.DataFrame()
        
    def update_ds(self, dt, value):
        self.ds = self.ds.append(pd.Series(data=value, index={dt} ))
        
    def get_ds(self):
        return self.ds
        
    def make_df(self):
        if 'portfolio_value' not in self.df:
            self.df = pd.DataFrame(self.ds, columns=['portfolio_value'])
        
    def make_dd(self):
        '''
            inspired by: https://code.google.com/p/trading-with-python/source/browse/trunk/lib/functions.py
        Input:
        s, price or cumulative pnl curve $
        
        Output:
            'pnl in currency unit'
            'daily drawdowns in %'
            'dd_duration'
            'high_watermark'
        '''
        self.make_df()
        
        if 'drawdowns' not in self.df:
#            self.df['drawdowns'] = 100*(self.df['portfolio_value'] - self.df['portfolio_value'].shift(-1)) / self.df['portfolio_value']
            # daily pnl            
            self.df['pnl'] = self.df['portfolio_value'].shift(-1) - self.df['portfolio_value']
            # global cumulative pnl
            cumsum_pnl = np.cumsum(self.df['pnl'])
            cumsum_pnl[-1] = cumsum_pnl[-2]
            
            # convert to array if got pandas series, 10x speedup
            idx = self.df.index
            s = cumsum_pnl.values
             
            if s.min() < 0: # offset if signal minimum is less than zero
                s = s-s.min()
             
            highwatermark = np.zeros(len(s))
            drawdown = np.zeros(len(s))
            drawdowndur = np.zeros(len(s))
         
            for t in range(1,len(s)):
                highwatermark[t] = max(highwatermark[t-1], s[t])
                drawdown[t] = (highwatermark[t]-s[t])
                drawdowndur[t]= (0 if drawdown[t] == 0 else drawdowndur[t-1]+1)
                
            self.df['drawdowns'] = pd.Series(index=idx,data=drawdown) #, pd.Series(index=idx,data=drawdowndur)
            self.df['dd_duration'] = pd.Series(index=idx,data=drawdowndur)
            self.df['highwatermark'] = pd.Series(index=idx,data=self.df['portfolio_value'][0]+highwatermark)
        
    def get_from_trough_to_depth_trough(self, thresh_dd=0, first_n=0):
        '''
         query the table for all drawdowns that were more than thres_dd%, 
         or the first_n biggest drawdowns;
         # http://stackoverflow.com/questions/27060037/pandas-way-to-groupby-like-itertools-groupby
        '''
        
        self.make_df()
        self.make_dd()
        
        x = -100* (self.df['drawdowns']/self.df['highwatermark'])
        x[np.isnan(x)]=0
    
        if thresh_dd >0: thresh_dd = -thresh_dd
    
        # this should return the max depth and length
        mask = x <= thresh_dd
        groupnum = mask.diff().fillna(method='bfill').cumsum()
            
        print("\n DRAWDOWNS ANALYSIS \n ------------------")
        print(" DD period below the " +str(thresh_dd) +"% watermark" )
        
        if max(groupnum) == 0:
            print("   -> No occurence of DD <= " +str(thresh_dd) +"%")
            print(" Max DD is " +str(round(min(x),2)) +"%" )
            return None
            
        col = ['From', 'maxDD', 'To', 'mDD', 'Length', 'To mDD', 'Recovery']
        temp_df = pd.DataFrame(columns=col)
        
        for key,grp in x.groupby(groupnum):
            if (max(grp) <= thresh_dd):
                length = len(grp)-1
                temp_df.loc[len(temp_df)] = [ grp.index[0].strftime("%Y-%m-%d"), grp.idxmin().strftime("%Y-%m-%d") ,grp.index[length].strftime("%Y-%m-%d"), 
                       grp.min(), (grp.index[length]-grp.index[0]).days, (grp.argmin()-grp.index[0]).days, (grp.index[length]-grp.argmin()).days]
        
        tot_days = (self.df['portfolio_value'].index[len(self.df['portfolio_value'])-1] - self.df['portfolio_value'].index[0]).days
        print(" %-time in High DD watermark: " +str(round(100*temp_df['Length'].sum()/tot_days ,0) ) +"% \n") 
        print(" Max DD is " +str(round(min(temp_df['mDD']),2)) +"%" )
        print temp_df
        
        return temp_df