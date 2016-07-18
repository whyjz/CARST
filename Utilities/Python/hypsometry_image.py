#!/usr/bin/python

import subprocess;

HYP="/home/akm26/Documents/CDI/ELAs/cdi_hypsometry.txt";

cmd="\nminmax -C -H "+HYP+"\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
minmax=pipe.read().strip().split();
pipe.close();

emin=minmax[0];
emax=minmax[1];
amin=str(float(minmax[2])/1000000.);
amax=str(float(minmax[3])/1000000.);
vmin=str(float(minmax[6])/1000000000.);
vmax=str(float(minmax[7])/1000000000.);

R="-R"+emin+"/"+emax+"/"+amin+"/"+amax;
ecr_R="-R"+emin+"/"+emax+"/"+vmin+"/"+vmax;

psname="cdi_hypsometry.ps";

cmd="\npsbasemap -JX15c "+R+" -B500:\"Elevation (m)\":/5:\"Area (sq. km)\":WSn -K -P --ANNOT_FONT_SIZE_PRIMARY=20 --PAPER_MEDIA=A3 > "+psname+"\n";
cmd+="\ngawk 'NR > 1 {print $1\" \"$2/1000000}' "+HYP+" | psxy -J -R -Ss0.2c -Gred -O -K >> "+psname+"\n";
cmd+="\npsbasemap -J "+ecr_R+" -B500:\"\":/0.004:\"Volume Change Rate (cubic km/yr)\":E -O -K --ANNOT_FONT_SIZE_PRIMARY=20 >> "+psname+"\n";
cmd+="\ngawk 'NR > 1 {print $1\" \"$4/1000000000}' "+HYP+" | psxy -J -R -Ss0.2c -Gblue -O >> "+psname+"\n";
cmd+="\nps2raster -A -Tf "+psname+"\n";
subprocess.call(cmd,shell=True);

exit();
