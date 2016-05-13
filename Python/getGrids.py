#!/usr/bin/python


# getGrids.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

# Description
# ***********
# Copy *eastxyz.grd and *northxyz.grd files from directories given in input text file

# Usage
# *****
# python getGrids.py input_list.txt
#	input_list.txt: ASCII text file with five columns, 1st column: pair directories to copy grid files from
#							   2nd column: file minimum longitude, minimum latitude, maximum longitude, maximum latitude to cut grid files to
#							   3rd column: Ice boundary file in GMT polygon format
#							   4th column: Rock boundary file in GMT polygon format
#							   5th column: DEM grid file to use for motion-elevation correction


def getGrids(input_list_txt_path):

	import os;

	assert os.path.exists(input_list_txt_path), "\n***** ERROR: " + input_list_txt_path + " does not exist\n";

	import re;

	infile = open(input_list_txt_path, "r");

	pair_dirs = [];

	for line in infile:

		pair_dir, bounds_path, ice_path, rock_path, dem_path = line.split();

		if not os.path.exists(pair_dir):
			continue;

		pair_dirs.append(pair_dir);

		contents   = os.listdir(pair_dir);
		ns_ew_grds = [item for item in contents if re.search("\d{14}_\d{14}_eastxyz\.grd$", item) or re.search("\d{14}_\d{14}_northxyz\.grd$", item)];

		if len(ns_ew_grds) < 2:
			print("\n***** ERROR: NS or EW grid missing for " + pair_dir + " or does not match expected name (14 digits, underscore, 14 digits, east/northxyz.grd), skipping...\n");
			continue;

		ns_grd_path = ns_ew_grds[0];
		ew_grd_path = ns_ew_grds[1];

		if ns_ew_grds[1].find("north") > -1:
			ns_grd_path = ns_ew_grds[1];
			ew_grd_path = ns_ew_grds[0];

		pair_date = ew_grd_path[re.search("\d{14}_\d{14}_east", ew_grd_path).start(0) : re.search("\d{14}_\d{14}_east", ew_grd_path).end(0) - 5];

		if pair_date[0:2] != "20" and pair_date[0:2] != "19":
			pair_date = pair_date[4:8] + pair_date[0:4] + pair_date[8:14] + "_" + pair_date[19:23] + pair_date[15:19] + pair_date[23:29];

		ew_grd_path = pair_dir + "/" + ew_grd_path;
		ns_grd_path = pair_dir + "/" + ns_grd_path;

		new_ew_grd = pair_date + "_eastxyz.grd";
		new_ns_grd = pair_date + "_northxyz.grd";

		bounds_file = open(bounds_path, "r");

		xmin, ymin = bounds_file.readline().split();
		xmax, ymax = bounds_file.readline().split();

		import subprocess;

		cmd  = "\ngrdinfo " + ew_grd_path + "\n";
		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		info = pipe.read().strip();
		pipe.close();

		resolution = info[re.search("x_inc: ",info).end(0):re.search("x_inc: \-*\d+\.*\d*",info).end(0)];
		ew_xmin   = info[re.search("x_min: ",info).end(0):re.search("x_min: \-*\d+\.*\d*",info).end(0)];
		ew_xmax   = info[re.search("x_max: ",info).end(0):re.search("x_max: \-*\d+\.*\d*",info).end(0)];
		ew_ymin   = info[re.search("y_min: ",info).end(0):re.search("y_min: \-*\d+\.*\d*",info).end(0)];
		ew_ymax   = info[re.search("y_max: ",info).end(0):re.search("y_max: \-*\d+\.*\d*",info).end(0)];

		if float(ew_xmin) > float(xmin):
			xmin = str(float(ew_xmin) + float(resolution));

		if float(ew_xmax) < float(xmax):
			xmax = str(float(ew_xmax) - float(resolution));

		if float(ew_ymin) > float(ymin):
			ymin = str(float(ew_ymin) + float(resolution));

		if float(ew_ymax) < float(ymax):
			ymax = str(float(ew_ymax) - float(resolution));

		R = "-R" + xmin + "/" + ymin + "/" + xmax + "/" + ymax + "r";

		cmd  = "\ngrdcut " + ew_grd_path + " " + R + " -G" + new_ew_grd + "\n";
		cmd += "\ngrdcut " + ns_grd_path + " " + R + " -G" + new_ns_grd + "\n";
		subprocess.call(cmd, shell=True);

		new_mag_grd = pair_date + "_magnitude.grd";
		new_mag_ps  = pair_date + "_magnitude.ps";

		scale = "300000";

		cmd  = "\ngrdmath " + new_ew_grd + " " + new_ns_grd + " HYPOT = " + new_mag_grd + "\n";
		cmd += "\nmakecpt -Chaxby -T0/3.5/0.01 > mag.cpt\n";
		cmd += "\ngrdimage " + new_mag_grd + " -Jx1:" + scale + " " + R + " -Cmag.cpt -Q -P -K > " + new_mag_ps + "\n";
		cmd += "\npsxy " + ice_path + " -Jx1:" + scale + " " + R + " -W1p,black -m -O -K >> " + new_mag_ps + "\n";
		cmd += "\npsxy " + rock_path + " -Jx1:" + scale + " " + R + " -W1p,black -m -O -K >> " + new_mag_ps + "\n";
		cmd += "\npsscale -D10c/4c/3c/0.1c -Cmag.cpt -B0.5:\"Speed\":/:\"m day@+-1@+\": -O >> " + new_mag_ps + "\n";
		cmd += "\nps2raster -A -Tf " + new_mag_ps + "\n";
		subprocess.call(cmd,shell=True);

		os.remove(new_mag_ps);

		filt_ew_grd  = pair_date + "_eastxyz_filt.grd";
		filt_ns_grd  = pair_date + "_northxyz_filt.grd";
		filt_mag_grd = pair_date + "_magnitude_filt.grd";
		filt_mag_ps  = pair_date + "_magnitude_filt.ps";

		cmd  = "\nmatlab -nodesktop -nosplash -r \"noiseremoval('" + new_ew_grd + "','" + new_ns_grd + "')\"\n";
		cmd += "\ngrdmath " + filt_ew_grd + " " + filt_ns_grd + " HYPOT = " + filt_mag_grd + "\n";
		cmd += "\ngrdimage " + filt_mag_grd + " -Jx1:" + scale + " " + R + " -Cmag.cpt -Q -P -K > " + filt_mag_ps + "\n";
		cmd += "\npsxy " + ice_path + " -Jx1:" + scale + " " + R + " -W1p,black -m -O -K >> " + filt_mag_ps + "\n";
		cmd += "\npsxy " + rock_path + " -Jx1:" + scale + " " + R + " -W1p,black -m -O -K >> " + filt_mag_ps + "\n";
		cmd += "\npsscale -D10c/4c/3c/0.1c -Cmag.cpt -B0.5:\"Speed\":/:\"m day@+-1@+\": -O >> " + filt_mag_ps + "\n";
		cmd += "\nps2raster -A -Tf " + filt_mag_ps + "\n";	
		subprocess.call(cmd, shell=True);

		os.remove(filt_mag_ps);

		filt_ew_txt = pair_date + "_eastxyz_filt.txt";
		filt_ns_txt = pair_date + "_northxyz_filt.txt";

		cmd  = "\ngrd2xyz " + filt_ew_grd + " | gawk '$3 !~ /a/ && $3 != 0 {print $0}' > " + filt_ew_txt + "\n";
		cmd += "\ngrd2xyz " + filt_ns_grd + " | gawk '$3 !~ /a/ && $3 != 0 {print $0}' > " + filt_ns_txt + "\n";
		subprocess.call(cmd, shell=True);

		from motionElevCorrection import *;

		motionElevCorrection(filt_ew_grd, dem_path, ice_path, rock_path, resolution);	
		motionElevCorrection(filt_ns_grd, dem_path, ice_path, rock_path, resolution);	

		cor_filt_ew_grd  = pair_date + "_eastxyz_filt_corrected.grd";
		cor_filt_ns_grd  = pair_date + "_northxyz_filt_corrected.grd";
		cor_filt_mag_grd = pair_date + "_magnitude_filt_corrected.grd";
		cor_filt_mag_ps  = pair_date + "_magnitude_filt_corrected.ps";

		cmd  = "\ngrdmath " + cor_filt_ew_grd + " " + cor_filt_ns_grd + " HYPOT = " + cor_filt_mag_grd + "\n";
		cmd += "\ngrdimage " + cor_filt_mag_grd + " -Jx1:" + scale + " " + R + " -Cmag.cpt -Q -P -K > " + cor_filt_mag_ps + "\n";
		cmd += "\npsxy " + ice_path + " -Jx1:" + scale + " " + R + " -W1p,black -m -O -K >> " + cor_filt_mag_ps + "\n";
		cmd += "\npsxy " + rock_path + " -Jx1:" + scale + " " + R + " -W1p,black -m -O -K >> " + cor_filt_mag_ps + "\n";
		cmd += "\npsscale -D10c/4c/3c/0.1c -Cmag.cpt -B0.5:\"Speed\":/:\"m day@+-1@+\": -O >> " + cor_filt_mag_ps + "\n";
		cmd += "\nps2raster -A -Tf " + cor_filt_mag_ps + "\n";	
		subprocess.call(cmd, shell=True);

		os.remove(cor_filt_mag_ps);

		break;


	infile.close();

	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: getGrids.py requires at least one argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	getGrids(sys.argv[1]);

	exit();

