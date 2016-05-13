#!/usr/bin/python


# parseOutlines.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

# Description
# ***********
# parseOutlines.py takes a GMT polygon format boundary file from GLIMS and parses it into individual glacier as well as overall ice and rock outlines.
#		   These are writtent to output files.

# Usage
# *****
# python parseOutlines.py glims_boundaries.gmt
#	glims_boundaries.gmt: A GMT polygon file formatted according to GLIMS standards as of 2014/06/25


def parseOutlines(glims_gmt_path, output_icefield_label):

	import os;

	assert os.path.exists(glims_gmt_path), "\n***** ERROR: " + glims_gmt_path + " does not exist\n";

	glaciers_ice  = {};
	glaciers_rock = {};
	glaciers_type = {};
	glaciers_meta = {};
	glaciers      = {};
	cur_glacier   = "";
	metadata      = "";
	ice	      = True;

	infile       = open(glims_gmt_path, "r");

	while 1:

		line = infile.readline();

		if not line:
			break;

		line = line.strip();

		if not line:
			continue;

		if line.find("Glacier") > -1:

			elements    = line.split("|");
			nrgiid      = elements[0][elements[0].rfind(".") + 2 : ];
			area        = float(elements[9]);
			land        = elements[10];
			name        = elements[11].replace(" ","_").replace("(","").replace(")","").replace("'","").replace(".","").replace("\"","").replace("-","").replace("/","").replace("?","").replace("_Glacier","").replace("Glacier","").replace("_glacier","").replace("glacier","");

			cur_glacier = name + "_" + nrgiid;
			glaciers[cur_glacier] = cur_glacier;
			glaciers_meta[cur_glacier] = line + "\n";
			glaciers_type[cur_glacier] = land;

		elif line.find("@P") > -1:
			ice = True;

		elif line.find("@H") > -1:
			ice = False;

		elif line.find("#") > -1:
			metadata += line + "\n";

		if ice:

			if cur_glacier not in glaciers_ice:
				glaciers_ice[cur_glacier] = line + "\n";

			else:
				glaciers_ice[cur_glacier] += line + "\n";

		else:
			if cur_glacier not in glaciers_rock:
				glaciers_rock[cur_glacier] = line + "\n";

			else:
				glaciers_rock[cur_glacier] += line + "\n";

	metadata += ">\n";

	for glacier in glaciers:

#		if glaciers_type[glacier] != "9199":
#			continue;

		outfile = open(glacier + "_ice.gmt", "w");
		outfile.write(metadata);
		outfile.write(glaciers_meta[glacier]);
		outfile.write(glaciers_ice[glacier]);
		outfile.close();

		if glacier in glaciers_rock:
			outfile = open(glacier + "_rock.gmt", "w");
			outfile.write(metadata);
			outfile.write(glaciers_meta[glacier]);
			outfile.write(glaciers_rock[glacier]);
			outfile.close();

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: parseOutlines.py requires at least one argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";

	output_label = "EntireIcefield";

	if len(sys.argv) > 2:
		output_label = sys.argv[2];	

	parseOutlines(sys.argv[1], output_label);

	exit();


