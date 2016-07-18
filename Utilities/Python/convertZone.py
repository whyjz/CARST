#!/usr/bin/python


# convertZone.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def convertZone(input_grd_path, input_zone, output_zone):

	import os;

	assert os.path.exists(input_grd_path), "\n***** ERROR: " + input_grd_path + " does not exist\n";

	output_grd_path = input_grd_path[ : input_grd_path.rfind(".")] + "_zone" + output_zone + ".grd";

	import subprocess;

	cmd  = "\ngdalwarp -of GTiff -srcnodata \"nan\" -dstnodata \"nan\" -t_srs '+proj=utm +zone=" + input_zone + " +datum=WGS84 +north' " + input_grd_path + " temp.tif\n";
	cmd += "\ngdalwarp -of GTiff -srcnodata \"nan\" -dstnodata \"nan\" -t_srs '+proj=utm +zone=" + output_zone + " +datum=WGS84 +north' temp.tif temp2.tif\n";
	cmd += "\ngdal_translate -of GMT temp2.tif " + output_grd_path + "\n";
	subprocess.call(cmd, shell=True);

	os.remove("temp.tif");
	os.remove("temp2.tif");

	if os.path.exists(output_grd_path + ".aux.xml"):
		os.remove(output_grd_path + ".aux.xml");


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 3, "\n***** ERROR: convertZone.py requires 3 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	convertZone(sys.argv[1], sys.argv[2], sys.argv[3]);

	exit();

