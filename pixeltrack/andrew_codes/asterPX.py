#!/usr/bin/python


# asterPX.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# modified by Whyjay Zheng on Apr 27 2016

# USAGE
# *****
# 	python asterPX.py /path/to/params.txt


# DEPENDENCIES
# ************

# The following software and scripts are REQUIRED by this script:

# REQUIRES the following software packages to be installed, with paths to executables in the PATH environment variable:
#	Python WITH numpy, scipy
#	GDAL
#	GMT
#	ROI_PAC

# REQUIRES the following scripts in the SAME directory as asterPX.py:
#	splitAmpcor.py
#	findOffset.py
#	getxyzs.py

# The following software and scripts are not necessary for pixel-tracking, but are necessary for optional parts of the processing:

# If "PREFILTER" is set to "True" in the parameters file (see below) the following software must be installed:
#	IDL/ENVI

# If "PREFILTER" is set to "True", the following script must be present and compiled in the program "idlde":
#	gausshighpassfiltgausstretch.pro

# Post-filtering requires the following software:
#	MATLAB

# Post-filtering requires the following scripts in the "MATLAB" directory specified in the parameters file (see below):
#	noiseremoval.m
#	remloners.m
#	remnoise.m
#	grdread2.m
#	grdwrite2.m

# Motion-elevation correction requires the following script to be in the SAME directory as asterPX.py:
#	motionElevCorrection.py


# INPUT
# *****
#	/path/to/params.txt: Path to ASCII text file containing all the necessary parameters, example below

# Example parameters file

# ***********************
# /path/to/params.txt
# ***********************
"""

UTM_ZONE	= 7
UTM_LETTER	= V
ICE		= /home/user/Region_utm7v_ice.gmt
ROCK		= /home/user/Region_utm7v_rock.gmt
METADATA_DIR	= /home/user/ASTER/Images
PAIRS_DIR	= /home/user/ASTER/Pairs
PROCESSORS	= 4
RESOLUTION	= 15
SNR_CUTOFF	= 0
DEM_GRD		= /home/user/DEMs/DEM_utm7v.grd
PREFILTER       = False
REF_X           = 32
REF_Y           = 32
SEARCH_X        = 32
SEARCH_Y        = 32
STEP            = 8
M_SCRIPTS_DIR   = /home/user/MATLAB/scripts
VEL_MAX         = 10
TOL             = 0.2
NUMDIF          = 3
SCALE           = 1500000
PAIRS		= /home/user/ASTER/Pairs/aster_pairs.txt

"""
# ***********************

# Parameter descriptions
# ***********************

# UTM_ZONE
#	Number of UTM zone to use (imagery will be reprojected to this zone if not already projected in it)

# UTM_LETTER
#	Letter of UTM zone (for use by GMT scripts)

# ICE		
#	Path to GMT polygon file containing glacier outlines projected in UTM_ZONE.
#	Outlines for many regions available via Global Land Ice Measurements from Space (GLIMS, www.glims.org).

# ROCK		
#	Path to GMT polygon file containing internal rock outlines projected in UTM_ZONE.

# METADATA_DIR	
#	Directory containing metadata, metadata files MUST have the same identifier as image files
#	e.g. if image file is LC81760062014211LGN00_B8.TIF, metadata file MUST be LC81760062014211LGN00_MTL.txt

# PAIRS_DIR	
#	Directory where all file created by this script will be written.
#	A separate directory will be created for each pair, with the following format: YYYYMMDDHHMMSS_YYYYMMDDHHMMSS
#	The first date/time-stamp corresponds to the later image in the pair, the second to the earlier image
#	DO NOT MODIFY the pair directory names created by the script if you expect the script to work

# PROCESSORS	
#	Number of processors to use when running "ampcor"
#	To find the number of "processors" available on your machine (if you are using linux), enter the command "top" then type the number "1"
#	NOTE: You can enter any number here, but if that number is higher than the number of "processors" available on your machine you will not see a performance increase.

# RESOLUTION	
#	Resolution of the input imagery in meters (e.g. "15" for band 8 of ASTER 7 and 8).

# SNR_CUTOFF	
#	Signal-to-noise ratio threshold, *_filt.grd velocity grids created by the script during post-processing will be clipped so that all pixels 
#	with an SNR below this threshold are masked out.

# DEM_GRD
#	Path to NetCDF grid file of elevations projected in UTM_ZONE.
#	MAKE SURE this covers the maximum extent of the imagery if you plan on using motion-elevation corrected results.
#	Motion-elevation correction cannot be performed where the elevation is unknown.
 
# PREFILTER     
#	Set to True if you are using IDLDE to perform gaussian high-pass filtering using the gausshighpassgausstretch.pro script.
#	If you set this to "True" DO NOT modify the file names created by the *.pro script, let asterPX.py deal with it.
#	NOTE: This is often not necessary for Landsat 7 and 8. 

# REF_X
#	Reference window size in pixels for the longitude/width/columns/samples direction. 
#	NOTE: 32 has proved successful, but you may wish to modify, e.g. a smaller window for smaller glaciers/faster processing.

# REF_Y         
#	Reference window size in pixels for the latitude/length/rows/lines direction. 
#	NOTE: 32 has proved successful, but you may wish to modify, e.g. a smaller window for smaller glaciers/faster processing.

# SEARCH_X      
#	Search window size in pixels for the longitude/width/columns/samples direction.
#	Set this so that it is twice the maximum offset (maximum velocity multiplied by time interval, then divided by RESOLUTION).

# SEARCH_Y      
#	Search window size in pixels for the latitude/length/rows/lines direction. 
#	Set this so that it is twice the maximum offset (maximum velocity multiplied by time interval, then divided by RESOLUTION).

# STEP
#	Pixel-tracking is performed every STEP pixels.
#	The smaller this number, the higher resolution the velocity results will be and the longer "ampcor" will take to run.
   
# M_SCRIPTS_DIR 
#	Directory containing the Matlab scripts "noiseremoval.m", "remloners.m", "remnoise.m", "grdread2.m", "grdwrite2.m"
#	NOTE: This is not necessary for processing.

# VEL_MAX       
#	Maximum velocity threshold (in m/day) for use by "noiseremoval.m".
#	Velocities above this value will be clipped for *_filt.grd files.
#	Lower values filter out MORE, higher values filter out LESS.
#	NOTE: This applies to E-W and N-S velocities, NOT to overall speed.

# TOL 
#	Adjacent pixels whose velocity is within TOL*VEL_MAX are considered  "similar" pixels.
#	For example, if TOL is 0.2 and VEL_MAX is 10, pixels that are with 2 m/day of each other are considered "similar".
#	Lower values filter out MORE, higher values filter out LESS.
#	This is used in conjunction with NUMDIF (see below).

# NUMDIF        
#	The minimum number of "similar" pixels that must "adjacent" to the pixel being considered.
#	If less than this number of "similar" adjacent pixels are found, the pixel will be filtered out of the *_filt.grd velocity results.
#	Lower values filter out LESS, higher values filter out MORE.

# SCALE 
#	Scale to be used by GMT when plotting results, 1500000 often works for an entire Landsat 8 image.

# PAIRS
#	Path to two-column ASCII text file listing image pair paths.
#	Each row corresponds to an image pair, containing two entries that are paths to each image in the pair.


# OUTPUT
# ******

# A directory will be created in the "PAIRS_DIR" directory for each valid pair given in the "PAIRS" file with the following format:
#	YYYYMMDDHHMMSS_YYYYMMDDHHMMSS
#       The first date/time-stamp corresponds to the later image in the pair, the second to the earlier image
#       DO NOT MODIFY the pair directory names created by the script or the filenames created by this script if you expect the script to work

# The following results will be created in these directories if the script runs sucessfully:
#	YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_*_eastxyz.txt	UTM Easting, UTM Northing, E-W offset in meters, SNR (space-delimited)
#	YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_*_northxyz.txt    UTM Easting, UTM Northing, N-S offset in meters, SNR (space-delimited)
# These are 4-column ASCII text files containing the E-W and N-S OFFSETS in METERS (NOT velocities)
# The first column is longitude (UTM easting), the second is latitude (UTM northing), the third is offset in meters, the fourth is signal-to-noise ratio

