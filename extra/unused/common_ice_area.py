#!/usr/bin/python

import re;
import subprocess;
import sys;

ICE="/home/akm26/Documents/Russia/NovZ/Glaciers/NovZ_bounds_ice_sub_utm41x.gmt";
INTERVAL="480";

image1=sys.argv[1];
image2=sys.argv[2];

cmd="\n/home/akm26/Downloads/gdal-1.8.0/apps/gdal_translate -of GMT -a_nodata 0 "+image1+" image1.grd\n";
cmd+="\ngrdsample image1.grd -I"+INTERVAL+"= -Qn -Gimage1_ds.grd\n";
cmd+="\ngrdclip image1_ds.grd -Sb1/NaN -Gimage1_ds.grd\n";
subprocess.call(cmd,shell=True);


cmd="\n/home/akm26/Downloads/gdal-1.8.0/apps/gdal_translate -of GMT -a_nodata 0 "+image2+" image2.grd\n";
cmd+="\ngrdsample image2.grd -I"+str(int(INTERVAL)/2)+"= -Qn -Gimage2_ds.grd\n";
cmd+="\ngrd2xyz image2_ds.grd | xyz2grd -Rimage1_ds.grd -Gimage2_resamp.grd\n";
cmd+="\ngrdclip image2_resamp.grd -Sb1/NaN -Gimage2_resamp.grd\n";
subprocess.call(cmd,shell=True);


cmd="\ngrdmask "+ICE+" -Rimage1_ds.grd -NNaN/NaN/1 -Gice.grd -m\n";
cmd+="\ngrdmath ice.grd image1_ds.grd OR = image1_ice.grd\n";
cmd+="\ngrdmath ice.grd image2_resamp.grd OR = image2_ice.grd\n";
cmd+="\ngrdmath image1_ice.grd image2_ice.grd OR = overlap.grd\n";
subprocess.call(cmd,shell=True);


cmd="\ngrdvolume overlap.grd\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
volume=pipe.read().split();
pipe.close();

overlap_area=float(volume[0]);

if overlap_area > 0:
 print(image1+" "+image2);




exit();
