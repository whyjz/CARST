#!/usr/bin/python


# hypsometry.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def hypsometry(dem_grd_path, increment):

	import math;
	import os;
	import re;
	import subprocess;
	import sys;

	assert os.path.exists(dem_grd_path), "\n***** ERROR: " + dem_grd_path + " does not exist, exiting...\n";
	
	cmd  = "\ngrdinfo " + dem_grd_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	zmin = info[re.search("z_min: ",info).end(0):re.search("z_min: \-*\d+\.*\d*",info).end(0)];
	zmax = info[re.search("z_max: ",info).end(0):re.search("z_max: \d+\.*\d*",info).end(0)];

	hyp_txt_path = dem_grd_path[dem_grd_path.rfind("/") + 1 : dem_grd_path.rfind(".")] + "_hyp.txt";

	low_bin  = int(float(zmin)) - int(float(zmin)) % 10;
	high_bin = int(float(zmax)) + (10 - int(float(zmax)) % 10);

	print("\nCreating and populating \"" + hyp_txt_path + "\" from \"" + dem_grd_path + "\"...\n")

	outfile = open(hyp_txt_path, "w");

	outfile.write("Elevation_Bin SRTM_Area\n");

	for i in range(low_bin, high_bin, int(increment)):

		cmd ="\ngrdclip " + dem_grd_path + " -Sb" + str(i) + "/NaN -Sa" + str(i + 9) + "/NaN -Gtemp.grd\n";
		subprocess.call(cmd,shell=True);

		cmd      = "\ngrdvolume temp.grd\n";
		pipe     = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		elements = pipe.read().strip().split();
		pipe.close();

		area = elements[1];

		outfile.write(str(i) + " " + area + "\n");

	outfile.close();

	os.remove("temp.grd");

	return;


if __name__ == "__main__":

        import os;
        import sys;

        assert len(sys.argv) > 1, "\n***** ERROR: hypsometry.py requires at least one argument, " + str(len(sys.argv)) + " given, exiting...\n";
        assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist, exiting...\n";

	increment = "10";

	if len(sys.argv) > 2:
		increment = sys.argv[2];

        hypsometry(sys.argv[1], increment);

        exit();

