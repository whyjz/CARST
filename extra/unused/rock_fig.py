#!/usr/bin/python

import subprocess;
import sys;

name=sys.argv[1];

path="./";
if name.find("/") > -1:
 path=name[:name.rfind("/")+1];

infile=open(name,"r");
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
if elev < 450 and elev > 0:
 elevs.append(elev);
 times.append(time);
 t_e[time]=elev;
 t_std[time]=stdv;
prev_x=x;
prev_y=y;
psname="";
while 1:
 line=infile.readline().strip();
 if not line:
  break;
 elements=line.split();
 x=elements[0].strip();
 y=elements[1].strip();
 elev=float(elements[2].strip());
 time=float(elements[3].strip());
 stdv=float(elements[4].strip());
 if elev > 450 or elev < 0:
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
  psname=name[:name.rfind(".")]+"_"+str(count)+".ps";
  if first:
   #cmd="\npsxy temp -JX5i -R51000/56000/500/700 -Ba730f365g365/a50f50g50 -W"+thickness+"p,"+str(r)+"/"+str(g)+"/"+str(b)+" -K > "+psname+"\n"; 
   cmd="\npsxy temp -X4c -JX5i -R51000/56000/0/450 -Ba730f365g365:\"Modified Julian Day\":/a50f50g50:\"Elevation (m)\":WeSn -Ey -Ss0.25c -W0.5p,black -G"+str(r)+"/"+str(g)+"/"+str(b)+" > "+psname+"\n"; 
   first=False;
  else:
   #cmd="\npsxy temp -JX5i -R51000/56000/500/700 -Ba730f365g365/a50f50g50 -W"+thickness+"p,"+str(r)+"/"+str(g)+"/"+str(b)+" -K -O >> "+psname+"\n"; 
   cmd="\npsxy temp -X4c -JX5i -R51000/56000/0/450 -Ba730f365g365:\"Modified Julian Day\":/a50f50g50:\"Elevation (m)\":WeSn -Ey -Ss0.25c -W0.5p,black -G"+str(r)+"/"+str(g)+"/"+str(b)+" > "+psname+"\n"; 
  count=count+1;
  subprocess.call(cmd,shell=True,stdout=subprocess.PIPE);
  r=r-3;
  g=g+3;
  b=b+3;
  #thickness=str(float(thickness)-0.05);
 prev_x=x;
 prev_y=y;
t_e=sorted(t_e.items());
t_std=sorted(t_std.items());
outfile=open("temp","w");
for i in range(0,len(t_e)):
 outfile.write(str(t_e[i][0])+" "+str(t_e[i][1])+" "+str(t_std[i][1])+"\n");
outfile.close();
#cmd="\npsxy temp -JX5i -R51000/56000/500/700 -Ba730f365g365/a50f50g50 -W"+thickness+"p,"+str(r)+"/"+str(g)+"/"+str(b)+" -O >> "+psname+"\n";
cmd="\npsxy temp -X4c -JX5i -R51000/56000/0/450 -Ba730f365g365:\"Modified Julian Day\":/a50f50g50:\"Elevation (m)\":WeSn -Ey -Ss0.25c -W0.5p,black -G"+str(r)+"/"+str(g)+"/"+str(b)+" > "+psname+"\n";
cmd+="\nrm temp\n";
subprocess.call(cmd,shell=True,stdout=subprocess.PIPE);
infile.close();

exit();
