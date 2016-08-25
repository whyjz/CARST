#!/usr/bin/python


# organize_landsat.py
# Author: Andrew K. Melkonian
# All rights reserved


# Description: 
# ************
# Finds Landsat *.TIF, *MTL.txt and *.tar* files, sorts by path and row, then places into "Images", "Metadata" and "ARCHIVE" folders for corresponding path and row


# Usage:
# ******
# python organize_landsat.py /dir/with/landsat /dir/to/put/in



def organize_landsat(match_str, input_path, output_path):

	import os;
	import re;

	assert os.path.exists(input_path), "\n***** ERROR: " + input_path  + " does not exist\n";
	assert os.path.exists(output_path), "\n***** ERROR: " + output_path + " does not exist\n";

	for root, dirnames, filenames in os.walk(input_path):

		for filename in filenames:

			if re.search(match_str, filename):

				path = filename[3:6];
				row  = filename[6:9];

				pathrow_dir = output_path + "/Path" + path + "_Row" + row;

				if not os.path.exists(pathrow_dir):
					os.mkdir(pathrow_dir);

				if not os.path.exists(pathrow_dir + "/Images"):
					os.mkdir(pathrow_dir + "/Images");

				if not os.path.exists(pathrow_dir + "/ARCHIVE"):
					os.mkdir(pathrow_dir + "/ARCHIVE");

				if not os.path.exists(pathrow_dir + "/Metadata"):
					os.mkdir(pathrow_dir + "/Metadata");

				output_file_path = "";

				if re.search("\.tif", filename.lower()):
					output_file_path = pathrow_dir + "/Images/" + filename;

				if re.search("mtl\.txt", filename.lower()):
					output_file_path = pathrow_dir + "/Metadata/" + filename;

				if re.search("\.tar", filename.lower()) or re.search("\.tar.gz", filename.lower()):
					output_file_path = pathrow_dir + "/ARCHIVE/" + filename;

				if not os.path.exists(output_file_path):
					print(root + "/" + filename);
					print(output_file_path);
					os.rename(root + "/" + filename, output_file_path);
					
			

	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 3, "\n***** ERROR: organize_landsat.py requires 3 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";
	
	organize_landsat(sys.argv[1], sys.argv[2], sys.argv[3]);

	exit();

