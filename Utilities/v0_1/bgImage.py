#!/usr/bin/python


# bgImage.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def bgImage(tif_list_path, box_dat_path):

	import datetime;
	import os;
	import re;
	import subprocess;

	assert os.path.exists(tif_list_path), "\n***** ERROR: " + tif_list_path + " does not exist\n";
	assert os.path.exists(box_dat_path), "\n***** ERROR: " + box_dat_path + " does not exist\n";

	ul_x = ul_y = lr_x = lr_y = "";

	infile = open(box_dat_path, "r");

	ul_x, ul_y = infile.readline().split();
	lr_x, lr_y = infile.readline().split();

	infile.close();

	infile = open(tif_list_path, "r");

	for line in infile:

		tif_path     = line.strip();
		tif_cut_path = tif_path[tif_path.rfind("/") + 1 : tif_path.rfind(".")] + "_cut.tif";
		grd_path     = tif_cut_path[tif_cut_path.rfind("/") + 1 : tif_cut_path.rfind(".")] + ".grd";
		ps_path      = grd_path.replace(".grd", ".ps");

		if not os.path.exists(tif_path):
			print("\n***** WARNING: \"" + tif_path + "\" does not exist, skipping...\n");
			continue;

		search_exp = "L[A-Z]\d{14}[A-Z]{3}\d{2}_B\d{1}\.[A-Z]{3}";
		date      = line[re.search(search_exp, tif_path).start(0) + 9 : re.search(search_exp, tif_path).start(0) + 16];
		date_str  = (datetime.datetime(int(date[0:4]), 1, 1, 0, 0, 0) + datetime.timedelta(days=int(date[4:7])-1)).isoformat(" ").replace("-", "/")[0:10];

		cmd  = "\ngdalinfo " + tif_path + "\n";
		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		info = pipe.read().strip();
		pipe.close();

		utm_zone = info[re.search("UTM\s*zone\s*", info).end(0) : re.search("UTM\s*zone\s*\d+[A-Z]", info).end(0)];

		cmd = "\necho \"" + ul_x + " " + lr_y + "\\n" + lr_x + " " + ul_y + "\" | mapproject -Ju" + utm_zone + "/1:1 -F -C -I\n";
		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		geo_min_x, geo_min_y, geo_max_x, geo_max_y = pipe.read().split();
		pipe.close();

		cmd  = "\ngdal_translate -of GTiff -projwin " + ul_x + " " + ul_y + " " + lr_x + " " + lr_y + " " + tif_path + " " + tif_cut_path + "\n";
		cmd += "\ngdal_translate -of GMT " + tif_cut_path + " " + grd_path + "\n";
		subprocess.call(cmd, shell=True);

		cmd  = "\ngrdinfo " + grd_path + "\n";
		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		info = pipe.read().strip();
		pipe.close();

		zmin = info[re.search("z_min:\s*", info).end(0) : re.search("z_min:\s*\d+\.*\d*", info).end(0)];
		zmax = info[re.search("z_max:\s*", info).end(0) : re.search("z_max:\s*\d+\.*\d*", info).end(0)];
#		zmin = "0";
#		zmax = "45000";
		R    = "-R" + ul_x + "/" + lr_y + "/" + lr_x + "/" + ul_y + "r";
		geoR = "-R" + geo_min_x + "/" + geo_min_y + "/" + geo_max_x + "/" + geo_max_y + "r";
		J    = "-Jx1:50000";
		geoJ = "-Ju" + utm_zone + "/1:50000";

		cmd  = "\nmakecpt -Cgray -T" + zmin + "/" + zmax + "/1 > grayscale.cpt\n";
		cmd += "\ngrdimage " + grd_path + " " + J + " " + R + " -Cgrayscale.cpt -Q --PS_MEDIA=letter -P -K > " + ps_path + "\n";  
		cmd += "\necho \"" + str(float(lr_x) - 1000) + " " + str(float(ul_y) - 200) + " 10p,1,black 0 ML " + date_str + "\" | pstext " + J + " " + R + " -F+f+a+j -Gwhite -W1p,black -O -K >> " + ps_path + "\n"; 
		cmd += "\npsbasemap " + geoJ + " " + geoR + " -Ba0.03125:\"\":/a0.0150625:\"\"::,::.\"\":wESn --FONT_LABEL=10p,1,black --FONT_ANNOT_PRIMARY=10p,1,black --FONT_ANNOT_SECONDARY=10p,1,black --MAP_FRAME_TYPE=inside -O -K >> " + ps_path + "\n";
		cmd += "\npsbasemap " + geoJ + " " + geoR + " -Lfx5.9c/6c/56.5/1k+jr+u --FONT_ANNOT_PRIMARY=8p,1,black --FONT_LABEL=8p,1,black -O >> " + ps_path + "\n";
		cmd += "\nps2raster -A -Tf " + ps_path + "\n";
		subprocess.call(cmd, shell=True);

	infile.close();
	
	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: bgImage.py requires 6 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";

	bgImage(sys.argv[1], sys.argv[2]);

	exit();

