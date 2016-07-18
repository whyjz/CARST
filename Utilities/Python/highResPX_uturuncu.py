#!/usr/bin/python


# hiResPX.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# USAGE
# *****
# 	python highResPX.py /path/to/params.txt


# DEPENDENCIES
# ************

# The following software and scripts are REQUIRED by this script:

# REQUIRES the following software packages to be installed, with paths to executables in the PATH environment variable:
#	Python WITH numpy, scipy
#	GDAL
#	GMT
#	ROI_PAC
#	sed
#	gawk

# REQUIRES the following scripts in the SAME directory as highResPX.py:
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

# Motion-elevation correction requires the following script to be in the SAME directory as highResPX.py:
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
METADATA_DIR	= /home/user/Landsat8/Images
PAIRS_DIR	= /home/user/Landsat8/Pairs
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
PAIRS		= /home/user/Landsat8/Pairs/landsat8_pairs.txt

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
#	Resolution of the input imagery in meters (e.g. "15" for band 8 of Landsat 7 and 8).

# SNR_CUTOFF	
#	Signal-to-noise ratio threshold, *_filt.grd velocity grids created by the script during post-processing will be clipped so that all pixels 
#	with an SNR below this threshold are masked out.

# DEM_GRD
#	Path to NetCDF grid file of elevations projected in UTM_ZONE.
#	MAKE SURE this covers the maximum extent of the imagery if you plan on using motion-elevation corrected results.
#	Motion-elevation correction cannot be performed where the elevation is unknown.
 
# PREFILTER     
#	Set to True if you are using IDLDE to perform gaussian high-pass filtering using the gausshighpassgausstretch.pro script.
#	If you set this to "True" DO NOT modify the file names created by the *.pro script, let highResPX.py deal with it.
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



#def highResPX(REF_PATH, SEARCH_PATH, REF_DEM_PATH, SEARCH_DEM_PATH, PAIRS_DIR, RESOLUTION, UTM_ZONE, BOUNDS_PATH, PROCESSORS, REF_X, REF_Y, SEARCH_X, SEARCH_Y, STEP):
def highResPX(params_path):

	import os;
	import re;
	import subprocess;

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

	assert os.path.exists(REF_PATH), "\n***** ERROR: \"" + REF_PATH + "\" not found, exiting...\n";
	assert os.path.exists(SEARCH_PATH), "\n***** ERROR: \"" + SEARCH_PATH + "\" not found, exiting...\n";
	assert os.path.exists(REF_DEM_PATH), "\n***** ERROR: \"" + REF_DEM_PATH + "\" not found, exiting...\n";
	assert os.path.exists(SEARCH_DEM_PATH), "\n***** ERROR: \"" + SEARCH_DEM_PATH + "\" not found, exiting...\n";
	assert os.path.exists(PAIRS_DIR), "\n***** ERROR: \"" + PAIRS_DIR + "\" not found, exiting...\n";
	assert os.path.exists(BOUNDS_PATH), "\n***** ERROR: " + BOUNDS_PATH + " not found, exiting...\n";

	NTF = False;

	if re.search("\.ntf$", REF_PATH.lower()):
		NTF = True;

	cmd = "\ngmtset FORMAT_GEO_OUT=+D\n";
	subprocess.call(cmd,shell=True);

	cmd  = "\n/home/akm26/Public/gdal-1.11.0/apps/gdalinfo " + REF_PATH + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

#	ref_ulx = ref_uly = ref_urx = ref_ury = ref_llx = ref_lly = ref_lrx = ref_lry = "";
#	search_ulx = search_uly = search_urx = search_ury = search_llx = search_lly = search_lrx = search_lry = "";
	 
