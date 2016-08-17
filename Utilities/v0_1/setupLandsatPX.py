#!/usr/bin/python


# setupLandsatPX.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def setupLandsatPX(params_txt_path, image_dir, pathrow):

	from dateInterval import *;
	import os;
	import re;

	assert os.path.exists(params_txt_path), "\n***** ERROR: " + params_txt_path + " does not exist\n";
	assert os.path.exists(image_dir), "\n***** ERROR: " + image_dir + " does not exist\n";

	params = {};

	infile = open(params_txt_path, "r");

	for line in infile:
		label, value = line.split("=");
		params[label.strip()] = value.strip();

	infile.close();

	contents = os.listdir(image_dir);
	images   = [item for item in contents if re.search(params["BAND"].lower() + ".tif$", item.lower()) and re.search(pathrow, item)];
	print(images);

	temp_pairs = {};

	outfile  = open("temp_pair_list.txt", "w");

	for image1 in images:

		for image2 in images:

			if image1 == image2:
				continue; 

			temp_pair1 = image1 + " " + image2;
			temp_pair2 = image2 + " " + image1;

			if temp_pair1 in temp_pairs or temp_pair2 in temp_pairs:
				continue;

			temp_pairs[temp_pair1] = temp_pair2;

			outfile.write(temp_pair1 + "\n");

	outfile.close();

	min_interval = 1;
	max_interval = 33;

	temp_pairs_intervals = dateInterval("temp_pair_list.txt");

	os.remove("temp_pair_list.txt");

	for temp_pair in temp_pairs_intervals:

		image_pair, date1, date2, interval, iso = temp_pairs_intervals[temp_pair];

		if float(interval) < min_interval or float(interval) > max_interval:
			continue;

		if date2 > date1:
			temp  = date1;
			date1 = date2;
			date2 = temp;

		image1, image2 = image_pair.split();

		if os.path.exists(params["SATELLITE"].lower() + "_" + date2 + "_to_" + date1 + ".txt"):
			continue;

		print(params["SATELLITE"].lower() + "_" + date2 + "_to_" + date1 + ".txt");

		outfile = open(params["SATELLITE"].lower() + "_" + date2 + "_to_" + date1 + ".txt", "w");

		outfile.write(image_dir + "/" + image1 + " " + image_dir + "/" + image2);

		outfile.close();

		outfile = open("params_" + params["SATELLITE"].lower() + "_" + date2 + "_to_" + date1 + "_r" + params["REF_X"] + "x" + params["REF_Y"] + "_s" + params["SEARCH_X"] + "x" + params["SEARCH_Y"] + ".txt", "w");

		for label in params:
			outfile.write(label + "    =    " + params[label] + "\n");

		outfile.write("PAIRS    =    " + params["SATELLITE"].lower() + "_" + date2 + "_to_" + date1 + ".txt");
		
		outfile.close();

		outfile = open("px_" + params["SATELLITE"].lower() + "_" + date2 + "_to_" + date1 + ".cmd", "w");

		outfile.write("python /data/akm/Python/landsatPX.py " + "params_" + params["SATELLITE"].lower() + "_" + date2 + "_to_" + date1 + "_r" + params["REF_X"] + "x" + params["REF_Y"] + "_s" + params["SEARCH_X"] + "x" + params["SEARCH_Y"] + ".txt");

		outfile.close();

	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 3, "\n***** ERROR: setupLandsatPX.py requires at least 3 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	setupLandsatPX(sys.argv[1], sys.argv[2], sys.argv[3]);

	exit();

