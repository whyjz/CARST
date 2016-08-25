#!/usr/bin/python

import subprocess;
import sys;

UTM_ZONE="19F";
ICE="/home/akm26/Documents/CDI/GLIMS/Glaciers/CDI_UTM_ICE.dat";
ROCK="/home/akm26/Documents/CDI/GLIMS/Glaciers/CDI_UTM_ROCK.dat";
SRTM="/home/akm26/Documents/CDI/SRTM/SRTM_CDI_clipped.grd";
SLOPE="/home/akm26/Documents/CDI/SRTM/SRTM_CDI_clipped_slope.grd";
ICEFIELD_NAME="cdi";
SLOPE_CUTOFF="10000";
ELEV_CUTOFF="0";

icesat=sys.argv[1];

out=icesat[:icesat.rfind(".")]+"_utm.dat";

cmd="\ngawk '{printf \"%.7f %.7f\\n\", -360+$5, $4}' "+icesat+" | mapproject -Ju"+UTM_ZONE+"/1:1 -F -C\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
utm_coords=pipe.read().strip().split("\n");
pipe.close();

n=0;
file_no=1;

outtrack=out[:out.rfind(".")]+"_"+str(file_no)+".dat";

infile=open(icesat,"r");
outfile=open(out,"w");
outtrackfile=open(outtrack,"w");

prev_time="";
line=infile.readline().strip();
elements=line.split();
cmd="\ndate +\"%s\" -d \""+elements[1]+" "+elements[2]+"\"\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
prev_time=pipe.read().strip();
pipe.close();
outfile.write(elements[0]+" "+elements[1]+" "+elements[2]+" "+utm_coords[n]+" "+str(float(elements[5])-float(elements[6]))+" "+elements[6]+"\n");
outtrackfile.write(elements[0]+" "+elements[1]+" "+elements[2]+" "+utm_coords[n]+" "+str(float(elements[5])-float(elements[6]))+" "+elements[6]+"\n");

while 1:
	line=infile.readline().strip();
	if not line:
		break;
	elements=line.split();
	cmd="\ndate +\"%s\" -d \""+elements[1]+" "+elements[2]+"\"\n";
	pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	time=pipe.read().strip();
	pipe.close();
	if abs(int(time)-int(prev_time)) > 60*60:
		outtrackfile.close();
		file_no+=1;
		outtrack=out[:out.rfind(".")]+"_"+str(file_no)+".dat";
		outtrackfile=open(outtrack,"w");
	outfile.write(elements[0]+" "+elements[1]+" "+elements[2]+" "+utm_coords[n]+" "+str(float(elements[5])-float(elements[6]))+" "+elements[6]+"\n");
	outtrackfile.write(elements[0]+" "+elements[1]+" "+elements[2]+" "+utm_coords[n]+" "+str(float(elements[5])-float(elements[6]))+" "+elements[6]+"\n");
        n=n+1;
	prev_time=time;

outfile.close();
outtrackfile.close();
infile.close();

srtm_out=out[:out.rfind(".")]+"_srtm_"+ICEFIELD_NAME+".dat";
cmd="\ngawk '{print $4\" \"$5\" \"$1\" \"$2\" \"$3\" \"$6\" \"$7}' "+out+" | grdtrack -Qn -G"+SRTM+" | ";
cmd+="grdtrack -Qn -G"+SLOPE+" | ";
cmd+="gawk '$4 !~ /N/ {printf \"%s %s %s %s %s %s %s %s %s %.6f\\n\", $1, $2, $3, $4, $5, $6, $7, $8, $9, $6-$8}' > "+srtm_out+"\n";
subprocess.call(cmd,shell=True);

rockout=srtm_out[:srtm_out.rfind(".")]+"_rock.dat";
iceout=srtm_out[:srtm_out.rfind(".")]+"_ice.dat";
cmd="\ngawk '$9 < "+SLOPE_CUTOFF+" && $8 > "+ELEV_CUTOFF+" {print $0}' "+srtm_out+" | gmtselect -F"+ICE+" -If > temp\n";
cmd+="\ngmtselect "+srtm_out+" -F"+ROCK+" >> temp\n";
cmd+="\nmapproject temp -Ju19F/1:1 -C -F -I | gmtselect -Ns/k/s/k/s | mapproject -Ju19F/1:1 -C -F > "+rockout+"\n";
cmd+="\ngmtselect "+srtm_out+" -F"+ICE+" | gmtselect -F"+ROCK+" -If > "+iceout+"\n";
cmd+="\nrm temp\n";
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

cmd="\ngawk '{print $10}' "+rockout+" | pshistogram -JXh -W1 -F -R-30/30/0/100 -B5:Difference:/10:Counts: -Gblack > "+rockout[:rockout.rfind(".")]+"_hist.ps\n";
cmd+="\ngawk '{print $10}' "+iceout+" | pshistogram -JXh -W1 -F -R-30/30/0/100 -B5:Difference:/10:Counts: -Gblack > "+iceout[:iceout.rfind(".")]+"_hist.ps\n";
subprocess.call(cmd,shell=True);

rock_dist=rockout[:rockout.rfind(".")]+"_dist.dat";
ice_dist=iceout[:iceout.rfind(".")]+"_dist.dat";
cmd="\npython /home/akm26/Documents/Python/track_distance.py "+rockout+" | gawk '{print $1\" \"$2\" \"$3/1000\" \"$4\" \"$5}' > "+rock_dist+"\n";
cmd+="\npython /home/akm26/Documents/Python/track_distance.py "+iceout+" | gawk '{print $1\" \"$2\" \"$3/1000\" \"$4\" \"$5}' > "+ice_dist+"\n";
subprocess.call(cmd,shell=True);

cmd="\nminmax -C "+rock_dist+"\n";
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

psname=rock_dist[:rock_dist.rfind(".")]+".ps";

cmd="\npsbasemap -X5c -JX15c "+R+" -Ba200g200:\"Distance (km)\":/a20f10g20:\"Elevation (m)\":WeSn -K > "+psname+"\n"; 
cmd+="\ngawk '$5 !~ /NaN/ {print $3\" \"$5-$4}' "+rock_dist+" | psxy -J -R -Sc0.1c -Gblue -O >> "+psname+"\n";
subprocess.call(cmd,shell=True);

cmd="\nminmax -C "+ice_dist+"\n";
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

psname=ice_dist[:ice_dist.rfind(".")]+".ps";

cmd="\npsbasemap -X5c -JX15c "+R+" -Ba200g200:\"Distance (km)\":/a20f10g20:\"Elevation (m)\":WeSn -K > "+psname+"\n";
cmd+="\ngawk '$5 !~ /NaN/ {print $3\" \"$5-$4}' "+ice_dist+" | psxy -J -R -Sc0.1c -Gblue -O >> "+psname+"\n";
subprocess.call(cmd,shell=True);

exit();



















