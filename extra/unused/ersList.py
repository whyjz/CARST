#!/usr/bin/python


# ersList.py - parses comma-separated ERS scene list from eolisa
# Author: Andrew Kenneth Melkonian
# All rights reserved


def ersList(ers_csv_path):

	assert os.path.exists(ers_csv_path), "\n***** ERROR: " + ers_csv_path + " does not exist\n";

	import re;
	
	dates = [];

	infile = open(ers_csv_path,"r");

	for line in infile:

		if re.search("\d{4}\-\d{2}\-\d{2}",line):

			date = line[re.search("\d{4}\-\d{2}\-\d{2}",line).start(0) : re.search("\d{4}\-\d{2}\-\d{2}",line).end(0)].replace("-","");
			dates.append(date);

			elements = line.split(",");

			asc_or_desc = elements[14];

			if re.search("\"D\"",line):
				print(line);

	infile.close();


	dates = sorted(dates);

	for i in range(1, len(dates)):

		if int(dates[i]) - int(dates[i-1]) == 1:
			print(dates[i] + " " + dates[i-1]);


	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: ersList.py requires 1 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	ersList(sys.argv[1]);

	exit();

