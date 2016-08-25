#!/usr/bin/python


# removeTrendDEM.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# USAGE
# *****
# python removeTrendDEM.py /path/to/vel.grd /path/to/rock.grd min_diff max_diff
# 	vel.grd:  velocity grid (netcdf format) to remove ramp from
# 	rock.grd: NetCDF-grid that defines off-ice area, must be on the same grid and have the same bounds as "vel.grd"
#	min_diff:  velocities below "min_diff" will be clipped before the a ramp is fitted
#	max_diff:  velocities above "max_diff" will be clipped before the a ramp is fitted


# OUTPUT
# ******
# dem_rr.grd - ramp removed version of vel.grd, written to current working directory


# DESCRIPTION
# ***********
# removeTrendDEM.py fits a planar ramp to the area of "vel.grd" defined in "rock.grd", then remove this ramp from "vel.grd"


def removeTrendDEM(dem_grd_path, diff_grd_path):

	import os;
	import re;
	import subprocess;

	assert os.path.exists(dem_grd_path), "\n***** ERROR: " + dem_grd_path + " does not exist\n";
	assert os.path.exists(diff_grd_path), "\n***** ERROR: " + diff_grd_path + " does not exist\n";

	dem_name = dem_grd_path[dem_grd_path.rfind("/") + 1 : dem_grd_path.rfind(".")];

	dem_dir = "./";

	if dem_grd_path.rfind("/") > -1:
		dem_dir = dem_grd_path[ : dem_grd_path.rfind("/") + 1];

	diff_name = diff_grd_path[diff_grd_path.rfind("/") + 1 : diff_grd_path.rfind(".")];

	diff_dir = "./";

	if diff_grd_path.rfind("/") > -1:
		diff_dir = diff_grd_path[ : diff_grd_path.rfind("/") + 1];

	diff_txt_path = diff_grd_path.replace(".grd", ".txt");

	cmd = "\ngrd2xyz " + diff_grd_path + " | gawk '$0 !~ /a/ {print $0}' > " + diff_txt_path + "\n";
	subprocess.call(cmd, shell=True);

	diff_rr_txt_path = diff_txt_path.replace(".txt", "_trendremoved.txt");

	cmd  = "\ntrend2d " + diff_txt_path + " -Fxyr -N3 -V > " + diff_rr_txt_path + "\n";
	pipe = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE).stderr;
	info = pipe.read();
	pipe.close();

	coeffs = info[re.search("Model Coefficients: ", info).end(0) : ].split();

	cmd  = "\ngmtinfo -C " + diff_rr_txt_path + "\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	xmin, xmax, ymin, ymax, zmin, zmax = pipe.read().split();
	pipe.close();

	x_int = str((float(xmax) - float(xmin)) / 2);
	y_int = str((float(ymax) - float(ymin)) / 2);

	os.remove(diff_txt_path);
	os.remove(diff_rr_txt_path);

	cmd  = "\ngrd2xyz " + dem_grd_path + " | gawk '$0 !~ /a/ {print $0}' > " + dem_dir + "/temp.txt\n";
	cmd += "\ngawk '{print $1\" \"$2\" \"$3-(" + coeffs[0] + "+(($1-" + xmin + ")/" + x_int + "-1)*" + coeffs[1] + "+(($2-" + ymin + ")/" + y_int + "-1)*" + coeffs[2] + ")}' " + dem_dir + "/temp.txt | xyz2grd -R" + dem_grd_path + " -G" + dem_dir + "/" + dem_name + "_rr.grd --IO_NC4_CHUNK_SIZE=c\n";
	subprocess.call(cmd, shell=True);

	cmd  = "\ngrd2xyz " + diff_grd_path + " | gawk '$0 !~ /a/ {print $0}' > " + diff_dir + "/temp.txt\n";
	cmd += "\ngawk '{print $1\" \"$2\" \"$3-(" + coeffs[0] + "+(($1-" + xmin + ")/" + x_int + "-1)*" + coeffs[1] + "+(($2-" + ymin + ")/" + y_int + "-1)*" + coeffs[2] + ")}' " + diff_dir + "/temp.txt | xyz2grd -R" + diff_grd_path + " -G" + diff_dir + "/" + diff_name + "_rr.grd --IO_NC4_CHUNK_SIZE=c\n";
	subprocess.call(cmd, shell=True);

	os.remove(dem_dir + "/temp.txt");
	os.remove(diff_dir + "/temp.txt");

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: removeTrendDEM.py requires 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	removeTrendDEM(sys.argv[1], sys.argv[2]);

	exit();

