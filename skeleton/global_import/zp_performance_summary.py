from necessary_import import *

class performance():
    
    def __init__ (self):
        self.ds = pd.Series()
        self.df = pd.DataFrame()
        
    def update_ds(self, dt, value):
        self.ds = self.ds.append(pd.Series(data=value, index={dt} ))
        
    def get_ds(self):
        return self.ds
            
    def store_ds_to_hdf (self, filename, directory="/equity_curves/", path=os.getcwd()):
        if not (os.path.isdir(path+directory)):
            print(" \n!!!!!\n --> Directory " +str(path+directory) +" does not exists. Attempting creation")
            os.makedirs(path+directory)
        filepath = path+directory+filename+'_'+str(datetime.today())+'.h5'
        store = pd.HDFStore(filepath, 'w')
        store['equity'] = self.df
        store.close()
        return filepath
        
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
    
        if abs(thresh_dd) == 0:
            thresh_dd = 0.000001
        if thresh_dd >0: thresh_dd = -thresh_dd
    
        # this should return the max depth and length
        mask = x <= thresh_dd
        groupnum = mask.diff().fillna(method='bfill').cumsum()
   
        if max(groupnum) == 0:
#            print("   -> No occurence of DD <= " +str(thresh_dd) +"%")
#            print(" Max DD is " +str(round(min(x),2)) +"%" )
            return []
            
        col = ['From', 'maxDD', 'To', 'mDD-%', 'mDD-$', 'Length', 'To mDD', 'Recovery']
        temp_df = pd.DataFrame(columns=col)
        
        for key,grp in x.groupby(groupnum):
            if (max(grp) <= thresh_dd):
                length = len(grp)-1
                temp_df.loc[len(temp_df)] = [ grp.index[0].strftime("%Y-%m-%d"), grp.idxmin().strftime("%Y-%m-%d") ,grp.index[length].strftime("%Y-%m-%d"), 
                       grp.min(), abs(round(grp.min()*self.df['highwatermark'][grp.idxmin()]/100)), (grp.index[length]-grp.index[0]).days, (grp.argmin()-grp.index[0]).days, (grp.index[length]-grp.argmin()).days]
        
#        tot_days = (self.df['portfolio_value'].index[len(self.df['portfolio_value'])-1] - self.df['portfolio_value'].index[0]).days
#        print(" %-time in High DD watermark: " +str(round(100*temp_df['Length'].sum()/tot_days ,0) ) +"% \n") 
#        print(" Max DD is " +str(round(min(temp_df['mDD-%']),2)) +"%" )
#        print temp_df
        
        return temp_df
        
    def render_from_trough_to_depth_trough(self, thresh_dd=0):
        dd = self.get_from_trough_to_depth_trough(thresh_dd, first_n=0)
        
        if len(dd) == 0:
            print("   -> No occurence of DD <= " +str(thresh_dd) +"%")
            x = -100* (self.df['drawdowns']/self.df['highwatermark'])
            x[np.isnan(x)]=0
            print(" Max DD is " +str(round(min(x),2)) +"%" )
            return
            
        print("\n DRAWDOWNS ANALYSIS \n ------------------")
        print(" DD period below the " +str(thresh_dd) +"% watermark" )
        
        tot_days = (self.df['portfolio_value'].index[len(self.df['portfolio_value'])-1] - self.df['portfolio_value'].index[0]).days
        print(" %-time in High DD watermark: " +str(round(100*dd['Length'].sum()/tot_days ,0) ) +"% \n") 
        print(" Max DD is " +str(round(min(dd['mDD-%']),2)) +"%\n" )
        print dd
        
        return
        
    def get_gain_to_pain (self):
        '''
        ref: Building reliable trading systems
        gain-to-pain metric is a ratio formed by dividing the average annual return in $ (the gain) by the average annual max drawdown in $ (the pain you experience to get your gain)
        -> the average annual maxDD is the average of the x largest DD divided by the number of year in the backtest, where x is the number of years        
        '''
        dd = self.get_from_trough_to_depth_trough(thresh_dd=0)
        
        nb_year = (self.df['portfolio_value'].idxmax().year - self.df['portfolio_value'].idxmin().year) +1
        gain = self.df['portfolio_value'][-1] - self.df['portfolio_value'][0]
        avg_dd = np.mean(dd.sort(['mDD-$'], ascending=False)[0:nb_year]['mDD-$'])
        
        print("\n GAIN TO PAIN RATIO\n ------------------\n >1.5:excellent|=1:good|<0:bad")
        
        return gain/ (avg_dd*nb_year)
        
    def render_get_gain_to_pain (self):
        g2p = self.get_gain_to_pain()
        print("The gain-to-pain ration is " +str(g2p))