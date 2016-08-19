#!/usr/bin/python

# kml2txt.py
# Author: Andrew Kenneth Melkonian (akm26@cornell.edu)
# All rights reserved


def kml2txt(kml_path, out_path):

	import os;

	assert os.path.exists(kml_path), "\n***** ERROR: " + kml_path + " does not exist\n";

	coords_str = "";

	import re;

	kml_file = open(kml_path,"r");

	while 1:

		line = kml_file.readline().strip();

		if not line:
			break;

		if re.search("\d+\.*\d*\s*,\s*\d+\.*\d*",line):
			coords_str = line+"\n";

	kml_file.close();

	coords = coords_str.split();

	outfile = open(out_path, "w");

	for coord in coords:
		coord = coord.replace(",", " ");

		if re.search("<coordinates>", coord):
			coord = coord[re.search("<coordinates>", coord).end(0) : ];

		if re.search("</coordinates>", coord):
			coord = coord[ : re.search("</coordinates>", coord).start(0)];
			if not coord:
				continue;

		if re.search(" 0$", coord):
			coord = coord[ : re.search(" 0$", coord).start(0)];

		outfile.write(coord.replace(","," ") + "\n");

	outfile.close();

	return;


if __name__ == "__main__":

	import os;
        import sys;

	assert len(sys.argv) > 2, "\n***** ERROR: flux.py requires 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";

        kml2txt(sys.argv[1], sys.argv[2]);

	exit();
	


