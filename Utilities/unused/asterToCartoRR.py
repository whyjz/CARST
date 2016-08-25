#!/usr/bin/python


# asterToCarto.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def asterToCarto(ref_dem_tif_path, search_dem_tif_path):

	from geoTiffDiff import *;
	import os;
	import re;
	from removeTrendDEM import *;
	import subprocess;

	assert os.path.exists(ref_dem_tif_path), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(search_dem_tif_path), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";

	temp_file_list = [item for item in os.listdir(".") if re.search("^temp",item)];

	for item in temp_file_list:
		os.remove(item);

	NO_DATA  = "nan";
	MIN_ELEV = "1";
	MAX_ELEV = "2500";

	search_name = search_dem_tif_path[search_dem_tif_path.rfind("/") + 1 : re.search("003\d{14}_",search_dem_tif_path).end(0) - 1];
	search_name = search_name[re.search("_003\d{14}",search_name).start(0) + 4 : ];

	if search_name[0:2] != "19" or search_name[0:2] != "20":
		search_name = search_name[4:8] + search_name[0:2] + search_name[2:4] + search_name[8:14];


#	Set up reference DEM for pc_align

	cmd  = "\ngdalinfo " + ref_dem_tif_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	ref_no_data = info[re.search("NoData\s*Value\s*=\s*",info).end(0) : re.search("NoData\s*Value\s*=\s*\S+",info).end(0)]; 
	ref_ns      = info[re.search("UTM\s*zone\s*\d+",info).end(0) : re.search("UTM\s*zone\s*\d+[A-Z]",info).end(0)];
	ref_zone    = info[re.search("UTM\s*zone\s*",info).end(0) : re.search("UTM\s*zone\s*\d+",info).end(0)];
	ref_type    = info[re.search("Type\s*=\s*",info).end(0) : re.search("Type\s*=\s*\S+",info).end(0)].replace(",","");
	ref_res     = info[re.search("Pixel\s*Size\s*=\s*\(\s*",info).end(0) : re.search("Pixel\s*Size\s*=\s*\(\s*\d+\.*\d*",info).end(0)];
	ref_res     = ref_res[ : re.search("0+$",ref_res).start(0)];
	
	if ref_res[len(ref_res) - 1] == ".":
		ref_res = ref_res[ : len(ref_res) - 1];

	if ref_ns.lower().find("n") > -1:
		ref_ns = "north";

	else:
		ref_ns = "south";

	cmd  = "\ngdal_calc.py -A " + ref_dem_tif_path + " --outfile=temp1.tif --calc=\"A*(A>" + MIN_ELEV + ")\" --NoDataValue=0\n";
	cmd += "\ngdalwarp -srcnodata \"0\" -dstnodata \"nan\" temp1.tif temp_ref.tif\n";
	subprocess.call(cmd,shell=True);

	os.remove("temp1.tif");


#	Set up search DEM for pc_align

	cmd  = "\ngdalinfo " + search_dem_tif_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	search_zone = info[re.search("UTM\s*zone\s*",info).end(0) : re.search("UTM\s*zone\s*\d+",info).end(0)];
	search_ns   = info[re.search("UTM\s*zone\s*\d+",info).end(0) : re.search("UTM\s*zone\s*\d+[A-Z]",info).end(0)];
	search_res = info[re.search("Pixel\s*Size\s*=\s*\(\s*",info).end(0) : re.search("Pixel\s*Size\s*=\s*\(\s*\d+\.*\d*",info).end(0)];
	search_res = search_res[ : re.search("0+$",search_res).start(0)];	

	if search_res[len(search_res) - 1] == ".":
		search_res = search_res[ : len(search_res) - 1];

	if search_ns.lower().find("n") > -1:
		search_ns = "north";

	else:
		search_ns = "south";

	cmd  = "\ngdal_calc.py -A " + search_dem_tif_path + " --outfile=temp1.tif --calc=\"A*(A>" + MIN_ELEV + ")\" --NoDataValue=0\n";
	cmd += "\ngdal_calc.py -A temp1.tif --outfile=temp2.tif --calc=\"A*(A<" + MAX_ELEV + ")\" --NoDataValue=0\n";
	cmd += "\ngdalwarp -ot " + ref_type + " -srcnodata \"0\" -dstnodata \"nan\" temp2.tif temp_search.tif\n";
	subprocess.call(cmd, shell=True);

	os.remove("temp1.tif");
	os.remove("temp2.tif");


