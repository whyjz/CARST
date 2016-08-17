#!/usr/bin/python


# asterToCarto.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def asterToCarto(ref_dem_tif_path, search_dem_tif_path):

	from geoTiffDiff import *;
	import os;
	import re;
	import subprocess;

	assert os.path.exists(ref_dem_tif_path), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(search_dem_tif_path), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";

	temp_file_list = [item for item in os.listdir(".") if re.search("^temp",item)];

	for item in temp_file_list:
		os.remove(item);

	NO_DATA  = "nan";
	MAX_ELEV = "2000";

	search_name = search_dem_tif_path[search_dem_tif_path.rfind("/") + 1 : re.search("003\d{14}_",search_dem_tif_path).end(0) - 1];
	search_name = search_name[re.search("_003\d{14}",search_name).start(0) + 4 : ];

	if search_name[0:2] != "19" or search_name[0:2] != "20":
		search_name = search_name[4:8] + search_name[0:2] + search_name[2:4] + search_name[8:14];

	cmd  = "\ngdalinfo " + ref_dem_tif_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	ref_no_data = info[re.search("NoData\s*Value\s*=\s*",info).end(0) : re.search("NoData\s*Value\s*=\s*\S+",info).end(0)]; 
	ref_zone    = info[re.search("UTM\s*zone\s*",info).end(0) : re.search("UTM\s*zone\s*\d+",info).end(0)];
	ref_type    = info[re.search("Type\s*=\s*",info).end(0) : re.search("Type\s*=\s*\S+",info).end(0)].replace(",","");
	ref_res     = info[re.search("Pixel\s*Size\s*=\s*\(\s*",info).end(0) : re.search("Pixel\s*Size\s*=\s*\(\s*\d+\.*\d*",info).end(0)];
	ref_res     = ref_res[ : re.search("0+$",ref_res).start(0)];
	
	if ref_res[len(ref_res) - 1] == ".":
		ref_res = ref_res[ : len(ref_res) - 1];

	cmd = "\ngdalwarp -srcnodata \"nan\" -dstnodata \"nan\" " + ref_dem_tif_path + " temp_ref.tif\n";
	subprocess.call(cmd,shell=True);

	
	cmd  = "\ngdalinfo " + search_dem_tif_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	search_zone = info[re.search("UTM\s*zone\s*",info).end(0) : re.search("UTM\s*zone\s*\d+",info).end(0)];
	search_ns   = info[re.search("UTM\s*zone\s*\d+",info).end(0) : re.search("UTM\s*zone\s*\d+[A-Z]",info).end(0)];

	if search_ns.lower().find("n") > -1:
		search_ns = "north";

	else:
		search_ns = "south";

	search_res  = info[re.search("Pixel\s*Size\s*=\s*\(\s*",info).end(0) : re.search("Pixel\s*Size\s*=\s*\(\s*\d+\.*\d*",info).end(0)];

	search_res = search_res[ : re.search("0+$",search_res).start(0)];
	
	if search_res[len(search_res) - 1] == ".":
		search_res = search_res[ : len(search_res) - 1];

	cmd  = "\ngdal_calc.py -A " + search_dem_tif_path + " --outfile=temp1.tif --calc=\"A*(A>0)\" --NoDataValue=0\n";
	cmd += "\ngdal_calc.py -A temp1.tif --outfile=temp2.tif --calc=\"A*(A<" + MAX_ELEV + ")\" --NoDataValue=0\n";
	cmd += "\ngdalwarp -ot " + ref_type + " -srcnodata \"0\" -dstnodata \"nan\" temp2.tif temp_search.tif\n";
	subprocess.call(cmd, shell=True);

	os.remove("temp1.tif");
	os.remove("temp2.tif");

	ref_at_search_res_tif = "temp_ref.tif";
	ref_at_search_res_grd = "temp_ref.grd";

	cmd = "\ngdalinfo temp_search.tif\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	ul_x = info[re.search("Upper Left\s*\(\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	ul_y = info[re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	ur_x = info[re.search("Upper Right\s*\(\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	ur_y = info[re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	lr_x = info[re.search("Lower Right\s*\(\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	lr_y = info[re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	ll_x = info[re.search("Lower Left\s*\(\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	ll_y = info[re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	xmin = str(min(float(ll_x), float(ul_x), float(lr_x), float(ur_x)));
	xmax = str(max(float(ll_x), float(ul_x), float(lr_x), float(ur_x)));
	ymin = str(min(float(ll_y), float(ul_y), float(lr_y), float(ur_y)));
	ymax = str(max(float(ll_y), float(ul_y), float(lr_y), float(ur_y)));
	
	if search_res != ref_res or search_zone != ref_zone:
		cmd = "\ngdalwarp -te " + xmin + " " + ymin + " " + xmax + " " + ymax + " -r cubic -tr " + search_res + " " + search_res + " -t_srs '+proj=utm +datum=WGS84 +zone=" + search_zone + " +" + search_ns + "' -srcnodata \"nan\" -dstnodata \"nan\" temp_ref.tif temp_ref_at_search_res.tif\n";
		subprocess.call(cmd, shell=True);
		ref_at_search_res_tif = "temp_ref_at_search_res.tif";
		ref_at_search_res_grd = "temp_ref_at_search_res.grd";

	geoTiffDiff("temp_search.tif", ref_at_search_res_tif, ".", "temp_diff.tif", NO_DATA);

	ref_at_search_res_clipped_tif = ref_at_search_res_tif[ : ref_at_search_res_tif.rfind(".")] + "_clipped.tif";

	cmd  = "\ngdal_translate -of GMT temp_diff.tif temp_diff.grd\n";
	cmd += "\ngdal_translate -of GMT " + ref_at_search_res_tif + " " + ref_at_search_res_grd + "\n";
	cmd += "\ngrdclip temp_diff.grd -Sb-100/NaN -Sa100/NaN -Gtemp_diff.grd\n";
	cmd += "\ngrdmath " + ref_at_search_res_grd + " temp_diff.grd OR --IO_NC4_CHUNK_SIZE=c = " + ref_at_search_res_grd + "\n";
	cmd += "\ngdalwarp -of GTiff -t_srs '+proj=utm +datum=WGS84 +zone=" + search_zone + " +" + search_ns + "' -srcnodata \"nan\" -dstnodata \"nan\" " + ref_at_search_res_grd + " " + ref_at_search_res_clipped_tif + "\n";
	subprocess.call(cmd, shell=True);

	if ref_at_search_res_tif == "temp_ref_at_search_res.tif":
		os.remove(ref_at_search_res_tif);

	os.remove(ref_at_search_res_grd);
	os.remove("temp_diff.tif");
	os.remove("temp_diff.grd");

	ast_tif_path = "ast_" + search_name + "_carto_aligned_DEM.tif";

	if not os.path.exists(ast_tif_path):
		cmd  = "\n/home/akm26/Public/StereoPipeline-2.4.2-2014-10-06-x86_64-Linux-GLIBC-2.5/bin/pc_align --max-displacement 120 --highest-accuracy --save-transformed-source-points -o temp_search_aligned " + ref_at_search_res_clipped_tif + " temp_search.tif\n";
#		cmd  = "\n/home/akm26/Public/StereoPipeline-2.4.2-2014-10-06-x86_64-Linux-GLIBC-2.5/bin/pc_align --max-displacement 120 --highest-accuracy --save-transformed-source-points -o temp_search_aligned temp_ref.tif temp_search.tif\n";
		cmd += "\n/home/akm26/Public/StereoPipeline-2.4.2-2014-10-06-x86_64-Linux-GLIBC-2.5/bin/point2dem --nodata-value NaN --t_srs '+proj=utm +datum=WGS84 +zone=" + search_zone + " +" + search_ns + "' -s " + search_res + " temp_search_aligned-trans_source.tif\n";
		cmd += "\nmv temp_search_aligned-trans_source-DEM.tif " + ast_tif_path + "\n";
		subprocess.call(cmd,shell=True);

	os.remove(ref_at_search_res_clipped_tif);

	cmd = "";

	if search_zone != ref_zone:
		cmd  = "\ngdalwarp -t_srs '+proj=utm +zone=" + ref_zone + " +" + search_ns + " +datum=WGS84' -r cubic -tr " + ref_res + " " + ref_res + " -srcnodata \"nan\" -dstnodata \"nan\" " + ast_tif_path + " temp1.tif\n";
		cmd += "\ngdalwarp -t_srs '+proj=utm +zone=" + ref_zone + " +" + search_ns + " +datum=WGS84' -r cubic -tr " + ref_res + " " + ref_res + " -srcnodata \"nan\" -dstnodata \"nan\" temp_search.tif temp2.tif\n";

	else:
		cmd  = "\ngdalwarp -r cubic -tr " + ref_res + " " + ref_res + " -srcnodata \"nan\" -dstnodata \"nan\" " + ast_tif_path + " temp1.tif\n";
		cmd += "\ngdalwarp -r cubic -tr " + ref_res + " " + ref_res + " -srcnodata \"nan\" -dstnodata \"nan\" temp_search.tif temp2.tif\n";

	subprocess.call(cmd,shell=True);

	ast_diff_tif_path         = "ast_" + search_name + "_carto_diff.tif";
	ast_diff_grd_path         = "ast_" + search_name + "_carto_diff.grd";
	ast_diff_ps_path          = "ast_" + search_name + "_carto_diff.ps";
	ast_aligned_diff_tif_path = "ast_" + search_name + "_carto_aligned_diff.tif";
	ast_aligned_diff_grd_path = "ast_" + search_name + "_carto_aligned_diff.grd";
	ast_aligned_diff_ps_path  = "ast_" + search_name + "_carto_aligned_diff.ps";

	geoTiffDiff("temp1.tif", "temp_ref.tif", ".", ast_aligned_diff_tif_path, NO_DATA);
	geoTiffDiff("temp2.tif", "temp_ref.tif", ".", ast_diff_tif_path, NO_DATA);

	os.remove("temp1.tif");
	os.remove("temp2.tif");

	cmd  = "\ngdal_translate -of GMT " + ast_aligned_diff_tif_path + " " + ast_aligned_diff_grd_path + "\n";
	cmd += "\ngdal_translate -of GMT " + ast_diff_tif_path + " " + ast_diff_grd_path + "\n";
	cmd += "\ngrd2xyz " + ast_aligned_diff_grd_path + " | gawk '$0 !~ /a/ && 3 > -100 && $3 < 100 {print $3}' | pshistogram -JX10c -W1 -R-100/100/0/2000 -Ba20g10:\"Difference (m)\":/a100g50:\"# of points\":WeSn -Gblack -P --LABEL_FONT_SIZE=14 > " + ast_aligned_diff_ps_path + "\n";
	cmd += "\ngrd2xyz " + ast_diff_grd_path + " | gawk '$0 !~ /a/ && 3 > -100 && $3 < 100 {print $3}' | pshistogram -JX10c -W1 -R-100/100/0/2000 -Ba20g10:\"Difference (m)\":/a100g50:\"# of points\":WeSn -Gblack -P --LABEL_FONT_SIZE=14 > " + ast_diff_ps_path + "\n";
	cmd += "\nps2raster -A -Tf " + ast_aligned_diff_ps_path + "\n";
	cmd += "\nps2raster -A -Tf " + ast_diff_ps_path + "\n";
	subprocess.call(cmd,shell=True);

	cmd  = "\ngrdclip " + ast_diff_grd_path + " -Sb-100/NaN -Sa100/NaN -G" + ast_diff_grd_path + "\n";
	cmd += "\ngrdclip " + ast_aligned_diff_grd_path + " -Sb-100/NaN -Sa100/NaN -G" + ast_aligned_diff_grd_path + "\n";
	subprocess.call(cmd, shell=True);

	cmd  = "\ngrdinfo -L2 " + ast_diff_grd_path + "\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	mean  = info[re.search("mean:\s*", info).end(0) : re.search("mean:\s*\-*\d+\.*\d*", info).end(0)];
	stdev = info[re.search("stdev:\s*", info).end(0) : re.search("stdev:\s*\-*\d+\.*\d*", info).end(0)];

	cmd  = "\ngrdinfo -L1 " + ast_diff_grd_path + "\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	median  = info[re.search("median:\s*", info).end(0) : re.search("median:\s*\-*\d+\.*\d*", info).end(0)];

	cmd  = "\ngrdinfo -L2 " + ast_aligned_diff_grd_path + "\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	a_mean  = info[re.search("mean:\s*", info).end(0) : re.search("mean:\s*\-*\d+\.*\d*", info).end(0)];
	a_stdev = info[re.search("stdev:\s*", info).end(0) : re.search("stdev:\s*\-*\d+\.*\d*", info).end(0)];

	cmd  = "\ngrdinfo -L1 " + ast_aligned_diff_grd_path + "\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	a_median  = info[re.search("median:\s*", info).end(0) : re.search("median:\s*\-*\d+\.*\d*", info).end(0)];

	outfile = open("ast_" + search_name + "_carto_aligned_stats.txt", "w");
	outfile.write("Median, mean, stdev BEFORE alignment: " + median + " " + mean + " " + stdev + "\nMedian, mean, stdev AFTER alignment: " + a_median + " " + a_mean + " " + a_stdev + "\n");
	outfile.close();
	
	os.remove(ast_aligned_diff_grd_path);
	os.remove(ast_diff_grd_path);

	if os.path.exists(ast_aligned_diff_grd_path + ".aux.xml"):
		os.remove(ast_aligned_diff_grd_path + ".aux.xml");
		os.remove(ast_diff_grd_path + ".aux.xml");

	temp_file_list = [item for item in os.listdir(".") if re.search("^temp",item)];

	for item in temp_file_list:
		os.remove(item);
	

	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: asterToCarto.py requires 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	asterToCarto(sys.argv[1], sys.argv[2]);

	exit();

