#!/usr/bin/python


# weightedRegression.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# DESCRIPTION
# ***********
# ``weightedRegression.py'' reads a 5-column ASCII text file of longitudes, latitudes, elevations, dates (in decimal years) and 
# uncertainties (same units as elevations) for individual pixels. Pixels are separated by a line containing only the greater than 
# character (">").
# The script applies a weighted linear regression on a pixel-by-pixel basis, excluding elevations that deviate by more than the upper and 
# lower thresholds provided by the user.


# USAGE
# *****
# python weightedRegression.py input_elevs.txt output_label min_year max_year upper_threshold lower_threshold reference_type


# EXAMPLE
# *******
# python weightedRegression.py input_elevs.txt glacier 1999 2015 5 30 first


# INPUTS
# ******
# input_elevs.txt: A five-column ASCII text file, the first column are longitudes, the second column latitudes, the third column elevations, 
#                  the fourth column dates (in decimal years), and the fifth column are uncertainties (same units as elevations). Single 
#		   lines containing the greater than character (">") separate different pixels/geographic locations
# output_label:    Used to name the output file, e.g., if upper_threshold and lower_threshold are 10 and output_label is "output_label" the 
#		   dh/dt will be outputted to a file named ``output_label_p10m10.txt''.
# min_year:        All elevations with dates less than ``min_year'' will be excluded, must be a number (e.g. 1999)
# max_year:        All elevations with dates greater than ``max_year'' will be excluded, must be a number (e.g., 2010)
# upper_threshold: Maximum allowed positive deviation per year from reference elevation, all elevations outside this threshold will be 
#                  excluded from the regression. Must be a number (e.g., 10).
# lower_threshold: Maximum allowed negative deviation per year from reference elevation, all elevations outside this threshold will be 
#                  excluded from the regression. Must be a number, DO NOT use a negative sign (e.g., should be 10, NOT -10).
# reference_type:  Indicates whether to use first elevation (in time), median elevation (in time) or elevation with the lowest uncertainty 
#		   as the reference elevation.


# OUTPUTS
# *******
# output_label_p10m10.txt (where upper_threshold and lower_threshold were both 10):
#                  Column  1: Longitude (floating point)
#                  Column  2: Latitude (floating point)
#                  Column  3: dh/dt (elevation change per unit time, floating point)
#                  Column  4: dh/dt uncertainty (from covariance matrix, floating point)
#                  Column  5: Intercept (floatin point)
#                  Column  6: Intercept uncertainty (floating point)
#                  Column  7: Number of elevations that were incorporated into the regression (integer)
#                  Column  8: Date of median elevation of elevations incorporated into the regression (floating point)
#                  Column  9: Elevation of median elevation of elevations incorporated into the regression (floating point)
#                  Column 10: Uncertainty of median elevation of elevations incorporated into the regression (floating point)
#                  Column 11: Date of first elevation (in time) of elevations incorporated into the regression (floating point)
#                  Column 12: Elevation of first elevation (in time) of elevations incorporated into the regression (floating point)
#                  Column 13: Uncertainty of first elevation (in time) of elevations incorporated into the regression (floating point)
#                  Column 14: Date of last elevation (in time) of elevations incorporated into the regression (floating point)
#                  Column 15: Elevation of last elevation (in time) of elevations incorporated into the regression (floating point)
#                  Column 16: Uncertainty of last elevation (in time) of elevations incorporated into the regression (floating point)
#                  Column 17: Date of reference elevation (in time) of elevations incorporated into the regression (floating point)
#                  Column 18: Elevation of reference elevation (in time) of elevations incorporated into the regression (floating point)
#                  Column 19: Uncertainty of reference elevation (in time) of elevations incorporated into the regression (floating point)
#                  Column 20: Time interval between first and last elevation incorporated into the regression

# Some Comments are added by Whyjay Zheng, Jul 21 2016.

# ``sort2DList'' sorts a 2-dimensional (row, column) list according to the values in the indicated column (must be an integer)
def sort2DList(input_list, column):

	length = len(input_list);
	width  = len(input_list[0]);
	temp   = [];
	output = [];

	for i in range(0, length):
		temp.append((float(input_list[i][column]), input_list[i]));

	temp = sorted(temp);

	for i in range(0, length):
		output.append(temp[i][1]);

	return output;


def weightedRegression(input_elevs_path, output_label, min_year, max_year, upper_threshold, lower_threshold, reference_type):

	import os;
	import subprocess;

#	Check input_elevs_path exists 
	assert os.path.exists(input_elevs_path), "\n***** ERROR: \"" + input_elevs_path + "\" not found\n";

#	Check "min_year" is a number
	try:
		val = float(min_year);
	except ValueError:
   		print("\n***** ERROR: \"" + min_year + "\" is not a valid number, input \"min_year\" must be a number\n");

