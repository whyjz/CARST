#!/usr/bin/python


def gmt2grd(gmt_path, output_path):

	assert os.path.exists(gmt_path), "\n***** ERROR: " + gmt_path + " does not exist\n";

	val = "";

	infile  = open(gmt_path, "r");
	outfile = open("temp", "w");

	for line in infile:
		if line.find("# @D") > -1:
			val = line[line.find("# @D") + 4 : line.find("|")];

		if line.find(">") < 0 and line.find("#") < 0:
			outfile.write(line.strip() + " " + val + "\n");

	infile.close();
	outfile.close();

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: gmt2grd.py requires 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	gmt2grd(sys.argv[1], sys.argv[2]);

	exit();

