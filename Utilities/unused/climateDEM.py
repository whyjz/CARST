#!/usr/bin/python


# climateDEM.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

# Description
# ***********
# Converts ENVI DEM to input DEM for "meltmodel"


def climateDEM(input_path, output_path):

	import os;
	import re;
	import struct;

	assert os.path.exists(input_path), "\n***** ERROR: " + input_path + " does not exist\n";

	hdr_path = input_path[ : input_path.rfind(".")] + ".hdr";
	
	assert os.path.exists(hdr_path), "\n***** ERROR: " + hdr_path + " does not exist\n";

	infile = open(hdr_path, "r");
	contents = infile.read().strip();
	infile.close();

	ncols    = contents[re.search("samples\s*=\s*", contents).end(0) : re.search("samples\s*=\s*\d+", contents).end(0)];
	nrows    = contents[re.search("lines\s*=\s*", contents).end(0) : re.search("lines\s*=\s*\d+", contents).end(0)];
	map_info = contents[re.search("map\s*info\s*=\s*\{", contents).end(0) : re.search("map\s*info\s*=\s*\{.*\}", contents).end(0) - 1].replace(",", " ").split();

	ul_x = map_info[3];
	ul_y = map_info[4];
	gs   = map_info[5];

	if gs.find(".") > -1:
		gs   = gs[ : gs.find(".")];

	ll_y = str(float(ul_y) - float(nrows) * float(gs));

	print(ncols, nrows, ul_x, ul_y, ll_y, gs);
	
	infile  = open(input_path, "rb");
	contents = infile.read();
	infile.close();

	outfile = open(output_path, "wb");
	outfile.write(struct.pack('f'*12, int(ncols), int(nrows), float(ul_x), float(ll_y), int(gs), -9999, 0, 0, 0, 0, 0, 0));
	outfile.write(contents);
	outfile.close();

	return;	



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: climateDEM.py requires two arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	climateDEM(sys.argv[1], sys.argv[2]);

	exit();

