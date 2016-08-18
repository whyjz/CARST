#!/usr/bin/python

import os;
import random;
import subprocess;
import sys;

ICE="/home/akm26/Documents/SPI/InternalRock/SPI_ICE_UTM.dat";
ROCK="/home/akm26/Documents/SPI/InternalRock/SPI_ROCK_UTM.dat";

cmd="\nminmax "+ICE+" -C -m\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
minmax=pipe.read().strip().split();
pipe.close();

xmin=minmax[0];
xmax=minmax[1];
ymin=minmax[2];
ymax=minmax[3];

R="-R"+xmin+"/"+xmax+"/"+ymin+"/"+ymax;

#name=sys.argv[1];
name="spi_ice_values.txt";

out=name[name.rfind("/")+1:name.rfind(".")]+"_2000.txt";

if not os.path.exists(out):
 infile=open(name,"r");

 points=[];
 point="";
 srtm_elev=0.0;

 for line in infile:
  line=line.strip();
  if line.find(">") > -1:
   if srtm_elev > 2000.0:
    point=point+">\n";
    points.append(point);
   point="";
   srtm_elev=0.0;
   continue;
  elements=line.split();
  if elements[4] == "5":
   srtm_elev=float(elements[2]);
  point=point+line+"\n";
 
 infile.close();
 
 outfile=open(out,"w");
 for point in points:
  outfile.write(point);
 outfile.close();

points=[];
point="";
srtm_elev=0.0;

infile=open(out,"r");

for line in infile:
 line=line.strip();
 if line.find(">") > -1:
  point=point+">\n";
  points.append(point);
  point="";
  srtm_elev=0.0;
  continue;
 elements=line.split();
 if elements[4] == "5":
  srtm_elev=float(elements[2]);
 point=point+line+"\n";
 
infile.close();

selected=out[out.rfind("/")+1:out.rfind(".")]+"_selected.txt";
outfile=open(selected,"w");
i=0;
while i < 10:
 point=points[random.randint(0,len(points))];
 elements=point.split();
 x=elements[0];
 y=elements[1];
 cmd="\necho \""+x+" "+y+"\" | gmtselect -F"+ICE+" | gmtselect -F"+ROCK+" -If\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 gmtselect=pipe.read().strip();
 pipe.close();
 if gmtselect.find(x) > -1:
  outfile.write(point);
  i=i+1;
outfile.close();

infile=open(selected,"r");
line=infile.readline().strip();
if not line:
 print("Empty");
 infile.close();
 exit();
elements=line.split();
r=255;
g=0;
b=0;
thickness="0.75";
count=0;
first=True;
times=[];
elevs=[];
t_e={};
t_std={};
x=elements[0].strip();
y=elements[1].strip();
elev=float(elements[2].strip());
time=float(elements[3].strip());
stdv=float(elements[4].strip());
if elev < 3500 and elev > 1800:
 elevs.append(elev);
 times.append(time);
 t_e[time]=elev;
 t_std[time]=stdv;
prev_x=x;
prev_y=y;
psname="";
psname=selected[:selected.rfind(".")]+"_plots.ps";
while 1:
 line=infile.readline().strip();
 if not line:
  break;
 if line.find(">") > -1:
  continue;
 elements=line.split();
 x=elements[0].strip();
 y=elements[1].strip();
 elev=float(elements[2].strip());
 time=float(elements[3].strip());
 stdv=float(elements[4].strip());
 if elev > 3500 or elev < 1800:
  continue;
 elevs.append(elev);
 times.append(time);
 t_e[time]=elev;
 t_std[time]=stdv;
 if x != prev_x or y != prev_y:
  t_e=sorted(t_e.items());
  t_std=sorted(t_std.items());
  outfile=open("temp","w");
  for i in range(0,len(t_e)):
   outfile.write(str(t_e[i][0])+" "+str(t_e[i][1])+" "+str(t_std[i][1])+"\n");
  outfile.close();
  t_e={};
  t_std={};
  cmd="";
  #psname=selected[:selected.rfind(".")]+"_"+str(count)+".ps";
  if first:
   cmd="\npsxy temp -X4c -JX13c -R51000/56000/1800/3500 -Ba730f365g365:\"Modified Julian Day\":/a50f50g50:\"Elevation (m)\":WeSn -Ey -Ss0.25c -W0.5p,black -G"+str(r)+"/"+str(g)+"/"+str(b)+" -K -P --PAPER_MEDIA=B0 > "+psname+"\n"; 
   cmd+="\npsxy -X14c "+ICE+" "+R+" -Jx1:3000000 -W0.3p,black -O -K -m >> "+psname+"\n";
   cmd+="\npsxy "+ROCK+" "+R+" -Jx1:3000000 -W0.3p,black -O -K -m >> "+psname+"\n";
   cmd+="\necho \""+prev_x+" "+prev_y+"\" | psxy -J -R -Sc0.2c -Gred -O -K >> "+psname+"\n";
   first=False;
  else:
   cmd="\npsxy temp -X6c -JX13c -R51000/56000/1800/3500 -Ba730f365g365:\"Modified Julian Day\":/a50f50g50:\"Elevation (m)\":WeSn -Ey -Ss0.25c -W0.5p,black -G"+str(r)+"/"+str(g)+"/"+str(b)+" -O -K >> "+psname+"\n"; 
   cmd+="\npsxy -X14c "+ICE+" "+R+" -Jx1:3000000 -W0.3p,black -O -K -m >> "+psname+"\n";
   cmd+="\npsxy "+ROCK+" "+R+" -Jx1:3000000 -W0.3p,black -O -K -m >> "+psname+"\n";
   cmd+="\necho \""+prev_x+" "+prev_y+"\" | psxy -J -R -Sc0.2c -Gred -O -K >> "+psname+"\n";
  count=count+1;
  subprocess.call(cmd,shell=True,stdout=subprocess.PIPE);
  r=r-3;
  g=g+3;
  b=b+3;
 prev_x=x;
 prev_y=y;

infile.close();

t_e=sorted(t_e.items());
t_std=sorted(t_std.items());
outfile=open("temp","w");
for i in range(0,len(t_e)):
 outfile.write(str(t_e[i][0])+" "+str(t_e[i][1])+" "+str(t_std[i][1])+"\n");
outfile.close();
#psname=selected[:selected.rfind(".")]+"_"+str(count)+".ps";
cmd="\npsxy temp -X6c -JX13c -R51000/56000/1800/3500 -Ba730f365g365:\"Modified Julian Day\":/a50f50g50:\"Elevation (m)\":WeSn -Ey -Ss0.25c -W0.5p,black -G"+str(r)+"/"+str(g)+"/"+str(b)+" -O -K >> "+psname+"\n";
cmd+="\npsxy -X14c "+ICE+" "+R+" -Jx1:3000000 -W0.3p,black -O -K -m >> "+psname+"\n";
cmd+="\npsxy "+ROCK+" "+R+" -Jx1:3000000 -W0.3p,black -O -K -m >> "+psname+"\n";
cmd+="\necho \""+x+" "+y+"\" | psxy -J -R -Sc0.2c -Gred -O >> "+psname+"\n";
cmd+="\nrm temp\n";
subprocess.call(cmd,shell=True,stdout=subprocess.PIPE);



exit();
