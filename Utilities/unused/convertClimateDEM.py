#!/usr/bin/python


# convertClimateDEM.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

# Description
# ***********
# Converts ENVI DEM to input DEM for "meltmodel"


def convertClimateDEM(input_path, output_path):

	import os;
	import re;
	import struct;

	assert os.path.exists(input_path), "\n***** ERROR: " + input_path + " does not exist\n";

	infile = open(input_path, "rb");
	infile.read(48);
	contents = infile.read();
	infile.close();

	outfile = open(output_path, "wb");
	outfile.write(contents);
	outfile.close();

	return;	



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: convertClimateDEM.py requires two arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	convertClimateDEM(sys.argv[1], sys.argv[2]);

	exit();