# Unfiltered NetCDF grid files containing VELOCITIES in METERS PER DAY will be created from the ASCII text files:
#	YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_*_eastxyz.grd	E-W velocities (NOTE: MAY NEED TO MULTIPLY BY -1)
#	YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_*_northxyz.grd	N-S velocities
#	YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_*_mag.grd		Speeds from E-W and N-S velocities
# A NetCDF grid file containing the SNRs will be created as well:
#	YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_*_snrxyz.grd	SNRs
# An image of the speeds will be created, as well as a file containing the GMT commands used to create the image (if you'd like to modify it to create your own image):
#	YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_mag.pdf		PDF image of speeds
#	YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_image.gmt		GMT commands used to create "YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_mag.pdf"

# If filtering scripts are present, filtered files will be created corresponding to each of the unfiltered files:
#	YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_*_eastxyz_filt.grd       Filtered E-W velocities
#       YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_*_northxyz_filt.grd      Filtered N-S velocities
#       YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_*_mag_filt.grd           Speeds from filtered E-W and N-S velocities
#       YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_*_mag_filt.pdf           PDF image of filtered speeds
#       YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_*_image_filt.gmt	       GMT commands used to create "YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_mag_filt.pdf"

# If a DEM is specified, motion-elevation corrected files will be created from either the filtered (if present) or unfiltered velocities
#	YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_*_eastxyz*_corrected.grd       Filtered E-W velocities
#       YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_*_northxyz*_corrected.grd      Filtered N-S velocities
#       YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_*_mag*_corrected.grd           Speeds from filtered E-W and N-S velocities
#       YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_*_mag*_corrected.pdf           PDF image of filtered speeds
#       YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_*_image*_corrected.gmt	     GMT commands used to create "YYYYMMDDHHMMSS_YYYYMMDDHHMMSS_mag_filt.pdf"


import sys;
sys.path.append("/data/akm/Python");


import aropInput;
import datetime;
from getxyzs import *;
from imageAmpResults import *;
from motionElevCorrection import *;
import os;
import re;
import subprocess;
import time;




def tail(input_path, num_lines):

	print(input_path)    #whyjay
	infile = open(input_path, "r");

	BLOCK_SIZE = 1024;
	infile.seek(0, 2);
	block_end_byte = infile.tell();

	block_end_byte = infile.tell();
	lines_to_go = num_lines;
	block_number = -1;
	blocks = [] 

	# blocks of size BLOCK_SIZE, in reverse order starting
	# from the end of the file

	while lines_to_go > 0 and block_end_byte > 0:

		if (block_end_byte - BLOCK_SIZE > 0):
			# read the last block we haven't yet read
			infile.seek(block_number*BLOCK_SIZE, 2);
			blocks.append(infile.read(BLOCK_SIZE));

		else:
			# file too small, start from begining
			infile.seek(0,0);
			# only read what was not read
			blocks.append(infile.read(block_end_byte));

		lines_found = blocks[-1].count('\n');
		lines_to_go -= lines_found;
		block_end_byte -= BLOCK_SIZE;
		block_number -= 1;

	infile.close();

	all_read_text = "".join(reversed(blocks));
	print(all_read_text)    #whyjay

	return "\n".join(all_read_text.splitlines()[-num_lines:]);



