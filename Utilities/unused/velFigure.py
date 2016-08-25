#!/usr/bin/python


# velFigure.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def velFigure(ew_grd_path, bimage_grd_path, ice_bounds_path, rock_bounds_path, cmax, utm_zone, ul_x, ul_y, lr_x, lr_y):

	import os;

	assert os.path.exists(ew_grd_path), "\n***** ERROR: " + ew_grd_path + " does not exist\n";
	assert os.path.exists(bimage_grd_path), "\n***** ERROR: " + bimage_grd_path + " does not exist\n";
	assert os.path.exists(ice_bounds_path), "\n***** ERROR: " + ice_bounds_path + " does not exist\n";
	assert os.path.exists(rock_bounds_path), "\n***** ERROR: " + rock_bounds_path + " does not exist\n";

	import re;

	pair_path = ew_grd_path[ : ew_grd_path.rfind("/")];
	pair      = ew_grd_path[re.search("\d{14}_\d{14}",ew_grd_path).start(0) : re.search("\d{14}_\d{14}",ew_grd_path).end(0)];
	out_pair  = pair;

	if not re.search("^20", pair) and not re.search("^19", pair):
		out_pair = pair[4:8] + pair[0:4] + pair[8:14] + "_" + pair[19:23] + pair[15:19] + pair[23:29];

	print(out_pair);

	east_grd_path  = ew_grd_path;
	north_grd_path = ew_grd_path.replace("east", "north");
	mag_grd_path   = ew_grd_path.replace("eastxyz","mag");

	if not os.path.exists(mag_grd_path):
		mag_grd_path   = ew_grd_path.replace("eastxyz","magnitude");

	ice_only = True;

	import subprocess;

	if ice_only:

		east_ice_only_grd_path  = east_grd_path[ : east_grd_path.rfind(".")] + "_ice_only.grd";
		north_ice_only_grd_path = north_grd_path[ : north_grd_path.rfind(".")] + "_ice_only.grd";

		if not os.path.exists(east_ice_only_grd_path):

			cmd  = "\ngrdmask " + ice_bounds_path + " -R" + mag_grd_path + " -NNaN/NaN/1 -Gice.grd\n";
			cmd += "\ngrdmask " + rock_bounds_path + " -R" + mag_grd_path + " -N1/NaN/NaN -Grock.grd\n";
			cmd += "\ngrdmath ice.grd rock.grd OR = " + pair_path + "/" + pair + "_ice_only.grd\n";
			cmd += "\ngrdmath " + east_grd_path + " " + pair_path + "/" + pair + "_ice_only.grd OR = " + east_ice_only_grd_path + "\n";
			cmd += "\ngrdmath " + north_grd_path + " " + pair_path + "/" + pair + "_ice_only.grd OR = " + north_ice_only_grd_path + "\n";
			cmd += "\ngrdmath " + east_ice_only_grd_path + " " + north_ice_only_grd_path + " HYPOT = " + mag_grd_path.replace("mag", "mag_ice_only") + "\n";
			subprocess.call(cmd,shell=True);

			os.remove("ice.grd");
			os.remove("rock.grd");

		east_grd_path  = east_ice_only_grd_path;
		north_grd_path = north_ice_only_grd_path;
		mag_grd_path   = mag_grd_path.replace("mag", "mag_ice_only");

	cmd  = "\ngrdinfo " + mag_grd_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	xmin = info[re.search("x_min: ",info).end(0):re.search("x_min: \d+\.*\d*",info).end(0)];
	xmax = info[re.search("x_max: ",info).end(0):re.search("x_max: \d+\.*\d*",info).end(0)];
	ymin = info[re.search("y_min: ",info).end(0):re.search("y_min: \d+\.*\d*",info).end(0)];
	ymax = info[re.search("y_max: ",info).end(0):re.search("y_max: \d+\.*\d*",info).end(0)];

	if ul_x:
		xmin = str(float(xmin) + float(ul_x));
		ymin = str(float(ymin) + float(ul_y));
		xmax = str(float(xmax) + float(lr_x));
		ymax = str(float(ymax) + float(lr_y));

	R = "-R" + xmin + "/" + ymin + "/" + xmax + "/" + ymax + "r";

	cmd = "\ngrdcut " + bimage_grd_path + " " + R + " -Gtemp_bimage.grd\n";
	subprocess.call(cmd, shell=True);

	cmd  = "\ngrdinfo " + bimage_grd_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	bimage_min = info[re.search("z_min:\s*",info).end(0):re.search("z_min:\s*\d+\.*\d*",info).end(0)];
	bimage_max = info[re.search("z_max:\s*",info).end(0):re.search("z_max:\s*\d+\.*\d*",info).end(0)];

	bimage_max = str(float(bimage_max) / 2.);

	cmd  = "\necho \"" + xmin + " " + ymin + "\n" + xmax + " " + ymax + "\" | mapproject -Ju" + utm_zone + "/1:1 -F -C -I\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	out  = pipe.read().strip().split();
	pipe.close();

	geo_R  = "-R" + out[0] + "/" + out[1] + "/" + out[2] + "/" + out[3] + "r";
	ratio  = "800000";
	psname = mag_grd_path.replace("grd", "ps");

	cmd  = "";
