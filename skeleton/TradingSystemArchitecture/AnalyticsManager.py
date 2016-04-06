from necessary_import import *;

'''
To Dos:
--------

Objectives
----------

This module enables other classes to track and write debug/log information in 
pandas format. 
1. The primary objective is to save strategy specific information
in terms of [conditions, allocations, orders, variables ...], and book-keeping 
information, so that new/debugged/updated versions of any component of a strategy
could be validated and checked for errors against previous ones.

2. A secondary objective is to provide loggig information to be realyed to 
the console and/or in a file. Each module may have its own logger.

NOTE FOR 2.: QUANTOPIAN HAS A STRONG LIMITATION: ONLY A SINGLE SCRIPT 
CAN BE RUN LIVE ON THEIR PLATFORM (NO MODULES), WHICH IS WHY I'VE CREATED 
zipline2quantopian (see github repo). STICHING ALL MODULES TOGETHER FOR 
QUANTOPIAN PREVENTED THE USUAL USE OF LOGGING AT THE BEGINING OF A MODULE.
ACCORDINGLY, SUCH A LOGGING CLASS WAS REQUIRED 
(I THINK ... LET ME KNOW OTHERWISE).

'''

class Analytics ():
    '''
    this class defines pandas operations for managing analytics
    '''
    def __init__ (self, name, columns):
        self.df = pd.DataFrame(columns=columns)
        self.name = name
        return
        
    def add_row (self, row):
        self.df.loc[len(self.df)] = row
        return
        

class AnalyticsManager (Analytics):
    '''
    this class manages logs and analytics
    '''
    def __init__(self, analytics_name, analytics_debug=False):
        
        self.analytics_name = analytics_name
        self.analytics_dump_dir = None
        
        self.__analyticsdump = False
        
        self.__log_state = False
        # create logger object
        self.__logger = None
        
        self.analytics = dict()
        return
        
    def set_log (self, status):
        self.__log_state = status
        
        if status:
            self.set_log_option()
        return
        
    def get_log (self):
        return self.__log_state
        
    def set_log_console (self, level):
        # creating a second handler to write log on console/terminal
        ch = log.StreamHandler()
        
        # create console handler with a higher log level
        ch.setLevel(level)
        formatter = log.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.__logger.addHandler(ch)
        
        msg = "logging activated in console"
        self.add_log('info',msg)
        return True
        
    def set_log_file (self, level):
        '''
        RotatingFileHandler cannot be used on Quantopian for security
        reasons. A warning during build will be issued but not an error.
        '''
        # redirecting log info in a file handler
        # append log info with a mx size of 1Mo
        fh = RotatingFileHandler(self.analytics_name+'.log', 'a', 1000000, 1)
        
        # create file handler which logs even debug messages
        fh.setLevel(level)
        # create formatter and add it to the handlers
        formatter = log.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.__logger.addHandler(fh)
        
        msg = "logging saved in file"
        self.add_log('info',msg)
        
        return True
        
    def set_log_option(self, logconsole=False, logfile=False, level=log.WARNING):       
        # create logger object
        self.__logger = log.getLogger(self.analytics_name)
        # clearing any existing handlers : not pretty but efficient, and
        # reassociating handlers based on user-configuration input param.
        self.__logger.handlers = []
        
        # create logger with 'spam_application'
        self.__logger.setLevel(level)
        
        self.__log_state = logconsole or logfile
                   
        if logfile:
            self.set_log_file(level)            
        if logconsole:        
            self.set_log_console(level)

        return
        
    def add_log(self, logtype, msg):
        if not self.get_log():
            return

        if logtype == 'critical':
            self.__logger.critical(msg)        
        elif logtype == 'error':
            self.__logger.error(msg)
        elif logtype == 'warning':
            self.__logger.warning(msg)
        elif logtype == 'info':
            self.__logger.info(msg)
        elif logtype == 'debug':
            self.__logger.debug(msg)
        return
        
    def set_dumpanalytics (self, status):
        self.__analyticsdump = status
        
    def get_dumpanalytics (self):
        return self.__analyticsdump
        
    def create_analytics (self, name, columns):
        self.analytics[name] = Analytics (name, columns)
        return
        
    def insert_analyticsdata (self, name, row):
        df = self.analytics[name]
        df.add_row (row)      
        return
        
    def create_dir (self, outdir):
        final_dir = outdir+self.analytics_name+"/"
        if not os.path.exists(final_dir):
            os.makedirs(final_dir)
        self.analytics_dump_dir = final_dir
        
    def write_analytics_tocsv (self, output_directory):
        self.create_dir(output_directory)
        filename = self.analytics_dump_dir+str(datetime.now())+'_analytics_'
        for name,an in self.analytics.iteritems():
            print('Getting Analytics for '+self.analytics_name +'/'+name)
            try:
                self.analytics[name].df.to_csv(filename+name+'.csv')
            except (SystemExit, KeyboardInterrupt):
                raise
            except Exception as e:
                log.error('Failed writing analytics:' +str(self.analytics_name) + str(traceback.format_exc()) )
            
        