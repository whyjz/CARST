#!/usr/bin/python

import subprocess;
import sys;

ICE="/home/akm26/Documents/CDI/GLIMS/Glaciers/CDI_UTM_ICE.dat";
ROCK="/home/akm26/Documents/CDI/GLIMS/Glaciers/CDI_UTM_ROCK.dat";
SRTM="/home/akm26/Documents/CDI/SRTM/SRTM_CDI_clipped.grd";
SRTM_SLOPE="/home/akm26/Documents/CDI/SRTM/SRTM_CDI_clipped_slope.grd";
SRTM_HILLSHADE="/home/akm26/Documents/CDI/SRTM/SRTM_CDI_clipped_hillshade.grd";
UTM_ZONE="19F";

icesat_diff_name=sys.argv[1];

cmd="\nminmax -C -m "+ICE+"\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
minmax=pipe.read().strip().split();
pipe.close();

xmin=str(float(minmax[0]));
xmax=str(float(minmax[1])+80000.);
ymin=str(float(minmax[2])-20000.);
ymax=str(float(minmax[3])+20000.);

R="-R"+xmin+"/"+xmax+"/"+ymin+"/"+ymax;

cmd="\necho \""+xmin+" "+ymin+"\n"+xmax+" "+ymax+"\" | mapproject -Ju"+UTM_ZONE+"/1:1 -F -C -I\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
coords=pipe.read().strip().split();
pipe.close();

geo_R="-R"+coords[0]+"/"+coords[1]+"/"+coords[2]+"/"+coords[3]+"r";

psname=icesat_diff_name[:icesat_diff_name.rfind(".")]+".ps";

cmd="\nmakecpt -Cpanoply -I -T-20/20/1 > diff.cpt\n";
cmd+="\nmakecpt -Cgray -I -T0/2000/1 > srtm.cpt\n";
cmd+="\nmakecpt -Cgray -I -T0/10/1 > slope.cpt\n";
cmd+="\npsbasemap -Jx1:1500000 "+R+" -B40000:\"UTM Easting\":/40000:\"UTM Northing\":WeSn -K > "+psname+"\n";
cmd+="\ngrdimage "+SRTM+" -J -R -Csrtm.cpt -I"+SRTM_HILLSHADE+" -Q -O -K >> "+psname+"\n";
cmd+="\npscoast -Ju"+UTM_ZONE+"/1:1500000 -Df "+geo_R+" -W0.2p,blue -Sblue -O -K >> "+psname+"\n";
cmd+="\ngawk '$3 < 200 {print $0}' "+icesat_diff_name+" | psxy -Jx1:1500000 "+R+" -Sc0.05c -Cdiff.cpt -O -K >> "+psname+"\n";
cmd+="\npsxy "+ICE+" -J -R -W0.2p,black -O -K -m >> "+psname+"\n";
cmd+="\npsxy "+ROCK+" -J -R -W0.2p,black -O -K -m >> "+psname+"\n";
#cmd+="\ngrdimage "+SRTM_SLOPE+" -J -R -Cslope.cpt -Q -O -K >> "+psname+"\n";
cmd+="\npsscale -D23c/4c/5c/0.5c -Cdiff.cpt -B5:\"Difference\":/:\"m\": -O >> "+psname+"\n";
subprocess.call(cmd,shell=True);


exit();
