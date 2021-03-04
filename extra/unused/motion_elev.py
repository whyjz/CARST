#!/usr/bin/python

import os;
import re;
import subprocess;
import sys;

SRTM="/home/akm26/Documents/SPI/SRTM/SRTM_SPI_new_clipped.grd";
ICE="/home/akm26/Documents/SPI/InternalRock/SPI_ICE_UTM.dat";
ROCK="/home/akm26/Documents/SPI/InternalRock/SPI_ROCK_UTM.dat";
SNR_THRESH="14";

path=sys.argv[1];
index=path.rfind("/");
directory=".";
if index > -1:
 directory=path[:index];
pair=path[path.rfind("/")+1:];
pair=pair[:re.search("\d{14}_\d{14}",pair).end(0)];
name=path[path.rfind("/")+1:path.rfind(".")];

R="-R"+path;

print(path);

if not os.path.exists(pair+"_adj_rock.grd"):
 cmd="\ngrdmask "+ICE+" "+R+" -I120= -S5000 -Gtest.grd -m -NNaN/1/1\n";
 cmd+="\ngrdmask "+ICE+" "+R+" -I120= -S600 -Gfirst_pixel.grd -m -NNaN/1/1\n";
 cmd+="\ngrdmask "+ROCK+" "+R+" -I120= -S5000 -Gtest2.grd -m -NNaN/1/1\n";
 cmd+="\ngrdmask "+ROCK+" "+R+" -I120= -S600 -Gfirst_pixel2.grd -m -NNaN/1/1\n";
 cmd+="\ngrdmask "+ICE+" "+R+" -I120= -Gtest3.grd -m -N1/NaN/NaN\n";
 cmd+="\ngrdmask "+ROCK+" "+R+" -I120= -Gtest4.grd -m -NNaN/NaN/1\n";
 cmd+="\ngrdmath test.grd test3.grd OR = bla.grd\n";
 cmd+="\ngrdmath bla.grd first_pixel.grd NAN = bla.grd\n";
 cmd+="\ngrdmath test2.grd test4.grd OR = bla2.grd\n";
 cmd+="\ngrdmath bla2.grd first_pixel2.grd NAN = bla2.grd\n";
 cmd+="\ngrdmath bla.grd bla2.grd XOR = "+pair+"_mask.grd\n";
 cmd+="\ngrdmath "+pair+"_mask.grd first_pixel.grd NAN = "+pair+"_mask.grd\n";
 cmd+="\ngrdmath "+path+" "+pair+"_mask.grd OR = "+pair+"_adj_rock.grd\n";
 cmd+="\ngrdclip "+pair+"_snr.grd -Sb"+SNR_THRESH+"/NaN -Gtemp.grd\n";
 cmd+="\ngrdmath "+pair+"_adj_rock.grd temp.grd OR = "+pair+"_adj_rock.grd\n";
 cmd+="\nrm temp.grd bla.grd test.grd test2.grd test3.grd test4.grd bla2.grd first_pixel.grd first_pixel2.grd\n";
 subprocess.call(cmd,shell=True);

cmd="\ngrdinfo "+pair+"_mask.grd\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
info=pipe.read().strip();
pipe.close();
x_min=info[re.search("x_min: ",info).end(0):re.search("x_min: \d+\.*\d*",info).end(0)];
x_max=info[re.search("x_max: ",info).end(0):re.search("x_max: \d+\.*\d*",info).end(0)];
y_min=info[re.search("y_min: ",info).end(0):re.search("y_min: \d+\.*\d*",info).end(0)];
y_max=info[re.search("y_max: ",info).end(0):re.search("y_max: \d+\.*\d*",info).end(0)];
R="-R"+x_min+"/"+x_max+"/"+y_min+"/"+y_max;

psname=pair+"_mask.ps";
cmd="makecpt -Crainbow -T-1/1/0.1 > mask.cpt\n";
cmd+="\ngrdimage "+pair+"_adj_rock.grd "+R+" -Jx1:400000 -Cmask.cpt -Q -K > "+psname+"\n";
cmd+="\npsxy "+ICE+" -R -J -W0.5p,black -m -O -K >> "+psname+"\n";
cmd+="\npsxy "+ROCK+" -R -J -W0.5p,black -m -O >> "+psname+"\n";
subprocess.call(cmd,shell=True);