#	Check "max_year" is a number
	try:
		val = float(max_year);
	except ValueError:
   		print("\n***** ERROR: \"" + max_year + "\" is not a valid number, input \"min_year\" must be a number\n");

#	Check "upper_threshold" is a number
	try:
		val = float(upper_threshold);
	except ValueError:
   		print("\n***** ERROR: \"" + upper_threshold + "\" is not a valid number, input \"min_year\" must be a number\n");

#	Check "lower_threshold" is a number
	try:
		val = float(lower_threshold);
	except ValueError:
   		print("\n***** ERROR: \"" + lower_threshold + "\" is not a valid number, input \"min_year\" must be a number\n");

#	Check "reference_type" is either "first", "median" or "lowest"
	assert (reference_type == "first" or reference_type == "median" or reference_type == "lowest"), "\n***** ERROR: \"" + \
                reference_type + "\" is not a valid value for reference_type, must be either \"first\", \"median\" or \"lowest\"\n";

#	Warn user if "max_year" is less than "min_year"
	if float(max_year) < float(min_year):
		print("\n***** WARNING: max_year \"" + max_year + "\" is less than min_year \"" + min_year + "\"...\n");

#	Set output file name according to "output_label", "upper_threshold" and "lower_threshold"
	upper_label = upper_threshold;

#	Ignore decimal digits in "upper_threshold" and "lower_threshold" when naming output file
	if upper_label.rfind(".") > 0:
		upper_label = upper_label[ : upper_label.rfind(".")];

	lower_label = lower_threshold;

	if lower_label.rfind(".") > 0:
		lower_label = lower_label[ : lower_label.rfind(".")];

#	Open output file for writing"
	outfile = open(output_label + "_p" + upper_label + "m" + lower_label + ".txt", "w");

#	Write output file header (column labels)
	outfile.write("X     Y     DHDT     DHDT_Sigma     Intercept     Intercept_Sigma     N     Median_Date     Median_Elev     Median_Sigma     First_Date     First_Elev     First_Sigma     Last_Date     Last_Elev     Last_Sigma     Ref_Date     Ref_Elev     Ref_Sigma     Date_Interval\n");

#	Import necessary libraries
	import datetime;
	import operator;
	import math;
	import scipy;
	import scipy.sparse;
	import scipy.linalg;

#	Initialize longitude ("x") and latitude ("y") variables
	x = "";
	y = "";

#	Initialize list to hold longitudes, latitudes, elevations, dates and uncertainties for input pixels
	coord = [];

#	Open input file for reading
	infile = open(input_elevs_path, "r");

#	Read input file line by line, performing regression when all data for a pixel has been read in
	for line in infile:

#		Read in normal 5-column input line containing longitude, latitude, elevation, date and uncertainty
		if not line.find(">") > -1:

			elements = line.split();

			x     = elements[0];
			y     = elements[1];
			elev  = elements[2];
			date  = elements[3];
			stdev = elements[4];

#			Add data for this elevation to the to coord list for the current pixel
			coord.append([date, elev, stdev]);

#		Found ">", indicates all data read in for current pixel, so filter and perform regression
		else:

#			Sort elevations according to time, set date, elevation and uncertainty for first elevation (in time)
			coord = sort2DList(coord, 0);

			first_date  = coord[0][0];
			first_elev  = coord[0][1];
			first_stdev = coord[0][2];

#			Sort elevations according to elevation, set date, elevation and uncertainty for median elevation
			coord = sort2DList(coord, 1);

			median_date  = coord[len(coord) / 2][0];
			median_elev  = coord[len(coord) / 2][1];
			median_stdev = coord[len(coord) / 2][2];

#			Sort elevations according to uncertainty, set date, elevation and uncertainty for lowest-uncertainty elevation
			coord = sort2DList(coord, 2);

			# min_unc = Minimum uncertainty
			min_unc_date  = coord[0][0];
			min_unc_elev  = coord[0][1];
			min_unc_stdev = coord[0][2];

#			Initialize list for elevation values that meet given criteria
			accepted_coord = [];

#			Check each elevation in "coord", only add the elevation to "accepted_coord" if it meets the given criteria
			for i in range(0, len(coord)):

				# cur = current
				cur_date  = coord[i][0];
				cur_elev  = coord[i][1];
				cur_stdev = coord[i][2];

#				If the date of the elevation currently being considered is greater than "max_year" or less than "min_year", do not add it to "accepted_coord"
				if float(cur_date) > float(max_year) or float(cur_date) < float(min_year):
					continue;

#				Initialize reference date, elevation and uncertainty to first elevation (in time), if reference_type is "median" or "first", re-assign values accordingly
				ref_date  = first_date;
				ref_elev  = first_elev;
				ref_stdev = first_stdev;

				if reference_type == "median":
					ref_date  = median_date;
					ref_elev  = median_elev;
					ref_stdev = median_stdev;

				if reference_type == "lowest":
					ref_date  = min_unc_date;
					ref_elev  = min_unc_elev;
					ref_stdev = min_unc_stdev;

