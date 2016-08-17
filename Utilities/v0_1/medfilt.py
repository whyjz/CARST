#!/usr/bin/python

# medfilt.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

USAGE = \
"\npython medfilt.py radius max_diff input.tif output.tif\n \
	\"radius\" is the radius of points to include when calculating the median at each point in input.tif\n \
	\"max_diff\" is the maximum difference, differences between the median at each point and input.tif that are greater than \"max_diff\" will be absent from output.tif\n \
	\"input.tif\" is the input file (GeoTiff format)\n \
	\"output.tif\" is the output file, with points that differ from the median by more than max_diff removed (changed to NaN)\n";


import os;
import subprocess;
import sys;


# Define "medfilt" function
def medfilt(radius,max_diff,input_gtiff,output_gtiff):

	input_name = input_gtiff[input_gtiff.rfind("/")+1:input_gtiff.rfind(".")];
	input_grd  = input_name + ".grd";

	output_name = output_gtiff[output_gtiff.rfind("/")+1:output_gtiff.rfind(".")];
	output_grd  = output_name  + ".grd";

	cmd = "";
	
	if not os.path.exists(input_grd):
		cmd +=  "\ngdal_translate -of GMT " + input_gtiff + " " + input_grd + "\n";

	cmd += "\ngrdclip " + input_grd + " -Sb-9000/NaN -Gclipped.grd\n";       
	cmd += "\ngrdfilter clipped.grd -D0 -Fm" + radius + " -Gmed.grd -Np -R" + input_grd + "\n";
	cmd += "\ngrdmath clipped.grd med.grd SUB = diff.grd\n";
	cmd += "\ngrdclip diff.grd -Sb-" + max_diff + "/NaN -Sa" + max_diff + "/NaN -Gdiff.grd\n";
	cmd += "\ngrdmath " + input_grd + " diff.grd OR = " + output_grd + "\n";
	cmd += "\ngdal_translate -of GTiff " + output_grd + " " + output_gtiff + "\n";
	subprocess.call(cmd,shell=True);


# Check for correct number of command-line parameters
if len(sys.argv) < 5:
	print(USAGE);
	exit();

# Read parameters from command line
radius		= sys.argv[1];
max_diff	= sys.argv[2];
input_gtiff	= sys.argv[3];
output_gtiff	= sys.argv[4];

# Call "medfilt" function
medfilt(radius,max_diff,input_gtiff,output_gtiff);



exit();
