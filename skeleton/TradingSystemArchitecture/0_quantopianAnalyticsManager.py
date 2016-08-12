from necessary_import import *;

'''
AnalyticsManager compatible with the Quantopian log (from logBook) constraint
'''    

class AnalyticsManager ():
    '''
    this class manages logs and analytics
    '''
    def __init__(self, analytics_name, analytics_debug=False):
        
        self.analytics_name = analytics_name
        self.analytics_dump_dir = None
        
        self.__analyticsdump = False
        
        self.__log_state = False
        # create logger object - Only a single logger in Quantopian
        # (not per object instance)
        # self.__logger = log
        
        '''
        by default log.level is at lowest, =0
        we must set opposite at max, =4, to account for user choices
        '''
        if log.level == 0:
            log.level = 4
        
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
        msg = "logging activated in console"
        self.add_log('info',msg)
        return True
        
    def set_log_file (self, level):
        pass
        return True
        
    def set_log_option(self, logconsole=False, logfile=False, level=3):              
        # in Quantopian, only one logger, thus Last Setup Applies to All
        # we make sure we pick the lowest level desired        
        if level < log.level:
            log.level = level
        
        self.__log_state = logconsole or logfile
                   
        if logfile:
            self.set_log_file(level)            
        if logconsole:        
            self.set_log_console(level)

        return
        
    def add_log(self, logtype, msg):
        if not self.get_log():
            return
            
        # get_datetime is UTC by default so set it to NYC exchange for Quantopian
        timestamped_msg = "backtest time: " +str(get_datetime('US/Eastern')) + msg
        # no critical in Quantopian logbook       
        if log.level >3 and logtype in ['error', 'critical']:
            log.error(timestamped_msg)
        elif log.level ==3 and logtype in ['warning', 'error', 'critical']:
            log.warn(timestamped_msg)
        elif log.level <= 2 and logtype in ['info', 'warning', 'error', 'critical']:
            log.info(timestamped_msg)
        elif log.level < 2 and logtype in ['debug', 'info', 'warning', 'error', 'critical']:
            log.debug(timestamped_msg)
        return
        
    def set_dumpanalytics (self, status):
        pass
        
    def get_dumpanalytics (self):
        pass
        
    def create_analytics (self, name, columns):
        pass
        return
        
    def insert_analyticsdata (self, name, row):
        pass      
        return
        
    def create_dir (self, outdir):
        pass
        
    def write_analytics_tocsv (self, output_directory):
        pass
            
        