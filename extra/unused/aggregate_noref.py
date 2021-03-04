#!/usr/bin/python


# aggregate.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def aggregate(input_dem_xyz_txt_dir, input_dem_xyz_txt_identifier, output_label):

	import os;

	assert os.path.exists(input_dem_xyz_txt_dir), "\n***** ERROR: " + input_dem_xyz_txt_dir + " does not exist, exiting...\n";

	max_elev     = "1520";
	min_elev     = "-100";
#	output_label = "novz_ice_values_all_2015_02_26";
#	output_label = "novz_ice_values_hires_icesat";

	coords = {};

	contents = os.listdir(input_dem_xyz_txt_dir);

	import re;

	input_dem_xyz_txt_names = [item for item in contents if re.search(".*" + input_dem_xyz_txt_identifier + ".*\.txt$", item)];

	for item in input_dem_xyz_txt_names:

		print(item);

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
					coords[xy] = "";

				coords[xy] = coords[xy] + xy + " " + elements[2].strip() + " " + elements[3].strip() + " " + elements[4].strip() + "\n";

		infile.close();

	outfile = open(output_label + ".txt", "w");

	for xy in coords:
		outfile.write(coords[xy]);
		outfile.write(">\n");

	outfile.close();

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 3, "\n***** ERROR: aggregate_noref.py requires 3 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	aggregate(sys.argv[1], sys.argv[2], sys.argv[3]);

	exit();

