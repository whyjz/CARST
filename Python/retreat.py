#!/usr/bin/python


def retreat(bg_grd_path, gmt_paths, utm_zone):

	LEGEND_Y = 0.6;
	LEGEND_YSPACING = 3;
	LEGEND_X = 0.7;
	LEGEND_XSPACING = 1.0;
	LEGEND_FONTSIZE = "8";
	LEGEND_FONT	= "1";
	LEGEND_BOXWIDTH = 0.12;

	ice_bounds_path  = "/home/akm26/Documents/Russia/NovZ/Boundaries/NovZ_bounds_ice_sub_utm42x.gmt"
	rock_bounds_path = "/home/akm26/Documents/Russia/NovZ/Boundaries/NovZ_bounds_rock_sub_utm42x.gmt"

	existing_gmt_paths = [];

	for path in gmt_paths:

		if not os.path.exists(path):
			print("\n***** WARNING, " + path + " does not exist, skipping...\n");

		existing_gmt_paths.append(path);

	import re;
	import subprocess;

	cmd  = "\ngrdinfo " + bg_grd_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	xmin = info[re.search("x_min: ",info).end(0):re.search("x_min: \d+\.*\d*",info).end(0)];
	xmax = info[re.search("x_max: ",info).end(0):re.search("x_max: \d+\.*\d*",info).end(0)];
	ymin = info[re.search("y_min: ",info).end(0):re.search("y_min: \d+\.*\d*",info).end(0)];
	ymax = info[re.search("y_max: ",info).end(0):re.search("y_max: \d+\.*\d*",info).end(0)];
	bg_min = info[re.search("z_min:\s*",info).end(0):re.search("z_min:\s*\d+\.*\d*",info).end(0)];
	bg_max = info[re.search("z_max:\s*",info).end(0):re.search("z_max:\s*\d+\.*\d*",info).end(0)];

