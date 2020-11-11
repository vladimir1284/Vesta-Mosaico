'''
Created on Apr 28, 2013

@author: Vladimir
'''
import logging
import commands
import time
from ImageUpload import ImageUpload

logger = logging.getLogger("GenerateMosaic")
PCODE = {'R':200, 'CR':201, 'ET': 202, 'VIL':203, 'NTP':204, 'N1P':205}

class GenerateMosaic:
    '''
    Clase para ejecutar los script de nex2img
    '''
    
    def __init__(self, script, radars, db_conn):
        '''
        Constructor
        '''
        self.generated = False
        
        # Get Product name
        name = script.split('_')[1]
        name = name.split('.')[0]  
        logger.debug('Product name: %s' % name)
        
        # Excecute script
        out = commands.getoutput('./mosaic_scripts/%s' % script)
        #logger.debug(out)
        
        # Check for used radars        
        try:
            nex2img_log = file('nex2img.log','r')
            self.script_log = nex2img_log.read()
            nex2img_log.close()
        except:
            logger.error('Problem reading nex2img log file: nex2img.log')
                  
        used = []
        for radar in radars:
            if self.usedRadar(radar):
                used.append(radar)
                
        # Upload and update db if generated
        if self.generated:
            start_ftp = time.time()
            
            now_time = time.gmtime(start_ftp)
            
            dirname = "Mosaic/%s/%04i/%02i/%02i" % (name,
                        now_time.tm_year, now_time.tm_mon, 
                        now_time.tm_mday)
            
            iname = "%s_%04i-%02i-%02i_%02i-%02i-00.png" % (name, now_time.tm_year, 
                        now_time.tm_mon,now_time.tm_mday,
                        now_time.tm_hour, now_time.tm_min)
            
            iu = ImageUpload('vesta-web', 'vesta_web_ftp', 'billar') 
            
            ifile = file('radar.png','rb')
            iu.upload(ifile, iname, dirname)
            
            ifile.close()
            iu.disconnect()
            
            logger.debug('FTP image upload time: %ims' % int(1e3*(time.time()
                                                                   -start_ftp)))
            
            # Cuba Norte mosaic extent
            [minx, miny, maxx, maxy] = [-302183,-409851,1497816,790148]
            datetime = "%04i-%02i-%02i %02i:%02i:00" % (self.vol_time.tm_year, 
                        self.vol_time.tm_mon,self.vol_time.tm_mday,
                        self.vol_time.tm_hour, self.vol_time.tm_min)
            
            query_str = """SELECT insert_raster_product
                    ('%s','%s',%i,'%s',ST_GeomFromText('POLYGON(
                    (%i %i,%i %i,%i %i,%i %i,%i %i))', 2085),'%s','%s');""" % \
                    (datetime, 'Mosaic', PCODE[name], dirname + '/' + iname,
                    minx, miny, maxx, miny, maxx, maxy, minx, maxy, minx, miny,
                    '', '')
            logger.debug(query_str)
            try:      
                result = db_conn.query(query_str)
                print result
            except:
                logger.error(db_conn.error)
                
            for radar in used:
                query_str = "SELECT insert_mosaic_radar(%i,'%s')" % (result, radar)
                logger.debug(query_str)
                try:      
                    db_conn.query(query_str)
                except:
                    logger.error(db_conn.error)
            
            
    def usedRadar(self,radar):
        '''
        Find if radar was used in mosaic generation
        '''
        found = False
         
        if self.script_log.find('Using:   $RAD/NIDS/%s' % radar) != -1:
            self.generated = True
            found = True
            logger.debug("Used radar: %s" % radar)
            
        return found
    
    
    