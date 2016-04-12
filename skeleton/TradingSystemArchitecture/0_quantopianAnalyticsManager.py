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
        # create logger object
        self.__logger = log
        
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
        # create logger with 'spam_application'
        self.__logger.level = level
        
        self.__log_state = logconsole or logfile
                   
        if logfile:
            self.set_log_file(level)            
        if logconsole:        
            self.set_log_console(level)

        return
        
    def add_log(self, logtype, msg):
        if not self.get_log():
            return

        # no critical in Quantopian logbook
        if logtype == 'critical':
            self.__logger.error(msg)        
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
            
        