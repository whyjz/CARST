#!/usr/bin/python

import math;
import os;
import re;
import subprocess;
import sys;

UTM_ZONE="19F";

name="";
option="-u";

for i in range(1,len(sys.argv)):
 arg=sys.argv[i];
 if arg.find("-") != 0:
  name=arg;
  if not os.path.exists(name):
   print("\nCan't find "+name+"\n");
   exit();
 else:
   if arg == "-g":
    option="-g";
   elif arg == "-u":
    option="-u";
   else:
    print("\nOption not recognized, assuming any input is UTM\n");

coords=[];
infile=open(name,"r");
line=infile.readline().strip();
elements=line.split();
if option == "-g":
 cmd="\necho \""+line+"\" | mapproject -Ju"+UTM_ZONE+"/1:1 -F -C\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 elements=pipe.read().strip().split();
 pipe.close();
prev_elements=elements;
distance=0.0;
while 1:
 out=elements[0]+" "+elements[1]+" "+str(distance);
 for i in range(2,len(elements)):
  out=out+" "+elements[i];
 print(out);
 line=infile.readline().strip();
 if not line:
  break;
 line=line.strip();
 elements=line.split();
 if option == "-g":
  cmd="\necho \""+line+"\" | mapproject -Ju"+UTM_ZONE+"/1:1 -F -C\n";
  pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
  elements=pipe.read().strip().split();
  pipe.close();
 distance+=((float(elements[0])-float(prev_elements[0]))**2+(float(elements[1])-float(prev_elements[1]))**2)**0.5;
 prev_elements=elements;
infile.close();

exit();

















