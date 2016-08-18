#!/usr/bin/python


# ntfOverlap.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

# Description
# ***********
# Returns area of overlap between two .ntf (JPEG2000) files

# Usage
# *****
# python ntfOverlap.py ntf1_path ntf2_path [resolution] [min_overlap_area]
#	ntf1_path: Path to first ntf file, must be ntf
#	ntf2_path: Path to second ntf file, must be ntf
#	(OPTIONAL) resolution: Resolution at which overlap calculation is performed (in m), lower resolution, faster processing, higher resolution, slower but slightly more precise, default is 240 m
#	(OPTIONAL) min_overlap_area: Minimum overlap area in km^2, overlap areas below this amount will not be reported, default is 0 km^2 (all results with overlap returned)

# Output
# ******
# ntf1_path ntf2_path area_of_overlap(km^2)
# The output is the path to the first ntf file, the path to the second ntf file, and the area of overlap in km^2 between the two (no output if there is zero overlap)


def getUTMZone(ll_long, ll_lat):

	import math;

	adj_ll_lon = int(math.floor(ll_long));
	adj_ll_lat  = int(math.floor(ll_lat));

	number = "";
	letter = "";

	if adj_ll_lon >= 0 and adj_ll_lon < 6:
		number = "1";
	if adj_ll_lon >= 6 and adj_ll_lon < 12:
		number = "2";
	if adj_ll_lon >= 12 and adj_ll_lon < 18:
		number = "3";
	if adj_ll_lon >= 18 and adj_ll_lon < 24:
		number = "4";
	if adj_ll_lon >= 24 and adj_ll_lon < 30:
		number = "5";
	if adj_ll_lon >= 30 and adj_ll_lon < 36:
		number = "6";
	if adj_ll_lon >= 36 and adj_ll_lon < 42:
		number = "7";
	if adj_ll_lon >= 42 and adj_ll_lon < 48:
		number = "8";
	if adj_ll_lon >= 48 and adj_ll_lon < 54:
		number = "9";
	if adj_ll_lon >= 54 and adj_ll_lon < 60:
		number = "10";
	if adj_ll_lon >= 60 and adj_ll_lon < 66:
		number = "11";
	if adj_ll_lon >= 66 and adj_ll_lon < 72:
		number = "12";
	if adj_ll_lon >= 72 and adj_ll_lon < 78:
		number = "13";
	if adj_ll_lon >= 78 and adj_ll_lon < 84:
		number = "14";
	if adj_ll_lon >= 84 and adj_ll_lon < 90:
		number = "15";
	if adj_ll_lon >= 90 and adj_ll_lon < 96:
		number = "16";
	if adj_ll_lon >= 96 and adj_ll_lon < 102:
		number = "17";
	if adj_ll_lon >= 102 and adj_ll_lon < 108:
		number = "18";
	if adj_ll_lon >= 108 and adj_ll_lon < 114:
		number = "19";
	if adj_ll_lon >= 114 and adj_ll_lon < 120:
		number = "20";
	if adj_ll_lon >= 120 and adj_ll_lon < 126:
		number = "21";
	if adj_ll_lon >= 126 and adj_ll_lon < 132:
		number = "22";
	if adj_ll_lon >= 132 and adj_ll_lon < 138:
		number = "23";
	if adj_ll_lon >= 138 and adj_ll_lon < 144:
		number = "24";
	if adj_ll_lon >= 144 and adj_ll_lon < 150:
		number = "25";
	if adj_ll_lon >= 150 and adj_ll_lon < 156:
		number = "26";
	if adj_ll_lon >= 156 and adj_ll_lon < 162:
		number = "27";
	if adj_ll_lon >= 162 and adj_ll_lon < 168:
		number = "28";
	if adj_ll_lon >= 168 and adj_ll_lon < 174:
		number = "29";
	if adj_ll_lon >= 174 and adj_ll_lon < 180:
		number = "30";
	if adj_ll_lon >= 180 and adj_ll_lon < 186:
		number = "31";
	if adj_ll_lon >= 186 and adj_ll_lon < 192:
		number = "32";
	if adj_ll_lon >= 192 and adj_ll_lon < 198:
		number = "33";
	if adj_ll_lon >= 198 and adj_ll_lon < 204:
		number = "34";
	if adj_ll_lon >= 204 and adj_ll_lon < 210:
		number = "35";
	if adj_ll_lon >= 210 and adj_ll_lon < 216:
		number = "36";
	if adj_ll_lon >= 216 and adj_ll_lon < 222:
		number = "37";
	if adj_ll_lon >= 222 and adj_ll_lon < 228:
		number = "38";
	if adj_ll_lon >= 228 and adj_ll_lon < 234:
		number = "39";
	if adj_ll_lon >= 234 and adj_ll_lon < 240:
		number = "40";
	if adj_ll_lon >= 240 and adj_ll_lon < 246:
		number = "41";
	if adj_ll_lon >= 246 and adj_ll_lon < 252:
		number = "42";
	if adj_ll_lon >= 252 and adj_ll_lon < 258:
		number = "43";
	if adj_ll_lon >= 258 and adj_ll_lon < 264:
		number = "44";
	if adj_ll_lon >= 264 and adj_ll_lon < 270:
		number = "45";
	if adj_ll_lon >= 270 and adj_ll_lon < 276:
		number = "46";
	if adj_ll_lon >= 276 and adj_ll_lon < 282:
		number = "47";
	if adj_ll_lon >= 282 and adj_ll_lon < 288:
		number = "48";
	if adj_ll_lon >= 288 and adj_ll_lon < 294:
		number = "49";
	if adj_ll_lon >= 294 and adj_ll_lon < 300:
		number = "50";
	if adj_ll_lon >= 300 and adj_ll_lon < 306:
		number = "51";
	if adj_ll_lon >= 306 and adj_ll_lon < 312:
		number = "52";
	if adj_ll_lon >= 312 and adj_ll_lon < 318:
		number = "53";
	if adj_ll_lon >= 318 and adj_ll_lon < 324:
		number = "54";
	if adj_ll_lon >= 324 and adj_ll_lon < 330:
		number = "55";
	if adj_ll_lon >= 330 and adj_ll_lon < 336:
		number = "56";
	if adj_ll_lon >= 336 and adj_ll_lon < 342:
		number = "57";
	if adj_ll_lon >= 342 and adj_ll_lon < 348:
		number = "58";
	if adj_ll_lon >= 348 and adj_ll_lon < 354:
		number = "59";
	if adj_ll_lon >= 354 and adj_ll_lon < 360:
		number = "60";

	if adj_ll_lat >= 10 and adj_ll_lat < 18:
		letter = "C";
	if adj_ll_lat >= 18 and adj_ll_lat < 26:
		letter = "D";
	if adj_ll_lat >= 26 and adj_ll_lat < 34:
		letter = "E";
	if adj_ll_lat >= 34 and adj_ll_lat < 42:
		letter = "F";
	if adj_ll_lat >= 42 and adj_ll_lat < 50:
		letter = "G";
	if adj_ll_lat >= 50 and adj_ll_lat < 58:
		letter = "H";
	if adj_ll_lat >= 58 and adj_ll_lat < 66:
		letter = "J";
	if adj_ll_lat >= 66 and adj_ll_lat < 74:
		letter = "K";
	if adj_ll_lat >= 74 and adj_ll_lat < 82:
		letter = "L";
	if adj_ll_lat >= 82 and adj_ll_lat < 90:
		letter = "M";
	if adj_ll_lat >= 90 and adj_ll_lat < 98:
		letter = "N";
	if adj_ll_lat >= 98 and adj_ll_lat < 106:
		letter = "P";
	if adj_ll_lat >= 106 and adj_ll_lat < 114:
		letter = "Q";
	if adj_ll_lat >= 114 and adj_ll_lat < 122:
		letter = "R";
	if adj_ll_lat >= 122 and adj_ll_lat < 130:
		letter = "S";
	if adj_ll_lat >= 130 and adj_ll_lat < 138:
		letter = "T";
	if adj_ll_lat >= 138 and adj_ll_lat < 146:
		letter = "U";
	if adj_ll_lat >= 146 and adj_ll_lat < 154:
		letter = "V";
	if adj_ll_lat >= 154 and adj_ll_lat < 162:
		letter = "W";
	if adj_ll_lat >= 162 and adj_ll_lat < 174:
		letter = "X";

	utm_zone = number + letter;

	return utm_zone;




