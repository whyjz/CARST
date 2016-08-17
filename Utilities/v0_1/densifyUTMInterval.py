#!/usr/bin/python

# densifyUTMInterval.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def densifyUTMInterval(track_path, out_path, interval):

	import os;

	assert os.path.exists(track_path), "\n***** ERROR: " + track_path + " does not exist\n";

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

			densify_factor = (diff_x**2 + diff_y**2)**0.5 / float(interval);	

			for i in range(1, int(round(densify_factor))):

				cur_x = str(float(prev_x) + float(i) * diff_x / float(densify_factor));
				cur_y = str(float(prev_y) + float(i) * diff_y / float(densify_factor));
				distance = distance + ((float(cur_x) - float(last_x))**2 + (float(cur_y) - float(last_y))**2)**0.5;
				last_x = cur_x;
				last_y = cur_y

				outfile.write(cur_x + " " + cur_y + " " + str(distance) + "\n");

			distance = distance + ((float(x) - float(last_x))**2 + (float(y) - float(last_y))**2)**0.5;

		prev_x = x;
		prev_y = y;

	outfile.write(prev_x + " " + prev_y + " " + str(distance) + "\n");

	track_file.close();
	outfile.close();

	return;


if __name__ == "__main__":

	import os;
	import sys;

	assert len(sys.argv) > 3, "\n***** ERROR: denseUTMInterval.py requires 3 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";

	denseUTMInterval(sys.argv[1], sys.argv[2], sys.argv[3]);

	exit();

