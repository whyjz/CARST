#!/usr/bin/python

# resampGrids.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

# USAGE
# *****
# python resampGrids.py /path/to/one_grid.grd /path/to/two_grid.grd resolution
#	/path/to/one_grid.grd: Path to a valid netCDF grid file
#	/path/to/two_grid.grd: A valid netCDF grid file
#	resolution:   A number indicating the desired output resolution in the units of one_grid.grd and two_grid.grd
# NOTE: one_grid.grd and two_grid.grd must use the same coordinate system

# OUTPUT
# ******
# This script outputs /path/to/one_grid_resamp.grd and /path/to/two_grid_resamp.grd, which will have the minimum bounds that cover both one_grid.grd and two_grid.grd, and the specified resolution

# REQUIREMENTS
# ************
# This script requires GMT installed and in the default path, tested with GMT4 and python 2.6.5


def resampGrids(input1_grd_path, input2_grd_path, resolution):

#	Check input grids exist

	assert os.path.exists(input1_grd_path), "\n***** ERROR: " + input1_grd_path + " does not exist\n";
	assert os.path.exists(input2_grd_path), "\n***** ERROR: " + input2_grd_path + " does not exist\n";

	import subprocess;

#	Find bounds of first grid

	cmd  = "\ngrdinfo " + input1_grd_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	import re;

	xmin1 = info[re.search("x_min: ",info).end(0):re.search("x_min: -*\d+\.*\d*",info).end(0)];
	xmax1 = info[re.search("x_max: ",info).end(0):re.search("x_max: -*\d+\.*\d*",info).end(0)];
	ymin1 = info[re.search("y_min: ",info).end(0):re.search("y_min: -*\d+\.*\d*",info).end(0)];
	ymax1 = info[re.search("y_max: ",info).end(0):re.search("y_max: -*\d+\.*\d*",info).end(0)];

#	Initialize global bounds to first grid's bounds

	min_x = xmin1;
	max_x = xmax1;
	min_y = ymin1;
	max_y = ymax1;

#	Find bounds of second grid

	cmd  = "\ngrdinfo " + input2_grd_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	xmin2 = info[re.search("x_min: ",info).end(0):re.search("x_min: -*\d+\.*\d*",info).end(0)];
	xmax2 = info[re.search("x_max: ",info).end(0):re.search("x_max: -*\d+\.*\d*",info).end(0)];
	ymin2 = info[re.search("y_min: ",info).end(0):re.search("y_min: -*\d+\.*\d*",info).end(0)];
	ymax2 = info[re.search("y_max: ",info).end(0):re.search("y_max: -*\d+\.*\d*",info).end(0)];

#	Determine minimum bounds that encompass both grids

	if float(xmin2) < float(min_x):
		min_x = xmin2;

	if float(xmax2) > float(max_x):
		max_x = xmax2;

	if float(ymin2) < float(min_y):
		min_y = ymin2;

	if float(ymax2) > float(max_y):
		max_y = ymax2;

	grd1_resamp_path = input1_grd_path[ : input1_grd_path.rfind(".")] + "_resamp.grd";
	grd2_resamp_path = input2_grd_path[ : input2_grd_path.rfind(".")] + "_resamp.grd";

	R = "-R" + min_x + "/" + min_y + "/" + max_x + "/" + max_y + "r";

#	Run grd2xyz and xyz2grd to resample grids (grdsample will not work)

	cmd  = "\ngrd2xyz " + input1_grd_path + " | xyz2grd " + R + " -I" + resolution + "= -G" + grd1_resamp_path + "\n";
	cmd += "\ngrd2xyz " + input2_grd_path + " | xyz2grd " + R + " -I" + resolution + "= -G" + grd2_resamp_path + "\n";
	subprocess.call(cmd,shell=True);


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 3, "\n***** ERROR: resampGrids.py requires 3 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	resampGrids(sys.argv[1], sys.argv[2], sys.argv[3]);

	exit();


