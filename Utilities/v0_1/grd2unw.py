#!/usr/bin/python


# grd2unw.py
# Author: Andrew Kenneth Melkonian
# All rights Reserved


# USAGE
# *****
# 	python grd2unw.py /path/to/stuff.grd /path/to/stuff.unw


# INPUT
# *****
#	/path/to/stuff.grd : Path to input NetCDF-grid file
#	/path/to/stuff.unw : Path to output unw file


# DESCRIPTION
# ***********
#	"grd2unw.py" converts an input NetCDF-format grid file into a ROI_PAC unw file


# REQUIREMENTS
# ************
#	GDAL (with NetCDF support)
#	Python
#	ROI_PAC



def grd2unw(grd_path, unw_path):

	import os;
	import subprocess;

	assert os.path.exists(grd_path), "\n***** ERROR: " + grd_path + " does not exist\n";

	cmd  = "\ngdal_translate -of ENVI -ot Float32 " + grd_path + " temp\n";
	subprocess.call(cmd, shell=True);

	samples = "";

	infile = open("temp.hdr", "r");

	for line in infile:
		if line.lower().find("samples") > -1:
			label, samples = line.split("=");

	infile.close();

	cmd = "\nmag_phs2rmg temp temp " + unw_path + " " + samples + "\n";
	subprocess.call(cmd, shell=True);

	os.remove("temp");
	os.remove("temp.hdr");

	if os.path.exists("temp.aux.xml"):
		os.remove("temp.aux.xml");

	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: grd2unw.py requires 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	grd2unw(sys.argv[1], sys.argv[2]);

	exit();