def asterPX(params_path):

	infile = open(params_path,"r");

	while 1:
		line = infile.readline();

		if not line:
			break;

		line = line.strip();

		name = "";
		value = "";
		elements = line.split("=");

		if len(elements) < 2 or len(elements[0]) < 1 or len(elements[1]) < 1:
			print("\n***** ERROR, parameter file line format is \"name = value\", \"" + line + "\" does not conform to this format\n");
			sys.exit();

		name = elements[0].strip();
		value = elements[1].strip();
		vars()[name] = value;

	infile.close();

	if not os.path.exists(PAIRS_DIR):
		print("\n***** ERROR: Pair directory specified (\"" + PAIRS_DIR + "\") not found, make sure full path is provided, exiting...\n");
		return;

	if not os.path.exists(METADATA_DIR):
		print("\n***** ERROR: Metadata directory specified (\"" + METADATA_DIR + "\") not found, make sure full path is provided, exiting...\n");
		return;

	if not os.path.exists(PAIRS):
		print("\n***** ERROR: Pair list \"" + PAIRS + "\" not found, make sure full path is provided, exiting...\n");

	pairs_hash = {};	

	infile = open(PAIRS, "r");

	for pair in infile:

		if re.search("^\s*#", pair):
			continue;

		image1_path, image2_path = pair.split();

		if not os.path.exists(image1_path):
			print("\n***** WARNING: \"" + image1_path + "\" not found, make sure full path is provided, skipping corresponding pair...\n");
			continue;

		elif not os.path.exists(image2_path):
			print("\n***** WARNING: \"" + image2_path + "\" not found, make sure full path is provided, skipping corresponding pair...\n");
			continue;

		pairs_hash[pair] = pair;

	infile.close();

	if len(pairs_hash) == 0:
		print("\n***** ERROR: No valid pairs found,  make sure correct paths were provided in \"" + PAIRS + "\", exiting...\n");
		return;

	for pair in pairs_hash:

		image1_path, image2_path = pair.split();

		image1_name = image1_path[image1_path.rfind("/") + 1 : image1_path.rfind("_")];
		image2_name = image2_path[image2_path.rfind("/") + 1 : image2_path.rfind("_")];

		image1_metadata_path = METADATA_DIR + "/" + image1_name + ".zip.met";
		image2_metadata_path = METADATA_DIR + "/" + image2_name + ".zip.met";

		if not os.path.exists(image1_metadata_path):
			print("\n***** WARNING: \"" + image1_metadata_path + "\" not found, make sure full path is provided, skipping...\n");
			continue;

		if not os.path.exists(image2_metadata_path):
			print("\n***** WARNING: \"" + image2_metadata_path + "\" not found, make sure full path is provided, skipping...\n");
			continue;

		image1_time = "";
		image1_date = "";

		infile = open(image1_metadata_path, "r");

		while 1:

			line = infile.readline();

			if not line:
				break;

			if line.find("SINGLEDATETIME") > -1:

				while 1:

					line=infile.readline();

					if not line or line.find("SINGLEDATETIME") > -1:
						break;

					if re.search("\d{2}\:\d{2}\:\d{2}", line):
						image1_time = line[re.search("\d{2}\:\d{2}\:\d{2}", line).start(0) : re.search("\d{2}\:\d{2}\:\d{2}", line).end(0)];
						image1_time = image1_time.replace(":","");

					elif re.search("\d{4}\-\d{2}\-\d{2}", line):
						image1_date = line[re.search("\d{4}\-\d{2}\-\d{2}", line).start(0) : re.search("\d{4}\-\d{2}\-\d{2}", line).end(0)];
						image1_date = image1_date.replace("-","");

		infile.close();

		image2_time = "";
		image2_date = "";

		infile = open(image2_metadata_path, "r");

		while 1:

			line = infile.readline();

			if not line:
				break;

			if line.find("SINGLEDATETIME") > -1:

				while 1:

					line=infile.readline();

					if not line or line.find("SINGLEDATETIME") > -1:
						break;

					if re.search("\d{2}\:\d{2}\:\d{2}", line):
						image2_time = line[re.search("\d{2}\:\d{2}\:\d{2}", line).start(0) : re.search("\d{2}\:\d{2}\:\d{2}", line).end(0)];
						image2_time = image2_time.replace(":","");

					elif re.search("\d{4}\-\d{2}\-\d{2}", line):
						image2_date = line[re.search("\d{4}\-\d{2}\-\d{2}", line).start(0) : re.search("\d{4}\-\d{2}\-\d{2}", line).end(0)];
						image2_date = image2_date.replace("-","");

		infile.close();

		image1_link_path = image1_path[image1_path.rfind("/") + 1 : ];
		image2_link_path = image2_path[image2_path.rfind("/") + 1 : ];

		early_image_path = image2_link_path;
		later_image_path = image1_link_path;
		early_date       = image2_date + image2_time;
		later_date       = image1_date + image1_time;

		if image2_date > image1_date:
			early_image_path = image1_link_path;
			later_image_path = image2_link_path;
			early_date       = image1_date + image1_time;
			later_date       = image2_date + image2_time;

		pair_label = later_date + "_" + early_date;
		pair_path  = PAIRS_DIR + "/" + pair_label;

		image1_link_path  = pair_path + "/" + image1_link_path;
		image2_link_path  = pair_path + "/" + image2_link_path;
		early_image_path  = pair_path + "/" + early_image_path;
		later_image_path  = pair_path + "/" + later_image_path;

		if not os.path.exists(pair_path):
			os.mkdir(pair_path);

		if not os.path.exists(image1_link_path):
			os.symlink(image1_path, image1_link_path);

		if not os.path.exists(image2_link_path):
			os.symlink(image2_path, image2_link_path);

		if PREFILTER == "True":

			early_ghp_path = pair_path + "/" + early_image_path[early_image_path.rfind("/") + 1 : early_image_path.rfind(".")] + "_ghp_stretch.img"; 
			later_ghp_path = pair_path + "/" + later_image_path[later_image_path.rfind("/") + 1 : later_image_path.rfind(".")] + "_ghp_stretch.img"; 

			if not os.path.exists(early_ghp_path) or not os.path.exists(later_ghp_path):
				print("\n***** WARNING: \"" + early_ghp_path + " or " + later_ghp_path + " not found, plese open \"idlde\" and run the commands:\n\n \
				       envi\n \
				       gausshighpassfiltergausstretch,\"" + early_link_path + "\"\n \
				       gausshighpassfiltergausstretch,\"" + later_link_path + "\"\n\n \
				       Skipping this pair...\n");
				continue;

			early_image_path = early_ghp_path;
			later_image_path = later_ghp_path;

		early_cut_path = early_image_path[ : early_image_path.rfind(".")] + "_cut.img";
		later_cut_path = later_image_path[ : later_image_path.rfind(".")] + "_cut.img";

		cmd = "\ngdalinfo " + early_image_path + "\n";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		info = pipe.read();
		pipe.close();
		#print info      # whyjay
		#print UTM_ZONE  # whyjay

		#zone1  = info[re.search("UTM\s*zone\s*",info).end(0) : re.search("UTM\s*zone\s*\d+",info).end(0)];   #whyjay
		zone1 = UTM_ZONE    #whyjay

		cmd = "\ngdalinfo " + later_image_path + "\n";
	        pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	        info = pipe.read();
	        pipe.close();

		#zone2  = info[re.search("UTM\s*zone\s*",info).end(0) : re.search("UTM\s*zone\s*\d+",info).end(0)];    #whyjay
		zone2 = UTM_ZONE    #whyjay

		if zone1 != UTM_ZONE:
			cmd = "\ngdalwarp -t_srs '+proj=utm +zone=" + UTM_ZONE + " +north +datum=WGS84' -tr " + RESOLUTION + " " + early_image_path + " " + pair_path + "/temp\n";
			subprocess.call(cmd, shell=True);
			os.rename(pair_path + "/temp", early_image_path);

		if zone2 != UTM_ZONE:
			cmd = "\ngdalwarp -t_srs '+proj=utm +zone=" + UTM_ZONE + " +north +datum=WGS84' -tr " + RESOLUTION + " " + later_image_path + " " + pair_path + "/temp\n";
			subprocess.call(cmd, shell=True);
			os.rename(pair_path + "/temp", later_image_path);

		cmd = "\ngdalinfo " + early_image_path + "\n";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		info = pipe.read();
		pipe.close();

		ul_1_x = info[re.search("Upper Left\s*\(\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
		ul_1_y = info[re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
		ur_1_x = info[re.search("Upper Right\s*\(\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
		ur_1_y = info[re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
		lr_1_x = info[re.search("Lower Right\s*\(\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
		lr_1_y = info[re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
		ll_1_x = info[re.search("Lower Left\s*\(\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
		ll_1_y = info[re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

		cmd = "\ngdalinfo " + later_image_path + "\n";
	        pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	        info = pipe.read();
	        pipe.close();

	        ul_2_x = info[re.search("Upper Left\s*\(\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	        ul_2_y = info[re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	        ur_2_x = info[re.search("Upper Right\s*\(\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	        ur_2_y = info[re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	        lr_2_x = info[re.search("Lower Right\s*\(\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	        lr_2_y = info[re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	        ll_2_x = info[re.search("Lower Left\s*\(\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	        ll_2_y = info[re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

		ul_x = str(max([float(ul_1_x), float(ul_2_x)]));
		ul_y = str(min([float(ul_1_y), float(ul_2_y)]));
		lr_x = str(min([float(lr_1_x), float(lr_2_x)]));
		lr_y = str(max([float(lr_1_y), float(lr_2_y)]));

		early_cut_path = early_image_path[ : early_image_path.rfind(".")] + "_cut.img";
		later_cut_path = later_image_path[ : later_image_path.rfind(".")] + "_cut.img";

		if not os.path.exists(early_cut_path):
			cmd  = "\ngdal_translate -of ENVI -ot Float32 -projwin " + ul_x + " " + ul_y + " " + lr_x + " " + lr_y + " " + early_image_path + " " + early_cut_path + "\n";
			subprocess.call(cmd, shell=True);

		if not os.path.exists(later_cut_path):
			cmd = "\ngdal_translate -of ENVI -ot Float32 -projwin " + ul_x + " " + ul_y + " " + lr_x + " " + lr_y + " " + later_image_path + " " + later_cut_path + "\n";
			subprocess.call(cmd,shell=True);

		if not os.path.exists(early_cut_path) or not os.path.exists(later_cut_path):
			print("\n***** ERROR: \"gdal_translate\" to cut images to common region unsuccessful skipping \"" + pair_label + "...\n");

		from splitAmpcor import *;

		ampcor_label = "r" + REF_X + "x" + REF_Y + "_s" + SEARCH_X + "x" + SEARCH_Y;

		if not os.path.exists(pair_path + "/ampcor_" + ampcor_label + "_1.in"):
			print("\nRunning \"splitAmpcor.py\" to create \"ampcor\" input files...\n");
			splitAmpcor(early_cut_path, later_cut_path, pair_path, PROCESSORS, RESOLUTION, REF_X, REF_Y, SEARCH_X, SEARCH_Y, STEP); 

		else:
			print("***** \"" + pair_path + "/ampcor_" + ampcor_label + "_1.in\" already exists, assuming \"ampcor\" input files already made...\n");

		if not os.path.exists(pair_path + "/ampcor_" + ampcor_label + "_1.off"):

			cmd = "";
			cmd += "cd " + pair_path  #whyjay

			for i in range(1, int(PROCESSORS) + 1):
				#cmd += "\nampcor " + pair_path + "/ampcor_" + ampcor_label + "_" + str(i) + ".in rdf > " + pair_path + "/ampcor_" + ampcor_label + "_" + str(i) + ".out &\n";     #whyjay
				cmd += "\nampcor " + "ampcor_" + ampcor_label + "_" + str(i) + ".in rdf > " + pair_path + "/ampcor_" + ampcor_label + "_" + str(i) + ".out &\n"
			print("\n\"ampcor\" running as " + PROCESSORS + " separate processes, this step will likely take at least several hours to complete...\n");
			#print(cmd)    #whyjay 
			#subprocess.call('pwd', shell=True);    #whyjay
			subprocess.call(cmd, shell=True);
			subprocess.call('cd ..', shell=True);   #whyjay

		raw_input('If all ampcors are finished, please press enter.')

		pair_done = True;

		for i in range(1, int(PROCESSORS) + 1):

			infile = open(pair_path + "/ampcor_" + ampcor_label + "_" + str(i) + ".in", "r");

			for line in infile:

				if line.find("Start, End and Skip Lines in Reference Image") > -1:
					end_line = line.split("=")[1].split()[1];

			infile.close();
			print('=======')    #whyjay
			print(tail(pair_path + "/ampcor_" + ampcor_label + "_" + str(i) + ".off", 1))    #whyjay
			print('=======')    #whyjay

			# ==== By whyjay ====
			'''last_line_processed = tail(pair_path + "/ampcor_" + ampcor_label + "_" + str(i) + ".off", 1).split()[2];

			if (int(end_line) - int(last_line_processed)) > (int(REF_Y) + int(SEARCH_Y) + 200):
				print("\n***** ERROR, last line processed in \"" + pair_path + "/ampcor_" + ampcor_label + "_" + str(i) + ".off\" is " \
				       + last_line_processed + ", last line to be processes is " + end_line + ", the difference is greater than the \
				       search window size in lines plus the reference window size in lines (" \
				       + str(int(REF_Y) + int(SEARCH_Y)) + "), pair might still be processing, skipping...\n"); 
				pair_done = False;
			'''
			# ==== By whyjay ====

		if not pair_done:
			continue;

		print("\n***** Offset files in \"" + pair_path + "\" appear to have finished processing, composing results...\n");

		if os.path.exists(pair_path + "/ampcor_" + ampcor_label + ".off"):
			print("\n***** \"" + pair_path + "/ampcor_" + ampcor_label + ".off\" already exists, assuming it contains all offsets for this run...\n");

		else:

			cat_cmd = "\ncat ";

			for i in range(1, int(PROCESSORS) + 1):
				cmd = "\nsed -i '/\*/d' " + pair_path + "/ampcor_" + ampcor_label + "_" + str(i) + ".off\n";
				cat_cmd += pair_path + "/ampcor_" + ampcor_label + "_" + str(i) + ".off ";
				subprocess.call(cmd, shell=True);

			cat_cmd += "> " + pair_path + "/ampcor_" + ampcor_label + ".off\n";
			subprocess.call(cat_cmd, shell=True);

		ref_samples = "";
		ref_lines   = "";

		infile = open(early_cut_path.replace(".img",".hdr"), "r");

		for line in infile:

			if line.lower().find("samples") > -1:
				ref_samples = line.split("=")[1].strip();

			if line.lower().find("lines") > -1:
				ref_lines = line.split("=")[1].strip();

		infile.close();

		east_name      = pair_label + "_" + ampcor_label + "_eastxyz";
		north_name     = pair_label + "_" + ampcor_label + "_northxyz";
		mag_name       = pair_label + "_" + ampcor_label + "_mag";
		east_xyz_path  = pair_path + "/" + east_name + ".txt";
		north_xyz_path = pair_path + "/" + north_name + ".txt";

		if not os.path.exists(east_xyz_path):
			print("\n***** \"getxyzs.py\" running to create E-W and N-S ASCII files with offsets (in m) in the third column and SNR in the 4th column\n \
		       ***** NOTE: E-W MAY BE FLIPPED DEPENDING ON HEMISPHERE, PLEASE CHECK MANUALLY...\n");
			getxyzs(pair_path, ampcor_label, STEP, STEP, "1", RESOLUTION, ref_samples, ref_lines, ul_x, ul_y, pair_label);

		else:
			print("\n***** \"" + east_xyz_path + "\" already exists, assuming E-W and N-S ASCII offsets (in m) files created properly for this run...\n");

		east_grd_path  = pair_path + "/" + east_name + ".grd";
		north_grd_path = pair_path + "/" + north_name + ".grd";
		mag_grd_path   = pair_path + "/" + mag_name + ".grd";
		snr_grd_path   = pair_path + "/" + north_name.replace("north", "snr") + ".grd";
		c11_grd_path   = pair_path + "/" + pair_label + "_" + ampcor_label + "_c11.grd";
		c22_grd_path   = pair_path + "/" + pair_label + "_" + ampcor_label + "_c22.grd";

		R = "-R" + ul_x + "/" + lr_y + "/" + lr_x + "/" + ul_y + "r";

		if not os.path.exists(east_grd_path):
			print("\n***** Creating \"" + east_grd_path + "\" and \"" + north_grd_path + "\" using \"xyz2grd\"...\n");
			early_datetime = datetime.datetime(int(early_date[0:4]), int(early_date[4:6]), int(early_date[6:8]), \
							   int(early_date[8:10]), int(early_date[10:12]), int(early_date[12:14]));
			later_datetime = datetime.datetime(int(later_date[0:4]), int(later_date[4:6]), int(later_date[6:8]), \
							   int(later_date[8:10]), int(later_date[10:12]), int(later_date[12:14]));
			day_interval   = str((later_datetime - early_datetime).total_seconds() / (60. * 60. * 24.));
			cmd  = "\nxyz2grd " + east_xyz_path + " " + R + " -G" + east_grd_path + " -I" + str(int(STEP) * int(RESOLUTION)) + "=\n";
			cmd += "\nxyz2grd " + north_xyz_path + " " + R + " -G" + north_grd_path + " -I" + str(int(STEP) * int(RESOLUTION)) + "=\n";
			cmd += "\ngawk '{print $1\" \"$2\" \"$4}' " + north_xyz_path + " | xyz2grd " + R + " \
				-G" + snr_grd_path + " -I" + str(int(STEP) * int(RESOLUTION)) + "=\n";
			cmd += "\ngawk '{print $1\" \"$2\" \"$5}' " + north_xyz_path + " | xyz2grd " + R + " \
				-G" + c11_grd_path + " -I" + str(int(STEP) * int(RESOLUTION)) + "= --IO_NC4_CHUNK_SIZE=c\n";
			cmd += "\ngawk '{print $1\" \"$2\" \"$6}' " + north_xyz_path + " | xyz2grd " + R + " \
				-G" + c22_grd_path + " -I" + str(int(STEP) * int(RESOLUTION)) + "= --IO_NC4_CHUNK_SIZE=c\n";
			cmd += "\ngrdmath " + east_grd_path + " " + day_interval + " DIV --IO_NC4_CHUNK_SIZE=c = " + east_grd_path + "\n";
			cmd += "\ngrdmath " + north_grd_path + " " + day_interval + " DIV --IO_NC4_CHUNK_SIZE=c = " + north_grd_path + "\n";
			cmd += "\ngrdmath " + north_grd_path + " " + east_grd_path + " HYPOT --IO_NC4_CHUNK_SIZE=c = " + mag_grd_path + "\n";
			subprocess.call(cmd, shell=True);

		else:
			print("\n***** \"" + east_grd_path + "\" already exists, assuming m/day velocity grids already made for this run...\n"); 

		cmd  = "\necho \"" + ul_x + " " + ul_y + "\\n" + lr_x + " " + lr_y + "\" | mapproject -Ju" + UTM_ZONE + UTM_LETTER + "/1:1 -F -C -I\n";
		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		geo_ul_x, geo_ul_y, geo_lr_x, geo_lr_y = pipe.read().split();
		pipe.close();

		geoR = "-R" + geo_ul_x + "/" + geo_lr_y + "/" + geo_lr_x + "/" + geo_ul_y + "r";
		J    = "-Jx1:" + SCALE;
		geoJ = "-Ju" + UTM_ZONE + "/1:" + SCALE;

		mag_ps_path = pair_path + "/" + mag_name + ".ps";

		cmd  = "\nmakecpt -Chaxby -T0/" + VEL_MAX + "/0.01 --COLOR_BACKGROUND=white --COLOR_NAN=white --COLOR_FOREGROUND=white > " + pair_path + "/mag.cpt\n";
                cmd += "\ngrdimage " + mag_grd_path + " " + J + " " + R + " -C" + pair_path + "/mag.cpt -P -K > " + mag_ps_path + "\n";
		cmd += "\npsxy " + ICE + " " + J + " " + R + " -W1p,black -O -K >> " + mag_ps_path + "\n";
		cmd += "\npsxy " + ROCK + " " + J + " " + R + " -W1p,black -O -K >> " + mag_ps_path + "\n";
		cmd += "\npsbasemap " + geoJ + " " + geoR + " -Bf1a1g1:\"Longitude\":/a0.5g0.5:\"\"::,::.\"\":WeSn --MAP_FRAME_TYPE=inside --FORMAT_GEO_MAP=ddd:mmF --FONT_ANNOT_PRIMARY=12p,1,black --MAP_GRID_PEN_PRIMARY=0.25p,100/100/100,- -O -K >> " + mag_ps_path + "\n";
		cmd += "\npsbasemap " + geoJ + " " + geoR + " -Lfx3c/2c/60.5/40k+jr+u+p0.5,black+gwhite --FONT_ANNOT_PRIMARY=10p,1,black --FONT_LABEL=10p,1,black -O -K >> " + mag_ps_path + "\n";
		cmd += "\npsscale -D3c/4c/3c/0.1c -C" + pair_path + "/mag.cpt -B1:\"Speed\":/:\"m day@+-1@+\": --FONT_ANNOT_PRIMARY=10p,1,black --FONT_LABEL=10p,1,black -O >> " + mag_ps_path + "\n";
		cmd += "\nps2raster -A -Tf " + mag_ps_path + "\n";
		print(cmd);
		subprocess.call(cmd, shell=True);

		os.remove(mag_ps_path);

		east_cov_path   = pair_path + "/" + east_name + "_cov.grd"; 
		north_cov_path  = pair_path + "/" + north_name + "_cov.grd"; 
		mag_cov_path    = pair_path + "/" + mag_name + "_cov.grd";

		if not os.path.exists(east_cov_path):

			print("\n***** Clipping using covariance matrices, creating \"" + east_cov_path + "\" and \"" + north_cov_path + "\"...\n");

			cmd  = "\ngrdclip " + c11_grd_path + " -Sa2/NaN -Gc11_clipped.grd\n";
			cmd += "\ngrdclip " + c22_grd_path + " -Sa2/NaN -Gc22_clipped.grd\n";
			cmd += "\ngrdmath c11_clipped.grd c22_clipped.grd AND = cov.grd\n";
			subprocess.call(cmd, shell=True);

			cmd  = "\ngrdmath " + east_grd_path + " cov.grd OR --IO_NC4_CHUNK_SIZE=c = " + east_cov_path + "\n";
			cmd += "\ngrdmath " + north_grd_path + " cov.grd OR --IO_NC4_CHUNK_SIZE=c = " + north_cov_path + "\n";
			cmd += "\ngrdmath " + north_cov_path + " " + east_cov_path + " HYPOT --IO_NC4_CHUNK_SIZE=c = " + mag_cov_path + "\n";
			subprocess.call(cmd, shell=True);	

		rock_grd_path   = pair_path + "/" + pair_label + "_off_ice.grd";
		east_rr_path    = pair_path + "/" + east_name + "_rr.grd";
		north_rr_path   = pair_path + "/" + north_name + "_rr.grd";
		mag_rr_path     = pair_path + "/" + mag_name + "_rr.grd";
		east_rock_path  = pair_path + "/" + east_name + "_off_ice.grd";
		north_rock_path = pair_path + "/" + north_name + "_off_ice.grd";
		east_filt_path  = pair_path + "/" + east_name + "_filt.grd";
		north_filt_path = pair_path + "/" + north_name + "_filt.grd";
		mag_filt_path   = pair_path + "/" + mag_name + "_filt.grd";

		if not os.path.exists(east_rr_path):

			print("\n***** Removing ramp, creating \"" + east_rr_path + "\" and \"" + north_rr_path + "\"...\n");

			if not os.path.exists(rock_grd_path):
				cmd  = "\ngrdmask " + ICE + " -N1/NaN/NaN -R" + east_grd_path + " -G" + pair_path + "/" + pair_label + "_outside_ice.grd\n";
				cmd += "\ngrdmask " + ROCK + " -NNaN/NaN/1 -R" + east_grd_path + " -G" + pair_path + "/" + pair_label + "_inside_rock.grd\n";
				cmd += "\ngrdmath " + pair_path + "/" + pair_label + "_outside_ice.grd " + pair_path + "/" + pair_label + "_inside_rock.grd AND = " + rock_grd_path + "\n";
				subprocess.call(cmd, shell=True);

				os.remove(pair_path + "/" + pair_label + "_outside_ice.grd");
				os.remove(pair_path + "/" + pair_label + "_inside_rock.grd");

			if not os.path.exists("noiseremoval.m"):
				os.symlink(M_SCRIPTS_DIR + "/noiseremoval.m", "noiseremoval.m");
				os.symlink(M_SCRIPTS_DIR + "/remloners.m", "remloners.m");
				os.symlink(M_SCRIPTS_DIR + "/remnoise.m", "remnoise.m");
				os.symlink(M_SCRIPTS_DIR + "/grdread2.m", "grdread2.m");
				os.symlink(M_SCRIPTS_DIR + "/grdwrite2.m", "grdwrite2.m");

			cmd  = "\nmatlab -nodesktop -nosplash -r \"noiseremoval(2,0.3,3,'" + east_grd_path + "','" + north_grd_path + "'); exit;\"\n";
			subprocess.call(cmd, shell=True);

			os.remove("noiseremoval.m");
			os.remove("remloners.m");
			os.remove("remnoise.m");
			os.remove("grdread2.m");
			os.remove("grdwrite2.m");
			
			cmd  = "\ngrdmath " + east_filt_path + " " + rock_grd_path + " OR = " + east_rock_path + "\n";
			cmd += "\ngrdmath " + north_filt_path + " " + rock_grd_path + " OR = " + north_rock_path + "\n";
			subprocess.call(cmd, shell=True);

			os.remove(east_filt_path);
			os.remove(north_filt_path);

			from removeTrendNoOutlines import *;

			removeTrendNoOutlines(east_grd_path, east_rock_path, "-2", "2");
			removeTrendNoOutlines(north_grd_path, north_rock_path, "-2", "2");

			os.remove(east_rock_path);
			os.remove(north_rock_path);

			cmd = "\ngrdmath " + east_rr_path + " " + north_rr_path + " HYPOT --IO_NC4_CHUNK_SIZE=c = " + mag_rr_path + "\n";
			subprocess.call(cmd, shell=True);

		else:
			print("\n***** \"" + east_rr_path + "\" already exists, assuming results already ramp-removed...\n");

		mag_rr_ps_path = pair_path + "/" + mag_name + "_rr.ps";

		cmd  = "\nmakecpt -Chaxby -T0/" + VEL_MAX + "/0.01 --COLOR_BACKGROUND=white --COLOR_NAN=white --COLOR_FOREGROUND=white > " + pair_path + "/mag.cpt\n";
                cmd += "\ngrdimage " + mag_rr_path + " " + J + " " + R + " -C" + pair_path + "/mag.cpt -P -K > " + mag_rr_ps_path + "\n";
		cmd += "\npsxy " + ICE + " " + J + " " + R + " -W1p,black -O -K >> " + mag_rr_ps_path + "\n";
		cmd += "\npsxy " + ROCK + " " + J + " " + R + " -W1p,black -O -K >> " + mag_rr_ps_path + "\n";
		cmd += "\npsbasemap " + geoJ + " " + geoR + " -Bf1a1g1:\"Longitude\":/a0.5g0.5:\"\"::,::.\"\":WeSn --MAP_FRAME_TYPE=inside --FORMAT_GEO_MAP=ddd:mmF --FONT_ANNOT_PRIMARY=12p,1,black --MAP_GRID_PEN_PRIMARY=0.25p,100/100/100,- -O -K >> " + mag_rr_ps_path + "\n";
		cmd += "\npsbasemap " + geoJ + " " + geoR + " -Lfx3c/2c/60.5/40k+jr+u+p0.5,black+gwhite --FONT_ANNOT_PRIMARY=10p,1,black --FONT_LABEL=10p,1,black -O -K >> " + mag_rr_ps_path + "\n";
		cmd += "\npsscale -D3c/4c/3c/0.1c -C" + pair_path + "/mag.cpt -B1:\"Speed\":/:\"m day@+-1@+\": --FONT_ANNOT_PRIMARY=10p,1,black --FONT_LABEL=10p,1,black -O >> " + mag_rr_ps_path + "\n";
		cmd += "\nps2raster -A -Tf " + mag_rr_ps_path + "\n";
		subprocess.call(cmd, shell=True);

		os.remove(mag_rr_ps_path);

		east_filt_path  = east_rr_path[ : east_rr_path.rfind(".")] + "_filt.grd";
		north_filt_path = north_rr_path[ : north_rr_path.rfind(".")] + "_filt.grd";
		mag_filt_path   = mag_rr_path[ : mag_rr_path.rfind(".")] + "_filt.grd";

		if not os.path.exists(east_filt_path):

			print("\n***** Filtering results, creating \"" + east_filt_path + "\" and \"" + north_filt_path + "\"...\n");

			if not os.path.exists("noiseremoval.m"):
				os.symlink(M_SCRIPTS_DIR + "/noiseremoval.m", "noiseremoval.m");
				os.symlink(M_SCRIPTS_DIR + "/remloners.m", "remloners.m");
				os.symlink(M_SCRIPTS_DIR + "/remnoise.m", "remnoise.m");
				os.symlink(M_SCRIPTS_DIR + "/grdread2.m", "grdread2.m");
				os.symlink(M_SCRIPTS_DIR + "/grdwrite2.m", "grdwrite2.m");

			cmd  = "\nmatlab -nodesktop -nosplash -r \"noiseremoval(" + \
			       VEL_MAX + "," + TOL + "," + NUMDIF + ",'" + east_rr_path + "','" + north_rr_path + "'); exit;\"\n";
			cmd += "\ngrdmath " + east_filt_path + " " + north_filt_path + " HYPOT --IO_NC4_CHUNK_SIZE=c = " + mag_filt_path + "\n";
			subprocess.call(cmd, shell=True);

			os.remove("noiseremoval.m");
			os.remove("remloners.m");
			os.remove("remnoise.m");
			os.remove("grdread2.m");
			os.remove("grdwrite2.m");

		else:
			print("\n***** \"" + east_filt_path + "\" already exists, assuming results already filtered...\n");

		mag_filt_ps_path = pair_path + "/" + mag_name + "_rr_filt.ps";

		cmd  = "\nmakecpt -Chaxby -T0/" + VEL_MAX + "/0.01 --COLOR_BACKGROUND=white --COLOR_NAN=white --COLOR_FOREGROUND=white > " + pair_path + "/mag.cpt\n";
                cmd += "\ngrdimage " + mag_filt_path + " " + J + " " + R + " -C" + pair_path + "/mag.cpt -P -K > " + mag_filt_ps_path + "\n";
		cmd += "\npsxy " + ICE + " " + J + " " + R + " -W1p,black -O -K >> " + mag_filt_ps_path + "\n";
		cmd += "\npsxy " + ROCK + " " + J + " " + R + " -W1p,black -O -K >> " + mag_filt_ps_path + "\n";
		cmd += "\npsbasemap " + geoJ + " " + geoR + " -Bf1a1g1:\"Longitude\":/a0.5g0.5:\"\"::,::.\"\":WeSn --MAP_FRAME_TYPE=inside --FORMAT_GEO_MAP=ddd:mmF --FONT_ANNOT_PRIMARY=12p,1,black --MAP_GRID_PEN_PRIMARY=0.25p,100/100/100,- -O -K >> " + mag_filt_ps_path + "\n";
		cmd += "\npsbasemap " + geoJ + " " + geoR + " -Lfx3c/2c/60.5/40k+jr+u+p0.5,black+gwhite --FONT_ANNOT_PRIMARY=10p,1,black --FONT_LABEL=10p,1,black -O -K >> " + mag_filt_ps_path + "\n";
		cmd += "\npsscale -D3c/4c/3c/0.1c -C" + pair_path + "/mag.cpt -B1:\"Speed\":/:\"m day@+-1@+\": --FONT_ANNOT_PRIMARY=10p,1,black --FONT_LABEL=10p,1,black -O >> " + mag_filt_ps_path + "\n";
		cmd += "\nps2raster -A -Tf " + mag_filt_ps_path + "\n";
		subprocess.call(cmd, shell=True);

		os.remove(mag_filt_ps_path);

		try: DEM
		except NameError:
			print("\n***** WARNING: DEM not set in \"" + params_path + "\", skipping motion-elevation correction...\n");
			continue;

		if not os.path.exists(DEM):
			print("\n***** ERROR: DEM \"" + DEM + "\" not found, skipping motion-elevation correction...\n");
			continue;

		east_filt_txt_path  = east_filt_path[ : east_filt_path.rfind(".")] + ".txt";
		north_filt_txt_path = north_filt_path[ : north_filt_path.rfind(".")] + ".txt";

		if not os.path.exists(east_filt_txt_path):
			print("***** Creating \"" + east_filt_txt_path + "\" and \"" + north_filt_txt_path + "\" from filtered grids...\n");
			cmd  = "\ngrd2xyz " + east_filt_path + " | gawk '$0 !~ /a/ && $3 != 0 {print $0}' > " + east_filt_txt_path + "\n";
			cmd += "\ngrd2xyz " + north_filt_path + " | gawk '$0 !~ /a/ && $3 != 0 {print $0}' > " + north_filt_txt_path + "\n";
			subprocess.call(cmd, shell=True);

		else:
			print("***** \"" + east_filt_txt_path + "\" already exists, assuming current E-W and N-S filtered offsets already converted to ASCII files...\n");

		east_corr_path  = east_filt_path[ : east_filt_path.rfind(".")] + "_corrected.grd";
		north_corr_path = north_filt_path[ : north_filt_path.rfind(".")] + "_corrected.grd";
		mag_corr_path   = mag_filt_path[ : mag_filt_path.rfind(".")] + "_corrected.grd";

		if os.path.exists(east_corr_path):
			print("***** \"" + east_corr_path + "\" already exists, assuming motion-elevation correction performed on most recent results...\n");

		else:
			motionElevCorrection(east_filt_path, DEM, ICE, ROCK, str(int(RESOLUTION) * int(STEP)), SNR_CUTOFF);
			motionElevCorrection(north_filt_path, DEM, ICE, ROCK, str(int(RESOLUTION) * int(STEP)), SNR_CUTOFF);
			cmd = "\ngrdmath " + east_corr_path + " " + north_corr_path + " HYPOT --IO_NC4_CHUNK_SIZE=c = " + mag_corr_path + "\n";
			subprocess.call(cmd, shell=True);

		mag_corr_ps_path = pair_path + "/" + mag_name + "_filt_corrected.ps";

		cmd  = "\nmakecpt -Chaxby -T0/" + VEL_MAX + "/0.01 --COLOR_BACKGROUND=white --COLOR_NAN=white --COLOR_FOREGROUND=white > " + pair_path + "/mag.cpt\n";
                cmd += "\ngrdimage " + mag_corr_path + " " + J + " " + R + " -C" + pair_path + "/mag.cpt -Q -P -K > " + mag_corr_ps_path + "\n";
		cmd += "\npsxy " + ICE + " " + J + " " + R + " -W1p,black -O -K >> " + mag_corr_ps_path + "\n";
		cmd += "\npsxy " + ROCK + " " + J + " " + R + " -W1p,black -O -K >> " + mag_corr_ps_path + "\n";
		cmd += "\npsbasemap " + geoJ + " " + geoR + " -Bf1a1g1:\"Longitude\":/a0.5g0.5:\"\"::,::.\"\":WeSn --MAP_FRAME_TYPE=inside --FORMAT_GEO_MAP=ddd:mmF --FONT_ANNOT_PRIMARY=12p,1,black --MAP_GRID_PEN_PRIMARY=0.25p,100/100/100,- -O -K >> " + mag_corr_ps_path + "\n";
		cmd += "\npsbasemap " + geoJ + " " + geoR + " -Lfx3c/2c/60.5/40k+jr+u+p0.5,black+gwhite --FONT_ANNOT_PRIMARY=10p,1,black --FONT_LABEL=10p,1,black -O -K >> " + mag_corr_ps_path + "\n";
		cmd += "\npsscale -D3c/4c/3c/0.1c -C" + pair_path + "/mag.cpt -B1:\"Speed\":/:\"m day@+-1@+\": --FONT_ANNOT_PRIMARY=10p,1,black --FONT_LABEL=10p,1,black -O >> " + mag_corr_ps_path + "\n";
		cmd += "\nps2raster -A -Tf " + mag_corr_ps_path + "\n";
                subprocess.call(cmd, shell=True);

		os.remove(mag_corr_ps_path);
		
	return;

		
"""	
	if step == "setup":
	
		cmd="\nls *_" + BAND + ".TIF\n";
		pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		images=pipe.read().split();
		pipe.close();
	
		for image in images:
	
			cmd="\ngdalinfo "+image+"\n";
			pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
			info=pipe.read();
			pipe.close();
	
			if info.find("40N") > -1:
				cmd="\ngdalwarp -of GTiff -t_srs '+proj=utm +zone=41 +datum=WGS84 +north' -tr " + RESOLUTION + " " + RESOLUTION + " -r cubic "+image+" "+image[:image.rfind(".")]+"_zone41.TIF\n";
				subprocess.call(cmd,shell=True);
	
	
		elif step == "cut":
	
		cmd="\nls *_" + BAND + "*.TIF\n";
		pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		images=pipe.read().split();
		pipe.close();
	
		for image in images:
	
			cmd="\n/home/akm26/Downloads/gdal-1.8.0/apps/gdal_translate -of ENVI -ot Float32 -projwin 577000 8494000 595000 8484000 "+image+" "+image[:image.rfind(".")]+"_Ino.img\n";
			subprocess.call(cmd,shell=True);
	
	
	elif step == "setup1":
	
		infile=open(PAIRS,"r");
	
		for line in infile:
	
			elements = line.split();
			
			limage = elements[0];
			eimage = elements[1];
	
			cmd="\nfind /home/akm26/Documents/Russia/NovZ/Landsat/ -name \""+limage+"*TIF\"\n";
			pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
			limage=pipe.read().split()[0];
			pipe.close(); 
	
			cmd="\nfind /home/akm26/Documents/Russia/NovZ/Landsat/ -name \""+eimage+"*TIF\"\n";
			pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
			eimage=pipe.read().split()[0];
			pipe.close();
	
			pair = line.strip().replace(" ","_").replace("_" + BAND,"").replace(".TIF","").replace("_zone41","");
			pair_dir = PAIRS_DIR + "/" + pair;
	
			cmd = "\ngdalinfo " + limage + "\n";
			pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
			limage_info = pipe.read().strip();
			pipe.close();
	
			cmd = "\ngdalinfo " + eimage + "\n";
			pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
			eimage_info = pipe.read().strip();
			pipe.close();
	
			limage_utm = limage_info[re.search("UTM zone\s+",limage_info).end(0):re.search("UTM zone\s+\d+",limage_info).end(0)];
			limage_rez = limage_info[re.search("Pixel Size = \(",limage_info).end(0):re.search("Pixel Size = \(\d+",limage_info).end(0)]; 
			eimage_utm = eimage_info[re.search("UTM zone\s+",eimage_info).end(0):re.search("UTM zone\s+\d+",eimage_info).end(0)];
			eimage_rez = eimage_info[re.search("Pixel Size = \(",eimage_info).end(0):re.search("Pixel Size = \(\d+",eimage_info).end(0)]; 
	
			coreg_limage = pair_dir + "/coreg_" + limage[limage.rfind("/")+1:limage.rfind(".")] + ".img";
	
			#if not os.path.exists(pair_dir):
	
			#	cmd = "\nmkdir " + PAIRS_DIR + "/" + pair + "\n";
	
			arop_inp_path = pair_dir + "/" + pair + ".inp";
	
			if not os.path.exists(arop_inp_path):
				
				arop_inp = aropInput.AropInput();
				
				arop_inp.setBasePixelSize(eimage_rez);
				arop_inp.setBaseLandsat(eimage);
				arop_inp.setUTMZone(eimage_utm);
				arop_inp.setBaseSatellite(SATELLITE);
	
				arop_inp.setWarpFileType("GEOTIFF");
				arop_inp.setWarpNSample("-1");
				arop_inp.setWarpNLine("-1");
				arop_inp.setWarpUpperLeftCorner("-1, -1");
				arop_inp.setWarpSatellitePointingAngle("0");
				arop_inp.setWarpOrientationAngle("0");
				arop_inp.setWarpLandsatBand(limage);
				arop_inp.setWarpBaseMatchBand(limage);
			
				arop_inp.setWarpPixelSize(limage_rez);
				arop_inp.setWarpSatellite(SATELLITE);
				arop_inp.setWarpUTMZone(limage_utm);
	
				# Set output image parameters
				arop_inp.setOutPixelSize(eimage_rez);
				arop_inp.setResampleMethod("CC");
				arop_inp.setOutLandsatBand(coreg_limage);
				arop_inp.setOutBaseMatchBand(coreg_limage);
	
				#print(arop_inp_path);
				arop_inp.write_arop(arop_inp_path);
	
	
	elif step == "ampcor":
	
		infile = open(PAIRS,"r");
	
		for line in infile:
	
			elements=line.split();
			limage=elements[0];
			eimage=elements[1];
			cmd="\nfind /home/akm26/Documents/Russia/NovZ/Landsat/ -name \""+limage+"*TIF*ghp_stretch\"\n";
			pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
			limage=pipe.read().split()[0];
			pipe.close(); 
			cmd="\nfind /home/akm26/Documents/Russia/NovZ/Landsat/ -name \""+eimage+"*TIF*ghp_stretch\"\n";
			pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
			eimage=pipe.read().split()[0];
			pipe.close();
			pair=line.replace(" ","_").replace("_" + BAND,"").replace(".TIF","").replace("_zone41","");
	
			if not os.path.exists("/home/akm26/Documents/Russia/NovZ/Landsat/pairs/"+pair):
	
				cmd="\nmkdir /home/akm26/Documents/Russia/NovZ/Landsat/pairs/"+pair+"\n";
				cmd+="\ncp -p /home/akm26/Documents/Russia/NovZ/Landsat/pairs/*.py /home/akm26/Documents/Russia/NovZ/Landsat/pairs/"+pair+"\n";
				cmd+="\ncd /home/akm26/Documents/Russia/NovZ/Landsat/pairs/"+pair+"\n";
				cmd+="\npython split_ampcor.py "+eimage+" "+limage+" 8\n";
				cmd+="\ncd /home/akm26/Documents/Russia/NovZ/Landsat/pairs\n";
				subprocess.call(cmd,shell=True);
				
				outfile=open("/home/akm26/Documents/Russia/NovZ/Landsat/pairs/"+pair.strip()+"/run_amp.cmd","w");
				outfile.write("ampcor ampcor_1.in rdf > ampcor_1.out &\n");
				outfile.write("ampcor ampcor_2.in rdf > ampcor_2.out &\n");
				outfile.write("ampcor ampcor_3.in rdf > ampcor_3.out &\n");
				outfile.write("ampcor ampcor_4.in rdf > ampcor_4.out &\n");
				outfile.write("ampcor ampcor_5.in rdf > ampcor_5.out &\n");
				outfile.write("ampcor ampcor_6.in rdf > ampcor_6.out &\n");
				outfile.write("ampcor ampcor_7.in rdf > ampcor_7.out &\n");
				outfile.write("ampcor ampcor_8.in rdf > ampcor_8.out &\n");
				outfile.close();
	
		infile.close();
	
		exit();
	
	
	elif step == "results":
	
		pairs = {};
		pair_images = {};
		images = {};
	
		infile=open(PAIRS,"r");
	
		for line in infile:
	
			elements = line.split();
			image1 = elements[0];
			image1 = image1[image1.rfind("/") + 1 :];
			image1 = image1[: image1.find("_")];
			image2 = elements[1];
			image2 = image2[image2.rfind("/") + 1 :];
			image2 = image2[: image2.find("_")];
	
			if image1 not in pair_images:
				pair_images[image1] = image1;
	
			if image2 not in pair_images:
				pair_images[image2] = image2;
	
			pair = image1 + "_" + image2;
			
			if pair not in pairs:
				pairs[pair] = pair;
	
		infile.close();
	
		contents = os.listdir(IMAGE_DIR);
	
		for item in contents:
	
			item = item.strip(); 
	
			if not re.search(BAND + ".TIF$",item) and not re.search(BAND + "_zone" + UTM_ZONE + ".TIF$",item):
				continue;
	
			label = item[item.rfind("/") + 1 :]
			label = label[: label.find("_")];
	
			if label in pair_images:
				images[label] = IMAGE_DIR + "/" + item;
	
	
		for pair in pairs:
	
			print("\nCurrent pair is " + pair + "\n");
	
			elements = pair.split("_");
			limage = elements[0];
			eimage = elements[1];
			limage_path = images[limage];
			eimage_path = images[eimage];
	
			later_date = "";
	
			limage_metfile = open(METADATA_DIR + "/" + limage + "_MTL.txt","r"); 
	
			for line in limage_metfile:
	
				if line.find("DATE_ACQUIRED") > -1:
					elements = line.split();
					date = elements[2];
					later_date = later_date + date[0:4] + date[5:7] + date[8:];
	
				elif line.find("SCENE_CENTER_TIME") > -1:
					elements = line.split();
					time = elements[2];
					seconds = str(int(time[6:8])+int(round(float(time[8:11]))));
	
					if len(seconds) < 2:
						seconds = "0" + seconds;
	
					later_date = later_date + time[0:2] + time[3:5] + seconds;
	
			limage_metfile.close();
	
			earlier_date = "";
			
			eimage_metfile=open(METADATA_DIR + "/" + eimage + "_MTL.txt","r");
	
			for line in eimage_metfile:
	
				if line.find("DATE_ACQUIRED") > -1:
					elements = line.split();
					date = elements[2];
					earlier_date = earlier_date + date[0:4] + date[5:7] + date[8:];
	
				elif line.find("SCENE_CENTER_TIME") > -1:
					elements = line.split();
					time = elements[2];
					seconds = str(int(time[6:8])+int(round(float(time[8:11]))));
	
					if len(seconds) < 2:
						seconds = "0" + seconds;
	
					earlier_date = earlier_date + time[0:2] + time[3:5] + seconds;
	
			eimage_metfile.close();
	
			pair_label = later_date + "_" + earlier_date;
	
			pair_dir = PAIRS_DIR + "/" + pair_label;
	
			print(pair_dir);
	
			if not os.path.exists(pair_dir + "/ampcor_1.off"):
				continue;
	
			cat_cmd = "\ncat ";
			contents = os.listdir(pair_dir);
	
			for item in contents:
	
				if re.search("ampcor_\d\.off",item):
					cat_cmd += pair_dir + "/" + item.strip() + " ";
	
			cat_cmd += "> " + pair_dir + "/ampcor.off\n";
			#subprocess.call(cat_cmd,shell=True);
	
			rwin = "";
			awin = "";
			input_res = "";
			input_width = "";
			input_length = "";
			utm_z = "";
			ns = "";
			ul_lat = "";
			ul_lon = "";
			
			infile = open(pair_dir + "/ampcor_1.in");
	
			for line in infile:
	
				if line.find("Reference Image Input File") > -1:
	
					elements = line.split();
	
					hdr_path = elements[len(elements) - 1] + ".hdr";
	
					if hdr_path.find("/") < 0 or hdr_path.find("./") > -1:
						hdr_path = pair_dir + "/" + hdr_path;
	
					if not os.path.exists(hdr_path):
						hdr_path = hdr_path[ : hdr_path.find(".")] + ".hdr";
	
					hdr_file = open(hdr_path, "r");
	
					for hdr_line in hdr_file:
	
						if hdr_line.find("samples") > -1:
							hdr_elements  = hdr_line.split();
							input_width = hdr_elements[len(hdr_elements)-1].strip();
	
						elif hdr_line.find("lines") > -1:
							hdr_elements  = hdr_line.split();
							input_length = hdr_elements[len(hdr_elements)-1].strip();
	
						elif hdr_line.find("map") > -1:
							print(hdr_line);
	
							hdr_elements = hdr_line.split();
							ul_long = hdr_elements[6].strip().replace(",","");
							ul_lat = hdr_elements[7].strip().replace(",","");
							input_res = str(int(float(hdr_elements[8].strip().replace(",",""))));
							utm_z = hdr_elements[10].strip().replace(",","");
							ns = hdr_elements[11].strip().replace(",","");
	
					hdr_file.close();
	
				elif line.find("Start, End and Skip Lines in Reference Image") > -1:
					elements = line.split();
					awin = elements[len(elements) - 1].strip();
	
				elif line.find("Start, End and Skip Samples in Reference Image") > -1:
					elements = line.split();
					rwin = elements[len(elements) - 1].strip();
	
			infile.close();
	
			if not os.path.exists(pair_dir + "/" + pair_label + "_eastxyz.txt"):
				getxyzs(pair_dir, rwin, awin, "1", input_res, input_width, input_length, ul_long, ul_lat, pair_label);
	
			later_date_str	 = later_date[0:4] + "-" + later_date[4:6] + "-" + later_date[6:8] + " " + later_date[8:10] + ":" + later_date[10:12] + ":" + later_date[12:14];
			earlier_date_str = earlier_date[0:4] + "-" + earlier_date[4:6] + "-" + earlier_date[6:8] + " " + earlier_date[8:10] + ":" + earlier_date[10:12] + ":" + earlier_date[12:14];
	
			cmd="\ndate +\"%s\" -d \"" + later_date_str + "\"\n";
			pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
			later_seconds = pipe.read().strip();
			pipe.close();
	
			cmd="\ndate +\"%s\" -d \"" + earlier_date_str + "\"";
			pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
			earlier_seconds = pipe.read().strip();
			pipe.close();
	
			day_diff=abs(float(later_seconds)/(60*60*24) - float(earlier_seconds)/(60*60*24));
			mperday_factor = str(day_diff * 100.0);
	
			cmd="\nminmax -C " + pair_dir + "/" + pair_label + "_northxyz.txt\n";
			pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
			bounds = pipe.read().split();
			pipe.close();
	
			bounds	= bounds[0:4];
			min_x	= bounds[0];
			max_x	= bounds[1];
			min_y	= bounds[2];
			max_y	= bounds[3];
			R	= "-R" + min_x + "/" + min_y + "/" + max_x + "/" + max_y + "r";
	
			n_grd = pair_dir + "/" + pair_label + "_northxyz.grd";
			e_grd = pair_dir + "/" + pair_label + "_eastxyz.grd";
	
			if not os.path.exists(n_grd):
				cmd = "";
				cmd += "\ngawk '$4 !~ /a/ {print $1\" \"$2\" \"$4}' " + pair_dir + "/" + pair_label + "_northxyz.txt | xyz2grd -I" + str(int(input_res) * int(rwin)) + "= -G" + pair_dir + "/" + pair_label + "_snr.grd " + R + "\n"; 
				cmd += "\nxyz2grd " + pair_dir + "/" + pair_label + "_eastxyz.txt -I120= -G" + pair_dir + "/" + pair_label + "_eastxyz.grd " + R + "\n";
				cmd += "\nxyz2grd " + pair_dir + "/" + pair_label + "_northxyz.txt -I120= -G" + pair_dir + "/" + pair_label + "_northxyz.grd " + R + "\n";
				cmd += "\ngrdmath " + pair_dir + "/" + pair_label + "_eastxyz.grd " + mperday_factor + " DIV = " + pair_dir + "/" + pair_label + "_eastxyz.grd\n";
				cmd += "\ngrdmath " + pair_dir + "/" + pair_label + "_northxyz.grd " + mperday_factor + " DIV = " + pair_dir + "/" + pair_label + "_northxyz.grd\n";
				subprocess.call(cmd,shell=True);
	
			n_corrected_grd	= pair_dir + "/" + pair_label + "_northxyz_corrected.grd";
			e_corrected_grd	= pair_dir + "/" + pair_label + "_eastxyz_corrected.grd";
	
			if not os.path.exists(n_corrected_grd):
				motionElevCorrection(n_grd, DEM_GRD, ICE, ROCK, SNR_CUTOFF);
				motionElevCorrection(e_grd, DEM_GRD, ICE, ROCK, SNR_CUTOFF);
	
			mag_grd		= pair_dir + "/" + pair_label + "_magnitude_corrected.grd";
			ratio		= "1000000";
			cscale		= "3";
	
			print("\nCreating magnitude grid and image for " + pair_dir + " ...\n");
			imageAmpResults(pair_dir, pair_label, n_corrected_grd, e_corrected_grd, bounds[0], bounds[1], bounds[2], bounds[3], ratio, cscale, utm_z + UTM_LETTER, IMAGE_DIR, ICE, ROCK);

	"""
	
	
	
if __name__ == "__main__":

	import os;
	import sys;

	assert len(sys.argv) > 1, "\n***** ERROR: asterPX.py requires 1 argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: \"" + sys.argv[1] + "\" not found, exiting...\n";

	asterPX(sys.argv[1]);

	exit();

exit();
