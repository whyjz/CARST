#!/usr/bin/python


# polygonsContainingPoints.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def polygonsContainingPoints(polygon_dir, points_path, label1, label2):

	import os;

	assert os.path.exists(polygon_dir), "\n***** ERROR: " + polygon_dir + " does not exist\n";
	assert os.path.exists(points_path), "\n***** ERROR: " + points_path + " does not exist\n";

	import re;

	contents = os.listdir(polygon_dir);
	polygons = [item for item in contents if re.search("_ice\.gmt$", item)];

	import subprocess;

	outfile1 = open(label1 + "_Glaciers.txt", "w");
	outfile2 = open(label2 + "_Glaciers.txt", "w");

	for polygon in polygons:

		cmd   = "\ngmtselect " + points_path + " -F" + polygon_dir + "/" + polygon + "\n";
		pipe  = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		point = pipe.read().strip();
		pipe.close();

		if point:
			outfile1.write(polygon_dir + "/" + polygon + "\n");

		else:
			outfile2.write(polygon_dir + "/" + polygon + "\n");

	outfile1.close();
	outfile2.close();

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 4, "\n***** ERROR: polygonsContainingPoints.py requires 4 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	polygonsContainingPoints(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]);

	exit();

