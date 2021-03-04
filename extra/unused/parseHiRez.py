#!/usr/bin/python

# parseHiRez.py
# Author: Andrew Kenneth Melkonian (akm26@cornell.edu)
# All rights reserved


def parseHiRez(hirez_path, metadata_path, utm_zone):

	import re;

	hirez_dir = ".";

	index = hirez_path.rfind("/");

	if index > -1:
		hirez_dir = hirez_path[ : index];

	hirez_name = hirez_path[index + 1 : ];


	assert re.search("_[a-zA-Z0-9]+_DEM",hirez_name), "\n***** ERROR: " + hirez_path + " lacks valid identifier for searching metadata\n";

	identifier = hirez_name[re.search("_[a-zA-Z0-9]+_DEM",hirez_name).start(0) + 1 : re.search("_[a-zA-Z0-9]+_DEM",hirez_name).end(0) - 4];

	contents = os.listdir(metadata_path);
	metadata_xmls = [item for item in contents if identifier + ".xml" in item];

	assert len(metadata_xmls) > 0, "\n***** ERROR, no xml metadata files found for " + hirez_path + " in " + metadata_path + "\n";


	coords = {"ULLON" : "", "ULLAT" : "", "URLON" : "", "URLAT" : "", "LLLON" : "", "LLLAT" : "", "LRLON" : "", "LRLAT" : ""};

	for metadata_xml in metadata_xmls:

		temp_coords = {"ULLON" : "", "ULLAT" : "", "URLON" : "", "URLAT" : "", "LLLON" : "", "LLLAT" : "", "LRLON" : "", "LRLAT" : ""};

		metadata_file = open(metadata_path + "/" + metadata_xml, "r");

		for line in metadata_file:

			if any(corner in line for corner in coords.keys()):
				corner = line[line.find("<") + 1 : line.find(">")];
				coord  = line[line.find(">") + 1 : line.rfind("<")].strip();			
				temp_coords[corner] = coord;	
		
		metadata_file.close();

		#print(coords["LRLON"] + " " + coords["LRLAT"] + "\n");
		#print(coords["LLLON"] + " " + coords["LLLAT"] + "\n");
		#print(coords["ULLON"] + " " + coords["ULLAT"] + "\n");
		#print(coords["URLON"] + " " + coords["URLAT"] + "\n");
		#print(coords["LRLON"] + " " + coords["LRLAT"] + "\n");

		for corner in temp_coords:

			if coords[corner]:
				
				if hirez_path.find("WV01") > -1:

					if corner == "ULLAT" and float(temp_coords[corner]) < float(coords[corner]):
						coords["ULLAT"] = temp_coords["ULLAT"];
						coords["ULLON"] = temp_coords["ULLON"];
					elif corner == "URLAT" and float(temp_coords[corner]) < float(coords[corner]):
						coords["URLAT"] = temp_coords["URLAT"];
						coords["URLON"] = temp_coords["URLON"];
					elif corner == "LLLAT" and float(temp_coords[corner]) > float(coords[corner]):
						coords["LLLAT"] = temp_coords["LLLAT"];
						coords["LLLON"] = temp_coords["LLLON"];
					elif corner == "LRLAT" and float(temp_coords[corner]) > float(coords[corner]):
						coords["LRLAT"] = temp_coords["LRLAT"];
						coords["LRLON"] = temp_coords["LRLON"];

				elif hirez_path.find("WV02") > -1:

					if corner == "ULLAT" and float(temp_coords[corner]) > float(coords[corner]):
						coords["ULLAT"] = temp_coords["ULLAT"];
						coords["ULLON"] = temp_coords["ULLON"];
					elif corner == "URLAT" and float(temp_coords[corner]) > float(coords[corner]):
						coords["URLAT"] = temp_coords["URLAT"];
						coords["URLON"] = temp_coords["URLON"];
					elif corner == "LLLAT" and float(temp_coords[corner]) < float(coords[corner]):
						coords["LLLAT"] = temp_coords["LLLAT"];
						coords["LLLON"] = temp_coords["LLLON"];
					elif corner == "LRLAT" and float(temp_coords[corner]) < float(coords[corner]):
						coords["LRLAT"] = temp_coords["LRLAT"];
						coords["LRLON"] = temp_coords["LRLON"];

				

			else:
				coords[corner] = temp_coords[corner];


	bounds_path = metadata_path + "/" + hirez_name[ : hirez_name.rfind(".")] + "_box.gmt";
	
	bounds_file = open(bounds_path, "w");
	bounds_file.write(">\n");
	bounds_file.write(coords["LRLON"] + " " + coords["LRLAT"] + "\n");
	bounds_file.write(coords["LLLON"] + " " + coords["LLLAT"] + "\n");
	bounds_file.write(coords["ULLON"] + " " + coords["ULLAT"] + "\n");
	bounds_file.write(coords["URLON"] + " " + coords["URLAT"] + "\n");
	bounds_file.write(coords["LRLON"] + " " + coords["LRLAT"] + "\n");
	bounds_file.close();


	bounds_utm_path = metadata_path + "/" + hirez_name[ : hirez_name.rfind(".")] + "_box_utm" + utm_zone + ".gmt";

	import subprocess;

	cmd = "\nmapproject -Ju" + utm_zone + "/1:1 -F -C -m " + bounds_path + " > " + bounds_utm_path + "\n";
	subprocess.call(cmd,shell=True);

	cmd = "\ngdalinfo " + hirez_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	utm_zone_num = utm_zone[re.search("\d+",utm_zone).start(0) : re.search("\d+",utm_zone).end(0)];	
	utm_zone_letter = "";
	utm_n_or_s = "north";

	if re.search("\D",utm_zone):
		utm_zone_letter = utm_zone[re.search("[a-zA-Z]",utm_zone).start(0) : re.search("[a-zA-Z]",utm_zone).start(0) + 1];
		if utm_zone_letter.lower() < "n":
			utm_n_or_s = "s";

	hirez_utm_path = hirez_path[ : hirez_path.rfind(".")] + "_utm" + utm_zone + ".tif";

	if not re.search("UTM zone " + utm_zone_num,info) and not os.path.exists(hirez_utm_path):
		cmd = "\ngdalwarp -t_srs '+proj=utm +zone=" + utm_zone_num + " +datum=WGS84 +" + utm_n_or_s + "' -of GTiff " + hirez_path + " " + hirez_utm_path + "\n";
		subprocess.call(cmd,shell=True);

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 3, "\n***** ERROR: parseHiRez.py requires 3 arguments, " + str(len(sys.argv)) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	parseHiRez(sys.argv[1], sys.argv[2], sys.argv[3]);

	exit();

