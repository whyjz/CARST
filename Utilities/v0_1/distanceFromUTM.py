#!/usr/bin/python

# distanceFromUTM.py
# Author: Andrew Kenneth Melkonian (akm26@cornell.edu)
# All rights reserved


import subprocess;
import sys;


def distanceFromUTM(track_path, out_path):

	prev_x   = "";
	prev_y   = "";
	distance = 0.0;
	diff_x   = 0.0;
	diff_y   = 0.0;

	track_file = open(track_path, "r");
	outfile    = open(out_path, "w");

	while 1:

		line = track_file.readline().strip();

		if not line:
			break;

		elements = line.split();
		x = elements[0].strip();
		y = elements[1].strip();

		rest_of_line = line[line.find(y) + len(y) : ];

		if prev_x:
			
			diff_x = float(x) - float(prev_x);
			diff_y = float(y) - float(prev_y);

			distance = distance + (diff_x**2 + diff_y**2)**0.5;

		outfile.write(x + " " + y + " " + str(distance) + " " + rest_of_line + "\n");

		prev_x = x;
		prev_y = y;

#	outfile.write(prev_x + " " + prev_y + " " + str(distance) + " " + rest_of_line + "\n");

	track_file.close();
	outfile.close();

	return;


