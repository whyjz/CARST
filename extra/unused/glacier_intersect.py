#!/usr/bin/python

import subprocess;

GLACIER="Marinelli";
ICE="/home/akm26/Documents/CDI/GLIMS/Glaciers/"+GLACIER+"_Glacier_UTM_ICE.dat";

cmd="\nls /home/akm26/Documents/CDI/ASTER/L1B/Pairs/band3n/*/*_eastxyz.txt\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
speeds=pipe.read().strip().split();
pipe.close();

for speed in speeds:
 cmd="\ngawk '$4 !~ /a/ {print $0}' "+speed+" | gmtselect -F"+ICE+"\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 out=pipe.read().strip().split();
 pipe.close();
 if len(out) > 10000:
  print(GLACIER+" "+speed);

exit();
