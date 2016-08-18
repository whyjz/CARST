#!/usr/bin/python


# geoTiffOverlap.py
# Author: Andrew Kenneth Melkonian
# All Rights Reserved


def geoTiffOverlap(input1_tif_path, input2_tif_path, output_res, input_nodata_val, area_threshold):

	lowres1_tif_path = input1_tif_path[ : input1_tif_path.rfind(".")] + "_lowres.tif";
	lowres2_tif_path = input2_tif_path[ : input2_tif_path.rfind(".")] + "_lowres.tif";


	import subprocess;

	cmd = "\ngdalinfo " + input1_tif_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	import re;

	ul_1_x = info[re.search("Upper Left\s*\(\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	ul_1_y = info[re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	ur_1_x = info[re.search("Upper Right\s*\(\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	ur_1_y = info[re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	lr_1_x = info[re.search("Lower Right\s*\(\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	lr_1_y = info[re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	ll_1_x = info[re.search("Lower Left\s*\(\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	ll_1_y = info[re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	cmd = "\ngdalinfo " + input2_tif_path + "\n";
        pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
        info = pipe.read();
        pipe.close();

        import re;

        ul_2_x = info[re.search("Upper Left\s*\(\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
        ul_2_y = info[re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
        ur_2_x = info[re.search("Upper Right\s*\(\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
        ur_2_y = info[re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
        lr_2_x = info[re.search("Lower Right\s*\(\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
        lr_2_y = info[re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
        ll_2_x = info[re.search("Lower Left\s*\(\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
        ll_2_y = info[re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	ul_x = str(max([float(ul_1_x), float(ul_2_x)]));
	ul_y = str(min([float(ul_1_y), float(ul_2_y)]));
	lr_x = str(min([float(lr_1_x), float(lr_2_x)]));
	lr_y = str(max([float(lr_1_y), float(lr_2_y)]));


	if not os.path.exists(lowres1_tif_path):
		cmd = "\ngdalwarp -r near -tr " + output_res + " " + output_res + " -srcnodata " + input_nodata_val + " -dstnodata NaN -q " + input1_tif_path + " " + lowres1_tif_path + "\n";
		subprocess.call(cmd,shell=True);

	if not os.path.exists(lowres2_tif_path):
		cmd = "\ngdalwarp -r near -tr " + output_res + " " + output_res + " -srcnodata " + input_nodata_val + " -dstnodata NaN -q " + input2_tif_path + " " + lowres2_tif_path + "\n";
		subprocess.call(cmd,shell=True);

	output1_cut = lowres1_tif_path[ : lowres1_tif_path.rfind(".")] + "_cut.tif";
	output2_cut = lowres2_tif_path[ : lowres2_tif_path.rfind(".")] + "_cut.tif";

	cmd  = "\ngdal_translate -projwin " + ul_x + " " + ul_y + " " + lr_x + " " + lr_y + " -q " + lowres1_tif_path + " " + output1_cut + "\n";
	cmd += "\ngdal_translate -projwin " + ul_x + " " + ul_y + " " + lr_x + " " + lr_y + " -q " + lowres2_tif_path + " " + output2_cut + "\n";
	subprocess.call(cmd,shell=True);

	if not os.path.exists("overlap_error_report.txt"):
		outfile = open("overlap_error_report.txt","w");
		outfile.write("");
		outfile.close();

	if not os.path.exists(output1_cut) or not os.path.exists(output2_cut):
		outfile = open("overlap_error_report.txt","a");
		outfile.write(input1_tif_path + " " + input2_tif_path + "\n");
		outfile.close();
		return;	

	cmd = "\ngdal_calc.py -A " + output1_cut + " -B " + output2_cut + " --outfile=temp.tif --calc=\"(A+B)>0\" --NoDataValue=0\n";
	subprocess.call(cmd,shell=True);

	if not os.path.exists("temp.tif"):
		os.remove(output1_cut);
		os.remove(output1_cut + ".aux.xml");
		os.remove(output2_cut);
		os.remove(output2_cut + ".aux.xml");
		outfile = open("overlap_error_report.txt","a");
		outfile.write(input1_tif_path + " " + input2_tif_path + " temp.tif does not exist\n");
		outfile.close();
		return;

	cmd = "\ngdal_translate -of GMT -q temp.tif temp.grd\n";
	subprocess.call(cmd,shell=True);

	cmd = "\ngrdvolume temp.grd\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().split();
	pipe.close();

	if len(info) < 2:	
		os.remove("temp.tif");
		os.remove("temp.grd");
		os.remove("temp.grd.aux.xml");
		os.remove(output1_cut);
		os.remove(output1_cut + ".aux.xml");
		os.remove(output2_cut);
		os.remove(output2_cut + ".aux.xml");
		outfile = open("overlap_error_report.txt","a");
		outfile.write(input1_tif_path + " " + input2_tif_path + " grdvolume error\n");
		outfile.close();
		return;	

	area = info[1];

	if float(area)/1e6 > float(area_threshold):
		print(input1_tif_path + " " + input2_tif_path + " " + str(float(area)/1e6));

	os.remove("temp.tif");
	os.remove("temp.grd");
	os.remove("temp.grd.aux.xml");
	os.remove(output1_cut);

	if os.path.exists(output1_cut + ".aux.xml"):
		os.remove(output1_cut + ".aux.xml");

	os.remove(output2_cut);

	if os.path.exists(output2_cut + ".aux.xml"):
		os.remove(output2_cut + ".aux.xml");


	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 5, "\n***** ERROR: geoTiffOverlap.py requires 5 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	geoTiffOverlap(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]);

	exit();



exit();
