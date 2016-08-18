#!/usr/bin/python

# displacement_from_vel.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

# Usage
# *****
# python displacement_from_vel.py ew_vel.txt ns_vel.txt disp.txt [id] [snr_thresh]
#	ew_vel.txt: space-separated, column-data ASCII file, with columns x-position, y-position, and E-W velocity/displacement
#	ns_vel.txt: space-separated, column-data ASCII file, with columns x-position, y-position, and N-S velocity/displacement
#	disp.txt:   space-separated, column-data ASCII file, with columns x-position, y-position, new x-position, and new y-position
#	id:	    OPTIONAL, "Y", "y", "yes", "Yes" or "YES" to indicate id should be added for each row, "N", "n", "No", "NO" or "no" to indicate no id should be added
#	snr_thresh: OPTIONAL, minimum snr_threshold, must have valid floating point format
#
# NOTE: "ew_vel.txt" and "ns_vel.txt" MUST have the same number of rows


import sys;


ew_path  = sys.argv[1];
ns_path  = sys.argv[2];
out_path = sys.argv[3];

row_id = "n";

if len(sys.argv) > 4:
	if sys.argv[4].lower().find("y") > -1:
		row_id = "y";

snr_thresh = "0";

if len(sys.argv) > 5:
	snr_thresh = sys.argv[5];


i = 0;

ew_infile  = open(ew_path, "r");
ns_infile  = open(ns_path, "r");
outfile    = open(out_path, "w");

while 1:

# Read and parse line from E-W velocity/displacement file, calculate new x-position
	line = ew_infile.readline();

	if not line:
		break;

	elements = line.split();

	x      = elements[0];
	y      = elements[1];
	ew_vel = elements[2];

	snr = "";

	if len(elements) > 3:
		snr = elements[3];

	new_x = str(float(x) + float(ew_vel));

# Read and parse line from N-S velocity/displacement file, calculate new y-position
	line = ns_infile.readline();

	if not line:
		break;

	if snr and float(snr) < float(snr_thresh):
		continue;

	elements = line.split();

	ns_vel = elements[2];

	if ns_vel.lower().find("a") > -1 or float(ns_vel) == 0.0 or float(ew_vel) == 0.0:
		continue;

	new_y = str(float(y) + float(ns_vel));

	prepend = "";

	if row_id.find("y") > -1:
		prepend = str(i) + " ";
		i += 1;

	outfile.write(prepend + x + " " + y + " " + new_x + " " + new_y + "\n");

ew_infile.close();
ns_infile.close();
outfile.close();


exit();