def ntfOverlap(ntf1_path, ntf2_path, resolution, min_overlap_area):

	import os;

	assert os.path.exists(ntf1_path), "\n***** ERROR: " + ntf1_path + " does not exist\n";
	assert os.path.exists(ntf2_path), "\n***** ERROR: " + ntf2_path + " does not exist\n";

#	ice = sys.argv[3];

	import subprocess;

	cmd  = "\ngdalinfo " + ntf1_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	import re;

	first_search_exp  = "Upper\s*Left\s*,*\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(";
	second_search_exp = "Upper\s*Left\s*,*\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\-*\d+\.*\d*\s*,\s*\-*\d+\.*\d*";

	if not re.search(first_search_exp, info):
		first_search_exp  = "Upper\s*Left\s*\(\s*";
		second_search_exp = "Upper\s*Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*";

	ntf1_path_ul = info[re.search(first_search_exp, info).end(0) : re.search(second_search_exp, info).end(0)];
	elements = ntf1_path_ul.split(",");
	ntf1_path_ulx = elements[0].strip();
	ntf1_path_uly = elements[1].strip();

	first_search_exp  = first_search_exp.replace("Left", "Right");
	second_search_exp = second_search_exp.replace("Left", "Right");
	
	ntf1_path_ur = info[re.search(first_search_exp, info).end(0) : re.search(second_search_exp,info).end(0)];
	elements = ntf1_path_ur.split(",");
	ntf1_path_urx = elements[0];
	ntf1_path_ury = elements[1];

	first_search_exp  = first_search_exp.replace("Upper", "Lower");
	first_search_exp  = first_search_exp.replace("Right", "Left");
	second_search_exp = second_search_exp.replace("Upper", "Lower");
	second_search_exp = second_search_exp.replace("Right", "Left");

	ntf1_path_ll = info[re.search(first_search_exp,info).end(0) : re.search(second_search_exp,info).end(0)];
	elements = ntf1_path_ll.split(",");
	ntf1_path_llx = elements[0];
	ntf1_path_lly = elements[1];

	first_search_exp  = first_search_exp.replace("Left", "Right");
	second_search_exp = second_search_exp.replace("Left", "Right");

	ntf1_path_lr = info[re.search(first_search_exp,info).end(0) : re.search(second_search_exp,info).end(0)];
	elements = ntf1_path_lr.split(",");
	ntf1_path_lrx = elements[0];
	ntf1_path_lry = elements[1];

	cmd  = "\ngdalinfo " + ntf2_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	first_search_exp  = "Upper\s*Left\s*,*\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(";
	second_search_exp = "Upper\s*Left\s*,*\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\-*\d+\.*\d*\s*,\s*\-*\d+\.*\d*";

	if not re.search(first_search_exp, info):
		first_search_exp  = "Upper\s*Left\s*\(\s*";
		second_search_exp = "Upper\s*Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*";

	ntf2_path_ul = info[re.search(first_search_exp, info).end(0) : re.search(second_search_exp,info).end(0)];
	elements = ntf2_path_ul.split(",");
	ntf2_path_ulx = elements[0];
	ntf2_path_uly = elements[1];

	first_search_exp  = first_search_exp.replace("Left", "Right");
	second_search_exp = second_search_exp.replace("Left", "Right");

	ntf2_path_ur = info[re.search(first_search_exp,info).end(0) : re.search(second_search_exp,info).end(0)];
	elements = ntf2_path_ur.split(",");
	ntf2_path_urx = elements[0];
	ntf2_path_ury = elements[1];

	first_search_exp  = first_search_exp.replace("Upper", "Lower");
	first_search_exp  = first_search_exp.replace("Right", "Left");
	second_search_exp = second_search_exp.replace("Upper", "Lower");
	second_search_exp = second_search_exp.replace("Right", "Left");

	ntf2_path_ll = info[re.search(first_search_exp,info).end(0) : re.search(second_search_exp,info).end(0)];
	elements = ntf2_path_ll.split(",");
	ntf2_path_llx = elements[0];
	ntf2_path_lly = elements[1];

	first_search_exp  = first_search_exp.replace("Left", "Right");
	second_search_exp = second_search_exp.replace("Left", "Right");

	ntf2_path_lr = info[re.search(first_search_exp,info).end(0) : re.search(second_search_exp,info).end(0)];
	elements = ntf2_path_lr.split(",");
	ntf2_path_lrx = elements[0];
	ntf2_path_lry = elements[1];

	gmt_proj_str = "";

