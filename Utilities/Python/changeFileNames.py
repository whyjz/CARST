#!/usr/bin/python


# changeFileNames.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# Usage
# *****
# python /path/to/directory string_to_replace string_to_replace_it_with


def changeFileNames(check_dir, search_str, replace_str, rename):

	import glob;
	import os;
	import sys;

	assert os.path.exists(check_dir), "\n***** ERROR: " + check_dir + " does not exist\n";

	azo_file_list = glob.glob(check_dir + "/*" + search_str + "*");

	for item in azo_file_list:

		if item.find(search_str) > -1:

			new_path = item.replace(search_str, replace_str);	
			print(item, new_path);

			if rename:
				os.rename(item, new_path);


	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 3, "\n***** ERROR: changeFileNames.py requires 3 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";

	rename = False;

	if len(sys.argv) > 4:
		rename = True;
	
	changeFileNames(sys.argv[1], sys.argv[2], sys.argv[3], rename);

	exit();



