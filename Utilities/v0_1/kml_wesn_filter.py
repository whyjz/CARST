#!/usr/bin/python

import re;
import sys;

name=sys.argv[1];
w=sys.argv[2];
e=sys.argv[3];
s=sys.argv[4];
n=sys.argv[5];

coords_str="";

kml="";
temp="";
coords="";
outside=False;

infile=open(name,"r");

while 1:
 line=infile.readline();
 if not line:
  break;
 if line.find("<Placemark") < 0:
  kml=kml+line;
 else:
  temp=temp+line;
  while 1:
   line=infile.readline();
   if not line:
    break;
   temp=temp+line;
   if line.find("</Placemark") > -1:
    if not outside:
     kml=kml+temp;
    temp="";
    outside=False;
    break;
   if line.find("<coordinates") > -1:
    coords=coords+line+" ";
    if line.find("</coordinates") < 0:
     while 1:
      line=infile.readline();
      if not line:
       break;
      temp=temp+line;
      coords=coords+line.strip()+" ";
      if line.find("</coordinates") > -1:
       break;
    coords_list=coords[coords.find("<coordinates>")+13:coords.find("</coordinates>")].split();
    for coord in coords_list:
     coord=coord.replace(","," ");
     elements=coord.split();
     lon=float(elements[0]);
     lat=float(elements[1]);
     if lon < float(w) or lon > float(e) or lat < float(s) or lat > float(n):
      outside=True;
      break;
    coords="";

infile.close();

print(kml);

exit();

