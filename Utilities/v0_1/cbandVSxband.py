#!/usr/bin/python


# cbandVSxband.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def cbandVSxband(cband_dem_grd_path, xband_minus_cband_grd_path):

	import re;
	import subprocess;

	assert os.path.exists(cband_dem_grd_path), "\n***** ERROR: " + cband_dem_grd_path + " does not exist\n";
	assert os.path.exists(xband_minus_cband_grd_path), "\n***** ERROR: " + xband_minus_cband_grd_path + " does not exist\n";

	name = xband_minus_cband_grd_path[ : xband_minus_cband_grd_path.rfind(".")] + "_by_elev.txt";

	cmd  = "\ngrdinfo " + cband_dem_grd_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	zmax = info[re.search("z_max: ",info).end(0) : re.search("z_max: \d+\.*\d*",info).end(0)];

	outfile = open(name, "w");

	outfile.write("Elevation_Bin CBand_Area(km2) Diff_Area(km2) Avg_Diff(m) Median_Diff(m)\n");

	for i in range(0, int(zmax), 10):

		cmd  = "\ngrdclip " + cband_dem_grd_path + " -Sb" + str(i) + "/NaN -Sa" + str(i + 9) + "/NaN -Gtemp.grd\n";
		cmd += "\ngrdmath " + xband_minus_cband_grd_path + " temp.grd OR = temp2.grd\n";
		cmd += "\ngrdclip -Sb-10/NaN -Sa10/NaN temp2.grd -Gtemp2.grd\n";
		subprocess.call(cmd,shell=True);

		cmd  = "\ngrdinfo -L1 temp2.grd\n";	
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		info = pipe.read().strip();
		pipe.close();

		median = info[re.search("median:\s*", info).end(0) : re.search("median:\s*\-*\d+\.*\d*", info).end(0)];

		cmd  = "\ngrdvolume temp.grd\n";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		srtm_volume = pipe.read().strip();
		pipe.close();

		elements  = srtm_volume.split();
		srtm_area = elements[1];

		cmd  = "\ngrdvolume temp2.grd\n";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		diff_volume = pipe.read().strip();
		pipe.close();

		elements = diff_volume.split();
		diff     = elements[3];

		outfile.write(str(i) + " " + srtm_area + " " + elements[1] + " " + diff + " " + median + "\n");
		print(str(i) + " " + srtm_area + " " + elements[1] + " " + diff + " " + median);

	outfile.close();

	os.remove("temp.grd");
	os.remove("temp2.grd");

	return;

if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: cbandVSxband.py requires 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	cbandVSxband(sys.argv[1], sys.argv[2]);

	exit();

