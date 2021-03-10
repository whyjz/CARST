#!/usr/bin/python

import os;
import random;
import subprocess;
import sys;

ICE="/home/akm26/Documents/SPI/InternalRock/SPI_ICE_UTM.dat";
ROCK="/home/akm26/Documents/SPI/InternalRock/SPI_ROCK_UTM.dat";
ECRS="/home/akm26/Documents/SPI/NEW_ASTER/L14/VerticalCoregistration/spi_std_var_srtmrate60_new_ice_only.txt";
ALT_ECRS="/home/akm26/Documents/SPI/NEW_ASTER/L14/VerticalCoregistration/spi_ecrs_plusminus10_ice_only.txt";

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
name="/home/akm26/Documents/SPI/NEW_ASTER/L14/VerticalCoregistration/spi_ice_values.txt";

out=name[name.rfind("/")+1:name.rfind(".")]+"_1000.txt";

if not os.path.exists(out):
 infile=open(name,"r");

 points=[];
 point="";
 srtm_elev=0.0;

 for line in infile:
  line=line.strip();
  if line.find(">") > -1:
   if srtm_elev > 1000.0:
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

out="spi_ice_values_1000_inpoly.txt";

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

selected_points={};
infile=open(selected,"r");
for line in infile:
 line=line.strip();
 if line.find(">") > -1:
  continue;
 elements=line.split();
 selected_points[elements[0]+" "+elements[1]]=line;
infile.close();

infile=open(ECRS,"r");
for line in infile:
 line=line.strip();
 elements=line.split();
 xy=elements[0]+" "+elements[1];
 if xy in selected_points:
  selected_points[xy]=selected_points[xy]+" "+elements[2]+" "+elements[3];
infile.close();

infile=open(ALT_ECRS,"r");
for line in infile:
 line=line.strip();
 elements=line.split();
 xy=elements[0]+" "+elements[1];
 if xy in selected_points:
  selected_points[xy]=selected_points[xy]+" "+elements[2]+" "+elements[3];
infile.close();

infile=open(selected,"r");
line=infile.readline().strip();
if not line:
 print("Empty");
 infile.close();
 exit();
elements=line.split();
v_shift="60";
h_shift="4";
thickness="0.75";
count=0;
first=True;
times=[];
elevs=[];
xs=[];
ys=[];
t_e={};
t_std={};
x=elements[0].strip();
y=elements[1].strip();
elev=float(elements[2].strip());
time=float(elements[3].strip());
stdv=float(elements[4].strip());
if elev < 2500 and elev > 800:
 elevs.append(elev);
 times.append(time);
 t_e[time]=elev;
 t_std[time]=stdv;
