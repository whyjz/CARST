#!/usr/bin/python



def getPointsAtICESat(icesat_path, dhdt_path):

	assert os.path.exists(icesat_path), "\n***** ERROR: " + icesat_path + " does not exist\n";
	assert os.path.exists(dhdt_path), "\n***** ERROR: " + dhdt_path + " does not exist\n";

	icesat_coords = {};	

	infile = open(icesat_path, "r");
	infile.readline();

	for line in infile:
		elements = line.split();
		x        = elements[0];
		y        = elements[1];
		icesat_coords[x + " " + y] = x + " " + y;

	infile.close();

	out_path = dhdt_path[dhdt_path.rfind("/") + 1 : dhdt_path.rfind(".")] + "_at_icesat.txt";

	print(out_path);

	outfile = open(out_path, "w");
	infile  = open(dhdt_path, "r");

	line = infile.readline();
	outfile.write(line);

	for line in infile:

		elements = line.split();
		x        = elements[0];
		y        = elements[1];

		if (x + " " + y) in icesat_coords:
			outfile.write(line);

	infile.close();
	outfile.close();

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: getPointsAtICESat.py requires 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	getPointsAtICESat(sys.argv[1], sys.argv[2]);

	exit();