#	Latitude positive, assume Greenland
	if float(ntf2_path_lry) > 0:
		gmt_proj_str = "-R-180/180/0/90 -Js-45/90/70/1:1";
		
#	Latitude negative, assume Antarctica
	if float(ntf2_path_lry) < 0:
		gmt_proj_str = "-R-180/180/-90/0 -Js0/-90/-71/1:1";

	cmd = "\necho \"" + ntf1_path_ulx + " " + ntf1_path_uly + "\n" + ntf1_path_urx + " " + ntf1_path_ury + "\n" + ntf1_path_lrx + " " + ntf1_path_lry + "\n" + ntf1_path_llx + " " + ntf1_path_lly + "\"";
	cmd += " | mapproject " + gmt_proj_str + " -F -C ";
	cmd += " | gmtinfo -C\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	[ntf1_xmin, ntf1_xmax, ntf1_ymin, ntf1_ymax] = pipe.read().split();
	pipe.close();

	cmd = "\necho \"" + ntf2_path_ulx + " " + ntf2_path_uly + "\n" + ntf2_path_urx + " " + ntf2_path_ury + "\n" + ntf2_path_lrx + " " + ntf2_path_lry + "\n" + ntf2_path_llx + " " + ntf2_path_lly + "\"";
	cmd += " | mapproject " + gmt_proj_str + " -F -C ";
	cmd += " | gmtinfo -C\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	[ntf2_xmin, ntf2_xmax, ntf2_ymin, ntf2_ymax] = pipe.read().split();
	pipe.close();

