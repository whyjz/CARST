#!/usr/bin/python


# combineColumns.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def combineColumns(xyz1_path, xyz2_path, id_col_num_1, id_col_num_2):

	assert os.path.exists(xyz1_path), "\n***** ERROR: " + xyz1_path + " does not exist\n";
	assert os.path.exists(xyz2_path), "\n***** ERROR: " + xyz2_path + " does not exist\n";

	combined = {};

	infile = open(xyz1_path, "r");

	for line in infile:
		elements = line.strip().split();
		combined[elements[id_col_num_1]] = line.strip();

	infile.close();
	
	infile = open(xyz2_path, "r");

	for line in infile:

		elements = line.strip().split();

		if elements[id_col_num_2] in combined:
			combined[elements[id_col_num_2]] += " " + line.strip();

	infile.close();

	outfile = open("temp_combined.txt", "w");

	for key in combined:
		outfile.write(combined[key] + "\n");

	outfile.close();

	return;



if __name__ == "__main__":

	import os;
	import sys;

	assert len(sys.argv) > 2, "\n***** ERROR: combineColumns.py requires at least 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";

	input_id_col_num_1 = 0;
	input_id_col_num_2 = 0;

	if len(sys.argv) > 3:
		input_id_col_num_1 = int(sys.argv[3]);

	if len(sys.argv) > 4:
		input_id_col_num_2 = int(sys.argv[4]);

	combineColumns(sys.argv[1], sys.argv[2], input_id_col_num_1, input_id_col_num_2);

	sys.exit();
