#!/usr/bin/python


# sstPlot.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# USAGE
# *****
# python sstPlot.py /path/to/grid_list.txt /another/path/to/kml_bounds.kml
#		grid_list.txt:  one-column ASCII text file with paths to grids that will be sampled
#		kml_bounds.kml: kml file defining bounds over which the grids in grid_list will be sampled


def sstPlot(grid_list_path, kml_bounds_path):

	import datetime;
	from kml2txt import *;
	import os;
	import re;
	import subprocess;

	assert os.path.exists(grid_list_path), "\n***** ERROR: " + grid_list_path + " does not exist\n";
	assert os.path.exists(kml_bounds_path), "\n***** ERROR: " + kml_bounds_path + " does not exist\n";

	bounds_name = kml_bounds_path[kml_bounds_path.rfind("/") + 1 : kml_bounds_path.rfind(".")];
	bounds_txt  = bounds_name + ".txt";
	ssts_txt    = bounds_name + "_ssts.txt";

	kml2txt(kml_bounds_path, bounds_txt);

	dates   = {};
	medians = {};
	means   = {};
	stdevs  = {};

	min_date = "";
	max_date = "";
	min_med  = "";
	max_med  = "";
	min_mean = "";
	max_mean = "";

	outfile = open(ssts_txt, "w");
	infile  = open(grid_list_path, "r");

	for grid_path in infile:

		grid_path = grid_path.strip();

		cmd  = "\ngrdmask " + bounds_txt + " -NNaN/NaN/1 -R" + grid_path + " -Gtemp.grd\n";
		cmd += "\ngrdmath " + grid_path + " temp.grd OR = temp2.grd\n";
		cmd += "\ngrdclip temp2.grd -Sb-50/NaN -Gtemp2.grd\n";
		subprocess.call(cmd, shell=True);

		cmd  = "\ngrdinfo -L1 temp2.grd\n";
		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		info = pipe.read().strip();
		pipe.close();

		median = info[re.search("median:\s*", info).end(0) : re.search("median:\s*\d+\.*\d*", info).end(0)];

		cmd  = "\ngrdinfo -L2 temp2.grd\n";
		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		info = pipe.read().strip();
		pipe.close();

		mean = info[re.search("mean:\s*", info).end(0) : re.search("mean:\s*\d+\.*\d*", info).end(0)];
		stdev = info[re.search("stdev:\s*", info).end(0) : re.search("stdev:\s*\d+\.*\d*", info).end(0)];	

		os.remove("temp.grd");
		os.remove("temp2.grd");

		grid_year  = int(grid_path[0:4]);
		grid_month = int(grid_path[4:6]);
		grid_day   = int(grid_path[6:8]);

		grid_date_year = datetime.datetime(grid_year, 1, 1, 0, 0, 0);
		grid_date      = datetime.datetime(grid_year, grid_month, grid_day, 0, 0, 0);
		year_frac = float((grid_date - grid_date_year).total_seconds()) / (365.25 * 24. * 60. * 60.);

		date = str(float(grid_year) + year_frac);

		dates[date]   = date;
		medians[date] = median;
		means[date]   =  mean;
		stdevs[date]  = stdev;

		outfile.write(date + " " + median + " " + mean + " " + stdev + "\n");

		if not min_date or float(date) < float(min_date):
			min_date = date;

		if not max_date or float(date) > float(max_date):
			max_date = date;

		if not min_med or float(median) < float(min_med):
			min_med = median;

		if not max_med or float(median) > float(max_med):
			max_med = median;

		if not min_mean or float(mean) < float(min_mean):
			min_mean = mean;

		if not max_mean or float(mean) > float(max_mean):
			max_mean = mean;

	infile.close();
	outfile.close();

	ps_path = bounds_name + "_ssts.ps";
	J       = "-JX10c";
	R       = "-R" + min_date[0:4] + "/" + str(int(max_date[0:4]) + 1) + "/" + min_med + "/" + max_med;

	cmd  = "\ngawk '{print $1\" \"$3}' " + ssts_txt + " | psxy " + J + " " + R + " -Ss0.1c -W0.5p,darkgray -Gred -P -K > " + ps_path + "\n";
	cmd += "\npsbasemap " + J + " " + R + " -B1:\"Date (Year)\":/1:\"Mean SST (C)\":WeSn --FONT_LABEL=12p,1,black --FONT_ANNOT_PRIMARY=12p,1,black --FONT_ANNOT_SECONDARY=12p,1,black -O >> " + ps_path + "\n";
	cmd += "\nps2raster -A -Tf " + ps_path + "\n";
	subprocess.call(cmd, shell=True);

	os.remove(ps_path);

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: sstPlot.py requires 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	sstPlot(sys.argv[1], sys.argv[2]);

	exit();