#	xmin = "368914.24565";
#	xmax = "389991.512562";
#	ymin = "8385656.90714";
#	ymax = "8403318.96781";

	R = "-R" + xmin + "/" + ymin + "/" + xmax + "/" + ymax + "r";

	cmd  = "\necho \"" + xmin + " " + ymin + "\n" + xmax + " " + ymax + "\" | /usr/local/gmt/bin/mapproject -Ju" + utm_zone + "/1:1 -F -C -I\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	out  = pipe.read().strip().split();
	pipe.close();

	geo_R  = "-R" + out[0] + "/" + out[1] + "/" + out[2] + "/" + out[3] + "r";

	ps_path = existing_gmt_paths[0];
	ps_path = ps_path[ps_path.rfind("/") + 1 : re.search("_\d{14}", ps_path).start(0)];
	ps_path = ps_path + "_retreat.ps";

	scale = "40000";
	J     = "-Jx1:" + scale;
	geo_J = "-Ju" + utm_zone + "/1:" + scale; 

	legend_barwidth  = str(0.01 * (float(xmax) - float(xmin)));
	legend_xpos      = str(LEGEND_X * (float(xmax) - float(xmin)) + float(xmin));
	legend_xint      = str(float(legend_barwidth) * float(LEGEND_XSPACING));
	legend_barend    = str(float(legend_xpos) + float(legend_barwidth));
	legend_text_xpos = str(float(legend_xint) + float(legend_barend));
	legend_ypos      = str(LEGEND_Y * (float(ymax) - float(ymin)) + float(ymin));
	legend_yint      = str((float(ymax) - float(ymin)) / 100 * LEGEND_YSPACING);
	legend_box_l     = str(float(legend_xpos) - float(legend_xint));
	legend_box_r     = str(float(legend_xpos) + LEGEND_BOXWIDTH * (float(xmax) - float(xmin)));
	legend_box_u     = str(float(legend_ypos) + float(legend_yint) * (len(existing_gmt_paths) + 1) - float(legend_yint) / 2);
	legend_box_d     = str(float(legend_ypos) - float(legend_yint) / 2);

	cmd  = "\nmakecpt -Cgray -T" + bg_min + "/" + bg_max + "/1 > grayscale.cpt";
	cmd += "\nmakecpt -Cno_green -T0/" + str(len(existing_gmt_paths) - 1) + "/0.1 > retreat.cpt\n";
	cmd += "\ngrdimage " + bg_grd_path + " " + J + " " + R + " -Cgrayscale.cpt -Q -P -K > " + ps_path + "\n";
	cmd += "\npsxy " + ice_bounds_path + " " + J + " " + R + " -W2p,black -m -O -K >> " + ps_path + "\n";
	cmd += "\npsxy " + rock_bounds_path + " " + J + " " + R + " -W2p,black -m -O -K >> " + ps_path + "\n";
	cmd += "\npsbasemap " + geo_J + " " + geo_R + " -Bf0.125a0.125g0.125:\"Longitude\":/a0.0625g0.0625:\"\"::,::.\"\":wESn -K -O --BASEMAP_TYPE=inside --PLOT_DEGREE_FORMAT=ddd:mmF --ANNOT_FONT_PRIMARY=1 --ANNOT_FONT_SIZE_PRIMARY=12 --GRID_PEN_PRIMARY=0.25p,100/100/100,- --OBLIQUE_ANNOTATION=6 >> " + ps_path + "\n";

	cmd += "\necho \"" + legend_box_l + " " + legend_box_u + "\\n" + legend_box_r + " " + legend_box_u + "\\n" + legend_box_r + " " + legend_box_d + "\\n" + legend_box_l + " " +legend_box_d + "\" | psxy " + J + " " + R + " -L -Gwhite -W0.5p,black -O -K >> " + ps_path + "\n";
	cmd += "\necho \"" + legend_xpos + " " + str(float(legend_ypos) + float(legend_yint) * len(existing_gmt_paths)) + " " + LEGEND_FONTSIZE + " 0 " + LEGEND_FONT + " LM Front position\" | pstext " + J + " " + R + " -O -K >> " + ps_path + "\n";

	i = 0;

	for path in existing_gmt_paths:

		label = path[re.search("\d{14}", path).start(0) : re.search("\d{14}", path).end(0)];
		label = label[0:4] + "/" + label[4:6] + "/" + label[6:8];

		cmd += "\n/usr/local/gmt/bin/mapproject -m -Ju" + utm_zone + "/1:1 -F -C " + path + " | psxy -m " + J + " " + R + " -W1p -Cretreat.cpt -O -K >> " + ps_path + "\n";
		cmd += "\necho \"" + legend_barend + " " + str(float(legend_ypos) + float(legend_yint) * i) + " " + str(i) + "\" | psxy " + J + " " + R + " -SB0.1cb" + legend_xpos + " -Cretreat.cpt -O -K >> " + ps_path + "\n"; 
		cmd += "\necho \"" + legend_text_xpos + " " + str(float(legend_ypos) + float(legend_yint) * i) + " " + LEGEND_FONTSIZE + " 0 " + LEGEND_FONT + " LM " + label + "\" | pstext " + J + " " + R + " -O -K >> " + ps_path + "\n";
		i   += 1;

	cmd += "\npsbasemap " + geo_J + " " + geo_R + " -Lfx2c/2c/76.5/1k+jr+u+p0.5,black+fwhite -O --ANNOT_FONT_PRIMARY=1 --LABEL_FONT=1 --ANNOT_FONT_SIZE_PRIMARY=10 --LABEL_FONT_SIZE=10 >> " + ps_path + "\n";
	cmd += "\nps2raster -A -Tf " + ps_path + "\n";
	print(cmd);
	subprocess.call(cmd,shell=True);


	

if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: retreat.py requires at least 2 arguments, " + str(len(sys.argv) - 1) + " given\n";

	bg_grd_path = sys.argv[1];

	gmt_paths = [];

	for i in range(2, len(sys.argv)):
		gmt_paths.append(sys.argv[i]);	

	utm_zone = "41X";

	if not os.path.exists(sys.argv[len(sys.argv) - 1]):
		utm_zone  = sys.argv[len(sys.argv) - 1];
		gmt_paths = gmt_paths[0 : len(gmt_paths) - 1];

	retreat(bg_grd_path, gmt_paths, utm_zone);

	exit();

