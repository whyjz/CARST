#!/usr/bin/python


# ecrMap.py
# Author: Andrew Kenneth Melkonian (akm26@cornell.edu)
# All rights reserved


def ecrMap(input_tif_path, bg_grd_path, min_dhdt, max_dhdt, ul_x, ul_y, lr_x, lr_y):

#	SRTM		= "/home/akm26/Documents/Russia/NovZ/DEMs/NovZ_carto_dem_utm41x_clipped.grd";
#	SRTM_HILLSHADE	= "/home/akm26/Documents/Russia/NovZ/DEMs/NovZ_carto_dem_utm41x_clipped_hillshade.grd";
	ICE		= "/home/akm26/Documents/Russia/NovZ/Boundaries/NovZ_bounds_ice_sub_utm41x.gmt";
	ROCK		= "/home/akm26/Documents/Russia/NovZ/Boundaries/NovZ_bounds_rock_sub_utm41x.gmt";
#	UTM_ZONE	= "41X";
	

	import re;
	import subprocess;

	index = input_tif_path.rfind("/");

	input_tif_dir = ".";

	if index > -1:
		input_tif_dir = input_tif_path[ : index];

	input_tif_name = input_tif_path[index + 1 : input_tif_path.rfind(".")];

	input_grd_path = input_tif_dir + "/" + input_tif_name + ".grd";

	if not os.path.exists(input_grd_path):
		cmd = "\ngdal_translate -of GMT " + input_tif_path + " " + input_grd_path + "\n";
		subprocess.call(cmd,shell=True);


	cmd  = "\ngrdinfo " + input_grd_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	xmin = info[re.search("x_min: ",info).end(0) : re.search("x_min: \-*\d+\.*\d*",info).end(0)];
	xmax = info[re.search("x_max: ",info).end(0) : re.search("x_max: \-*\d+\.*\d*",info).end(0)];
	ymin = info[re.search("y_min: ",info).end(0) : re.search("y_min: \-*\d+\.*\d*",info).end(0)];
	ymax = info[re.search("y_max: ",info).end(0) : re.search("y_max: \-*\d+\.*\d*",info).end(0)];

	if ul_x:
		xmin = ul_x;
	
	if ul_y:
		ymax = ul_y;

	if lr_x:
		xmax = lr_x;

	if lr_y:
		ymin = lr_y;

	R = "-R" + xmin + "/" + ymin + "/" + xmax + "/" + ymax + "r";

	#cmd  = "\necho \"" + xmin + " " + ymin + "\n" + xmax + " " + ymax + "\" | /usr/local/gmt/bin/mapproject -Js61/90/70/1:1 -F -C -I " + R + "\n";
	cmd  = "\necho \"" + xmin + " " + ymin + "\n" + xmax + " " + ymax + "\" | /usr/local/gmt/bin/mapproject -Ju41X/1:1 -F -C -I\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	out  = pipe.read().strip().split();
	pipe.close();

	geo_R = "-R" + out[0] + "/" + out[1] + "/" + out[2] + "/" + out[3] + "r";

	ratio = 300000;

	ps_path = input_tif_name + ".ps";

	cmd =  "";
	cmd =  "\nmakecpt -I -Cpanoply -T" + min_dhdt + "/" + max_dhdt + "/0.01 > ecr.cpt\n";
	cmd += "\nmakecpt -Cgray -T1/170/1 > grayscale.cpt\n";
	cmd += "\ngrdimage " + bg_grd_path + " -Jx1:" + str(ratio) + " " + R + " -E300 -Cgrayscale.cpt --PAGE_ORIENTATION=portrait --PAPER_MEDIA=A3 -P -K > " + ps_path + "\n";
	cmd += "\ngrdimage " + input_grd_path + " -Jx1:" + str(ratio) + " " + R + " -Q -Cecr.cpt -O -K >> " + ps_path + "\n";
	#cmd += "\npscoast -Ju" + UTM_ZONE + "/1:" + str(ratio) + " " + geo_R + " -Df -Swhite -W0.5p,black -K -O >> " + ps_path + "\n";
	cmd += "\npsxy " + ICE + " " + R + " -Jx1:" + str(ratio) + " -W1p,black -m -O -K >> " + ps_path + "\n";
	cmd += "\npsxy " + ROCK + " -J -R -W1p,black -m -O -K >> " + ps_path + "\n";
	#cmd += "\npsbasemap -Js61/90/70/1:" + str(ratio) + " " + geo_R + " -Bf0.125a0.125g0.125:\"Longitude\":/a0.0625g0.0625:\"Latitude\"::,::.\"\":wESn -K -O --BASEMAP_TYPE=inside --ANNOT_FONT_SIZE_PRIMARY=10 --PLOT_DEGREE_FORMAT=ddd:mmF --OBLIQUE_ANNOTATION=6 --ANNOT_FONT_PRIMARY=1 >> " + ps_path + "\n";
	cmd += "\npsbasemap -Ju41X/1:" + str(ratio) + " " + geo_R + " -Bf0.25a0.25g0.25:\"Longitude\":/a0.25g0.25:\"Latitude\"::,::.\"\":wESn -K -O --BASEMAP_TYPE=inside --ANNOT_FONT_SIZE_PRIMARY=12 --PLOT_DEGREE_FORMAT=ddd:mmF --OBLIQUE_ANNOTATION=6 --ANNOT_FONT_PRIMARY=1 >> " + ps_path + "\n";
#	cmd += "\necho \"9 2.33 2 3\" | psxy -X-3c -JX7i -R0/10/0/10 -Sr -Gwhite -O -K >> " + ps_path + "\n";
#	cmd += "\necho \"9 2.33 2 3\" | psxy -JX7i -R0/10/0/10 -Sr -Wthin,black -O -K >> " + ps_path + "\n";
	#cmd += "\npsbasemap -Js61/90/70/1:" + str(ratio) + " " + geo_R + " -Lfx3.9i/0.7i/76/5k+jl+u+p1p,black+fwhite -O -K --ANNOT_FONT_SIZE_PRIMARY=8 --ANNOT_FONT_PRIMARY=1 --LABEL_FONT_SIZE=10 >> " + ps_path + "\n";
	cmd += "\npsscale -D11c/6c/3c/0.1c -Cecr.cpt -B5:\"\":/:\"dh/dt (m yr@+-1@+)\": -O --ANNOT_FONT_SIZE_PRIMARY=10 --ANNOT_FONT_PRIMARY=1 --LABEL_FONT=1 --ANNOT_FONT_SECONDARY=1 --LABEL_FONT_SIZE=12 --ANNOT_OFFSET_PRIMARY=0.2c --ANNOT_OFFSET_SECONDARY=0.1c --LABEL_OFFSET=0.2c --D_FORMAT=%.1f >> " + ps_path + "\n";
	cmd += "\nps2raster -A -Tf " + ps_path + "\n";
	print(cmd);
	subprocess.call(cmd,shell=True);


	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 4, "\n***** ERROR: ecrMap.py requires 4 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";

	ul_x = "";
	ul_y = "";
	lr_x = "";
	lr_y = "";	

	if len(sys.argv) > 8:
		ul_x = sys.argv[5];
		ul_y = sys.argv[6];
		lr_x = sys.argv[7];
		lr_y = sys.argv[8];	
	
	ecrMap(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], ul_x, ul_y, lr_x, lr_y);

	exit();

