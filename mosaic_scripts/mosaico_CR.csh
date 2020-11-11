#!/bin/csh

# Replace to fit your environment!
source /home/gempak/NAWIPS/Gemenviron

set gtime=`date -u +'%y%m%d/%H%M'`

rm -f radar.gif radar.tif >& /dev/null

nex2img << EOF > nex2img.log
 GRDAREA  = 15.94;-88.3;26.53;-70.85
 PROJ     = LCC/22.35;-81;0
 KXKY     = 1800;1200
 CPYFIL   =  
 GFUNC    = CR
 RADTIM   = ${gtime}
 RADDUR   = 15
 RADFRQ   = 
 STNFIL   = cuba.tbl
 RADMODE  = 
 RADFIL   = radar.gif
 LUTFIL   = upc_rad16.tbl
 list
 run

 exit
EOF

if (-e radar.gif) then
  convert radar.gif -transparent black radar.png
  #cp radar.tif /var/www/htdocs/radmapserver/gisdata
endif