#	cmd  = "\nmakecpt -Cgray -T" + bimage_min + "/" + bimage_max + "/1 > grayscale.cpt\n";
	cmd += "\nmakecpt -Chaxby -T0/" + cmax + "/0.05 > mag.cpt\n";
	cmd += "\ngrdimage temp_bimage.grd -Cgrayscale.cpt -Jx1:" + ratio + " " + R + " -K --PS_MEDIA=A3 -P > " + psname + "\n";
#	cmd += "\ngrdvector -Jx1:" + ratio + " " + R + " -I120 " + east_grd_path + " " + north_grd_path + " -Q0.1c+e+jb -Sl0.2c -Cmag.cpt -O -K >> " + psname + "\n";
#	cmd += "\ngrdimage " + mag_grd_path + " -Jx1:" + ratio + " " + R + " -Cmag.cpt -Q --PS_MEDIA=A3 -P -K > " + psname + "\n"; 
	cmd += "\ngrdimage " + mag_grd_path + " -Jx1:" + ratio + " " + R + " -Cmag.cpt -Q -O -K >> " + psname + "\n"; 
	cmd += "\npsxy " + ice_bounds_path + " -Jx1:" + ratio + " " + R + " -W1p,black -O -K >> " + psname + "\n";
	cmd += "\npsxy " + rock_bounds_path + " -Jx1:" + ratio + " " + R + " -W1p,black -O -K >> " + psname + "\n";
	cmd += "\npsbasemap -Ju" + utm_zone + "/1:" + ratio + " " + geo_R + " -Bf0.5a0.5g0.5:\"Longitude\":/a0.25g0.25:\"\"::,::.\"\":wESn -K -O --MAP_FRAME_TYPE=inside --FORMAT_GEO_MAP=ddd:mmF --FONT_ANNOT_PRIMARY=12p,1,white --MAP_GRID_PEN_PRIMARY=0.25p,100/100/100,- >> " + psname + "\n";
	cmd += "\npsbasemap -Ju" + utm_zone + "/1:" + ratio + " " + geo_R + " -Lfx2c/1.5c/58.5/20k+jr+u+p0.5,black+gwhite -K -O --FONT_ANNOT_PRIMARY=8p,1,black --FONT_LABEL=10p,1,black >> " + psname + "\n";
#	cmd += "\necho \"0.15 2.1\\n2.7 2.1\\n2.7 0.95\\n0.15 0.95\" | psxy -JX7i -R0/10/0/10 -Gwhite -W1p,black -O -K >> " + psname + "\n";
	cmd += "\npsscale -D0.5c/4c/4c/0.2c -B1:\"Velocity (m/day)\":/:\"\": -Cmag.cpt -O --MAP_ANNOT_OFFSET_PRIMARY=0.1c --MAP_DEFAULT_PEN=1p,white --MAP_LABEL_OFFSET=0.1c --FONT_LABEL=12p,1,white --FONT_ANNOT_PRIMARY=12p,1,white --FONT_ANNOT_SECONDARY=12p,1,white >> " + psname + "\n";
	cmd += "\nps2raster -A -Tf " + psname + "\n";
	subprocess.call(cmd,shell=True);

	os.remove("temp_bimage.grd");

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 6, "\n***** ERROR: velFigure.py requires 6 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";
	assert os.path.exists(sys.argv[4]), "\n***** ERROR: " + sys.argv[4] + " does not exist\n";

	ul_x = ul_y = lr_x = lr_y = "";

	if len(sys.argv) > 10:
		ul_x = sys.argv[7];
		ul_y = sys.argv[8];
		lr_x = sys.argv[9];
		lr_y = sys.argv[10];
	
	velFigure(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], ul_x, ul_y, lr_x, lr_y);

	exit();

