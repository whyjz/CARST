#!/usr/bin/python

import os;
import subprocess;
import sys;

GLACIERS="/home/akm26/Documents/Juneau/GLIMS/Glaciers/Working/";
ROCK="/home/akm26/Documents/Juneau/GLIMS/JUNEAU_ROCK_BOUNDS_UTM.dat";
SRTM="/home/akm26/Documents/Juneau/SRTM/juneau_ffB01_fB01_ffB03_combined_srtm.grd";

cwd=os.getcwd();

path=sys.argv[1];

elas=open(path,"r");

line=elas.readline().strip();
while 1:
 line=elas.readline().strip();
 if not line:
  break;
 if not line.find("Lemon") > -1:
  continue;

 print(line);
 elements=line.split();
 glacier=elements[0].strip();
 ela=elements[1].strip();

 if not os.path.exists(glacier+"_Glacier"):
  cmd="\nmkdir "+glacier+"_Glacier\n";
  subprocess.call(cmd,shell=True);

 os.chdir(glacier+"_Glacier");

 cmd="\nfind "+GLACIERS+" -name \""+glacier+"_Glacier_UTM.dat\" -print\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 glac_bounds=pipe.read().strip();
 pipe.close();
 
 cmd="\nminmax -C -m "+glac_bounds+"\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 minmax=pipe.read().split();
 pipe.close();
 
 xmin=minmax[0].strip();
 xmax=minmax[1].strip();
 ymin=minmax[2].strip();
 ymax=minmax[3].strip();
 R="-R"+xmin+"/"+xmax+"/"+ymin+"/"+ymax;
 
 cmd="\ngrdcut "+SRTM+" "+R+" -G"+glacier+"_Glacier_SRTM.grd\n";
 subprocess.call(cmd,shell=True);
 
 cmd="\ngrdmask "+glac_bounds+" -R"+glacier+"_Glacier_SRTM.grd -G"+glacier+"_Glacier_mask.grd -NNaN/NaN/1 -m\n";
 subprocess.call(cmd,shell=True);

 cmd="\ngrdmath "+glacier+"_Glacier_SRTM.grd "+glacier+"_Glacier_mask.grd MUL = "+glacier+"_Glacier_SRTM.grd\n";
 subprocess.call(cmd,shell=True);

 cmd="\nmakecpt -Ctopo -T0/3000/10 > srtm.cpt\n";
 cmd+="\ngrdimage "+glacier+"_Glacier_SRTM.grd -Jx1:300000 -Csrtm.cpt "+R+" -Q -P > "+glacier+"_Glacier_SRTM.ps\n";
 subprocess.call(cmd,shell=True);

 cmd="echo \""+ela+"\" > temp\n";
 cmd+="\ngrdcontour "+glacier+"_Glacier_SRTM.grd -Ctemp -D"+glacier+"_Glacier_contour.dat -Jx1:300000 -m > temp.ps\n";
 cmd+="\nrm temp temp.ps\n";
 subprocess.call(cmd,shell=True);

 cmd="\ngrdclip "+glacier+"_Glacier_SRTM.grd -Sa"+ela+"/NaN -G"+glacier+"_Glacier_SRTM_Ablation.grd\n";
 cmd+="\ngrdclip "+glacier+"_Glacier_SRTM.grd -Sb"+str(int(ela)+1)+"/NaN -G"+glacier+"_Glacier_SRTM_Accumulation.grd\n";
 cmd+="\ngrdimage "+glacier+"_Glacier_SRTM_Ablation.grd -Jx1:300000 -Csrtm.cpt "+R+" -Q -P > "+glacier+"_Glacier_SRTM_Ablation.ps\n";
 cmd+="\ngrdimage "+glacier+"_Glacier_SRTM_Accumulation.grd -Jx1:300000 -Csrtm.cpt "+R+" -Q -P > "+glacier+"_Glacier_SRTM_Accumulation.ps\n";
 cmd+="\nps2raster -A -Tf "+glacier+"_Glacier_SRTM_Ablation.ps\n";
 cmd+="\nps2raster -A -Tf "+glacier+"_Glacier_SRTM_Accumulation.ps\n";
 cmd+="\nrm "+glacier+"_Glacier_SRTM_Ablation.ps "+glacier+"_Glacier_SRTM_Accumulation.ps\n";
 cmd+="\ngrdmath "+glacier+"_Glacier_SRTM_Ablation.grd ISNAN = "+glacier+"_Glacier_SRTM_Ablation.grd\n"
 cmd+="\ngrdmath "+glacier+"_Glacier_SRTM_Accumulation.grd ISNAN = "+glacier+"_Glacier_SRTM_Accumulation.grd\n"
 cmd+="\necho \"1\" > temp\n";
 cmd+="\ngrdcontour "+glacier+"_Glacier_SRTM_Ablation.grd -Ctemp -D"+glacier+"_Glacier_Ablation_contour.dat -Jx1:300000 -m > temp.ps\n";
 cmd+="\ngrdcontour "+glacier+"_Glacier_SRTM_Accumulation.grd -Ctemp -D"+glacier+"_Glacier_Accumulation_contour.dat -Jx1:300000 -m > temp.ps\n";
 cmd+="\nrm temp temp.ps\n";
 cmd+="\ngrdtrack "+glac_bounds+" -G"+SRTM+" -m | gawk '$0 ~ />/ || $4 < "+ela+" {print $0}' > "+glacier+"_Glacier_Ablation_Zone.dat\n";
 subprocess.call(cmd,shell=True);

 segments=[];
 infile=open(glacier+"_Glacier_contour.dat","r");
 segment=[];
 for line in infile:
  if line.find(">") > -1 and len(segment) > 0:
   segments.append(segment);
   segment=[];
  elif line.find(">") < 0:
   segment.append(line);
 infile.close();
 segments.append(segment);

 outfile=open("temp.dat","w");
 infile=open(glacier+"_Glacier_Ablation_Zone.dat","r");
 for segment in segments:
  first=segment[0].strip().split();
  first_x=first[0];
  first_y=first[1];
  last=segment[len(segment)-1].strip().split();
  last_x=last[0];
  last_y=last[1];
  min_distance=10000.0;
  min_x="";
  min_y="";
  prev_distance=10000.0;
  for line in infile:
   if line.find(">") > -1:
    outfile.write(line.strip()+"\n");
    continue;
   elements=line.strip().split();
   x=elements[0];
   y=elements[1];
   distance=((float(x)-float(first_x))**2+(float(y)-float(first_y))**2)**0.5;
   if distance < min_distance:
    min_distance=distance;
    min_x=x;
    min_y=y;
  print(min_x+" "+min_y); 
 infile.close();
 outfile.close();

 """

 zones=["Ablation", "Accumulation"];

 for zone in zones:
  cmd="\nls "+glacier+"*"+zone+"*xyz\n";
  pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
  contours=pipe.read().strip().split();
  pipe.close();
  max_size=0.0;
  max_contour="";
  second_size=0.0;
  second_contour="";
  for contour in contours:
   size=float(os.path.getsize(contour));
   if size > float(max_size):
    max_size=size;
    max_contour=contour;
   if size < float(max_size) and size > float(second_size):
    second_size=size; 
    second_contour=contour;
  #print(max_contour+" "+second_contour);
 
  infile=open(second_contour,"r");
  second_contour_lines=[];
  for line in infile:
   second_contour_lines=[line]+second_contour_lines;
  infile.close();
 
  outfile=open("temp","w");
  for line in second_contour_lines:
   outfile.write(line+"\n");
  outfile.close();
 
  cmd="\ncat "+max_contour+" temp > "+glacier+"_Glacier_"+zone+"_contour.dat\n";
  cmd+="\npsxy "+glacier+"_Glacier_"+zone+"_contour.dat -Jx1:300000 "+R+" -W0.5p,red -P -L -m > "+glacier+"_Glacier_"+zone+"_contour.ps\n";
  cmd+="\nps2raster -A -Tf "+glacier+"_Glacier_"+zone+"_contour.ps\n";
  cmd+="\nrm temp *"+zone+"*.xyz\n";
  #cmd+="\npsxy "+glacier+"_Glacier_"+zone+"_contour.dat -Jx1:300000 "+R+" -W0.5p,red -P -m > "+glacier+"_Glacier_"+zone+"_contour.ps\n";
  #cmd+="\ngrdimage "+glacier+"_Glacier_"+zone+"_mask.grd -Jx1:300000 "+R+" -Csrtm.cpt -Q > "+glacier+"_Glacier_"+zone+"_contour.ps\n";
  #cmd+="\ngrdimage "+glacier+"_Glacier_"+zone+"_mask.grd -Jx1:300000 "+R+" -Csrtm.cpt -Q > "+glacier+"_Glacier_"+zone+"_contour.ps\n";
  #cmd+="\nps2raster -A -Tf "+glacier+"_Glacier_"+zone+"_contour.ps\n";
  #cmd+="\nps2raster -A -Tf "+glacier+"_Glacier_"+zone+"_contour.ps\n";
  #cmd+="\nrm "+glacier+"_Glacier_"+zone+"_contour.ps "+glacier+"_Glacier_"+zone+"_contour.ps\n";
  subprocess.call(cmd,shell=True);
  """

 os.chdir("..");

elas.close();

exit();
