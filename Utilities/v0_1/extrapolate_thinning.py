#!/usr/bin/python

import re;
import subprocess;
import sys;

SRTM="/home/akm26/Documents/SPI/SRTM/SRTM_SPI_large_subset_clipped_ice_only.grd";
ECRS_low=sys.argv[1];
ECRS_high=sys.argv[2];
BOUND=1100;

cmd="\ngrdinfo "+SRTM+"\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
info=pipe.read().strip();
pipe.close();

zmax=info[re.search("z_max: ",info).end(0):re.search("z_max: \d+\.*\d*",info).end(0)];

for i in range(0,int(zmax),10):
 cmd="\ngrdclip "+SRTM+" -Sb"+str(i)+"/NaN -Sa"+str(i+9)+"/NaN -Gtemp.grd\n";
 if i < BOUND: 
  cmd+="\ngrdmath "+ECRS_low+" temp.grd OR = temp2.grd\n";
 else: 
  cmd+="\ngrdmath "+ECRS_high+" temp.grd OR = temp2.grd\n";
 subprocess.call(cmd,shell=True);
 cmd="\ngrdvolume temp.grd\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 srtm_volume=pipe.read().strip();
 pipe.close();
 elements=srtm_volume.split();
 area=elements[0];
 cmd="\ngrdvolume temp2.grd\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 ecr_volume=pipe.read().strip();
 pipe.close();
 elements=ecr_volume.split();
 ecr=elements[2];
 extrapolated_volume_change=str(float(area)*float(ecr)/1000000000.);
 print(str(i)+" "+area+" "+extrapolated_volume_change+" "+ecr);
 cmd="\nrm temp.grd temp2.grd\n";
 subprocess.call(cmd,shell=True);


exit();
