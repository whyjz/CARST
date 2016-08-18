#!/usr/bin/python

import os;
import re;
import subprocess;


def imageAmpResults(pair_dir, pair, n_grd, e_grd, bounds_xmin, bounds_xmax, bounds_ymin, bounds_ymax, ratio, cscale, utm_zone, image_dir, ice, rock):

	suffix       = n_grd[n_grd.rfind("northxyz_") + len("northxyz_") : n_grd.rfind(".grd")];
	mag_grd_path = pair_dir + "/" + pair + "_magnitude_" + suffix + ".grd";

	if not os.path.exists(mag_grd_path):
		cmd = "";
		cmd += "\ngrdmath " + e_grd + " " + n_grd + " HYPOT = " + mag_grd_path + "\n";
		subprocess.call(cmd,shell=True);

	xmin = bounds_xmin;
	xmax = bounds_xmax;
	ymin = bounds_ymin;
	ymax = bounds_ymax;

	R = "-R" + xmin + "/" + ymin + "/" + xmax + "/" + ymax + "r";
	
	cmd  = "\necho \"" + xmin + " " + ymin + "\n" + xmax + " " + ymax + "\" | /usr/local/bin/mapproject -Ju" + utm_zone + "/1:1 -F -C -I\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	out  = pipe.read().strip().split();
	pipe.close();

	geo_R = "-R" + out[0] + "/" + out[1] + "/" + out[2] + "/" + out[3] + "r";
	mid_lat = str((float(out[1]) + float(out[2])) / 2);

	psname = pair_dir + "/" + pair + "_magnitude_" + suffix + ".ps";

	cmd = "";
	cmd += "\nmakecpt -Chaxby -T0/" + cscale + "/0.05 > " + pair_dir + "/magnitude.cpt\n";
	cmd += "\ngrdimage -Jx1:" + str(ratio) + " " + R + " " + mag_grd_path + " -Q -C" + pair_dir + "/magnitude.cpt -P -K --PAPER_MEDIA=A3 > " + psname + "\n";
	cmd += "\npsxy " + ice + " -Jx1:" + str(ratio) + " " + R + " -W1p,black -m -O -K >> " + psname+"\n";
	cmd += "\npsxy " + rock + " -Jx1:" + str(ratio) + " " + R + " -W1p,black -m -O -K >> " + psname + "\n";
	cmd += "\npsbasemap -Ju" + utm_zone + "/1:" + str(ratio) + " " + geo_R + " -Bf1a1g1:\"Longitude\":/a0.5g0.5:\"\"::,::.\"\":wESn -K -O --BASEMAP_TYPE=inside --PLOT_DEGREE_FORMAT=ddd:mmF --ANNOT_FONT_PRIMARY=1 --ANNOT_FONT_SIZE_PRIMARY=12 --GRID_PEN_PRIMARY=0.25p,100/100/100,- --OBLIQUE_ANNOTATION=6 >> " + psname + "\n";
	cmd += "\necho \"7.25 1.25 3.55 0.9\" | psxy -Sr -JX7i -R0/10/0/10 -Gwhite -O -K >> " + psname + "\n";
	cmd += "\necho \"7.25 1.25 3.55 0.9\" | psxy -Sr -JX7i -R0/10/0/10 -W0.5p,black -O -K >> " + psname + "\n";
	cmd += "\npsbasemap -Ju" + utm_zone + "/1:" + str(ratio) + " " + geo_R + " -Lfx5i/1i/" + mid_lat + "/10k+l+jr -K -O --ANNOT_FONT_PRIMARY=1 --LABEL_FONT=1 --ANNOT_FONT_SIZE_PRIMARY=10 --LABEL_FONT_SIZE=10 >> " + psname + "\n";
	cmd += "\necho \"5.4 1.45 6 2.3\" | psxy -Sr -JX7i -R0/10/0/10 -Gwhite -O -K >> " + psname + "\n";
	cmd += "\necho \"5.4 1.45 6 2.3\" | psxy -Sr -JX7i -R0/10/0/10 -Wblack -O -K >> " + psname + "\n";
	cmd += "\npsscale -D5i/1.4i/1.5i/0.2ih -B1:\"Velocity (m/day)\":/:\"\": -C" + pair_dir + "/magnitude.cpt -O --ANNOT_OFFSET_PRIMARY=0.1c --LABEL_OFFSET=0.1c --LABEL_FONT_SIZE=12 --LABEL_FONT=1 --ANNOT_FONT_PRIMARY=1 --ANNOT_FONT_SIZE_PRIMARY=12 --ANNOT_FONT_SECONDARY=1 --ANNOT_FONT_SIZE_SECONDARY=12 >> " + psname + "\n";
	cmd += "\nps2raster -A -Tf " + psname + "\n";
	subprocess.call(cmd,shell=True);

	outfile = open(pair_dir + "/" + pair + "_image.cmd", "w");
	outfile.write(cmd);
	outfile.close();

	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 14, "\n***** ERROR: imageAmpResults.py requires 14 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	imageAmpResults(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10], sys.argv[11], sys.argv[12], sys.argv[13], sys.argv[14]);

	exit();