#	xmin = str(min(float(ntf1_path_ulx),float(ntf1_path_llx),float(ntf2_path_ulx),float(ntf2_path_llx)));
#	xmax = str(max(float(ntf1_path_urx),float(ntf1_path_lrx),float(ntf2_path_urx),float(ntf2_path_lrx)));
#	ymin = str(min(float(ntf1_path_lly),float(ntf1_path_lry),float(ntf2_path_lly),float(ntf2_path_lry)));
#	ymax = str(max(float(ntf1_path_uly),float(ntf1_path_ury),float(ntf2_path_uly),float(ntf2_path_ury)));
	xmin = str(min(float(ntf1_xmin), float(ntf2_xmin)));
	xmax = str(max(float(ntf1_xmax), float(ntf2_xmax)));
	ymin = str(min(float(ntf1_ymin), float(ntf2_ymin)));
	ymax = str(max(float(ntf1_ymax), float(ntf2_ymax)));

#	cmd  = "\necho \"" + xmin + " " + ymin + "\n" + xmax + " " + ymax + "\"";
#	cmd += " | mapproject " + gmt_proj_str + " -F -C\n";
#	print(cmd);
#	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
#	bounds = pipe.read().split();
#	pipe.close();

#	xmin = bounds[0];
#	ymin = bounds[1];
#	xmax = bounds[2];
#	ymax = bounds[3];

	R = "-R" + xmin + "/" + ymin + "/" + xmax + "/" + ymax + "r";

	cmd = "\necho \"" + ntf1_path_ulx + " " + ntf1_path_uly + "\n" + ntf1_path_urx + " " + ntf1_path_ury + "\n" + ntf1_path_lrx + " " + ntf1_path_lry + "\n" + ntf1_path_llx + " " + ntf1_path_lly + "\"";
	cmd += " | mapproject " + gmt_proj_str + " -F -C ";
	cmd += " | grdmask -Gntf1_path.grd -I" + resolution + "= " + R + " -NNaN/NaN/1\n";
	subprocess.call(cmd,shell=True);

	cmd = "\necho \"" + ntf2_path_ulx + " " + ntf2_path_uly + "\n" + ntf2_path_urx + " " + ntf2_path_ury + "\n" + ntf2_path_lrx + " " + ntf2_path_lry + "\n" + ntf2_path_llx + " " + ntf2_path_lly + "\"";
	cmd += " | mapproject " + gmt_proj_str + " -F -C ";
	cmd += " | grdmask -Gntf2_path.grd -I" + resolution + "= " + R + " -NNaN/NaN/1\n";
	subprocess.call(cmd,shell=True);

	cmd = "";
#	cmd = "\ngrdmask " + ice + " -Gice_mask.grd -I" + resolution + "= " + R + " -NNaN/NaN/1 -m\n";
#	cmd += "\ngrdmath ntf1_path.grd ice_mask.grd OR = ntf1_path.grd\n";
#	cmd += "\ngrdmath ntf2_path.grd ice_mask.grd OR = ntf2_path.grd\n";
	cmd += "\ngrdmath ntf1_path.grd ntf2_path.grd OR = image_overlap.grd\n";
	subprocess.call(cmd,shell=True);

	cmd = "\ngrdvolume image_overlap.grd\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	volume_info = pipe.read().split();
	pipe.close();

	area = volume_info[0];

	if len(volume_info) > 3:
		area = volume_info[1];

	if float(area) / 1e6 > float(min_overlap_area):
		print(ntf1_path + " " + ntf2_path + " " + area);

	os.remove("ntf1_path.grd");
	os.remove("ntf2_path.grd");
	os.remove("image_overlap.grd");
