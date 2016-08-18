#!/usr/bin/python

import subprocess;
import sys;

UTM_ZONE="18G";
DENSIFY_FACTOR=1000;

name=sys.argv[1];

prev_x="";
prev_y="";

infile=open(name,"r");
while 1:
 line=infile.readline().strip();
 if not line:
  break;
 elements=line.split();
 x=elements[0].strip();
 y=elements[1].strip();
 distance=0.0;
 if prev_x:
  print(prev_x+" "+prev_y+" "+str(distance));
  diff_x=float(x)-float(prev_x);
  diff_y=float(y)-float(prev_y);
  last_x=prev_x;
  last_y=prev_y;
  for i in range(1,DENSIFY_FACTOR):
   cur_x=str(float(prev_x)+float(i)*diff_x/float(DENSIFY_FACTOR));
   cur_y=str(float(prev_y)+float(i)*diff_y/float(DENSIFY_FACTOR));
   distance=distance+((float(cur_x)-float(last_x))**2+(float(cur_y)-float(last_y))**2)**0.5;
   last_x=cur_x;
   last_y=cur_y
   print(cur_x+" "+cur_y+" "+str(distance));
  distance=distance+((float(x)-float(last_x))**2+(float(y)-float(last_y))**2)**0.5;
 prev_x=x;
 prev_y=y;

infile.close();

print(prev_x+" "+prev_y+" "+str(distance));

exit();
