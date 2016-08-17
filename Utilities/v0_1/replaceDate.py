#!/usr/bin/python


# replaceDate.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

# Usage
# *****
# python replaceDate.py /path/to/input_file /path/to/output_file
#	/path/to/input_file - full path of input file
#	/path/to/output_file - full path of output file



def replaceDate(input_file_path, output_file_path):

	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";

	num_to_month = {"01" : "January", "02" : "February", "03" : "March", "04" : "April", "05" : "May", "06" : "June", "07" : "July", "08" : "August", "09" : "September", "10" : "October", "11" : "November", "12" : "December"};

	infile = open(input_file_path,"r");
	outfile = open("temp","w");

	import re;

	for line in infile:

		while 1:

			if not re.search("\d\d\d\d\/\d\d\/\d\d", line):
				break;

			index1 = re.search("\d\d\d\d\/\d\d\/\d\d",line).start(0);
			index2 = re.search("\d\d\d\d\/\d\d\/\d\d",line).end(0);

			date  = line[index1 : index2];
			year  = date[0 : 4];
			month = date[5 : 7];
			day   = date[8 : 10];

			if day[0] == "0":
				day = day[1];

			if line[index2] == "-":
				line = line[ : index1] + day + " " + num_to_month[month] + " " + year + " to " + line[index2 + 1 : ];

			else:
				line = line[ : index1] + day + " " + num_to_month[month] + " " + year + line[index2 : ];

		outfile.write(line);

	infile.close();
	outfile.close();

	infile = open("temp","r");
	outfile = open(output_file_path,"w");
	
	for line in infile:

		while 1:

			if not re.search("\d\d\d\d\/\d\d\D",line):
				break;

			index1 = re.search("\d\d\d\d\/\d\d\D",line).start(0);
			index2 = re.search("\d\d\d\d\/\d\d\D",line).end(0) - 1;

			date  = line[index1 : index2];
			year  = date[0 : 4];
			month = date[5 : 7];

			if line[index2] == "-":
				line = line[ : index1] + num_to_month[month] + " " + year + " to " + line[index2 + 1: ];

			else:
				line = line[ : index1] + num_to_month[month] + " " + year + line[index2: ];

		outfile.write(line);

	infile.close();
	outfile.close();



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: replaceDate.py requires 3 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	replaceDate(sys.argv[1], sys.argv[2]);

	exit();




exit();
