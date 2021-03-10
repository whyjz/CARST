#!/usr/bin/python

# Copyright 2013 Andrew K. Melkonian, all rights reserved

import math;
import re;
import subprocess;


def blender(input_grd_path_1, input_grd_path_2, resolution):
UTM_ZONE = "41X";
REGION   = "Novaya_Zemlya";
PAIR_DIR = "/home/akm26/Documents/Russia/NovZ/Landsat/Blend";
VEL      = "3.0";
ICE	 = "/home/akm26/Documents/Russia/NovZ/Glaciers/NovZ_bounds_ice_sub_utm41x.gmt";


cmd="\nls "+PAIR_DIR+"/*_filt.grd\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
grids=pipe.read().split();
pipe.close(); 

cmd="\ngrdinfo "+grids[0].strip()+"\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
grdinfo=pipe.read();
pipe.close();
g_xmin=grdinfo[re.search("x_min: ",grdinfo).end(0):re.search("x_min: -*\d+\.*\d*",grdinfo).end(0)];
g_xmax=grdinfo[re.search("x_max: ",grdinfo).end(0):re.search("x_max: -*\d+\.*\d*",grdinfo).end(0)];
g_ymin=grdinfo[re.search("y_min: ",grdinfo).end(0):re.search("y_min: -*\d+\.*\d*",grdinfo).end(0)];
g_ymax=grdinfo[re.search("y_max: ",grdinfo).end(0):re.search("y_max: -*\d+\.*\d*",grdinfo).end(0)];

min_x=g_xmin;
max_x=g_xmax;
min_y=g_ymin;
max_y=g_ymax;

R="-R"+g_xmin+"/"+g_xmax+"/"+g_ymin+"/"+g_ymax;
mag_blend_path=PAIR_DIR+"/mag_blend.txt";

blend_file=open(mag_blend_path,"w");
blend_file.write(grids[0].strip()+" "+R+" 1\n");

for i in range(1,len(grids)):
 grid=grids[i].strip();
 resamp_grid=grid[:grid.rfind(".")]+"_resamp.grd";
 cmd="\ngrdinfo "+grid+"\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 grdinfo=pipe.read();
 pipe.close();
 xmin=grdinfo[re.search("x_min: ",grdinfo).end(0):re.search("x_min: -*\d+\.*\d*",grdinfo).end(0)];
 xmax=grdinfo[re.search("x_max: ",grdinfo).end(0):re.search("x_max: -*\d+\.*\d*",grdinfo).end(0)];
 ymin=grdinfo[re.search("y_min: ",grdinfo).end(0):re.search("y_min: -*\d+\.*\d*",grdinfo).end(0)];
 ymax=grdinfo[re.search("y_max: ",grdinfo).end(0):re.search("y_max: -*\d+\.*\d*",grdinfo).end(0)];
 new_xmin=str(float(math.ceil((float(xmin)-float(g_xmin))/120.0))*120.0+float(g_xmin));
 new_xmax=str(float(math.floor((float(xmax)-float(g_xmax))/120.0))*120.0+float(g_xmax));
 new_ymin=str(float(math.ceil((float(ymin)-float(g_ymin))/120.0))*120.0+float(g_ymin));
 new_ymax=str(float(math.floor((float(ymax)-float(g_ymax))/120.0))*120.0+float(g_ymax));
 R="-R"+new_xmin+"/"+new_xmax+"/"+new_ymin+"/"+new_ymax;
 cmd="";
 cmd+="\ngrdsample "+grid+" -G"+resamp_grid+" "+R+" -F -I120=\n";
 subprocess.call(cmd,shell=True);
 blend_file.write(resamp_grid+" "+R+" 1\n");
 if float(new_xmin) < float(min_x):
  min_x=new_xmin;
 if float(new_xmax) > float(max_x):
  max_x=new_xmax;
 if float(new_ymin) < float(min_y):
  min_y=new_ymin;
 if float(new_ymax) > float(max_y):
  max_y=new_ymax;

blend_file.close();

R="-R"+min_x+"/"+min_y+"/"+max_x+"/"+max_y+"r";
scale="3000000";
composite_grd_path=PAIR_DIR+"/2001_composite_mag.grd";
composite_ps_path=composite_grd_path.replace("grd","ps");
vel_cpt_path=PAIR_DIR+"/vel.cpt";
vel_ps_path=vel_cpt_path.replace("cpt","ps");

cmd="\nmakecpt -Crainbow -T0/"+VEL+"/0.01 > "+vel_cpt_path+"\n";

if float(VEL) >= 1.0:
 cpttick="0.5";
elif float(VEL) >= 0.4:
 cpttick="0.2";
else:
 cpttick="0.05";

cmd+="\npsscale -D1.5c/1.5c/6c/0.3c -C"+vel_cpt_path+" -B"+cpttick+":\"m/day\": > "+vel_ps_path+"\n";
subprocess.call(cmd,shell=True);

cmd  = "\ngrdblend "+mag_blend_path+" "+R+" -I120= -G"+composite_grd_path+"\n";
cmd += "\ngrdimage "+composite_grd_path+" -Jx1:"+scale+" "+R+" -C"+vel_cpt_path+" -Q -P -K > "+composite_ps_path+"\n";
cmd += "\npsxy " + ICE + " -J -R -W0.5p,black -m -O >> " + composite_ps_path + "\n";
subprocess.call(cmd,shell=True);
