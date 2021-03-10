#!/usr/bin/python


# grds2txts.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

# ***** Description *****
# grds2txts.py reads a 3-column ASCII text file where the first column is the path to the netcdf grid file, the second column is the decimal year of the grid file, 
#            and the third column is the uncertainty associated with the values in the grid file.
#	     It outputs a 5-column ASCII text file for each grid file in the input list with the same label as the corresponding grid file where the first column 
#	     is the longitude, the second is the latitude, the third is the value at that point from the grid file, the fourth is the decimal year, and the fifth 
#	     is the uncertainty.


def grds2txts(list_txt_path):

	import os;
	import subprocess;

	assert os.path.exists(list_txt_path), "\n***** ERROR: \"" + list_txt_path + "\" does not exist\n";

	infile = open(list_txt_path, "r");

	for line in infile:

		grd_path, dec_year, unc = line.strip().split();

		if not os.path.exists(grd_path):
			print("\n***** WARNING: \"" + grd_path + "\" not found, skipping...\n");

		txt_path = grd_path[grd_path.rfind("/") + 1 : grd_path.rfind(".")] + ".txt";

		print("\n***** Writing to \"" + txt_path + "\"...\n");

		cmd = "\ngrd2xyz " + grd_path + " | gawk '$0 !~ /a/ {print $1\" \"$2\" \"$3\" " + dec_year + " " + unc + "\"}' > " + txt_path + "\n";
		subprocess.call(cmd, shell=True);

	infile.close();



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: grds2txts.py requires one argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	grds2txts(sys.argv[1]);

	exit();