#				if float(ref_stdev) == 5 and float(ref_elev) > 1000:
#					ref_elev = str(float(ref_elev) + 2.0);

#				Check that elevation being considered does not deviate too much from the reference elevation 
				cur_upper_bound = 0.0;
				cur_lower_bound = 0.0;
				interval	= 0.0;

				# If the elevation is beyond the possible value calculated from the rate range [lower_thres upper_thres],
				# the discard it
				# Note the reference DEM is always selected.
				if float(ref_date) < float(cur_date):
					interval        = float(cur_date) - float(ref_date);
					cur_upper_bound = float(ref_elev) + interval * float(upper_threshold);
					cur_lower_bound = float(ref_elev) - interval * float(lower_threshold);

				elif float(ref_date) > float(cur_date):
					interval        = float(ref_date) - float(cur_date);
					cur_upper_bound = float(ref_elev) + interval * float(lower_threshold);
					cur_lower_bound = float(ref_elev) - interval * float(upper_threshold);

				else:
					accepted_coord.append(coord[i]);

				if float(cur_elev) > cur_upper_bound or float(cur_elev) < cur_lower_bound:
					continue; 

				accepted_coord.append(coord[i]);

			coord = [];
     
			# This is the final array we want to fit with the regression model
			accepted_coord = sorted(accepted_coord);

			length = len(accepted_coord);

#			If too few (less than two) elevations met the given criteria, or the time separation between the first and last elevation is less than 
#			one year, skip this pixel
			if len(accepted_coord) < 2 or abs(float(accepted_coord[0][0]) - float(accepted_coord[length - 1][0])) < 1:
				continue;

#			Set up sparse matrices, populate with accepted input data
			xs  = scipy.sparse.lil_matrix((length, 2));
			ys  = scipy.sparse.lil_matrix((length, 1));
			ws  = scipy.sparse.lil_matrix((length, length));
			c_d = scipy.sparse.lil_matrix((length, length));

			ws.setdiag(scipy.ones(length));

			# Model: Y = m0 + m1 * X
			# W = 1/[sqrt(C_d)], where C_d is diag(variance list --> square of uncertainty list)
			# Weighted Solution: [m0 m1] = (X^T * W * X)^-1 * X^T * W * Y
			for i in range(0, length):
				xs[i,1]   = float(accepted_coord[i][0]) - float(accepted_coord[0][0]);
				ys[i,0]   = float(accepted_coord[i][1]);
				ws[i,i]   = 1.0 / math.pow(float(accepted_coord[i][2]), 1);
				c_d[i,i] = math.pow(float(accepted_coord[i][2]), 2);

			xs[0,0] = 0.0;
			xs[:,0] = 1;

#			Densify matrices to perform regression
			dense_xs  = xs.todense();
			dense_ys  = ys.todense();
			dense_ws   = ws.todense();
			dense_c_d = c_d.todense();

#			Perform regression, assign relevant information to variables
			b 	   = scipy.linalg.inv(dense_xs.transpose() * dense_ws * dense_xs) * dense_xs.transpose() * dense_ws * dense_ys;
     			intercept  = float(b[0][0]);
     			dhdt       = float(b[1][0]);
     			c_m        = scipy.linalg.inv(dense_xs.transpose() * scipy.linalg.inv(dense_c_d) * dense_xs);
     			dhdt_stdev = math.sqrt(c_m[1][1]);

#			Write regression output to output file
     			outfile.write(x + " " + y + " " + str(dhdt) + " " + str(dhdt_stdev) + " " + str(intercept) + " " + str(math.sqrt(c_m[0][0])) + " " + str(length) + " " + accepted_coord[0][0] + " " + accepted_coord[0][1] + " " + accepted_coord[0][2] + " " + accepted_coord[length/2][0] + " " + accepted_coord[length/2][1] + " " + accepted_coord[length/2][2] + " " + accepted_coord[length - 1][0] + " " + accepted_coord[length - 1][1] + " " + accepted_coord[length - 1][2] + " " + ref_date + " " + ref_elev + " " + ref_stdev + " " + str(float(accepted_coord[length - 1][0]) - float(accepted_coord[0][0])) + "\n");

	infile.close();
	outfile.close();

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	usage = "python weightedRegression.py input_elevs.txt output_label min_year max_year upper_threshold lower_threshold reference_type";

	assert len(sys.argv) > 6, "\n***** ERROR: weightedRegression.py requires at least 6 arguments, " + str(len(sys.argv) - 1) + " given. \
				   USAGE: \"" + usage + "\"\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";

	reference_type = "first";

	if len(sys.argv) > 7:
		reference_type = sys.argv[7];
	
	weightedRegression(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], reference_type);

	exit();

