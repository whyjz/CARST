#!/usr/bin/python


# convertMEaSUREsTSX.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

# Converts binary MEaSUREs TSX data to ASCII 4-column, space-separated text files


# Usage
# *****
# python convertMEaSUREsTSX.py /path/containing/TSX/

# Example
# *******
# python convertMEaSUREsTSX.py /home/user/data/TSX_Jan-26-2009_Feb-06-2009_09-23-10

# Input
# *****
# 	/path/containing/TSX - Directory for a SINGLE pair containing *.vx, *.vy and *.geodat files, must follow MEaSUREs naming convention

# Output
# ******
# TSX_Jan-26-2009_Feb-06-2009_09-23-10.dat (in current working directory), 4-column, space-separated ASCII text file, first column longitude, second latitude, third E-W velocity, fourth N-S velocity



def convertMEaSUREsTSX(tsx_pair_path):

	import os;
	import re;
	import struct;

	assert os.path.exists(tsx_pair_path), "\n***** ERROR: " + tsx_pair_path + " does not exist\n";

	contents = os.listdir(tsx_pair_path);

	geo_path = tsx_pair_path;
	vx_path  = tsx_pair_path;
	vy_path  = tsx_pair_path;

	for item in contents:

		if re.search("\.vx$", item):
			vx_path += "/" + item;

		if re.search("\.vy$", item):
			vy_path += "/" + item;

		if re.search("\.vx.geodat$", item):
			geo_path += "/" + item;

	vxs = [];
	vys = [];

	infile = open(vx_path, "rb");

	try:	
		data   = infile.read(4);

		while data:
			(num,) = struct.unpack(">f", data); 
			vxs.append(num);
			data   = infile.read(4);
	finally:
		infile.close();

	infile = open(vy_path, "rb");

	try:	
		data   = infile.read(4);

		while data:
			(num,) = struct.unpack(">f", data); 
			vys.append(num);
			data   = infile.read(4);
	finally:
		infile.close();

	desc = nx = ny = res = ul_lon = ul_lat = "";

	infile = open(geo_path, "r");

	for line in infile:

		if re.search("[A-Za-z]", line):
			desc = line.strip();

		if re.search("^\d+\s+\d+\s*$", line):
			nx, ny = line.split();

		if re.search("^\-*\d+\.*\d*\s+\-*\d+\.*\d*\s*$", line):

			if desc.find("Pixel") > -1:
				res = line.split()[0];

			else:
				ul_lon, ul_lat = line.split();

	infile.close();

	out_name = tsx_pair_path[tsx_pair_path.rfind("/") + 1 : ] + ".dat";

	outfile = open(out_name, "w");

	for i in range(0, int(nx) - 1):
		lon = str(float(ul_lon) * 1000 + i * float(res));

		for j in range(0, int(ny) - 1):
			lat = str(float(ul_lat) * 1000 + j * float(res));
			outfile.write(lon + " " + lat + " " + str(vxs[i * j]) + " " + str(vys[i * j]) + "\n");

	outfile.close();
		

	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: convertMEaSUREsTSX.py requires one argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	convertMEaSUREsTSX(sys.argv[1]);

	exit();

