#!/usr/bin/python

import os;
import re;
import scipy;
import subprocess;
import sys;

SNR_THRESH="50";

path=sys.argv[1];
snr=path;

if path.find("azimuth") > -1:
 snr=snr.replace("azimuth","snr");
 label="azimuth";
elif path.find("range") > -1:
 snr=snr.replace("range","snr");
 label="range";

cmd="\ngrdclip "+snr+" -Sb"+SNR_THRESH+"/NaN -Gtemp.grd\n";
cmd+="\ngrdmath "+path+" temp.grd OR = "+label+"_orig.grd\n";
cmd+="\ngrdclip "+label+"_orig.grd -Sa15000/NaN -Sb-15000/NaN -G"+label+"_orig.grd\n";
cmd+="\ngrd2xyz "+label+"_orig.grd > "+label+"_orig.txt\n";
subprocess.call(cmd,shell=True);

cmd="\ngrdinfo "+label+"_orig.grd\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
info=pipe.read();
pipe.close();
xmin=info[re.search("x_min: ",info).end(0):re.search("x_min: -*\d+\.*\d*",info).end(0)];
xmax=info[re.search("x_max: ",info).end(0):re.search("x_max: -*\d+\.*\d*",info).end(0)];
ymin=info[re.search("y_min: ",info).end(0):re.search("y_min: -*\d+\.*\d*",info).end(0)];
ymax=info[re.search("y_max: ",info).end(0):re.search("y_max: -*\d+\.*\d*",info).end(0)];

vals={};
infile=open(""+label+"_orig.txt","r");
for line in infile:
 if line.find("a") < 0:
  elements=line.split();
  if elements[1] not in vals:
   vals[elements[1]]=[elements[2]];
  else:
   vals[elements[1]].append(elements[2]);
infile.close();

medians={};
for yval in vals:
 sorted_vals=sorted(vals[yval]);
 median=sorted_vals[len(sorted_vals)/2];
 medians[yval]=median;

outfile=open("temp_meds.txt","w");
for yval in medians:
 outfile.write(yval+" "+medians[yval]+"\n");
outfile.close();

cmd="\ngawk '$3 !~ /a/ {print $0}' temp_meds.txt | trend1d -Fxm -N10r -V > bla.txt\n";
pipe=subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE).stderr;
trend=pipe.read().strip().split("\n");
pipe.close();

med_grid=scipy.zeros(int(xmax)*int(ymax),dtype=scipy.float32).reshape(int(ymax),int(xmax));
infile=open("bla.txt","r");
for line in infile:
 line=line.strip();
 elements=line.split();
 med_grid[int(float(elements[0])-0.5),:]=elements[1];

med_grid=med_grid.reshape(int(xmax)*int(ymax),1);
med_grid.tofile("med_grid.bin");
cmd="\nxyz2grd med_grid.bin -ZBLf -R"+label+"_orig.grd -Gmed_grid.grd\n";
cmd+="\ngrdmath "+path+" med_grid.grd SUB = "+label+"_ramp_removed.grd\n";
subprocess.call(cmd,shell=True);

exit();
