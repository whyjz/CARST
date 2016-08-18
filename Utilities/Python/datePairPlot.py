#!/usr/bin/python


# datePairPlot.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def datePairPlot(pair_dir_list):

	import datetime;
	import os;
	import re;
	import subprocess;

	pairs = {};

	for pair_dir in pair_dir_list:

		assert os.path.exists(pair_dir), "\n***** ERROR: " + pair_dir + " does not exist\n";

		for root, dirnames, filenames in os.walk(pair_dir):

			for filename in filenames:

				if not re.search("\d{14}.*\d{14}", filename):
					continue;

				start_index = re.search("\d{14}.*\d{14}", filename).start(0); 
				end_index   = re.search("\d{14}.*\d{14}", filename).end(0); 
				early_date  = filename[end_index - 14 : end_index];
				later_date  = filename[start_index : start_index + 14];

				if early_date[0:2] != "20" and early_date[0:2] != "19":
					early_date = early_date[4:8] + early_date[0:2] + early_date[2:4] + early_date[8:14];

				if later_date[0:2] != "20" and later_date[0:2] != "19":
					later_date = later_date[4:8] + later_date[0:2] + later_date[2:4] + later_date[8:14];

				if early_date > later_date:
					temp       = later_date;
					later_date = early_date;
					early_date = temp;

				early_datetime      = datetime.datetime(int(early_date[0:4]), int(early_date[4:6]), int(early_date[6:8]), int(early_date[8:10]), int(early_date[10:12]), int(early_date[12:14]));
				early_year_datetime = datetime.datetime(int(early_date[0:4]), 01, 01, 0, 0, 0);

				later_datetime     = datetime.datetime(int(later_date[0:4]), int(later_date[4:6]), int(later_date[6:8]), int(later_date[8:10]), int(later_date[10:12]), int(later_date[12:14]));
				later_year_datetime = datetime.datetime(int(later_date[0:4]), 01, 01, 0, 0, 0);

				early_decimal_year = float(early_date[0:4]) + (early_datetime - early_year_datetime).total_seconds() / (365.25 * 24. * 60. * 60.);
				later_decimal_year = float(later_date[0:4]) + (later_datetime - later_year_datetime).total_seconds() / (365.25 * 24. * 60. * 60.);

				pairs[later_date + " " + early_date] = [early_decimal_year, later_decimal_year];

	sorted_pairs = sorted(pairs.values());
	min_year     = int(round(sorted_pairs[0][0]) - 1);
	max_year     = int(round(sorted_pairs[len(sorted_pairs) - 1][1] + 1));
	
	J       = "-JX10c";
	R       = "-R" + str(min_year) + "/" + str(max_year) + "/0/" + str(len(sorted_pairs) + 1);
	ps_path = "novz_vel_pairs.ps";

	cmd = "\npsbasemap " + J + " " + R + " -Ba5g1/a5g5::WeSn --MAP_GRID_PEN_PRIMARY=0.5p,gray,- -P -K > " + ps_path + "\n"; 

	for i in range(1, len(sorted_pairs) + 1):
		pair = sorted_pairs[i - 1];
		cmd += "\necho \"" + str(pair[0]) + " " + str(i) + "\\n" + str(pair[1]) + " " + str(i) + "\" | psxy " + J + " " + R + " -W2p,red -O -K >> " + ps_path + "\n";
		
	cmd  = cmd[ : cmd.rfind("-K") - 1] + cmd[cmd.rfind("-K") + 2 : ];
	cmd += "\nps2raster -A -Tf " + ps_path + "\n";

	subprocess.call(cmd, shell=True);

	os.remove(ps_path);

	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: datePairPlot.py requires at least one argument, " + str(len(sys.argv) - 1) + " given\n";

	pair_dir_list = [];

	for i in range(1, len(sys.argv)):
		assert os.path.exists(sys.argv[i]), "\n***** ERROR: " + sys.argv[i] + " does not exist\n";
		pair_dir_list.append(sys.argv[i]);

	datePairPlot(pair_dir_list);

	exit();