#	Make reference DEM fitted to search grid

	search_at_ref_res_tif = "temp_search.tif";
	search_at_ref_res_grd = "temp_search.grd";

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
		cmd = "\ngdalwarp -r cubic -tr " + ref_res + " " + ref_res + " -t_srs '+proj=utm +datum=WGS84 +zone=" + ref_zone + " +" + ref_ns + "' -srcnodata \"nan\" -dstnodata \"nan\" temp_search.tif temp_search_at_ref_res.tif\n";
		subprocess.call(cmd, shell=True);
		search_at_ref_res_tif = "temp_search_at_ref_res.tif";
		search_at_ref_res_grd = "temp_search_at_ref_res.grd";

	geoTiffDiff(search_at_ref_res_tif, "temp_ref.tif", ".", "temp_diff.tif", NO_DATA);

	cmd  = "\ngdal_calc.py -A temp_diff.tif --outfile=temp1.tif --calc=\"A*(A>-75)*(A<75)\" --NoDataValue=0\n";
	cmd += "\ngdal_translate -of GMT temp1.tif temp_diff.grd\n";
	subprocess.call(cmd, shell=True);

	cmd = "\ngrdinfo -L1 temp_diff.grd\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	median = info[re.search("median:\s*", info).end(0) : re.search("median:\s*\-*\d+\.*\d*", info).end(0)];

	os.remove("temp1.tif");
	os.remove("temp_diff.tif");
	os.remove("temp_diff.grd");

	cmd = "\ngdal_calc.py -A " + search_at_ref_res_tif + " --outfile=temp1.tif --calc=\"A-(" + median + ")\" --NoDataValue=0\n"; 
	subprocess.call(cmd, shell=True);

	os.remove(search_at_ref_res_tif);
	os.rename("temp1.tif", search_at_ref_res_tif);

	ast_tif_path    = "ast_" + search_name + "_carto_aligned_DEM.tif";
	ast_grd_path    = "ast_" + search_name + "_carto_aligned_DEM.grd";
	ast_rr_tif_path = "ast_" + search_name + "_carto_aligned_DEM_rr.tif";
	ast_rr_grd_path = "ast_" + search_name + "_carto_aligned_DEM_rr.grd";

	if not os.path.exists(ast_tif_path):
		cmd  = "\n/home/akm26/Public/StereoPipeline-2.4.2-2014-10-06-x86_64-Linux-GLIBC-2.5/bin/pc_align --outlier-ratio 0.8 --max-displacement 1200 --highest-accuracy --save-transformed-source-points -o temp_search_aligned temp_ref.tif " + search_at_ref_res_tif + "\n";
		cmd += "\n/home/akm26/Public/StereoPipeline-2.4.2-2014-10-06-x86_64-Linux-GLIBC-2.5/bin/point2dem --nodata-value NaN --t_srs '+proj=utm +datum=WGS84 +zone=" + ref_zone + " +" + ref_ns + "' -s " + ref_res + " temp_search_aligned-trans_source.tif\n";
		cmd += "\nmv temp_search_aligned-trans_source-DEM.tif " + ast_tif_path + "\n";
		subprocess.call(cmd,shell=True);

	cmd = "";

	ast_diff_tif_path         = "ast_" + search_name + "_carto_diff.tif";
	ast_diff_grd_path         = "ast_" + search_name + "_carto_diff.grd";
	ast_diff_ps_path          = "ast_" + search_name + "_carto_diff.ps";
	ast_aligned_diff_tif_path = "ast_" + search_name + "_carto_aligned_diff.tif";
	ast_aligned_diff_grd_path = "ast_" + search_name + "_carto_aligned_diff.grd";
	ast_aligned_diff_ps_path  = "ast_" + search_name + "_carto_aligned_diff.ps";
	ast_rr_tif_path           = "ast_" + search_name + "_carto_aligned_DEM_rr.tif";
	ast_rr_grd_path           = "ast_" + search_name + "_carto_aligned_DEM_rr.grd";
	ast_rr_diff_tif_path      = "ast_" + search_name + "_carto_aligned_rr_diff.tif";
	ast_rr_diff_grd_path      = "ast_" + search_name + "_carto_aligned_rr_diff.grd";
	ast_rr_diff_ps_path       = "ast_" + search_name + "_carto_aligned_rr_diff.ps";

	geoTiffDiff(ast_tif_path, "temp_ref.tif", ".", ast_aligned_diff_tif_path, NO_DATA);
	geoTiffDiff(search_at_ref_res_tif, "temp_ref.tif", ".", ast_diff_tif_path, NO_DATA);

	cmd  = "\ngdal_translate -of GMT " + ast_tif_path + " " + ast_grd_path + "\n";
	cmd += "\ngdal_translate -of GMT " + ast_aligned_diff_tif_path + " " + ast_aligned_diff_grd_path + "\n";
	cmd += "\ngdal_translate -of GMT " + ast_diff_tif_path + " " + ast_diff_grd_path + "\n";
	cmd += "\ngrdclip " + ast_aligned_diff_grd_path + " -Sa75/NaN -Sb-75/NaN -Gtemp1.grd\n";
	subprocess.call(cmd, shell=True);

	removeTrendDEM(ast_grd_path, "temp1.grd");
	os.remove("temp1.grd");

	cmd  = "\ngrdmath " + ast_rr_grd_path + " 1 MUL --IO_NC4_CHUNK_SIZE=c = " + ast_rr_grd_path + "\n";
	cmd += "\ngdalwarp -of GTiff -t_srs '+proj=utm +datum=WGS84 +zone=" + ref_zone + " +" + ref_ns + "' -srcnodata \"nan\" -dstnodata \"nan\" " + ast_rr_grd_path + " " + ast_rr_tif_path + "\n";
	subprocess.call(cmd, shell=True);

	geoTiffDiff(ast_rr_tif_path, "temp_ref.tif", ".", ast_rr_diff_tif_path, NO_DATA);

	cmd = "\ngdal_translate -of GMT " + ast_rr_diff_tif_path + " " + ast_rr_diff_grd_path + "\n";
	subprocess.call(cmd, shell=True);


