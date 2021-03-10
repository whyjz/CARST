#!/usr/bin/python


# resamp.py
# Author: Andrew Kenneth Melkonian
# All rights reserved



def resamp(input_dem_tif_path, ref_dem_tif_path):

	import os;

	assert os.path.exists(input_dem_tif_path), "\n***** ERROR: " + input_dem_tif_path + " does not exist\n";
	assert os.path.exists(ref_dem_tif_path), "\n***** ERROR: " + ref_dem_tif_path + " does not exist\n";

	print(input_dem_tif_path);

	NO_DATA = "-9999";

	import subprocess;

	cmd  = "\ndate +\"%s\" -d \"1858-11-17 00:00:00\"\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	julian_date = pipe.read().strip();
	pipe.close();

	import re;

	input_date = input_dem_tif_path[re.search("\d{14}",input_dem_tif_path).start(0) : re.search("\d{14}",input_dem_tif_path).end(0)];

	year   = input_date[0:4];
	month  = input_date[4:6];
	day    = input_date[6:8];
	hour   = input_date[8:10];
	minute = input_date[10:12];
	second = input_date[12:];

	cmd  = "\ndate +\"%s\" -d \"" + year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second + "\"\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	aster_secs = pipe.read().strip();
	pipe.close();

	cmd  = "\ndate +\"%s\" -d \"" + year + "-01-01 00:00:00\"\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	aster_year_secs = pipe.read().strip();
	pipe.close();

	aster_date = str(float(year) + (float(aster_secs) - float(aster_year_secs)) / (24.0 * 60.0 * 60.0 * 365.25));

	days_from_julian = str((float(aster_secs) - float(julian_date)) / (24.0 * 60.0 * 60.0));

	input_dem_diff_tif_path = input_dem_tif_path[ : input_dem_tif_path.rfind(".")] + "_diff.tif";

	assert os.path.exists(input_dem_diff_tif_path), "\n***** ERROR: " + input_dem_diff_tif_path + " does not exist\n";	

	cmd  = "\ngdal_calc.py -A " + input_dem_diff_tif_path + " --outfile=temp.tif --calc=\"A*(A>-100)\" --NoDataValue=\"" + NO_DATA + "\"\n";
	cmd += "\ngdal_calc.py -A temp.tif --outfile=temp2.tif --calc=\"A*(A<100)\" --NoDataValue=\"" + NO_DATA + "\"\n";
	subprocess.call(cmd,shell=True);

	os.remove("temp.tif");

	if os.path.exists("temp.tif.aux.xml"):
		os.remove("temp.tif.aux.xml");

	cmd  = "\ngdalinfo -stats temp2.tif\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();	

	stdev = info[re.search("STATISTICS_STDDEV\s*=\s*",info).end(0) : re.search("STATISTICS_STDDEV\s*=\s*\d+\.*\d*",info).end(0)];
	mean  = info[re.search("STATISTICS_MEAN\s*=\s*",info).end(0) : re.search("STATISTICS_MEAN\s*=\s*\-*\d+\.*\d*\e*\-*\d*",info).end(0)];

	upper_bound = str(float(mean) + 2 * float(stdev));
	lower_bound = str(float(mean) - 2 * float(stdev));

	cmd  = "\ngdal_calc.py -A temp2.tif --outfile=temp.tif --calc=\"(A*(A>" + lower_bound + "))\" --NoDataValue=\"" + NO_DATA + "\"\n";
	cmd += "\ngdal_calc.py -A temp.tif --outfile=temp3.tif --calc=\"(A*(A<" + upper_bound + "))\" --NoDataValue=\"" + NO_DATA + "\"\n";
	subprocess.call(cmd,shell=True);

	os.remove("temp.tif");

	if os.path.exists("temp.tif.aux.xml"):
		os.remove("temp.tif.aux.xml");
		
	os.remove("temp2.tif");

	if os.path.exists("temp2.tif.aux.xml"):
		os.remove("temp2.tif.aux.xml");
		
	cmd  = "\ngdalinfo -stats temp3.tif\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	stdev = info[re.search("STATISTICS_STDDEV\s*=\s*",info).end(0) : re.search("STATISTICS_STDDEV\s*=\s*\d+\.*\d*",info).end(0)];
	mean  = info[re.search("STATISTICS_MEAN\s*=\s*",info).end(0) : re.search("STATISTICS_MEAN\s*=\s*\-*\d+\.*\d*\e*\-*\d*",info).end(0)];

	os.remove("temp3.tif");

	if os.path.exists("temp3.tif.aux.xml"):
		os.remove("temp3.tif.aux.xml");

	print(mean, stdev);

	cmd  = "\ngdalinfo " + input_dem_tif_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	input_zone = info[re.search("UTM\s*zone\s*",info).end(0) : re.search("UTM\s*zone\s*\d+",info).end(0)];
	input_type = info[re.search("Type\s*=\s*",info).end(0) : re.search("Type\s*=\s*\S+",info).end(0)].replace(",","");
	input_res  = info[re.search("Pixel\s*Size\s*=\s*\(\s*",info).end(0) : re.search("Pixel\s*Size\s*=\s*\(\s*\d+\.*\d*",info).end(0)];
	input_res  = input_res[ : re.search("0+$",input_res).start(0)];

	input_no_data = NO_DATA;

	if not re.search("NoData",info):
		cmd = "\ngdal_edit.py " + input_dem_tif_path + " -a_nodata " + NO_DATA + "\n";
		subprocess.call(cmd,shell=True);

	else:
		input_no_data = info[re.search("NoData\s*Value\s*=\s*",info).end(0) : re.search("NoData\s*Value\s*=\s*\S+",info).end(0)];

	input_ns = info[re.search("UTM\s*zone\s*\d+",info).end(0) : re.search("UTM\s*zone\s*\d+[A-Z]",info).end(0)];

	if input_ns.lower().find("n") > -1:
		input_ns = "north";

	else:
		input_ns = "south";

	input_ul_x = info[re.search("Upper Left\s*\(\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	input_ul_y = info[re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	input_ur_x = info[re.search("Upper Right\s*\(\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	input_ur_y = info[re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	input_lr_x = info[re.search("Lower Right\s*\(\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	input_lr_y = info[re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	input_ll_x = info[re.search("Lower Left\s*\(\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	input_ll_y = info[re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	cmd  = "\ngdalinfo " + ref_dem_tif_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	ref_zone = info[re.search("UTM\s*zone\s*",info).end(0) : re.search("UTM\s*zone\s*\d+",info).end(0)];
	ref_type = info[re.search("Type\s*=\s*",info).end(0) : re.search("Type\s*=\s*\S+",info).end(0)].replace(",","");
	ref_res  = info[re.search("Pixel\s*Size\s*=\s*\(\s*",info).end(0) : re.search("Pixel\s*Size\s*=\s*\(\s*\d+\.*\d*",info).end(0)];
	ref_res  = ref_res[ : re.search("0+$",ref_res).start(0)];
	ref_no_data = info[re.search("NoData\s*Value\s*=\s*",info).end(0) : re.search("NoData\s*Value\s*=\s*\S+",info).end(0)];

	ref_ns   = info[re.search("UTM\s*zone\s*\d+",info).end(0) : re.search("UTM\s*zone\s*\d+[A-Z]",info).end(0)];

	if ref_ns.lower().find("n") > -1:
		ref_ns = "north";

	else:
		ref_ns = "south";

	ref_ul_x = info[re.search("Upper Left\s*\(\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	ref_ul_y = info[re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	ref_ur_x = info[re.search("Upper Right\s*\(\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	ref_ur_y = info[re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	ref_lr_x = info[re.search("Lower Right\s*\(\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	ref_lr_y = info[re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	ref_ll_x = info[re.search("Lower Left\s*\(\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	ref_ll_y = info[re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	ref_decimal_x = "";

	if ref_ul_x.find(".") > -1:
		ref_decimal_x = ref_ul_x[ref_ul_x.rfind(".") + 1 : ];

	ref_decimal_y = "";

	if ref_ul_y.find(".") > -1:
		ref_decimal_y = ref_ul_y[ref_ul_y.rfind(".") + 1 : ];

	cmd = "\necho \"" + input_ul_x + " " + input_ul_y + "\n" + input_ur_x + " " + input_ur_y + "\n" + input_lr_x + " " + input_lr_y + "\n" + input_ll_x + " " + input_ll_y + "\" | /usr/local/gmt/bin/mapproject -Ju" + input_zone + "X/1:1 -F -C -I | /usr/local/gmt/bin/mapproject -Ju" + ref_zone + "X/1:1 -F -C\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	reproj_coords = info.split();

	input_ul_x = reproj_coords[0];
	input_ul_y = reproj_coords[1];
	input_ur_x = reproj_coords[2];
	input_ur_y = reproj_coords[3];
	input_lr_x = reproj_coords[4];
	input_lr_y = reproj_coords[5];
	input_ll_x = reproj_coords[6];
	input_ll_y = reproj_coords[7];

	new_ul_x = str(float(input_ul_x) - abs(float(input_ul_x) - float(ref_ul_x)) % int(ref_res.replace(".",""))); 
	new_ul_y = str(float(input_ul_y) + abs(float(input_ul_y) - float(ref_ul_y)) % int(ref_res.replace(".",""))); 
	new_ur_x = str(float(input_ur_x) + abs(float(input_ur_x) - float(ref_ur_x)) % int(ref_res.replace(".",""))); 
	new_ur_y = str(float(input_ur_y) + abs(float(input_ur_y) - float(ref_ur_y)) % int(ref_res.replace(".",""))); 
	new_lr_x = str(float(input_lr_x) + abs(float(input_lr_x) - float(ref_lr_x)) % int(ref_res.replace(".",""))); 
	new_lr_y = str(float(input_lr_y) - abs(float(input_lr_y) - float(ref_lr_y)) % int(ref_res.replace(".",""))); 
	new_ll_x = str(float(input_ll_x) - abs(float(input_ll_x) - float(ref_ll_x)) % int(ref_res.replace(".",""))); 
	new_ll_y = str(float(input_ll_y) - abs(float(input_ll_y) - float(ref_ll_y)) % int(ref_res.replace(".",""))); 

	print(new_ul_x,new_ul_y,new_ur_x,new_ur_y,new_lr_x,new_lr_y,new_ll_x,new_ll_y);

	if abs(float(new_ul_x) - float(new_lr_x)) % 120. > 0.000001 or abs(float(new_ul_y) - float(new_lr_y)) % 120. > 0.000001:
		print("\n***** ERROR calculating bounds for resampled input image, exiting...\n");
		return;

	cmd  = "\ngdalwarp -ot " + ref_type + " -of GTiff -srcnodata \"" + NO_DATA + " 0\" -dstnodata \"NaN\" -t_srs '+proj=utm +datum=WGS84 +zone=" + ref_zone + " +" + ref_ns + "' -te " + new_ul_x + " " + new_lr_y + " " + new_lr_x + " " + new_ul_y + " -tr " + ref_res.replace(".","") + " " + ref_res.replace(".","") + " -r cubic " + input_dem_tif_path + " temp.tif\n";
	cmd += "\ngdal_translate -of GMT temp.tif temp.grd\n";
	cmd += "\ngrd2xyz temp.grd | gawk '$0 !~ /a/ {print $1\" \"$2\" \"$3\" " + aster_date + " " + stdev + "\"}' > " + input_dem_tif_path[input_dem_tif_path.rfind("/") + 1 : input_dem_tif_path.rfind(".tif")] + ".txt\n";
	subprocess.call(cmd,shell=True);

	os.remove("temp.tif");

	if os.path.exists("temp.tif.aux.xml"):
		os.remove("temp.tif.aux.xml");

	os.remove("temp.grd");

	if os.path.exists("temp.grd.aux.xml"):
		os.remove("temp.grd.aux.xml");

	


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: resamp.py requires 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	resamp(sys.argv[1], sys.argv[2]);

	exit();

