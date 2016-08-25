#!/usr/bin/python

import os;
import re;
import subprocess;
import sys;

UTM_ZONE="19F";

name=sys.argv[1];
glac_id="";

infile=open(name,"r");
while 1:
 line=infile.readline().strip();
 if not line:
  break;
 if line.find("ID") > -1:
  glac_id=line[line.find(">")+1:line.rfind("<")];
 if line.find("NOMBRE_GLA") > -1 or line.find("CODE_GLA") > -1: # and line.find("Marinelli") > -1:
  name=line[line.find(">")+1:line.rfind("<")];
  name=name.replace(" ","_");
  if name == "":
   continue;
  if not re.search("\D",name):
   name="CDI_"+glac_id;
  out=name+"_Glacier.dat";
  outfile="";
  if os.path.exists(out):
   outfile=open(out,"a");
  else:
   outfile=open(out,"w");
  while 1:
   line=infile.readline().strip();
   if not line:
    break;
   if line.find("coordinates") > -1:
    elements=line.split("/coordinates");
    for element in elements:
     if re.search("\d",element):
      element=element[element.rfind(">")+1:element.rfind("<")];
      coords=element.split();
      for coord in coords:
       coord=coord.replace(","," ");
       outfile.write(coord+"\n");
      outfile.write(">\n");
    break;
  outfile.close();
  cmd="\nmapproject "+out+" -Ju"+UTM_ZONE+"/1:1 -F -C -m > "+out[:out.find(".")]+"_UTM.dat\n";
  subprocess.call(cmd,shell=True);
  cmd="\nminmax -C -m "+out[:out.find(".")]+"_UTM.dat\n";
  pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
  minmax=pipe.read().split();
  pipe.close();
  xmin=minmax[0].strip();
  xmax=minmax[1].strip();
  ymin=minmax[2].strip();
  ymax=minmax[3].strip();
  R="-R"+xmin+"/"+xmax+"/"+ymin+"/"+ymax;
  cmd="\npsxy "+out[:out.find(".")]+"_UTM.dat -Jx1:150000 "+R+" -W0.5p,red -m > "+out[:out.find(".")]+"_UTM.ps\n";
  subprocess.call(cmd,shell=True);
infile.close();

cmd="\nls *Glacier_UTM.dat\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
glaciers=pipe.read().split();
pipe.close();

for glacier in glaciers:
  if glacier.find("CDI_0_") > -1 or glacier.find("CDI_525_") > -1 or glacier.find("CDI_418_") > -1 or glacier.find("CDI_23_") > -1:
   cmd="\nmv "+glacier+" "+glacier[:glacier.rfind(".")]+"_ICE.dat\n";
   subprocess.call(cmd,shell=True);
   continue;
  infile=open(glacier,"r");
  seg="";
  segs=[];
  while 1:
   line=infile.readline().strip();
   if not line:
    break;
   seg=seg+line+"\n";
   if line.find(">") > -1:
    segs.append(seg);
    seg=""; 
  infile.close();
  max_seg="";
  max_i=0;
  for i in range(0,len(segs)):
   if len(segs[i]) > len(max_seg):
    max_seg=segs[i];
    max_i=i;
  outfile=open(glacier[:glacier.rfind(".")]+"_ICE.dat","w");
  outfile.write(max_seg);
  outfile.close();
  if len(segs) < 2:
   cmd="\nrm "+glacier+"\n";
   subprocess.call(cmd,shell=True);
   continue;
  outfile=open(glacier[:glacier.rfind(".")]+"_ROCK.dat","w");
  for i in range(0,max_i):
   outfile.write(segs[i]);
  for i in range(max_i+1,len(segs)):
   outfile.write(segs[i]);
  outfile.close();
   

"""

for glacier in glaciers:
  if glacier.find("CDI_0_") > -1 or glacier.find("CDI_23_") > -1 or glacier.find("CDI_418_") > -1 or glacier.find("CDI_525_") > -1 or glacier.find("CDI_564_") > -1:
   continue;
  infile=open(glacier,"r");
  ice="";
  rock="";
  first_seg=True;
  while 1:
   line=infile.readline().strip();
   if not line:
    break;
   if line.find(">") > -1 and first_seg:
    outfile=open(glacier[:glacier.rfind(".")]+"_ICE.dat","w");
    outfile.write(ice+">\n");
    outfile.close();
    first_seg=False;
   if first_seg:
    ice=ice+line+"\n";
   else:
    rock=rock+line+"\n";
  infile.close();
  if not first_seg and re.search("\d",rock):
   outfile=open(glacier[:glacier.rfind(".")]+"_ROCK.dat","w");
   outfile.write(rock+"\n");
   outfile.close();

"""

exit();


















