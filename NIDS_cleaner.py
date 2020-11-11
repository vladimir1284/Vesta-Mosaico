'''
Created on May 6, 2013

@author: vladimir
'''
import logging
import time
import traceback
import sys
import commands


if __name__ == '__main__':
    loglevel = "debug"
    for arg in sys.argv:
        if str(arg[2:5]).lower() == "log":
            loglevel = arg[6:]
            
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    
    log_format = "%(levelname)s | %(asctime)s | %(name)s | %(message)s"
    logging.basicConfig(filename="nids_cleaner.log", level=numeric_level, 
                        format=log_format, datefmt='%H:%M:%S %d/%m/%Y')
    logger = logging.getLogger("NIDS_cleaner")
    
    logger.debug("Initializing NIDS_cleaner...")
    
    try:
        now_time = time.mktime(time.gmtime())
        
        nids_dir = commands.getoutput('''source $HOME/NAWIPS/Gemenviron.profile;
                                        cd $RAD/NIDS;pwd''')
        logger.debug('NIDS dir: ' + nids_dir)
        
        radar_dirs = commands.getoutput('cd %s; ls' % nids_dir).split('\n')
        
        for radar_dir in radar_dirs:
            logger.debug('Cleaning site: %s...' % radar_dir)
            prod_dirs = commands.getoutput('cd %s/%s; ls' % 
                                           (nids_dir,radar_dir)).split('\n')
            
            for prod_dir in prod_dirs:
                logger.debug('Cleaning product: %s...' % prod_dir)
                prod_files = commands.getoutput('cd %s/%s/%s; ls' % 
                                                (nids_dir,radar_dir,
                                                 prod_dir)).split('\n')
                if prod_files[0] != '':
                    for prod_file in prod_files:
                        pfile = prod_file.split('_')
                        pdatetime = [0,0,0,0,0,0,0,0,0]
                        pdatetime[0] = int(pfile[1][0:4])
                        pdatetime[1] = int(pfile[1][4:6])
                        pdatetime[2] = int(pfile[1][6:8])
                        pdatetime[3] = int(pfile[2][0:2])
                        pdatetime[4] = int(pfile[2][2:4])
    
                        ptime = time.mktime(pdatetime)
                        if now_time - ptime > 3600:
                            commands.getoutput('rm %s/%s/%s/%s' %
                                               (nids_dir,radar_dir,prod_dir,
                                                prod_file))
                            logger.debug('Delete old product : %s' % prod_file)            
                
                
    except:        
        class Myfile:
            def __init__(self):
                pass
            def write(self,txt):
                logger.error(txt)
        logger_file = Myfile()
        traceback.print_exc(file = logger_file)
        