#!/usr/bin/python


# dem2txt.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def dem2txt(dem_tif_path):

	import datetime;
	import os;
	import re;
	import subprocess;

	assert os.path.exists(dem_tif_path), "\n***** ERROR: " + dem_tif_path + " does not exist\n";

	print(dem_tif_path);

	dem_diff_tif_path = dem_tif_path[ : re.search("\d{14}", dem_tif_path).end(0)] + "_diff_after.tif";

	assert os.path.exists(dem_diff_tif_path), "\n***** ERROR: " + dem_diff_tif_path + " does not exist\n";

	dem_diff_grd_path = dem_tif_path[ : re.search("\d{14}", dem_tif_path).end(0)] + "_diff_after.grd";

	cmd  = "\ngdal_translate -of GMT " + dem_diff_tif_path + " " + dem_diff_grd_path + "\n";
	cmd += "\ngrdclip " + dem_diff_grd_path + " -Sa100/NaN -Sb-100/NaN -Gtemp.grd\n";
	subprocess.call(cmd, shell=True);

	cmd  = "\ngrdinfo -L2 temp.grd\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	mean = info[re.search("mean:\s*", info).end(0) : re.search("mean:\s*\-*\d+\.*\d*", info).end(0)];
	stdev = info[re.search("stdev:\s*", info).end(0) : re.search("stdev:\s*\-*\d+\.*\d*", info).end(0)];

	cmd  = "\ngrdinfo -L1 temp.grd\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	median  = info[re.search("median:\s*", info).end(0) : re.search("median:\s*\-*\d+\.*\d*", info).end(0)];

	upper_bound = str(float(mean) + 2 * float(stdev));
	lower_bound = str(float(mean) - 2 * float(stdev));

	cmd = "\ngrdclip temp.grd -Sb" + lower_bound + "/NaN -Sa" + upper_bound + "/NaN -Gtemp.grd\n";
	subprocess.call(cmd, shell=True);

	cmd  = "\ngrdinfo -L2 temp.grd\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	stdev = info[re.search("stdev:\s*", info).end(0) : re.search("stdev:\s*\-*\d+\.*\d*", info).end(0)];

	os.remove("temp.grd");
	os.remove(dem_diff_grd_path);

	if os.path.exists("temp.grd.aux.xml"):
		os.remove("temp.grd.aux.xml");

	if os.path.exists(dem_diff_grd_path + ".aux.xml"):
		os.remove(dem_diff_grd_path + ".aux.xml");

	dem_datelabel = dem_tif_path[re.search("\d{14}", dem_tif_path).start(0) : re.search("\d{14}", dem_tif_path).end(0)];
	dem_datetime  = datetime.datetime(int(dem_datelabel[0:4]), int(dem_datelabel[4:6]), int(dem_datelabel[6:8]), int(dem_datelabel[8:10]), int(dem_datelabel[10:12]), int(dem_datelabel[12:14]));
	dem_yeartime  = datetime.datetime(int(dem_datelabel[0:4]), 1, 1, 0, 0, 0);
	decimal_years = (dem_datetime - dem_yeartime).total_seconds() / (60. * 60. * 24. * 365.25);
	dem_decyear   = str(float(dem_datelabel[0:4]) + decimal_years);

	dem_txt_path = dem_tif_path[dem_tif_path.rfind("/") + 1 : dem_tif_path.rfind(".")] + ".txt";

	cmd  = "\ngdal_translate -of GMT " + dem_tif_path + " temp.grd\n";
	cmd += "\ngrd2xyz temp.grd | gawk '$0 !~ /a/ {print $0\" " + dem_decyear + " " + stdev + "\"}' > " + dem_txt_path + "\n";
	subprocess.call(cmd, shell=True);

	os.remove("temp.grd");

	if os.path.exists("temp.grd.aux.xml"):
		os.remove("temp.grd.aux.xml");

	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: dem2txt.py requires one argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	dem2txt(sys.argv[1]);

	exit();

