#!/usr/bin/python


# aggregate_icesat.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def aggregate_icesat(icesat_path, input_dem_xyz_txt_dir, input_dem_xyz_txt_identifier, output_label):

	import os;

	assert os.path.exists(icesat_path), "\n***** ERROR: " + icesat_path + " does not exist, exiting...\n";
	assert os.path.exists(input_dem_xyz_txt_dir), "\n***** ERROR: " + input_dem_xyz_txt_dir + " does not exist, exiting...\n";

	max_elev     = "1520";
	min_elev     = "-100";
	interval     = 120.;
	icesat_unc   = "0.5";

	coords = {};
	xy     = "";

	import re;

	infile = open(icesat_path, "r");

	for line in infile:

		elements = line.split();

		if len(elements) > 2 and elements[2].find("NaN") < 0:

			x = elements[0].strip();
			y = elements[1].strip();
			x = x[ : re.search("0*$",x).start(0)];
			y = y[ : re.search("0*$",y).start(0)];

			if float(elements[5]) > float(max_elev):
				continue;

			elif float(elements[5]) <= float(min_elev):
				continue;

			xy = x + " " + y;

			if xy not in coords:
				coords[xy] = "";

			coords[xy] = coords[xy] + xy + " " + elements[2].strip() + " " + elements[3].strip() + " " + elements[4].strip() + "\n";

	infile.close();

	contents = os.listdir(input_dem_xyz_txt_dir);

	input_dem_xyz_txt_names = [item for item in contents if re.search(".*" + input_dem_xyz_txt_identifier + "\.txt$", item)];

	for item in input_dem_xyz_txt_names:

		if re.search(icesat_path[icesat_path.rfind("/") + 1 : ], input_dem_xyz_txt_dir + "/" + item):
			continue;

		infile = open(input_dem_xyz_txt_dir + "/" + item, "r");

		for line in infile:

			elements = line.split();

			if len(elements) > 2 and elements[2].find("NaN") < 0:

				x = elements[0].strip();
				y = elements[1].strip();
				x = x[ : re.search("0*$",x).start(0)];
				y = y[ : re.search("0*$",y).start(0)];

				if float(elements[2]) > float(max_elev):
					continue;

				elif float(elements[2]) <= float(min_elev):
					continue;

				xy = x + " " + y;

				if xy not in coords:
					continue;
#					coords[xy] = "";

				coords[xy] = coords[xy] + xy + " " + elements[2].strip() + " " + elements[3].strip() + " " + elements[4].strip() + "\n";

		infile.close();

#	import math;
#	import subprocess;

#	x_ref, y_ref = xy.split();

#	infile = open(icesat_path, "r");

#	for line in infile:
	
#		if line.find("# @D") > -1:

#			elements = line.split("|");
#			date     = elements[0];
#			x        = elements[3];
#			y        = elements[4];
#			h_ell    = elements[5];

#			new_x = str(float(math.ceil((float(x) - float(x_ref)) / interval)) * interval + float(x_ref));
#			new_y = str(float(math.ceil((float(y) - float(y_ref)) / interval)) * interval + float(y_ref));
#			xy    = new_x + " " + new_y;

#			year   = date[4:8];
#			month  = date[8:10];
#			day    = date[10:12];
#			hour   = "12";
#			minute = "00";
#			second = "00";

#			cmd  = "\ndate +\"%s\" -d \"" + year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second + "\"\n";
#			pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
#			secs = pipe.read().strip();
#			pipe.close();

#			cmd  = "\ndate +\"%s\" -d \"" + year + "-01-01 00:00:00\"\n";
#			pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
#			year_secs = pipe.read().strip();
#			pipe.close();

#			date = str(float(year) + (float(secs) - float(year_secs)) / (24.0 * 60.0 * 60.0 * 365.25));


#			if xy not in coords:
#				coords[xy] = "";

#			coords[xy] = coords[xy] + xy + " " + h_ell + " " + date + " " + icesat_unc + "\n";

#	infile.close();

	outfile = open(output_label + ".txt", "w");

	for xy in coords:
		outfile.write(coords[xy]);
		outfile.write(">\n");

	outfile.close();

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 4, "\n***** ERROR: aggregate_icesat.py requires 4 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	aggregate_icesat(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]);

	exit();

