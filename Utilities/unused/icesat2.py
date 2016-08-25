#!/usr/bin/python

import subprocess;
import sys;

path="/home/emgolos/ICESAT/";
cmd="\nfind "+path+" -name \"*_List*\"\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
lists=pipe.read().split();
pipe.close();

outfile=open("top.dat","w");
outfile.write("#");
outfile.close();

for item in lists:
 infile=open(item,"r");
 archip=item[:item.rfind("/")];
 print(archip);
 outfile=open("top.dat","a");
 outfile.write("# "+archip+"\n");
 outfile.close();
 points=[];
 lons=[];
 lats=[];
 prox_table={};
 minlat=90.0;
 maxlat=0.0;
 minlon=180.0;
 maxlon=0.0;
 outfile=open("temp.dat","w");
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
   outfile.write(lon+" "+lat+"\n");
  datfile.close();
 outfile.close();
 infile.close();
 i=0;
 infile=open(item,"r");
 while i < len(lons):
  if i % 100 == 0:
   print(i);
  cmd="\necho \""+lons[i]+" "+lats[i]+"\" > temp2.dat\n";
  subprocess.call(cmd,shell=True,stdout=subprocess.PIPE);
  outfile=open("top.dat","a");
  outfile.write(lons[i]+" "+lats[i]+"\n");
  outfile.close();
  cmd="\ngmtselect temp.dat -fg -C0.03/temp2.dat >> top.dat\n"; 
  subprocess.call(cmd,shell=True,stdout=subprocess.PIPE);
  outfile=open("top.dat","a");
  outfile.write(">\n");
  outfile.close();
  i=i+1;
 infile.close();
 print(cmd);


exit();