#	Input is raw ntf
	if NTF:
		ref_ul = info[re.search("UpperLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("UpperLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];

#	Input is orthorectified GTiff or ENVI
	else:
		ref_ul = info[re.search("Upper\s*Left\s*[A-Za-z]*=*\s*\(\s*",info).end(0) : re.search("Upper\s*Left\s*[A-Za-z]*=*\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	ref_ulx, ref_uly = ref_ul.split(",");

	if NTF:
		ref_ur = info[re.search("UpperRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("UpperRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];

	else:
		ref_ur = info[re.search("Upper\s*Right\s*[A-Za-z]*=*\s*\(\s*",info).end(0) : re.search("Upper\s*Right\s*[A-Za-z]*=*\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	
	ref_urx, ref_ury = ref_ur.split(",");

	if NTF:
		ref_ll = info[re.search("LowerLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("LowerLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];

	else:
		ref_ll = info[re.search("Lower\s*Left\s*[A-Za-z]*=*\s*\(\s*",info).end(0) : re.search("Lower\s*Left\s*[A-Za-z]*=*\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	ref_llx, ref_lly = ref_ll.split(",");

	if NTF:
		ref_lr = info[re.search("LowerRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("LowerRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];

	else:
		ref_lr = info[re.search("Lower\s*Right\s*[A-Za-z]*=*\s*\(\s*",info).end(0) : re.search("Lower\s*Right\s*[A-Za-z]*=*\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	ref_lrx, ref_lry = ref_lr.split(",");

#	Input is raw ntf
	if NTF:
		cmd  = "\necho \"" + ref_ulx + " " + ref_uly + "\n" + ref_urx + " " + ref_ury + "\n" + ref_llx + " " + ref_lly + "\n" + ref_lrx + " " + ref_lry + "\" | mapproject -Ju" + UTM_ZONE + "X/1:1 -F -C\n"; 
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		ref_ulx, ref_uly, ref_urx, ref_ury, ref_llx, ref_lly, ref_lrx, ref_lry = pipe.read().split(); 
		pipe.close();

#	Input is raw ntf
	if NTF:
		ref_ulx = str(min(float(ref_ulx), float(ref_urx), float(ref_llx), float(ref_lrx)));
		ref_uly = str(max(float(ref_uly), float(ref_ury), float(ref_lly), float(ref_lry)));
		ref_lrx = str(max(float(ref_ulx), float(ref_urx), float(ref_llx), float(ref_lrx)));
		ref_lry = str(min(float(ref_uly), float(ref_ury), float(ref_lly), float(ref_lry)));

	cmd  = "\n/home/akm26/Public/gdal-1.11.0/apps/gdalinfo " + SEARCH_PATH + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

#	Input is raw ntf
	if NTF:
		search_ul = info[re.search("UpperLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("UpperLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];

#	Input is orthorectified GTiff or ENVI
	else:
		search_ul = info[re.search("Upper\s*Left\s*[A-Za-z]*=*\s*\(\s*",info).end(0) : re.search("Upper\s*Left\s*[A-Za-z]*=*\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	search_ulx, search_uly = search_ul.split(",");

	if NTF:
		search_ur = info[re.search("UpperRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("UpperRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];

	else:
		search_ur = info[re.search("Upper\s*Right\s*[A-Za-z]*=*\s*\(\s*",info).end(0) : re.search("Upper\s*Right\s*[A-Za-z]*=*\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	
	search_urx, search_ury = search_ur.split(",");

	if NTF:
		search_ll = info[re.search("LowerLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("LowerLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];

	else:
		search_ll = info[re.search("Lower\s*Left\s*[A-Za-z]*=*\s*\(\s*",info).end(0) : re.search("Lower\s*Left\s*[A-Za-z]*=*\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	search_llx, search_lly = search_ll.split(",");

	if NTF:
		search_lr = info[re.search("LowerRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("LowerRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];

	else:
		search_lr = info[re.search("Lower\s*Right\s*[A-Za-z]*=*\s*\(\s*",info).end(0) : re.search("Lower\s*Right\s*[A-Za-z]*=*\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	search_lrx, search_lry = search_lr.split(",");

#	Input is raw ntf
	if NTF:
		cmd  = "\necho \"" + search_ulx + " " + search_uly + "\n" + search_urx + " " + search_ury + "\n" + search_llx + " " + search_lly + "\n" + search_lrx + " " + search_lry + "\" | mapproject -Ju" + UTM_ZONE + "X/1:1 -F -C\n"; 
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		search_ulx, search_uly, search_urx, search_ury, search_llx, search_lly, search_lrx, search_lry = pipe.read().split(); 
		pipe.close();

#	Input is raw ntf
	if NTF:
		search_ulx = str(min(float(search_ulx), float(search_urx), float(search_llx), float(search_lrx)));
		search_uly = str(max(float(search_uly), float(search_ury), float(search_lly), float(search_lry)));
		search_lrx = str(max(float(search_ulx), float(search_urx), float(search_llx), float(search_lrx)));
		search_lry = str(min(float(search_uly), float(search_ury), float(search_lly), float(search_lry)));

	bounds	   = [];
	bounds_str = "";

	infile = open(BOUNDS_PATH, "r");

	for line in infile:
		bounds_str += line.strip() + " ";

	infile.close();

	bounds = bounds_str.split();

	ul_x = bounds[0];
	ul_y = bounds[1];
	lr_x = bounds[2];
	lr_y = bounds[3];

#	ul_x = str(min([float(ref_ulx), float(search_ulx), float(ref_lrx), float(search_lrx), float(ref_urx), float(search_urx), float(ref_llx), float(search_llx), float(ul_x)]));
#	ul_y = str(max([float(ref_uly), float(search_uly), float(ref_lry), float(search_lry), float(ref_ury), float(search_ury), float(ref_lly), float(search_lly), float(ul_y)]));
#	lr_x = str(max([float(ref_ulx), float(search_ulx), float(ref_lrx), float(search_lrx), float(ref_urx), float(search_urx), float(ref_llx), float(search_llx), float(lr_x)]));
#	lr_y = str(min([float(ref_uly), float(search_uly), float(ref_lry), float(search_lry), float(ref_ury), float(search_ury), float(ref_lly), float(search_lly), float(lr_y)]));
	ul_x = str(max([float(ref_ulx), float(search_ulx), float(ul_x)]));
	ul_y = str(min([float(ref_uly), float(search_uly), float(ul_y)]));
	lr_x = str(min([float(ref_lrx), float(search_lrx), float(lr_x)]));
	lr_y = str(max([float(ref_lry), float(search_lry), float(lr_y)]));

	bounds_str = ul_x + " " + lr_y + " " + lr_x + " " + ul_y;

	months = {"JAN" : "01", "FEB" : "02", "MAR" : "03", "APR" : "04", "MAY" : "05", "JUN" : "06", "JUL" : "07", "AUG" : "08", "SEP" : "09", "OCT" : "10", "NOV" : "11", "DEC" : "12"};

	import re;

	ref_date = REF_PATH[re.search("\d\d[A-Z][A-Z][A-Z]\d\d\d\d\d\d\d\d\d", REF_PATH).start(0) : re.search("\d\d[A-Z][A-Z][A-Z]\d\d\d\d\d\d\d\d\d", REF_PATH).end(0)];

	ref_year   = "20" + ref_date[0:2];
	ref_month  = months[ref_date[2:5]];
	ref_day    = ref_date[5:7];
	ref_hour   = ref_date[7:9];
	ref_minute = ref_date[9:11];
	ref_second = str(int(round(float(ref_date[11:13] + "." + ref_date[13]))));

	if len(ref_second) < 2:
		ref_second = "0" + ref_second;

	ref_date = ref_year + ref_month + ref_day + ref_hour + ref_minute + ref_second;

	search_date = SEARCH_PATH[re.search("\d\d[A-Z][A-Z][A-Z]\d\d\d\d\d\d\d\d\d", SEARCH_PATH).start(0) : re.search("\d\d[A-Z][A-Z][A-Z]\d\d\d\d\d\d\d\d\d", SEARCH_PATH).end(0)];

	search_year   = "20" + search_date[0:2];
	search_month  = months[search_date[2:5]];
	search_day    = search_date[5:7];
	search_hour   = search_date[7:9];
	search_minute = search_date[9:11];
	search_second = str(int(round(float(search_date[11:13] + "." + search_date[13]))));

	if len(search_second) < 2:
		search_second = "0" + search_second;

	search_date = search_year + search_month + search_day + search_hour + search_minute + search_second;

	pair = search_date + "_" + ref_date;

	pair_path = PAIRS_DIR + "/" + pair;

	print(pair_path);

	if not os.path.exists(pair_path):
		os.mkdir(pair);

#	Input is ntf
	if NTF:
		ref_img_path    = pair_path + "/" + REF_PATH[REF_PATH.rfind("/") +1 : REF_PATH.rfind(".")] + ".img";
		search_img_path = pair_path + "/" + SEARCH_PATH[SEARCH_PATH.rfind("/") + 1 : SEARCH_PATH.rfind(".")] + ".img";

	else:
#	Input is orthod GTiff or ENVI
		ref_img_name	= REF_PATH[REF_PATH.rfind("/") +1 : REF_PATH.rfind(".")] + "_cut.img";
		ref_img_path    = pair_path + "/" + ref_img_name;
		search_img_name	= SEARCH_PATH[SEARCH_PATH.rfind("/") + 1 : SEARCH_PATH.rfind(".")] + "_cut.img";
		search_img_path = pair_path + "/" + search_img_name;

#	Input is ntf
	if NTF:
		if not os.path.exists(ref_img_path):
			cmd  = "\ngdalwarp -of ENVI -ot Float32 -t_srs '+proj=utm +zone=" + UTM_ZONE + " +datum=WGS84 +north' -multi -et 0 -tr " + RESOLUTION + " " + RESOLUTION + " -te " + bounds_str + " -rpc -to RPC_DEM=" + REF_DEM_PATH + " " + REF_PATH + " " + ref_img_path + "\n";
			cmd += "\ngdalwarp -of ENVI -ot Float32 -t_srs '+proj=utm +zone=" + UTM_ZONE + " +datum=WGS84 +north' -multi -et 0 -tr " + RESOLUTION + " " + RESOLUTION + " -te " + bounds_str + " -rpc -to RPC_DEM=" + SEARCH_DEM_PATH + " " + SEARCH_PATH + " " + search_img_path + "\n";
			print(cmd);
#			subprocess.call(cmd,shell=True);

		else:
			print("\n***** \"" + ref_img_path + "\" already exists, skipping orthorectification for " + pair + "...\n");

#	Input is orthod GTiff or ENVI
	else:
		if not os.path.exists(ref_img_path):
			cmd  = "\ngdal_translate -of ENVI -projwin " + ul_x + " " + ul_y + " " + lr_x + " " + lr_y + " " + REF_PATH + " " + ref_img_path + "\n";
			cmd += "\ngdal_translate -of ENVI -projwin " + ul_x + " " + ul_y + " " + lr_x + " " + lr_y + " " + SEARCH_PATH + " " + search_img_path + "\n";
			print(cmd);
#			subprocess.call(cmd,shell=True);

		else:
			print("\n***** \"" + ref_img_path + "\" already exists, skipping orthorectification for " + pair + "...\n");

	return;

	import sys;

	sys.path.append("/home/akm/Python");

	from splitAmpcor import *;

	if not os.path.exists(pair_path + "/ampcor_1.in"):
		splitAmpcor(ref_img_path, search_img_path, pair_path, PROCESSORS, RESOLUTION, REF_X, REF_Y, SEARCH_X, SEARCH_Y, STEP);

	else:
		print("\n***** \"ampcor_1.in\" already exists, skipping ampcor for " + pair + "...\n");

	outfile = open(pair_path + "/run_amp.cmd", "w");

	for i in range(1,int(PROCESSORS) + 1):
		outfile.write("\nampcor ampcor_" + str(i) + ".in rdf > ampcor_" + str(i) + ".out &\n");

	outfile.close();

	assert os.path.exists(pair_path + "/ampcor_1.off"), "\n***** ERROR: \"ampcor_1.off\" does not exist in current directory, please cd to directory with ampcor results or run ampcor for " + pair + "...\n";

	ref_hdr_path = ref_img_path.replace("img","hdr");

	if not os.path.exists(ref_hdr_path):
		ref_hdr_path = ref_hdr_path.replace(".hdr", ".img.hdr");

	assert os.path.exists(ref_hdr_path), "\n***** ERROR: \"" + ref_hdr_path + "/" + ref_hdr_path.replace(".img.hdr", ".hdr") + "\" not found...\n";

	if not os.path.exists(pair_path + "/ampcor.off"):

		amp_offs = [item for item in os.listdir(pair_path) if ".off" in item and "ampcor" in item];

		cmd = "\ncat ";

		for amp_off in amp_offs:
			cmd += pair_path + "/" + amp_off + " ";

		cmd += " > " + pair_path + "/ampcor.off\n";

		subprocess.call(cmd,shell=True);

	ref_hdr_info = "";

	infile = open(ref_hdr_path, "r");

	for line in infile:

		ref_hdr_info += line;

	infile.close();

	ref_hdr_info = ref_hdr_info.lower();

	ref_samples = ref_hdr_info[re.search("samples\s*=\s*", ref_hdr_info).end(0) : re.search("samples\s*=\s*\d+", ref_hdr_info).end(0)];
	ref_lines   = ref_hdr_info[re.search("lines\s*=\s*", ref_hdr_info).end(0) : re.search("lines\s*=\s*\d+", ref_hdr_info).end(0)];

	from getxyzs import *;	

	e_txt_path  = pair_path + "/" + pair + "_eastxyz.txt";
	n_txt_path = pair_path + "/" + pair + "_northxyz.txt";

	if not os.path.exists(e_txt_path):
		getxyzs(pair_path, STEP, STEP, "1", RESOLUTION, ref_samples, ref_lines, ul_x, ul_y, pair);

	else:
		print("\n***** \"" + e_txt_path + " already exists, skipping \"getxyzs\" for " + pair + "...\n");

	n_grd_path   = pair_path + "/" + pair + "_northxyz.grd";
	e_grd_path   = pair_path + "/" + pair + "_eastxyz.grd";
	snr_grd_path = pair_path + "/" + pair + "_snr.grd";

	vel_res = str(int(float(RESOLUTION) * float(STEP)));

	import datetime;
	from datetime import timedelta;

	if ref_second == "60":
		ref_second = str(int(ref_second) - 1);

	if search_second == "60":
		search_second = str(int(search_second) - 1);

	print(int(ref_year), int(ref_month), int(ref_day), int(ref_hour), int(ref_minute), int(ref_second));
	print(int(search_year), int(search_month), int(search_day), int(search_hour), int(search_minute), int(search_second));

	ref_time    = datetime.datetime(int(ref_year), int(ref_month), int(ref_day), int(ref_hour), int(ref_minute), int(ref_second));
	search_time = datetime.datetime(int(search_year), int(search_month), int(search_day), int(search_hour), int(search_minute), int(search_second));

	difference     = (search_time - ref_time).days + (search_time - ref_time).seconds / (60.0 * 60.0 * 24.0);
	mperday_factor = str(100.0 * difference);

	R = "-R" + ul_x + "/" + lr_y + "/" + lr_x + "/" + ul_y + "r";

	if not os.path.exists(e_grd_path):
	        cmd = "";
	        cmd += "\nawk '$4 !~ /a/ {print $1\" \"$2\" \"$4}' " + n_txt_path + " | xyz2grd -I" + vel_res + "= -G" + snr_grd_path + " " + R + "\n";
	        cmd += "\nxyz2grd " + e_txt_path + " -I" + vel_res + "= -G" + e_grd_path + " " + R + "\n";
	        cmd += "\nxyz2grd " + n_txt_path + " -I" + vel_res + "= -G" + n_grd_path + " " + R + "\n";
	        cmd += "\ngrdmath " + e_grd_path + " " + mperday_factor + " DIV = " + e_grd_path + "\n";
	        cmd += "\ngrdmath " + n_grd_path + " " + mperday_factor + " DIV = " + n_grd_path + "\n";
	        subprocess.call(cmd,shell=True);

	else:
		print("\n***** \"" + e_grd_path + " already exists, skipping making E-W and N-S grids for " + pair + "...\n");

	n_corrected_grd_path = pair_path + "/" + pair + "_northxyz_corrected.grd";
	e_corrected_grd_path = pair_path + "/" + pair + "_eastxyz_corrected.grd";

	dem_grd    = REF_DEM_PATH.replace(".tif", ".grd");
	ICE	   = "/home/mpguest/Garth/Russia/SVZ/Bounds/SevZ_glacieroutlines_ice_utm47x.gmt";
	ROCK	   = "/home/mpguest/Garth/Russia/SVZ/Bounds/SevZ_glacieroutlines_rock_utm47x.gmt";
	SNR_CUTOFF = "1";

	from motionElevCorrection import *;

	if not os.path.exists(e_corrected_grd_path):
		#print("\npython /home/akm/Python/motionElevCorrection.py " + n_grd_path + " " + dem_grd + " " + ICE + " " + ROCK + " " + vel_res + " " + SNR_CUTOFF + "\n");
	        motionElevCorrection(n_grd_path, dem_grd, ICE, ROCK, vel_res, SNR_CUTOFF);
	        motionElevCorrection(e_grd_path, dem_grd, ICE, ROCK, vel_res, SNR_CUTOFF);

	else:
		print("\n***** \"" + e_corrected_grd_path + " already exists, skipping \"motionElevCorrection\" for " + pair + "...\n");

	mag_grd_path    = pair_path + "/" + pair + "_magnitude_corrected.grd";
	ratio           = "1000000";
	cscale          = "3";

	if not os.path.exists(mag_grd_path):

		from imageAmpResults import *;

	        print("\nCreating magnitude grid and image for " + pair_path + " ...\n");

		ratio = "100000";

	        imageAmpResults(pair_path, pair, n_corrected_grd_path, e_corrected_grd_path, [bounds[0], bounds[2], bounds[3], bounds[1]], ratio, cscale, UTM_ZONE + "X", ICE, ROCK);


	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
#	assert len(sys.argv) > 12, "\n***** ERROR: highResPX.py requires 12 arguments, " + str(len(sys.argv) - 1) + " given\n";
#	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
#	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
#	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";
#	assert os.path.exists(sys.argv[4]), "\n***** ERROR: " + sys.argv[4] + " does not exist\n";
#	assert os.path.exists(sys.argv[5]), "\n***** ERROR: " + sys.argv[5] + " does not exist\n";
#	assert os.path.exists(sys.argv[8]), "\n***** ERROR: " + sys.argv[8] + " does not exist\n";
	
#	highResPX(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10], sys.argv[11], sys.argv[12]);

	assert len(sys.argv) > 1, "\n***** ERROR: highResPX.py requires one argument, " + str(len(sys.argv) - 1) + " given\n";

	highResPX(sys.argv[1]);

	exit();