#	os.remove("ice_mask.grd");

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: ntfOverlap.py requires at least 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	resolution = "240";

	if len(sys.argv) > 3:
		resolution = sys.argv[3];

	min_overlap_area = "50";

	if len(sys.argv) > 4:
		min_overlap_area = sys.argv[4];

	ntfOverlap(sys.argv[1], sys.argv[2], resolution, min_overlap_area);

	exit();


#def ntfOverlap(ntf1_path, ntf2_path, resolution, min_overlap_area):

#	import os;

#	assert os.path.exists(ntf1_path), "\n***** ERROR: " + ntf1_path + " does not exist\n";
#	assert os.path.exists(ntf2_path), "\n***** ERROR: " + ntf2_path + " does not exist\n";

#	import subprocess;

#	cmd  = "\ngdalinfo " + ntf1_path + "\n";
#	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
#	info = pipe.read().strip();
#	pipe.close();

#	import re;

#	ntf1_path_ul = info[re.search("UpperLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(", info).end(0) : re.search("UpperLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\-*\d+\.*\d*\s*,\s*\-*\d+\.*\d*",info).end(0)];
#	elements = ntf1_path_ul.split(",");
#	ntf1_path_ulx = elements[0].strip();
#	ntf1_path_uly = elements[1].strip();

#	ntf1_path_ur = info[re.search("UpperRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("UpperRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\-*\d+\.*\d*\s*,\s*\-*\d+\.*\d*",info).end(0)];
#	elements = ntf1_path_ur.split(",");
#	ntf1_path_urx = elements[0];
#	ntf1_path_ury = elements[1];

#	ntf1_path_ll = info[re.search("LowerLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("LowerLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\-*\d+\.*\d*\s*,\s*\-*\d+\.*\d*",info).end(0)];
#	elements = ntf1_path_ll.split(",");
#	ntf1_path_llx = elements[0];
#	ntf1_path_lly = elements[1];

#	ntf1_path_lr = info[re.search("LowerRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("LowerRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\-*\d+\.*\d*\s*,\s*\-*\d+\.*\d*",info).end(0)];
#	elements = ntf1_path_lr.split(",");
#	ntf1_path_lrx = elements[0];
#	ntf1_path_lry = elements[1];

#	cmd  = "\ngdalinfo " + ntf2_path + "\n";
#	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
#	info = pipe.read().strip();
#	pipe.close();

#	ntf2_path_ul = info[re.search("UpperLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("UpperLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\-*\d+\.*\d*\s*,\s*\-*\d+\.*\d*",info).end(0)];
#	elements = ntf2_path_ul.split(",");
#	ntf2_path_ulx = elements[0];
#	ntf2_path_uly = elements[1];

#	ntf2_path_ur = info[re.search("UpperRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("UpperRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\-*\d+\.*\d*\s*,\s*\-*\d+\.*\d*",info).end(0)];
#	elements = ntf2_path_ur.split(",");
#	ntf2_path_urx = elements[0];
#	ntf2_path_ury = elements[1];

#	ntf2_path_ll = info[re.search("LowerLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("LowerLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\-*\d+\.*\d*\s*,\s*\-*\d+\.*\d*",info).end(0)];
#	elements = ntf2_path_ll.split(",");
#	ntf2_path_llx = elements[0];
#	ntf2_path_lly = elements[1];

#	ntf2_path_lr = info[re.search("LowerRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0) : re.search("LowerRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\-*\d+\.*\d*\s*,\s*\-*\d+\.*\d*",info).end(0)];
#	elements = ntf2_path_lr.split(",");
#	ntf2_path_lrx = elements[0];
#	ntf2_path_lry = elements[1];

#	gmt_proj_str = "";

##	Latitude positive, assume Greenland
#	if float(ntf2_path_lry) > 0:
#		gmt_proj_str = "-R-180/180/0/90 -Js-45/90/70/1:1";
		
##	Latitude negative, assume Antarctica
#	if float(ntf2_path_lry) < 0:
#		gmt_proj_str = "-R-180/180/-90/0 -Js0/-90/-71/1:1";

