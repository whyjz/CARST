#!/usr/bin/python

# densifyUTM.py
# Author: Andrew Kenneth Melkonian (akm26@cornell.edu)
# All rights reserved


import subprocess;
import sys;


def densifyUTM(track_path, densify_factor, out_path):

	prev_x = "";
	prev_y = "";

	distance = 0.0;

	track_file = open(track_path, "r");
	outfile    = open(out_path, "w");

	while 1:

		line = track_file.readline().strip();

		if not line:
			break;

		elements = line.split();
		x = elements[0].strip();
		y = elements[1].strip();

		if prev_x:
			outfile.write(prev_x + " " + prev_y + " " + str(distance) + "\n");
			
			diff_x = float(x)-float(prev_x);
			diff_y = float(y)-float(prev_y);
			last_x = prev_x;
			last_y = prev_y;

			for i in range(1, int(densify_factor)):

				cur_x = str(float(prev_x)+float(i)*diff_x/float(densify_factor));
				cur_y = str(float(prev_y)+float(i)*diff_y/float(densify_factor));
				distance = distance+((float(cur_x)-float(last_x))**2+(float(cur_y)-float(last_y))**2)**0.5;
				last_x = cur_x;
				last_y = cur_y

				outfile.write(cur_x + " " + cur_y + " " + str(distance) + "\n");

			distance = distance+((float(x)-float(last_x))**2+(float(y)-float(last_y))**2)**0.5;

		prev_x = x;
		prev_y = y;

	outfile.write(prev_x + " " + prev_y + " " + str(distance) + "\n");

	track_file.close();
	outfile.close();


	return;

