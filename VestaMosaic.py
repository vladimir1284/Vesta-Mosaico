#!/opt/epd_free-7.3-1-rh5-x86/bin/python
# -*- coding: utf-8 -*-
'''
Created on 08/04/2013

@author: vladimir
'''
import logging
import time
import traceback
import sys
import commands
from GenerateMosaic import GenerateMosaic
import pg


if __name__ == '__main__':
    loglevel = "WARNING"
    for arg in sys.argv:
        if str(arg[2:5]).lower() == "log":
            loglevel = arg[6:]
            
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    
    log_format = "%(levelname)s | %(asctime)s | %(name)s | %(message)s"
    logging.basicConfig(filename="vesta_mosaic.log", level=numeric_level, 
                        format=log_format, datefmt='%H:%M:%S %d/%m/%Y')
    logger = logging.getLogger("VestaMosaic")
    
    logger.debug("Initializing Vesta-Mosaic...")
    
    try:
        # Get db connection
        db_conn = pg.connect(dbname='vesta-db', host='vesta-web', 
                                  user='wilfre', passwd='billar')
        
        # Get available radars
        try:
            site_list = file('cuba.tbl','r')
            site_lines = site_list.read().split('\n')
            site_list.close()
        except:
            logger.error('Problem reading Station information file: cuba.tbl')
            
        radars = [line[0:4] for line in site_lines]
        try:
            radars.remove('') # Exclude empty lines
        except:
            pass
        for radar in radars:
            logger.debug('Available site: %s' % radar)
        
        # Get Mosaic Scripts
        mosaic_scripts = commands.getoutput('ls mosaic_scripts').split('\n')
        
        # Excecute scripts
        for script in mosaic_scripts:
            logger.debug('Excecuting %s...' % script)
            
            start_time = time.time()
            GenerateMosaic(script, radars, db_conn)
            logger.debug('Total product time: %ims' % int(1e3*(time.time()
                                                    -start_time)) + '\n')
        
    except:        
        class Myfile:
            def __init__(self):
                pass
            def write(self,txt):
                logger.error(txt)
        logger_file = Myfile()
        traceback.print_exc(file = logger_file)
        
        
