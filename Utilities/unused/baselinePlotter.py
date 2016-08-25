#!/usr/bin/python


# baselinePlotter.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# Plots perpendicular baselines for all *baseline.rsc files in the input directory that contain a valid number identified as "P_BASELINE*"


# USAGE
# *****
# python /path/containing/ints /path/to/put/output.ps
#		/path/containing/ints:  Path to directory that contains all of the *baseline.rsc files to search and plot from
#		/path/to/put/output.ps: Path to output image (baselines plot)


def baselinePlotter(input_dir, output_path):

	import fnmatch;
	import os;
	import subprocess;
	import sys;
	import re;

	assert os.path.exists(input_dir), "\n***** ERROR: " + input_dir + " does not exist\n";

	output_dir = ".";

	index = output_path.rfind("/");

	if index > -1:
		output_dir = output_path[ : index];

	assert os.path.exists(output_dir), "\n***** ERROR: " + output_dir + " does not exist\n";

#	contents = os.listdir(input_dir);

#	date_dirs =  [item for item in contents if os.path.isdir(item) and re.search("^\d{6}$", item)];

#	outfile = open("temp_params.txt", "w");

#	outfile.write("WorkPath = " + input_dir + "\n");
#	outfile.write("DEM = " + input_dir + "\n");
#	outfile.write("MaxBaseline = 10000\n");
#	outfile.write("MinDateInterval = 1\n");
#	outfile.write("MaxDateInterval = 100000\n");
#	outfile.write("DataType = ERS\n");
#	outfile.write("Angle = 23\n");
#	outfile.write("rwin = 40\n");
#	outfile.write("awin = 80\n");
#	outfile.write("search_x = 8\n");
#	outfile.write("search_y = 8\n");
#	outfile.write("wsamp = 1\n");
#	outfile.write("numproc = 1\n");

#	outfile.close();

#	print("\npython /data/akm/Python/pixelTack_new.py params.txt setup offsets\n");

	baseline_dates  = {};
	baseline_values = {};

	for root, dirnames, filenames in os.walk(input_dir):

		for filename in fnmatch.filter(filenames, "*baseline.rsc"):

			baseline_dates[root + "/" + filename] = filename[re.search("\d{6}_\d{6}", filename).start(0) : re.search("\d{6}_\d{6}", filename).end(0)];

	p_b_t   = "";
	p_b_b   = "";

	for baseline_path in baseline_dates:

		infile = open(baseline_path, "r");

		for line in infile:

			if line.find("P_BASELINE_TOP") > -1:
				p_b_t = line.split()[1];

			if line.find("P_BASELINE_BOTTOM") > -1:
				p_b_b = line.split()[1];

		infile.close();

		p_b = abs(float(p_b_t) + float(p_b_b)) / 2;

		baseline_values[p_b] = baseline_path;

	sorted_p_b = sorted(baseline_values);

	min_p_b = sorted_p_b[0];
	max_p_b = sorted_p_b[len(sorted_p_b) - 1];

	min_p_b = round(min_p_b, -2) - 50;
	max_p_b = round(max_p_b, -2) + 50;

	R = "-R0/" + str(len(baseline_values.values()) + 2) + "/" + str(min_p_b) + "/" + str(max_p_b);

	ps_path = output_path;

	cmd  = "";	
	cmd +="\npsbasemap -Ba1f1:\"SAR Pair\":/a100f100:\"Average Baseline (m)\":WeSn -JX10c " + R + " -P -K > " + ps_path + "\n";

	i = 1;

	for p_b in sorted_p_b:
		cmd += "\necho \"" + str(i) + " " + str(p_b) + "\" | psxy -JX10c " + R + " -Ss0.2c -Gred -W0.5p,darkgray -O -K >> " + ps_path + "\n";
		cmd += "\necho \"" + str(float(i) + 0.1) + " " + str(p_b) + " 8p,1,black 0 LM " + baseline_dates[baseline_values[p_b]] + "\" | pstext -JX10c " + R + " -F+f+a+j -Gwhite -W1p,darkgray -O -K >> " + ps_path + "\n";
		i += 1;

	cmd  = cmd[ : cmd.rfind("-K") - 1] + cmd[cmd.rfind("-K") + 2 : ];

	cmd += "\nps2raster -A -Tf -D" + output_dir + " " + ps_path + "\n";

	subprocess.call(cmd,shell=True);
	
	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: baselinePlotter.py requires at least 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";

	baselinePlotter(sys.argv[1], sys.argv[2]);

	exit();

