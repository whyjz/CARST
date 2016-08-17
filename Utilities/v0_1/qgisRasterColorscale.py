#!/usr/bin/python


# qgisRasterColorscale.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def qgisRasterColorscale(qgs_path, qml_path):
	
	assert os.path.exists(qgs_path), "\n***** ERROR: " + qgs_path + " does not exist\n";
	assert os.path.exists(qml_path), "\n***** ERROR: " + qml_path + " does not exist\n";

	raster_renderer = "";

	infile = open(qml_path);

	for line in infile:

		raster_renderer += line;

	infile.close();

	import re;

	raster_renderer = raster_renderer[re.search("\s*<raster",raster_renderer).start(0) : re.search("</rasterrenderer>",raster_renderer).end(0)];

	raster_section = False;

	outfile = open("temp", "w");
	infile  = open(qgs_path, "r");

	for line in infile:

		if line.find("<rasterrenderer") > -1:
			raster_section = True;
			outfile.write(raster_renderer + "\n");

		elif line.find("</rasterrenderer") > -1:
			raster_section = False;

		elif raster_section == False:
			outfile.write(line);

	outfile.close();
	infile.close();

	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: qgisRasterColorscale.py requires 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	qgisRasterColorscale(sys.argv[1], sys.argv[2]);

	exit();

