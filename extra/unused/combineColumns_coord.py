#!/usr/bin/python


# combineColumnsCoord.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def combineColumnsCoord(xyz1_path, xyz2_path):

	assert os.path.exists(xyz1_path), "\n***** ERROR: " + xyz1_path + " does not exist\n";
	assert os.path.exists(xyz2_path), "\n***** ERROR: " + xyz2_path + " does not exist\n";

	combined = {};

	infile = open(xyz1_path, "r");

	for line in infile:
		elements = line.strip().split();
		coord = elements[0].strip() + " " + elements[1].strip();
		combined[coord] = line.strip();

	infile.close();
	
	infile = open(xyz2_path, "r");

	for line in infile:
		elements = line.strip().split();
		coord = elements[0].strip() + " " + elements[1].strip();

		if coord in combined:
			combined[coord] += " " + elements[2];

	infile.close();

	outfile = open("temp_combined.txt", "w");

	for key in combined:
		outfile.write(combined[key] + "\n");

	outfile.close();

	return;



if __name__ == "__main__":

	import os;
	import sys;

	assert len(sys.argv) > 2, "\n***** ERROR: combineColumnsCoord.py requires at least 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";

	combineColumnsCoord(sys.argv[1], sys.argv[2]);

	sys.exit();