cmd="\ngrdmath "+path+" "+pair+"_adj_rock.grd OR = "+name+"_adj.grd\n";
cmd+="\ngrd2xyz "+name+"_adj.grd > "+name+"_adj.txt\n";
cmd+="\ngrdtrack "+name+"_adj.txt -Qn -G"+SRTM+" > "+name+"_adj_elevs.txt\n";
subprocess.call(cmd,shell=True);

cmd="\nminmax -C "+name+"_adj_elevs.txt\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
info=pipe.read().split();
pipe.close();
ymin=info[4];
ymax=info[5];
xmin=info[6];
xmax=info[7];

cmd="gawk '$3 !~ /NaN/ {print $3}' "+name+"_adj_elevs.txt | gmtmath STDIN MEAN = mean.dat\n";
cmd+="gawk '$3 !~ /NaN/ {print $3}' "+name+"_adj_elevs.txt | gmtmath STDIN STD = std.dat\n";
cmd+="gawk '$3 !~ /NaN/ {print $3}' "+name+"_adj_elevs.txt | gmtmath STDIN MED = median.dat\n";
subprocess.call(cmd,shell=True);

infile=open("mean.dat","r");
mean=infile.readline().strip();
infile.close();

infile=open("std.dat","r");
std=infile.readline().strip();
infile.close();

infile=open("median.dat","r");
median=infile.readline().strip();
infile.close();

cmd="\nrm mean.dat std.dat median.dat\n";
subprocess.call(cmd,shell=True);

mean_plus_std=str(float(median)+float(std));
mean_minus_std=str(float(median)-float(std));

cmd="\ngawk '$3 !~ /NaN/ && $4 !~ /NaN/ && $3 < "+mean_plus_std+" && $3 > "+mean_minus_std+" {print $4\" \"$3}' "+name+"_adj_elevs.txt | trend1d -Fm -N2 -V > bla.txt\n";
pipe=subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE).stderr;
trend=pipe.read().strip().split("\n");
pipe.close();

intercept="";
slope="";

for item in trend:
 if item.find("Polynomial") > -1:
  elements=item.split();
  intercept=elements[4]
  slope=elements[5];

cmd="\ngawk '$3 !~ /NaN/ && $4 !~ /NaN/ && $3 < "+mean_plus_std+" && $3 > "+mean_minus_std+" {print $4\" \"$3}' "+name+"_adj_elevs.txt | psxy -JX5i/5i -R"+xmin+"/"+xmax+"/"+ymin+"/"+ymax+" -BSa500g500ne/Wa2g2 -Sc0.05c -Gred -K > "+name+"_adj_elevs_scatter.ps\n";
cmd+="\necho \"0 "+intercept+"\n2500 "+str(2500.*float(slope)+float(intercept))+"\" | psxy -J -R -W0.5p,black -O >> "+name+"_adj_elevs_scatter.ps\n";
subprocess.call(cmd,shell=True);

#cmd="\ngrd2xyz "+path+" > "+name+".txt\n";
cmd="\ngrdtrack "+name+".txt -Qn -G"+SRTM+" > "+name+"_elevs.txt\n";
cmd+="\ngawk '$3 !~ /NaN/ && $4 !~ /NaN/ {print $1\" \"$2\" \"$4}' "+name+"_elevs.txt | xyz2grd -R"+path+" -G"+name+"_elevs.grd\n";
cmd+="\ngrdmath "+name+"_elevs.grd "+slope+" MUL = "+name+"_elevs.grd\n";
cmd+="\ngrdmath "+name+"_elevs.grd "+intercept+" ADD = "+name+"_elevs.grd\n";
cmd+="\ngrdmath "+path+" "+name+"_elevs.grd SUB = "+name+"_corrected.grd\n";
cmd+="\nrm bla.txt "+name+"_elevs.txt "+name+"_elevs.grd\n";
subprocess.call(cmd,shell=True);

exit();
