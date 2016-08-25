#!/usr/bin/python

import subprocess;
import sys;

UTM_ZONE="19F";
ICE="/home/akm26/Documents/CDI/GLIMS/Glaciers/CDI_UTM_ICE.dat";
ROCK="/home/akm26/Documents/CDI/GLIMS/Glaciers/CDI_UTM_ROCK.dat";
SRTM="/home/akm26/Documents/CDI/SRTM/SRTM_CDI_clipped.grd";
ICEFIELD_NAME="cdi";

icesat=sys.argv[1];

out=icesat[:icesat.rfind(".")]+"_utm.dat";

cmd="\ngawk '{printf \"%.7f %.7f\\n\", -360+$5, $4}' "+icesat+" | mapproject -Ju"+UTM_ZONE+"/1:1 -F -C\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
utm_coords=pipe.read().strip().split("\n");
pipe.close();

n=0;

infile=open(icesat,"r");
outfile=open(out,"w");

for line in infile:
	line=line.strip();
	elements=line.split();
	outfile.write(elements[0]+" "+elements[1]+" "+elements[2]+" "+utm_coords[n]+" "+elements[5]+" "+elements[6]+"\n");
        n=n+1;

outfile.close();
infile.close();

rockout=out[:out.rfind(".")]+"_rock.dat";
iceout=out[:out.rfind(".")]+"_ice.dat";
cmd="\ngawk '{print $4\" \"$5\" \"$6}' "+out+" | gmtselect -F"+ICE+" -If > "+rockout+"\n";
cmd+="\ngawk '{print $4\" \"$5\" \"$6}' "+out+" | gmtselect -F"+ROCK+" >> "+rockout+"\n";
cmd+="\ngawk '{print $4\" \"$5\" \"$6}' "+out+" | gmtselect -F"+ICE+" | gmtselect -F"+ROCK+" -If > "+iceout+"\n";
subprocess.call(cmd,shell=True);

cmd="\nminmax -C -m "+ICE+"\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
minmax=pipe.read().strip().split();
pipe.close();

xmin=minmax[0];
xmax=minmax[1];
ymin=minmax[2];
ymax=minmax[3];

R="-R"+xmin+"/"+xmax+"/"+ymin+"/"+ymax;

psname=rockout[:rockout.rfind(".")]+".ps";

cmd="\npsbasemap "+R+" -Jx1:1000000 -B40000/40000 -K > "+psname+"\n";
cmd+="\npsxy "+ICE+" -R -J -W0.3p,black -m -O -K >> "+psname+"\n";
cmd+="\npsxy "+ROCK+" -R -J -W0.3p,black -m -O -K >> "+psname+"\n";
cmd+="\npsxy "+rockout+" -R -J -Ss0.1c -Gred -O >> "+psname+"\n";
subprocess.call(cmd,shell=True);

srtm_rock=rockout[:rockout.rfind(".")]+"_srtm_"+ICEFIELD_NAME+".dat";
srtm_rock_slope=rockout[:rockout.rfind(".")]+"_srtm_"+ICEFIELD_NAME+"_slope.dat";
cmd="\ngrdtrack "+rockout+" -Qn -G"+SRTM+" > "+srtm_rock+"\n";
cmd+="\ngrdtrack "+rockout+" -Qn -G"+SLOPE+" > "+srtm_rock_slope+"\n";
cmd+="\ngawk '$4 !~ /N/ {printf \"%.7f %.7f %.7f\\n\", $1, $2, $3-$4}' "+srtm_rock+" > "+srtm_rock[:srtm_rock.rfind(".")]+"_diff.dat\n";
cmd+="\ngawk '{print $3}' "+srtm_rock[:srtm_rock.rfind(".")]+"_diff.dat | pshistogram -JXh -W1 -F -R-30/30/0/100 -B5:Difference:/10:Counts: -Gblack > "+srtm_rock[:srtm_rock.rfind(".")]+"_diff_hist.ps\n";
subprocess.call(cmd,shell=True);

srtm_ice=iceout[:iceout.rfind(".")]+"_srtm_"+ICEFIELD_NAME+".dat";
srtm_ice_slope=iceout[:iceout.rfind(".")]+"_srtm_"+ICEFIELD_NAME+"_slope.dat";
cmd="\ngrdtrack "+iceout+" -Qn -G"+SRTM+" > "+srtm_ice+"\n";
cmd+="\ngrdtrack "+iceout+" -Qn -G"+SLOPE+" > "+srtm_ice_slope+"\n";
subprocess.call(cmd,shell=True);

dist=srtm_rock[:srtm_rock.rfind(".")]+"_dist.dat";
cmd="\npython /home/akm26/Documents/Python/track_distance.py "+srtm_rock+" | gawk '{print $1\" \"$2\" \"$3/1000\" \"$4\" \"$5}' > "+dist+"\n";
subprocess.call(cmd,shell=True);

dist_ice=srtm_ice[:srtm_ice.rfind(".")]+"_dist.dat";
cmd="\npython /home/akm26/Documents/Python/track_distance.py "+srtm_ice+" | gawk '{print $1\" \"$2\" \"$3/1000\" \"$4\" \"$5}' > "+dist_ice+"\n";
subprocess.call(cmd,shell=True);

cmd="\nminmax -C "+dist+"\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
minmax=pipe.read().strip().split();
pipe.close();

xmin=minmax[0];
xmax=minmax[1];
ymin=minmax[2];
ymax=minmax[3];
dist_min=minmax[4];
dist_max=minmax[5];
icesat_min=minmax[6];
icesat_max=minmax[7];
srtm_min=minmax[8];
srtm_max=minmax[9];

R="-R0/"+dist_max+"/-200/200";

psname=dist[:dist.rfind(".")]+".ps";

cmd="\npsbasemap -X5c -JX15c "+R+" -Ba200g200:\"Distance (km)\":/a20f10g20:\"Elevation (m)\":WeSn -K > "+psname+"\n"; 
cmd+="\ngawk '$5 !~ /NaN/ {print $3\" \"$5-$4}' "+dist+" | psxy -J -R -Sc0.1c -Gblue -O >> "+psname+"\n";
#cmd+="\ngawk '{print $3\" \"$5}' "+dist+" | psxy -J -R -Sc0.1c -Gred -O >> "+psname+"\n";
subprocess.call(cmd,shell=True);

cmd="\nminmax -C "+dist_ice+"\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
minmax=pipe.read().strip().split();
pipe.close();

xmin=minmax[0];
xmax=minmax[1];
ymin=minmax[2];
ymax=minmax[3];
dist_min=minmax[4];
dist_max=minmax[5];
icesat_min=minmax[6];
icesat_max=minmax[7];
srtm_min=minmax[8];
srtm_max=minmax[9];

R="-R0/"+dist_max+"/-200/200";

psname=dist_ice[:dist_ice.rfind(".")]+".ps";

cmd="\npsbasemap -X5c -JX15c "+R+" -Ba200g200:\"Distance (km)\":/a20f10g20:\"Elevation (m)\":WeSn -K > "+psname+"\n";
cmd+="\ngawk '$5 !~ /NaN/ {print $3\" \"$5-$4}' "+dist_ice+" | psxy -J -R -Sc0.1c -Gblue -O >> "+psname+"\n";
#cmd+="\ngawk '{print $3\" \"$5}' "+dist+" | psxy -J -R -Sc0.1c -Gred -O >> "+psname+"\n";
subprocess.call(cmd,shell=True);

exit();



















