#!/usr/bin/python

import subprocess;
import sys;

path="/home/emgolos/ICESAT/";
cmd="\nfind "+path+" -name \"*_List*\"\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
lists=pipe.read().split();
pipe.close();

for item in lists:
 infile=open(item,"r");
 archip=item[:item.rfind("/")];
 print(archip);
 points=[];
 lons=[];
 lats=[];
 prox_table={};
 minlat=90.0;
 maxlat=0.0;
 minlon=180.0;
 maxlon=0.0;
 for line in infile:
  line=line.strip();
  if line == "":
   continue;
  print(line);
  datfile=open(archip+"/"+line,"r");
  for line in datfile:
   elements=line.strip().split();
   lat=elements[5].strip();
   lon=elements[6].strip();
   lons.append(lon);
   lats.append(lat);
   points.append(line);
   prox_table[lon+" "+lat]=line;
   if float(lat) < minlat:
    minlat=lat;
   if float(lat) > maxlat:
    maxlat=lat;
   if float(lon) < minlon:
    minlon=lon;
   if float(lon) > maxlon:
    maxlon=lon;
   i=0;
   while i < len(lons)-1:
    if (float(lon)-float(lons[i])) > 0.000277 or (float(lat)-float(lats[i])) > 0.000277:
     i=i+1;
    else:
     i=i+1;
     prox_table[lon+" "+lat]=prox_table[lon+" "+lat]+"\n"+line;
     prox_table[lons[i]+" "+lats[i]]=prox_table[lons[i]+" "+lats[i]]+"\n"+line;
  datfile.close();
 print(minlon+" "+maxlon+" "+minlat+" "+maxlat);
 infile.close();


exit();