prev_x=x;
prev_y=y;
xs.append(x);
ys.append(y);
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
 if elev > 2500 or elev < 800:
  continue;
 elevs.append(elev);
 times.append(time);
 t_e[time]=elev;
 t_std[time]=stdv;
 if x != prev_x or y != prev_y:
  xs.append(x);
  ys.append(y);
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
  if count != 0 and count % 4 == 0:
   v_shift=str(int(v_shift)-13);
   h_shift="-42";
  elif count % 4 != 0:
   v_shift="0";
   h_shift="14";
  cmd="\nminmax -C temp\n";
  pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
  minmax=pipe.read().split();
  pipe.close();
  elements=selected_points[prev_x+" "+prev_y].split();
  print(elements);
  alt_point="";
  point="51596.0027546 "+elements[6]+"\\n56000 "+str(float(elements[6])+float(elements[5])*((56000.-51596.0027546)/365.25));
  if len(elements) > 7:
   alt_point="51596.0027546 "+elements[8]+"\\n56000 "+str(float(elements[8])+float(elements[7])*((56000.-51596.0027546)/365.25));
  if first:
   cmd="\nmakecpt -Crainbow -T0/9/1 > points.cpt\n";
   cmd+="\ngawk '{print $1\" \"$2\" "+str(count)+" \"$3}' temp | psxy -X4c -Y"+v_shift+"c -JX10c -R51000/56000/800/2500 -Ba730f365g365:\"Modified Julian Day\":/a50f50g50:\"Elevation (m)\":WeSn -Ey -Ss0.5c -Cpoints.cpt -W0.5p,black -K -P --PAPER_MEDIA=B0 > "+psname+"\n"; 
   cmd+="\necho \""+point+"\" | psxy -J -R -W1p,red -O -K >> "+psname+"\n";
   if len(elements) > 7:
    cmd+="\necho \""+alt_point+"\" | psxy -J -R -W1p,blue -O -K >> "+psname+"\n";
   #cmd+="\necho \"51100 2450\\n53690 2450\\n53690 2300\\n51100 2300\\n51100 2450\" | psxy -J -R -Gwhite -O -K >> "+psname+"\n";
   #cmd+="\necho \"51100 2450\\n53690 2450\\n53690 2300\\n51100 2300\\n51100 2450\" | psxy -J -R -W2p,black -O -K >> "+psname+"\n";
   #cmd+="\necho \"51230 2410\\n51830 2410\" | psxy -J -R -W5p,blue -O -K >> "+psname+"\n";
   #cmd+="\necho \"51230 2340\\n51830 2340\" | psxy -J -R -W5p,red -O -K >> "+psname+"\n";
   #cmd+="\necho \"51930 2400 16 0 0 0 +/- 10 m/yr\" | pstext -J -R -O -K >> "+psname+"\n";
   #cmd+="\necho \"51930 2330 16 0 0 0 +10/-60 m/yr\" | pstext -J -R -O -K >> "+psname+"\n";
   #cmd+="\npsxy -X14c "+ICE+" "+R+" -Jx1:3000000 -W0.3p,black -O -K -m >> "+psname+"\n";
   #cmd+="\npsxy "+ROCK+" "+R+" -Jx1:3000000 -W0.3p,black -O -K -m >> "+psname+"\n";
   #cmd+="\necho \""+prev_x+" "+prev_y+"\" | psxy -J -R -Sc0.2c -Gred -O -K >> "+psname+"\n";
   first=False;
  else:
   cmd="\ngawk '{print $1\" \"$2\" "+str(count)+" \"$3}' temp | psxy -X"+h_shift+"c -Y"+v_shift+"c -JX10c -R51000/56000/800/2500 -Ba730f365g365:\"Modified Julian Day\":/a50f50g50:\"Elevation (m)\":WeSn -Ey -Ss0.5c -Cpoints.cpt -W0.5p,black -O -K >> "+psname+"\n"; 
   cmd+="\necho \""+point+"\" | psxy -J -R -W1p,red -O -K >> "+psname+"\n";
   cmd+="\necho \""+alt_point+"\" | psxy -J -R -W1p,blue -O -K >> "+psname+"\n";
   #cmd+="\npsxy -X14c "+ICE+" "+R+" -Jx1:3000000 -W0.3p,black -O -K -m >> "+psname+"\n";
   #cmd+="\npsxy "+ROCK+" "+R+" -Jx1:3000000 -W0.3p,black -O -K -m >> "+psname+"\n";
   #cmd+="\necho \""+prev_x+" "+prev_y+"\" | psxy -J -R -Sc0.2c -Gred -O -K >> "+psname+"\n";
  count=count+1;
  subprocess.call(cmd,shell=True,stdout=subprocess.PIPE);
 prev_x=x;
 prev_y=y;

infile.close();

t_e=sorted(t_e.items());
t_std=sorted(t_std.items());
outfile=open("temp","w");
for i in range(0,len(t_e)):
 outfile.write(str(t_e[i][0])+" "+str(t_e[i][1])+" "+str(t_std[i][1])+"\n");
outfile.close();
if count != 0 and count % 4 == 0:
 v_shift=str(int(v_shift)-13);
 h_shift="-42";
elif count % 4 != 0:
 v_shift="0";
 h_shift="14";
cmd="\nminmax -C temp\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
minmax=pipe.read().split();
pipe.close();
elements=selected_points[prev_x+" "+prev_y].split();
point="51596.0027546 "+elements[6]+"\\n56000 "+str(float(elements[6])+float(elements[5])*((56000.-51596.0027546)/365.25));
alt_point="";
if len(elements) > 7:
 alt_point="51596.0027546 "+elements[8]+"\\n56000 "+str(float(elements[8])+float(elements[7])*((56000.-51596.0027546)/365.25));
#psname=selected[:selected.rfind(".")]+"_"+str(count)+".ps";
cmd="\ngawk '{print $1\" \"$2\" "+str(count)+" \"$3}' temp | psxy -X"+h_shift+"c -Y"+v_shift+"c -JX10c -R51000/56000/800/2500 -Ba730f365g365:\"Modified Julian Day\":/a50f50g50:\"Elevation (m)\":WeSn -Ey -Ss0.5c -Cpoints.cpt -W0.5p,black -O -K >> "+psname+"\n";
cmd+="\necho \""+point+"\" | psxy -J -R -W1p,red -O -K >> "+psname+"\n";
if len(elements) > 7:
 cmd+="\necho \""+alt_point+"\" | psxy -J -R -W1p,blue -O -K >> "+psname+"\n";
cmd+="\npsxy -X11c -Y-1c "+ICE+" "+R+" -Jx1:750000 -W0.5p,black -O -K -m >> "+psname+"\n";
cmd+="\npsxy "+ROCK+" "+R+" -Jx1:750000 -W0.5p,black -O -K -m >> "+psname+"\n";
echo_string=xs[0]+" "+ys[0]+" 0 0";
for i in range(1,len(xs)):
 echo_string+="\n"+xs[i]+" "+ys[i]+" "+str(i)+" 0";
cmd+="\necho \""+echo_string+"\" | psxy -J -R -Sc0.5c -W0.8p,black -Cpoints.cpt -O >> "+psname+"\n";
cmd+="\nrm temp\n";
subprocess.call(cmd,shell=True,stdout=subprocess.PIPE);



exit();
