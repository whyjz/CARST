#!/usr/bin/python


# geoTiffDiff.py
# Author: Andrew Kenneth Melkonian
# All Rights Reserved


def geoTiffDiff(ref_tif_path, search_tif_path, output_path):

	import math;
	import os;
	import re;
	import subprocess;

	cmd = "\ngdalinfo " + ref_tif_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	r_ul_x = info[re.search("Upper Left\s*\(\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	r_ul_y = info[re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	r_ur_x = info[re.search("Upper Right\s*\(\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	r_ur_y = info[re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	r_lr_x = info[re.search("Lower Right\s*\(\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	r_lr_y = info[re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	r_ll_x = info[re.search("Lower Left\s*\(\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	r_ll_y = info[re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	ref_res     = info[re.search("Pixel\s*Size\s*=\s*\(\s*",info).end(0) : re.search("Pixel\s*Size\s*=\s*\(\s*\d+\.*\d*",info).end(0)];
	ref_no_data = "-9999";

	if re.search("NoData\s*Value\s*=\s*",info):
		ref_no_data = info[re.search("NoData\s*Value\s*=\s*",info).end(0) : re.search("NoData\s*Value\s*=\s*\S+",info).end(0)];

	cmd = "\ngdalinfo " + search_tif_path + "\n";
        pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
        info = pipe.read();
        pipe.close();

        s_ul_x = info[re.search("Upper Left\s*\(\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
        s_ul_y = info[re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
        s_ur_x = info[re.search("Upper Right\s*\(\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
        s_ur_y = info[re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
        s_lr_x = info[re.search("Lower Right\s*\(\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
        s_lr_y = info[re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
        s_ll_x = info[re.search("Lower Left\s*\(\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
        s_ll_y = info[re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	search_res     = info[re.search("Pixel\s*Size\s*=\s*\(\s*",info).end(0) : re.search("Pixel\s*Size\s*=\s*\(\s*\d+\.*\d*",info).end(0)];
	search_no_data = "-9999";

	if re.search("NoData\s*Value\s*=\s*",info):
		search_no_data = info[re.search("NoData\s*Value\s*=\s*",info).end(0) : re.search("NoData\s*Value\s*=\s*\S+",info).end(0)];

	ul_x = str(float(r_ul_x) - math.floor((float(r_ul_x) - max(float(r_ul_x), float(s_ul_x))) / float(ref_res)) * float(ref_res));
	lr_x = str(float(r_ur_x) - math.floor((float(r_ur_x) - min(float(r_ur_x), float(s_ur_x))) / float(ref_res)) * float(ref_res));
	lr_y = str(float(r_ll_y) - math.floor((float(r_ll_y) - max(float(r_ll_y), float(s_ll_y))) / float(ref_res)) * float(ref_res));
	ul_y = str(float(r_ul_y) - math.floor((float(r_ul_y) - min(float(r_ul_y), float(s_ul_y))) / float(ref_res)) * float(ref_res));	

	ref_res = ref_res[ : re.search("\.0*$", ref_res).start(0)];

#	print("gdalwarp -of GTiff -te " + ul_x + " " + lr_y + " " + lr_x + " " + ul_y + " -tr " + ref_res + " " + ref_res + " -r cubic -srcnodata \"0\" -dstnodata \"nan\" " + search_tif_path + " " + search_tif_path.replace("DEM_orig","DEM_21m"));
#	return;

	temp_ref_path    = ref_tif_path[ : ref_tif_path.rfind(".")] + "_temp.tif";
	temp_search_path = search_tif_path[ : search_tif_path.rfind(".")] + "_temp.tif";

#	cmd  = "\ngdalwarp -of GTiff -te " + ul_x + " " + lr_y + " " + lr_x + " " + ul_y + " -tr " + ref_res + " " + ref_res + "  -r near -srcnodata \"" + ref_no_data + "\" -dstnodata \"-9999\" " + ref_tif_path + " " + temp_ref_path + "\n"; 
	cmd  = "\ngdalwarp -of GTiff -te " + ul_x + " " + lr_y + " " + lr_x + " " + ul_y + " -tr " + ref_res + " " + ref_res + " -srcnodata \"" + search_no_data + "\" -dstnodata \"-9999\" " + search_tif_path + " " + temp_search_path + "\n"; 
	cmd  += "\ngdalwarp -of GTiff -te " + ul_x + " " + lr_y + " " + lr_x + " " + ul_y + " -srcnodata \"nan\" -dstnodata \"-9999\" " + ref_tif_path + " " + temp_ref_path + "\n"; 
#	cmd += "\ngdalwarp -of GTiff -te " + ul_x + " " + lr_y + " " + lr_x + " " + ul_y + " -srcnodata \"" + search_no_data + "\" -dstnodata \"-9999\" " + search_tif_path + " " + temp_search_path + "\n"; 
	subprocess.call(cmd,shell=True);

	cmd =  "\ngdal_calc.py -A " + temp_ref_path + " -B " + temp_search_path + " --outfile=" + output_path + " --calc=\"A-B\" --NoDataValue=\"-9999\"\n";
	subprocess.call(cmd,shell=True);

	os.remove(temp_ref_path);
	os.remove(temp_search_path);

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 3, "\n***** ERROR: geoTiffDiff.py requires 3 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	geoTiffDiff(sys.argv[1], sys.argv[2], sys.argv[3]);

	exit();



