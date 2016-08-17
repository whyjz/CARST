#!/usr/bin/python


# hirez_pixel_track.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def highResPX(ref_ntf_path, search_ntf_path, ref_dem_path, search_dem_path, resolution, utm_zone, bounds_txt_path, num_proc, search_size, ref_size, step_size):


	import os;

	assert os.path.exists(ref_ntf_path), "\n***** ERROR: " + ref_ntf_path + " does not exist\n";
	assert os.path.exists(search_ntf_path), "\n***** ERROR: " + search_ntf_path + " does not exist\n";
	assert os.path.exists(ref_dem_path), "\n***** ERROR: " + ref_dem_path + " does not exist\n";
	assert os.path.exists(search_dem_path), "\n***** ERROR: " + search_dem_path + " does not exist\n";
	assert os.path.exists(bounds_txt_path), "\n***** ERROR: " + bounds_txt_path + " does not exist\n";

	import subprocess;

	cmd  = "\ngdalinfo " + ref_ntf_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	import re;

	ref_ul = info[re.search("UpperLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("UpperLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];
	elements = ref_ul.split(",");
	ref_ulx = elements[0];
	ref_uly = elements[1];

	ref_ur = info[re.search("UpperRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("UpperRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];
	elements = ref_ur.split(",");
	ref_urx = elements[0];
	ref_ury = elements[1];

	ref_ll = info[re.search("LowerLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("LowerLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];
	elements = ref_ll.split(",");
	ref_llx = elements[0];
	ref_lly = elements[1];

	ref_lr = info[re.search("LowerRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("LowerRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];
	elements = ref_lr.split(",");
	ref_lrx = elements[0];
	ref_lry = elements[1];

	cmd  = "\necho \"" + ref_ulx + " " + ref_uly + "\n" + ref_urx + " " + ref_ury + "\n" + ref_llx + " " + ref_lly + "\n" + ref_lrx + " " + ref_lry + "\" | /home/willismi/Public/GMTdev/gmt4/bin/mapproject -Ju" + utm_zone + "X/1:1 -F -C\n"; 
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	[ref_ulx, ref_uly, ref_urx, ref_ury, ref_llx, ref_lly, ref_lrx, ref_lry] = pipe.read().split(); 
	pipe.close();

	ref_ulx = str(min(float(ref_ulx), float(ref_urx), float(ref_llx), float(ref_lrx)));
	ref_uly = str(max(float(ref_uly), float(ref_ury), float(ref_lly), float(ref_lry)));
	ref_lrx = str(max(float(ref_ulx), float(ref_urx), float(ref_llx), float(ref_lrx)));
	ref_lry = str(min(float(ref_uly), float(ref_ury), float(ref_lly), float(ref_lry)));

	#print(ref_ulx, ref_uly, ref_urx, ref_ury, ref_llx, ref_lly, ref_lrx, ref_lry);

	cmd = "\ngdalinfo " + search_ntf_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	search_ul = info[re.search("UpperLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("UpperLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];
	elements = search_ul.split(",");
	search_ulx = elements[0];
	search_uly = elements[1];

	search_ur = info[re.search("UpperRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("UpperRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];
	elements = search_ur.split(",");
	search_urx = elements[0];
	search_ury = elements[1];

	search_ll = info[re.search("LowerLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("LowerLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];
	elements = search_ll.split(",");
	search_llx = elements[0];
	search_lly = elements[1];

	search_lr = info[re.search("LowerRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("LowerRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];
	elements = search_lr.split(",");
	search_lrx = elements[0];
	search_lry = elements[1];

	cmd  = "\necho \"" + search_ulx + " " + search_uly + "\n" + search_urx + " " + search_ury + "\n" + search_llx + " " + search_lly + "\n" + search_lrx + " " + search_lry + "\" | /home/willismi/Public/GMTdev/gmt4/bin/mapproject -Ju" + utm_zone + "X/1:1 -F -C\n"; 
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	[search_ulx, search_uly, search_urx, search_ury, search_llx, search_lly, search_lrx, search_lry] = pipe.read().split(); 
	pipe.close();

	search_ulx = str(min(float(search_ulx), float(search_urx), float(search_llx), float(search_lrx)));
	search_uly = str(max(float(search_uly), float(search_ury), float(search_lly), float(search_lry)));
	search_lrx = str(max(float(search_ulx), float(search_urx), float(search_llx), float(search_lrx)));
	search_lry = str(min(float(search_uly), float(search_ury), float(search_lly), float(search_lry)));

	#print(search_ulx, search_uly, search_urx, search_ury, search_llx, search_lly, search_lrx, search_lry);

	bounds	   = [];
	bounds_str = "";

	infile = open(bounds_txt_path, "r");

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

	ref_date = ref_ntf_path[re.search("\d\d[A-Z][A-Z][A-Z]\d\d\d\d\d\d\d\d", ref_ntf_path).start(0) : re.search("\d\d[A-Z][A-Z][A-Z]\d\d\d\d\d\d\d\d", ref_ntf_path).end(0)];

	ref_year   = "20" + ref_date[0:2];
	ref_month  = months[ref_date[2:5]];
	ref_day    = ref_date[5:7];
	ref_hour   = ref_date[7:9];
	ref_minute = ref_date[9:11];
	ref_second = ref_date[11:13];

	ref_date = ref_year + ref_month + ref_day + ref_hour + ref_minute + ref_second;

	search_date = search_ntf_path[re.search("\d\d[A-Z][A-Z][A-Z]\d\d\d\d\d\d\d\d", search_ntf_path).start(0) : re.search("\d\d[A-Z][A-Z][A-Z]\d\d\d\d\d\d\d\d", search_ntf_path).end(0)];

	search_year   = "20" + search_date[0:2];
	search_month  = months[search_date[2:5]];
	search_day    = search_date[5:7];
	search_hour   = search_date[7:9];
	search_minute = search_date[9:11];
	search_second = search_date[11:13];

	search_date = search_year + search_month + search_day + search_hour + search_minute + search_second;

	pair = search_date + "_" + ref_date;

#	if not os.path.exists(pair):
#		os.mkdir(pair);

	print(pair);

#	ref_img_path    = pair + "/" + ref_ntf_path[ref_ntf_path.rfind("/") +1 : ref_ntf_path.rfind(".")] + ".img";
#	search_img_path = pair + "/" + search_ntf_path[search_ntf_path.rfind("/") + 1 : search_ntf_path.rfind(".")] + ".img";\
	ref_img_path    = ref_ntf_path[ref_ntf_path.rfind("/") +1 : ref_ntf_path.rfind(".")] + ".img";
	search_img_path = search_ntf_path[search_ntf_path.rfind("/") + 1 : search_ntf_path.rfind(".")] + ".img";

	if not os.path.exists(ref_img_path):
		cmd  = "\ngdalwarp -of ENVI -ot Float32 -t_srs '+proj=utm +zone=" + utm_zone + " +datum=WGS84 +north' -multi -et 0 -tr " + resolution + " " + resolution + " -te " + bounds_str + " -rpc -to RPC_DEM=" + ref_dem_path + " " + ref_ntf_path + " " + ref_img_path + "\n";
		cmd += "\ngdalwarp -of ENVI -ot Float32 -t_srs '+proj=utm +zone=" + utm_zone + " +datum=WGS84 +north' -multi -et 0 -tr " + resolution + " " + resolution + " -te " + bounds_str + " -rpc -to RPC_DEM=" + search_dem_path + " " + search_ntf_path + " " + search_img_path + "\n";
		#subprocess.call(cmd,shell=True);

	else:
		print("\n***** \"" + ref_img_path + "\" already exists, skipping orthorectification for " + pair + "...\n");

	from splitAmpcor import *;

	ref_img_path    = ref_img_path[ref_img_path.rfind("/") + 1 : ];
	search_img_path = search_img_path[search_img_path.rfind("/") + 1 : ];

	if not os.path.exists("ampcor_1.in"):
		#splitAmpcor(ref_img_path, search_img_path, pair, num_proc, resolution, ref_size, ref_size, search_size, search_size, step_size);
		print("Hello");

	else:
		print("\n***** \"ampcor_1.in\" already exists, skipping ampcor for " + pair + "...\n");

	

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 11, "\n***** ERROR: highResPX.py requires 10 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";
	assert os.path.exists(sys.argv[4]), "\n***** ERROR: " + sys.argv[4] + " does not exist\n";
	assert os.path.exists(sys.argv[7]), "\n***** ERROR: " + sys.argv[7] + " does not exist\n";
	

	highResPX(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10], sys.argv[11]);


	exit();
