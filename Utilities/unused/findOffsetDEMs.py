#!/usr/bin/python

# findOffset.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

# Usage
# *****
# python findOffset.py ref_hdr search_hdr resolution
#	ref_hdr:    The *.hdr ENVI header file of the reference image
#	searc_hdr:  The *.hdr ENVI header file of the search image
#	resolution: Resolution of the reference and search images



import math;
import sys;


def findOffsetDEMs(ref_hdr, search_hdr, resolution):

	ref_img_samples    = "";
	ref_img_lines      = "";
	search_img_samples = "";
	search_img_lines   = "";

	ref_utm_ul_x  = "";
	ref_utm_ul_y  = "";
	search_utm_ul_x = "";
	search_utm_ul_y = "";

#	Read samples, lines, and upper-left coordinates from reference hdr file

	ref_hdr_file    = open(ref_hdr,"r");

	for line in ref_hdr_file:

		if line.find("samples") > -1:
			info = line.split("=");
			ref_img_samples = info[1].strip();

		elif line.find("lines") > -1:
			info = line.split("=");
			ref_img_lines = info[1].strip();

		elif line.find("map info") > -1:
			info = line.split();
			ref_utm_ul_x = info[6].replace(",","");
			ref_utm_ul_y = info[7].replace(",","");

	ref_hdr_file.close();

#	Read samples, lines, and upper-left coordinates from search hdr file

	search_hdr_file = open(search_hdr,"r");

	for line in search_hdr_file:

		if line.find("samples") > -1:
			info = line.split("=");
			search_img_samples = info[1].strip();

		elif line.find("lines") > -1:
			info = line.split("=");
			search_img_lines = info[1].strip();

		if line.find("map info") > -1:
			info = line.split();
			search_utm_ul_x = info[6].replace(",","");
			search_utm_ul_y = info[7].replace(",","");

	search_hdr_file.close();

#	Calculate mean offset in samples and lines from upper-left coordinates

	utm_offset1 = int(round((float(ref_utm_ul_x) - float(search_utm_ul_x)) / float(resolution)));
	utm_offset2 = int(round((float(search_utm_ul_y) - float(ref_utm_ul_y)) / float(resolution)));

#	Determine reference start/end samples, lines
#		Default: Reference image begins to the right of the search image on the x-axis, geographically, start at sample 1 of the reference image
#			 Reference image ends to the left of the search image on the x-axis, geographically, end at the last sample of the reference image
#			 Reference image begins below the search image on the y-axis, geographically, start at line 1 of the reference image
#			 Reference image ends above the search image on the y-axis, geographically, end at the last line of the reference image 
#		Alternatives:
#			 1) Reference image begins to the left of the search image on the x-axis, geographically, begin at mean offset plus one samples in the reference image
#			 2) Reference image ends to the right of the search image on the x-axis, geographically, end at sample in reference that is geographically the same as the last sample of the search image
#			 3) Reference image begins above the search image on the y-axis, geographically, begin at the mean offset plus one lines in the reference image
#			 3) Reference image ends below the search image on the y-axis, geographically, end at line in reference that is geographically the same as the last line of the search image
		
	ref_img_start_sample = "1";
	ref_img_start_line   = "1";

	ref_img_end_sample  = ref_img_samples;
	ref_img_end_line    = ref_img_lines;

	if float(ref_utm_ul_x) < float(search_utm_ul_x):
		ref_img_start_sample = str(abs(utm_offset1) + 1);

	if float(ref_utm_ul_x) + float(resolution) * float(ref_img_samples) > float(search_utm_ul_x) + float(resolution) * float(search_img_samples):
		ref_img_end_sample = str(int(math.floor(((float(search_utm_ul_x) + float(resolution) * float(search_img_samples)) - float(ref_utm_ul_x)) / int(resolution))));

	if float(ref_utm_ul_y) > float(search_utm_ul_y):
		ref_img_start_line = str(abs(utm_offset2) + 1);

	if float(ref_utm_ul_y) - float(resolution) * float(ref_img_lines) < float(search_utm_ul_y) - float(resolution) * float(search_img_lines):
		ref_img_end_line = str(int(math.floor((float(ref_utm_ul_y) - (float(search_utm_ul_y) - float(resolution) * float(search_img_lines))) / int(resolution))));


	return [ref_img_samples, search_img_samples, ref_img_lines, search_img_lines , ref_img_start_line, ref_img_end_line , ref_img_start_sample, ref_img_end_sample, str(utm_offset1), str(utm_offset2)];



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 3, "\n***** ERROR: findOffsetDEMs.py requires 3 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	findOffsetDEMs(sys.argv[1], sys.argv[2], sys.argv[3]);

	exit();

