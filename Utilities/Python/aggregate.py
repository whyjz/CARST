#!/usr/bin/python


# aggregate.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# DESCRIPTION
# ***********
# ``aggregate.py'' reads five-column ASCII text files (longitude, latitude, elevation, date in decimal years, uncertainty), with each file 
#  corresponding to a DEM, with the path to the reference DEM specified separately. It creates five-column ASCII text files as output. 
#  The data is organized on a pixel-by-pixel basis, with pixels separated by a single line containing the greater than character (">", 
#  e.g., GMT polygon file format). This script prepares the input file(s) for the ``weightedRegression.py'' script.


# USAGE
# *****
# python aggregate.py reference_dem_txt_path input_dem_txts_directory identifier increments


# EXAMPLE
# *******
# python /path/to/ref_dem.txt /path/to/inputs/ app 5


# INPUTS
# ******
# reference_dem_txt_path:   Path to 5-column ASCII text file of longitudes, latitudes, elevations, date in decimal years, and uncertainties 
# 			    for reference DEM. 
# input_dem_txts_directory: Path to directory containing input DEMs. The ASCII text file for each input DEM must have the same format as 
#			    the ASCII text file for the reference DEM.
# identifier:               String value, input DEMs in input_dem_txts_directory must end in "identifier.txt" to be read in. 
# increments:               Must be a number; the output will be split into this many files (e.g., "glacier_ice_values_1.txt", 
#                           "glacier_ice_values_2.txt" if increments is "2"). 


# OUTPUTS
# *******
# glacier_ice_values.txt: Five-column ASCII text file(s) with all of the data organized by pixel (pixels separated by single lines 
# containing ">" character). The "increments" input parameter determines how many of these will be made.
#              Column  1: Longitude (floating point)
#              Column  2: Latitude (floating point)
#              Column  3: Elevation (floating point)
#              Column  4: Decimal year (floating point)
#              Column  5: Uncertainty (floating point)


def aggregate(ref_xyz_txt_path, input_dem_xyz_txt_dir, input_dem_xyz_txt_identifier, increments):

#	Import necessary libraries

	import os;
	import re;
	import subprocess;

#	Check reference DEM text file and directory provided for input DEMs exist
	assert os.path.exists(ref_xyz_txt_path), "\n***** ERROR: " + ref_xyz_txt_path + " does not exist, exiting...\n";
	assert os.path.exists(input_dem_xyz_txt_dir), "\n***** ERROR: " + input_dem_xyz_txt_dir + " does not exist, exiting...\n";

#	Hardcoded values for the maximum elevation and minimum elevation that will be included in output, as well as label for output files
	max_elev     = "1520";
	min_elev     = "-5";
	output_label = "stikine_ice_values";

	cmd  = "\ngmtinfo -C " + ref_xyz_txt_path + "\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE).stdout;
	info = pipe.read().split();
	pipe.close();

	min_y = info[2];
	max_y = info[3];

	print(min_y, max_y);

	coords = {};

#	Get contents of directory containing input DEMs
	contents = os.listdir(input_dem_xyz_txt_dir);

#	Only read in files that end in the identifier provided followed by the ".txt" extension
	input_dem_xyz_txt_names = [item for item in contents if re.search(".*" + input_dem_xyz_txt_identifier + ".*\.txt$", item)];

#	Loop through files
	for item in input_dem_xyz_txt_names:

#		Output file name to show user progress is being made
		print("\nCurrently ingesting \"" + item + "\"\n");

#		Open current DEM text file for reading
		infile = open(input_dem_xyz_txt_dir + "/" + item, "r");

#		Read through current DEM text file line-by-line
		for line in infile:

#			Split line
			elements = line.split();

#			Ignore line if it has a NaN or less than two values in elements
			if len(elements) > 2 and elements[2].find("NaN") < 0:

				x = elements[0].strip();
				y = elements[1].strip();
				x = x[ : re.search("0*$",x).start(0)];
				y = y[ : re.search("0*$",y).start(0)];

#				Assume elevation is third column, ignore it if it is greater than the maximum elevation allowed or less than 
#                               the minimum
				if float(elements[2]) > float(max_elev):
					continue;

				elif float(elements[2]) <= float(min_elev):
					continue;

#				Assign coordinate to variable
				xy = x + " " + y;

#				Check if coordinate is already in coords, if not, initialize with coordinate as key
				if xy not in coords:
					coords[xy] = "";

#				Add the values for this DEM to the current coordinate
				coords[xy] = coords[xy] + xy + " " + elements[2].strip() + " " + elements[3].strip() + " " + elements[4].strip() + "\n";

		infile.close();

#	Initialize list that will contain output files
	outfiles = [];

#	Open output files for writing
	for i in range(1, int(increments) + 1):
		outfile = open(output_label + "_" + str(i) + ".txt", "w");
		outfiles.append(outfile);

#	Open reference DEM text file for reading
	infile = open(ref_xyz_txt_path, "r");

#	Read through reference DEM text file line-by-line
	for line in infile:

#		Split line
		elements=line.split();

		if len(elements) > 2 and elements[2].lower().find("a") < 0:

			x = elements[0].strip();
			y = elements[1].strip();
			x = x[ : x.find(".") + 4];
			y = y[ : y.find(".") + 4];

#			Skip elevation if greater than maximum allowed or less than minimum allowed
			if float(elements[2]) > float(max_elev):
				continue;

			elif float(elements[2]) <= float(min_elev):
				continue;

#			Assign coordinate to variable
			xy = x + " " + y;

#			If the coordinate is in coords, add reference DEM information and write to appropriate output file (determined 
#			based on latitude)
			if xy in coords:

				coords[xy] = coords[xy] + xy + " " + elements[2].strip() + " " + elements[3].strip() + " " + elements[4].strip() + "\n";

				increment = int(float(y) - float(min_y)) / int((float(max_y) - float(min_y)) / int(increments));

				if increment > len(outfiles) - 1:
					increment = len(outfiles) - 1;

				outfiles[increment].write(coords[xy]);
				outfiles[increment].write(">\n");

	infile.close();

#	Close output files
	for i in range(0, len(outfiles)):
		outfiles[i].close();

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 3, "\n***** ERROR: aggregate.py requires 4 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	aggregate(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]);

	exit();

