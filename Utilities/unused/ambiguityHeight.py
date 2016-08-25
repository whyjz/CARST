#!/usr/bin/python


# ambiguityHeight.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

# Usage
# *****
# python ambiguityHeight.py int_dir_path
#       int_dir_path: path to interferogram directory for which ambiguity height is to be calculated
#
# NOTE: "int_dir_path" MUST contain a valid *baseline.rsc and *int.rsc file.
# NOTE: If applying to TerraSARX, the T*X*.xml metadata files MUST be findable from the directory above "int_dir_path"


def ambiguityHeight(int_dir_path):

#	Check that the interferogram directory given exists

	import os;

	assert os.path.exists(int_dir_path), "***** ERROR: " + int_dir_path + " not found, cannot continue\n";


#	Read the contents of the interferogram directory

	contents = os.listdir(int_dir_path);


#	Check that the interferogram directory has a properly-named *baseline.rsc file and  *int.rsc file so that the necessary information can be obtained

	import re;

	baseline_paths = [item for item in contents if re.search("baseline.rsc$",item)];

	assert len(baseline_paths) > 0, "***** ERROR: " + int_dir_path + " does not contain a *baseline.rsc file, cannot continue\n";

	int_rsc_paths = [item for item in contents if re.search("^\d{6}\D\d{6}\S*\.int\.rsc$",item)];

	assert len(int_rsc_paths) > 0, "***** ERROR: " + int_dir_path + " does not contain a properly-formatted *.int.rsc file, cannot continue\n";


#	Read the top and bottom perpendicular baselines from the *baseline.rsc file

	p_baseline_top = "";
	p_baseline_bottom = "";

	baseline_file = open(int_dir_path + "/" + baseline_paths[0],"r");

	for line in baseline_file:
		
		if line.strip().lower().find("p_baseline") > -1:

			elements = line.strip().split();

			if line.strip().lower().find("top") > -1:
				p_baseline_top = elements[1];

			else:
				p_baseline_bottom = elements[1];

	baseline_file.close();

	p_baseline = str((float(p_baseline_top) + float(p_baseline_bottom)) / 2);


#	Read the necessary information from a valid *.int.rsc file: height (i.e. orbital height), wavelength, and platform type

	height     = "";
	wavelength = "";
	platform   = "";

	int_rsc_file = open(int_dir_path + "/" + int_rsc_paths[0],"r");

	for line in int_rsc_file:

		if re.search("^\s*height\s*\d+",line.strip().lower()):
			elements = line.split();
			height = elements[1];

		elif re.search("^wavelength",line.strip().lower()):
			elements = line.split();
			wavelength = elements[1];

		elif re.search("^platform\s*\S+",line.strip().lower()):
			elements = line.split();
			platform = elements[1]; 

	int_rsc_file.close();


#	Determine the data type

	data_type = "";

	if platform.find("ERS") > -1:
		data_type = "ERS";

	elif re.search("t[a-z]x",platform.lower()):
		data_type = "TSX";


#	Get the incidence angle for the data type

	angle = "";

	if data_type == "ERS":
		angle = "23";

	elif data_type == "TSX":

		angles = {};

		import subprocess;

		cmd = "\nfind " + int_dir_path + "/.. -name \"T*X*.xml\"\n";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		leader_file_paths = pipe.read().split();
		pipe.close();

		for path in leader_file_paths:

			date = "";

			infile = open(path,"r");

			for line in infile:

				if line.find("timeUTC") > -1:
					index = re.search("timeUTC>",line).end(0);
					year  = line[index + 2 : index + 4];
					month = line[index + 5 : index + 7];
					day   = line[index + 8 : index + 10];
					date  = year + month + day;

				elif line.find("coverageRegionMin incidenceAngle") > -1:
					min_inc_angle = line[re.search("\">",line).end(0) : re.search("</",line).start(0)];

				elif line.find("coverageRegionMax incidenceAngle") > -1:
					max_inc_angle = line[re.search("\">",line).end(0) : re.search("</",line).start(0)];

			infile.close();

			angles[date] = str((float(max_inc_angle) + float(min_inc_angle)) / 2.);
	
		temp = 0.0;

		for ymd in angles:

			if int_dir_path.find(ymd) > -1:
				temp = temp + float(angles[ymd]);

		angle = str(temp / 2.);


#	Calculate the ambiguity height

	import math;

	ambiguity_height = str(float(wavelength) * float(height) * math.sin(math.radians(float(angle))) / (2 * abs(float(p_baseline))));

	print(int_dir_path + " " + ambiguity_height);

	return;
	

if __name__ == "__main__":

        import os;
        import sys;

        assert len(sys.argv) > 1, "\n***** ERROR: ambiguityHeight.py requires 1 arguments, " + str(len(sys.argv) - 1) + " given\n";
        assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";

        ambiguityHeight(sys.argv[1]);


