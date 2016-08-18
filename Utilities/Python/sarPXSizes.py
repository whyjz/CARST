#!/usr/bin/python

# sarPXSizes.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


import numpy;
import pylab;
import scipy;
import sys;


def sarPXSizes(slc_rsc_path, angle): 

	import math;
	import os;
	import re;

	assert os.path.exists(slc_rsc_path), "\n***** ERROR: " + slc_rsc_path + " does not exist\n";

	angle = float(angle);

	infile = open(slc_rsc_path, "r");

	for line in infile:

		label, value = line.split();

		if label.find("AZIMUTH_PIXEL_SIZE") > -1:
			da_p = float(value.strip());

		elif re.search("^EARTH_RADIUS$", label) > -1:
			r_e = float(value.strip());

		elif re.search("^HEIGHT$", label):
			p_h = float(value.strip());

		elif label.find("RANGE_PIXEL_SIZE") > -1:
			dr = float(value.strip());

	infile.close();

	#da_p: azimuth pixel size at orbit radius
	#r_e: earth radius
	#p_h: platform height
	#dr: range pixel size

	r_p  = r_e + p_h;        #platform radius
	da_e = da_p * r_e / r_p; #az pixel size at earth surface, cm    
	dr_g = dr / math.sin(math.radians(angle));  #ground pixel size in range direction, cm

	print("\nAzimuth pixel size at earth surface (in meters): " + str(da_e) + "\n");
	print("\nRange pixel size at earth surface (in meters): " + str(dr_g) + "\n");	

	return;

if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: sarPXSizes.py requires 2 arguments, " + str(len(sys.argv)) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	sarPXSizes(sys.argv[1], sys.argv[2]);

	exit();