#	if float(ntf2_path_lry) < 60 and float(ntf2_path_lry) > -60:
#		utm_zone = getUTMZone(float(ntf2_path_lrx) + 180, float(ntf2_path_lry) + 90);
#		gmt_proj_str = "-Ju" + utm_zone + "/1:1";

#	cmd = "\necho \"" + ntf1_path_ulx + " " + ntf1_path_uly + "\n" + ntf1_path_urx + " " + ntf1_path_ury + "\n" + ntf1_path_lrx + " " + ntf1_path_lry + "\n" + ntf1_path_llx + " " + ntf1_path_lly + "\"";
#	cmd += " | mapproject " + gmt_proj_str + " -F -C ";
#	cmd += " | minmax -C\n";
#	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
#	[ntf1_xmin, ntf1_xmax, ntf1_ymin, ntf1_ymax] = pipe.read().split();
#	pipe.close();

#	cmd = "\necho \"" + ntf2_path_ulx + " " + ntf2_path_uly + "\n" + ntf2_path_urx + " " + ntf2_path_ury + "\n" + ntf2_path_lrx + " " + ntf2_path_lry + "\n" + ntf2_path_llx + " " + ntf2_path_lly + "\"";
#	cmd += " | mapproject " + gmt_proj_str + " -F -C ";
#	cmd += " | minmax -C\n";
#	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
#	[ntf2_xmin, ntf2_xmax, ntf2_ymin, ntf2_ymax] = pipe.read().split();
#	pipe.close();

#	xmin = str(min(float(ntf1_xmin), float(ntf2_xmin)));
#	xmax = str(max(float(ntf1_xmax), float(ntf2_xmax)));
#	ymin = str(min(float(ntf1_ymin), float(ntf2_ymin)));
#	ymax = str(max(float(ntf1_ymax), float(ntf2_ymax)));

#	R = "-R" + xmin + "/" + ymin + "/" + xmax + "/" + ymax + "r";

#	cmd = "\necho \"" + ntf1_path_ulx + " " + ntf1_path_uly + "\n" + ntf1_path_urx + " " + ntf1_path_ury + "\n" + ntf1_path_lrx + " " + ntf1_path_lry + "\n" + ntf1_path_llx + " " + ntf1_path_lly + "\"";
#	cmd += " | mapproject " + gmt_proj_str + " -F -C ";
#	cmd += " | grdmask -Gntf1_path.grd -I" + resolution + "= " + R + " -NNaN/NaN/1\n";
#	subprocess.call(cmd,shell=True);

#	cmd = "\necho \"" + ntf2_path_ulx + " " + ntf2_path_uly + "\n" + ntf2_path_urx + " " + ntf2_path_ury + "\n" + ntf2_path_lrx + " " + ntf2_path_lry + "\n" + ntf2_path_llx + " " + ntf2_path_lly + "\"";
#	cmd += " | mapproject " + gmt_proj_str + " -F -C ";
#	cmd += " | grdmask -Gntf2_path.grd -I" + resolution + "= " + R + " -NNaN/NaN/1\n";
#	subprocess.call(cmd,shell=True);

#	cmd = "";
#	cmd += "\ngrdmath ntf1_path.grd ntf2_path.grd OR = image_overlap.grd\n";
#	subprocess.call(cmd,shell=True);

#	cmd = "\ngrdvolume image_overlap.grd\n";
#	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
#	volume_info = pipe.read().split();
#	pipe.close();

#	area = volume_info[0];

#	if len(volume_info) > 3:
#		area = volume_info[1];

#	if float(area) / 1e6 > float(min_overlap_area):
#		print(ntf1_path + " " + ntf2_path + " " + area);

#	os.remove("ntf1_path.grd");
#	os.remove("ntf2_path.grd");
#	os.remove("image_overlap.grd");

#	return;


#if __name__ == "__main__":
	
#	import os;
#	import sys;
	
#	assert len(sys.argv) > 2, "\n***** ERROR: ntfOverlap.py requires at least 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
#	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
#	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
#	resolution = "240";

#	if len(sys.argv) > 3:
#		resolution = sys.argv[3];

#	min_overlap_area = "36";

#	if len(sys.argv) > 4:
#		min_overlap_area = sys.argv[4];

#	ntfOverlap(sys.argv[1], sys.argv[2], resolution, min_overlap_area);

#	exit();


