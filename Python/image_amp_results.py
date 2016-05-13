#!/usr/bin/python

import os;
import re;
import subprocess;


def image_amp_results(pair_dir, pair, n_grd, e_grd, bounds, ratio, cscale, utm_zone, image_dir, ice, rock):

	pair = item[re.search("\d{14}_\d{14}",item).start(0):re.search("\d{14}_\d{14}",item).end(0)];

	cmd += "\ngrdmath " + e_grd + " 2 POW = " + pair_dir + "/esq.grd\n";
	cmd += "\ngrdmath " + n_grd + " 2 POW = " + pair_dir + "/nsq.grd\n";
	cmd += "\ngrdmath " + pair_dir + "/esq.grd " + pair_dir + "/nsq.grd ADD = " + pair_dir + "/sum.grd\n";
	cmd += "\ngrdmath " + pair_dir + "/sum.grd SQRT = " + pair_dir + "/" + pair + "_magnitude_corrected_filt.grd\n";
	cmd += "\nrm " + pair_dir + "/esq.grd " + pair_dir + "/nsq.grd " + pair_dir + "/sum.grd\n";
	subprocess.call(cmd,shell=True);

	suffix = n_grd[n_grd.rfind("northxyz") : n_grd.rfind(".grd")];
	print(suffix);
	mag_grd = pair_dir + "/" + pair + "_magnitude_" + suffix + ".grd";

	return;
	exit();

	cmd = "\ngrdinfo " + pair_dir + "/" + pair + "_magnitude_corrected_filt.grd\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	xmin = info[re.search("x_min: ",info).end(0):re.search("x_min: \d+\.*\d*",info).end(0)];
	xmax = info[re.search("x_max: ",info).end(0):re.search("x_max: \d+\.*\d*",info).end(0)];
	ymin = info[re.search("y_min: ",info).end(0):re.search("y_min: \d+\.*\d*",info).end(0)];
	ymax = info[re.search("y_max: ",info).end(0):re.search("y_max: \d+\.*\d*",info).end(0)];

	xmin = bounds[0];
	xmax = bounds[1];
	ymin = bounds[2];
	ymax = bounds[3];

	R = "-R" + xmin + "/" + ymin + "/" + xmax + "/" + ymax + "r";
	
	cmd = "\necho \"" + xmin + " " + ymin + "\n" + xmax + " " + ymax + "\" | mapproject -Ju" + utm_zone + "/1:1 -F -C -I\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	out = pipe.read().strip().split();
	pipe.close();

	geo_R = "-R" + out[0] + "/" + out[1] + "/" + out[2] + "/" + out[3] + "r";
	earlier_date = pair[pair.find("_") + 1:pair.find("_") + 15];
	psname = pair + "_magnitude_corrected_filt.ps";

	cmd = "";
	#cmd += "\nmakecpt -Cgray -T0/255/1 > grayscale.cpt\n";
	cmd += "\nmakecpt -Chaxby -T0/" + cscale + "/0.05 > magnitude.cpt\n";
#	cmd += "\ngrdimage " + aster + " -Cgrayscale.cpt -Jx1:" + str(ratio) + " " + R + " -Q -K --PAPER_MEDIA=A3 -P > "  +  psname + "\n";
	cmd += "\npsxy " + ice + " -Jx1:" + str(ratio) + " " + R + " -W1p,black -m --PAPER_MEDIA=A3 -P -K > " + psname+"\n";
	cmd += "\npsxy " + rock + " -Jx1:" + str(ratio) + " " + R + " -W1p,black -m -O -K >> " + psname + "\n";
#	cmd += "\ngrdvector -Jx1:" + str(ratio) + " " + R + " -I1200 " + east + " " + north + " -Q0.01i/0.05i/0.02i -Sl0.25c -Cmagnitude.cpt -O -K >> " + psname + "\n";
	cmd += "\ngrdimage -Jx1:" + str(ratio) + " " + R + " " + pair + "_magnitude_corrected_filt.grd -Q -Cmagnitude.cpt -O -K >> " + psname + "\n";
	cmd += "\npsbasemap -Ju" + utm_zone + "/1:" + str(ratio) + " " + geo_R + " -Bf0.25a0.5g0.5:\"Longitude\":/a0.125g0.125:\"\"::,::.\"\":wESn -K -O --BASEMAP_TYPE=inside --PLOT_DEGREE_FORMAT=ddd:mmF --ANNOT_FONT_PRIMARY=1 --ANNOT_FONT_SIZE_PRIMARY=12 --GRID_PEN_PRIMARY=0.25p,100/100/100,- --OBLIQUE_ANNOTATION=6 >> " + psname + "\n";
	cmd += "\necho \"7.25 1.25 3.55 0.9\" | psxy -Sr -JX7i -R0/10/0/10 -Gwhite -O -K >> " + psname + "\n";
	cmd += "\necho \"7.25 1.25 3.55 0.9\" | psxy -Sr -JX7i -R0/10/0/10 -W0.5p,black -O -K >> " + psname + "\n";
	cmd += "\npsbasemap -Ju" + utm_zone + "/1:" + str(ratio) + " " + geo_R + " -Lfx5i/1i/75.5/5k+l+jr -K -O --ANNOT_FONT_PRIMARY=1 --LABEL_FONT=1 --ANNOT_FONT_SIZE_PRIMARY=10 --LABEL_FONT_SIZE=10 >> " + psname + "\n";
	cmd += "\necho \"5.4 1.45 6 2.3\" | psxy -Sr -JX7i -R0/10/0/10 -Gwhite -O -K >> " + psname + "\n";
	cmd += "\necho \"5.4 1.45 6 2.3\" | psxy -Sr -JX7i -R0/10/0/10 -Wblack -O -K >> " + psname + "\n";
	cmd += "\npsscale -D5i/1.4i/1.5i/0.2ih -B1:\"Velocity (m/day)\":/:\"\": -Cmagnitude.cpt -O --ANNOT_OFFSET_PRIMARY=0.1c --LABEL_OFFSET=0.1c --LABEL_FONT_SIZE=12 --LABEL_FONT=1 --ANNOT_FONT_PRIMARY=1 --ANNOT_FONT_SIZE_PRIMARY=12 --ANNOT_FONT_SECONDARY=1 --ANNOT_FONT_SIZE_SECONDARY=12 >> " + psname + "\n";
	cmd += "\nps2raster -A -Tf " + psname + "\n";
	subprocess.call(cmd,shell=True);

exit();