#	Get info on coregistered search DEM

	cmd  = "\ngrd2xyz " + ast_aligned_diff_grd_path + " | gawk '$0 !~ /a/ && 3 > -100 && $3 < 100 {print $3}' | pshistogram -JX10c -W1 -R-100/100/0/5000 -Ba20g10:\"Difference (m)\":/a500g500:\"# of points\":WeSn -Gblack -P --LABEL_FONT_SIZE=14 > " + ast_aligned_diff_ps_path + "\n";
	cmd += "\ngrd2xyz " + ast_rr_diff_grd_path + " | gawk '$0 !~ /a/ && 3 > -100 && $3 < 100 {print $3}' | pshistogram -JX10c -W1 -R-100/100/0/5000 -Ba20g10:\"Difference (m)\":/a500g500:\"# of points\":WeSn -Gblack -P --LABEL_FONT_SIZE=14 > " + ast_rr_diff_ps_path + "\n";
	cmd += "\ngrd2xyz " + ast_diff_grd_path + " | gawk '$0 !~ /a/ && 3 > -100 && $3 < 100 {print $3}' | pshistogram -JX10c -W1 -R-100/100/0/5000 -Ba20g10:\"Difference (m)\":/a500g500:\"# of points\":WeSn -Gblack -P --LABEL_FONT_SIZE=14 > " + ast_diff_ps_path + "\n";
	cmd += "\nps2raster -A -Tf " + ast_aligned_diff_ps_path + "\n";
	cmd += "\nps2raster -A -Tf " + ast_rr_diff_ps_path + "\n";
	cmd += "\nps2raster -A -Tf " + ast_diff_ps_path + "\n";
	subprocess.call(cmd,shell=True);

	cmd  = "\ngrdclip " + ast_diff_grd_path + " -Sb-100/NaN -Sa100/NaN -G" + ast_diff_grd_path + "\n";
	cmd += "\ngrdclip " + ast_aligned_diff_grd_path + " -Sb-100/NaN -Sa100/NaN -G" + ast_aligned_diff_grd_path + "\n";
	cmd += "\ngrdclip " + ast_rr_diff_grd_path + " -Sb-100/NaN -Sa100/NaN -G" + ast_rr_diff_grd_path + "\n";
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

	cmd  = "\ngrdinfo -L2 " + ast_rr_diff_grd_path + "\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	rr_mean  = info[re.search("mean:\s*", info).end(0) : re.search("mean:\s*\-*\d+\.*\d*", info).end(0)];
	rr_stdev = info[re.search("stdev:\s*", info).end(0) : re.search("stdev:\s*\-*\d+\.*\d*", info).end(0)];

	cmd  = "\ngrdinfo -L1 " + ast_rr_diff_grd_path + "\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	rr_median  = info[re.search("median:\s*", info).end(0) : re.search("median:\s*\-*\d+\.*\d*", info).end(0)];

	outfile = open("ast_" + search_name + "_carto_aligned_stats.txt", "w");
	outfile.write("Median, mean, stdev BEFORE alignment: " + median + " " + mean + " " + stdev + "\n");
	outfile.write("Median, mean, stdev AFTER alignment: " + a_median + " " + a_mean + " " + a_stdev + "\n");
	outfile.write("Median, mean, stdev AFTER ramp-removal: " + rr_median + " " + rr_mean + " " + rr_stdev + "\n");
	outfile.close();
	
	os.remove(ast_grd_path);
	os.remove(ast_rr_grd_path);
	os.remove(ast_aligned_diff_grd_path);
	os.remove(ast_rr_diff_grd_path);
	os.remove(ast_diff_grd_path);

	if os.path.exists(ast_aligned_diff_grd_path + ".aux.xml"):
		os.remove(ast_aligned_diff_grd_path + ".aux.xml");
		os.remove(ast_grd_path + ".aux.xml");
		os.remove(ast_rr_diff_grd_path + ".aux.xml");
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

