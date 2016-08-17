#!/usr/bin/python


# asterToCarto.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def asterToCarto(ref_dem_tif_path, search_dem_tif_path):

	from geoTiffDiff import *;
	import math;
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
	MIN_ELEV = "10";
	MAX_ELEV = "4000";
	MIN_DIFF = "-75";
	MAX_DIFF = "75";

	search_name = search_dem_tif_path[search_dem_tif_path.rfind("/") + 1 : re.search("003\d{14}_",search_dem_tif_path).end(0) - 1];
	search_name = search_name[re.search("_003\d{14}",search_name).start(0) + 4 : ];

	if search_name[0:2] != "19" or search_name[0:2] != "20":
		search_name = search_name[4:8] + search_name[0:2] + search_name[2:4] + search_name[8:14];

	cmd  = "\ngdalinfo " + search_dem_tif_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	s_ul_x = info[re.search("Upper Left\s*\(\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	s_ul_y = info[re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	s_ur_x = info[re.search("Upper Right\s*\(\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	s_ur_y = info[re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	s_lr_x = info[re.search("Lower Right\s*\(\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	s_lr_y = info[re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	s_ll_x = info[re.search("Lower Left\s*\(\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	s_ll_y = info[re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	search_no_data = "-9999";

	if info.find("NoData") > -1:
		search_no_data = info[re.search("NoData\s*Value\s*=\s*",info).end(0) : re.search("NoData\s*Value\s*=\s*\S+",info).end(0)]; 

	search_zone   = info[re.search("UTM\s*zone\s*",info).end(0) : re.search("UTM\s*zone\s*\d+",info).end(0)];
	search_res    = info[re.search("Pixel\s*Size\s*=\s*\(\s*",info).end(0) : re.search("Pixel\s*Size\s*=\s*\(\s*\d+\.*\d*",info).end(0)];
	search_res    = search_res[ : re.search("0+$",search_res).start(0)];	

	search_ns     = info[re.search("UTM\s*zone\s*\d+",info).end(0) : re.search("UTM\s*zone\s*\d+[A-Z]",info).end(0)];
	search_gmt_ns = "+";

	if search_res[len(search_res) - 1] == ".":
		search_res = search_res[ : len(search_res) - 1];

	if search_ns.lower().find("n") > -1:
		search_ns = "north";
		search_gmt_ns = "+";

	else:
		search_ns = "south";
		search_gmt_ns = "-";


#	Set up reference DEM for pc_align

	cmd  = "\ngdalinfo " + ref_dem_tif_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	r_ul_x = info[re.search("Upper Left\s*\(\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	r_ul_y = info[re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	r_ur_x = info[re.search("Upper Right\s*\(\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	r_ur_y = info[re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	r_lr_x = info[re.search("Lower Right\s*\(\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	r_lr_y = info[re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	r_ll_x = info[re.search("Lower Left\s*\(\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	r_ll_y = info[re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	ref_no_data = info[re.search("NoData\s*Value\s*=\s*",info).end(0) : re.search("NoData\s*Value\s*=\s*\S+",info).end(0)]; 
	ref_type    = info[re.search("Type\s*=\s*",info).end(0) : re.search("Type\s*=\s*\S+",info).end(0)].replace(",","");
	ref_res     = info[re.search("Pixel\s*Size\s*=\s*\(\s*",info).end(0) : re.search("Pixel\s*Size\s*=\s*\(\s*\d+\.*\d*",info).end(0)];
	ref_res     = ref_res[ : re.search("0+$",ref_res).start(0)];

	if ref_res[len(ref_res) - 1] == ".":
		ref_res = ref_res[ : len(ref_res) - 1];

	ref_zone    = "";
	ref_ns      = "";
	ref_gmt_ns  = "";

	if info.find("UTM") > -1:

		ref_zone = info[re.search("UTM\s*zone\s*",info).end(0) : re.search("UTM\s*zone\s*\d+",info).end(0)];

		ref_ns   = info[re.search("UTM\s*zone\s*\d+",info).end(0) : re.search("UTM\s*zone\s*\d+[A-Z]",info).end(0)];

		if search_ns.lower().find("n") > -1:
			ref_ns = "north";
			ref_gmt_ns = "+";

		else:
			ref_ns = "south";
			ref_gmt_ns = "-";


	if info.find("UTM") < 0 or ref_zone != search_zone:

		ref_dem_utm_tif_path = ref_dem_tif_path[ : ref_dem_tif_path.rfind(".")] + "_utm" + search_zone + ".tif";

		cmd  = "\necho \"" + r_ul_x + " " + r_ul_y + "\\n" + r_ur_x + " " + r_ur_y + "\\n" + r_lr_x + " " + r_lr_y + "\\n" + r_ll_x + " " + r_ll_y + "\" | mapproject -Ju" + search_gmt_ns + search_zone + "/1:1 -F -C\n";

		if ref_zone:
			cmd = "\necho \"" + r_ul_x + " " + r_ul_y + "\\n" + r_ur_x + " " + r_ur_y + "\\n" + r_lr_x + " " + r_lr_y + "\\n" + r_ll_x + " " + r_ll_y + "\" | mapproject -Ju" + ref_gmt_ns + ref_zone + "/1:1 -F -C -I | mapproject -Ju" + search_gmt_ns + search_zone + "/1:1 -F -C\n";

		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		r_ul_x, r_ul_y, r_ur_x, r_ur_y, r_lr_x, r_lr_y, r_ll_x, r_ll_y = pipe.read().strip().split();
		pipe.close();

#	xmin = str(max(float(r_ul_x), float(r_ll_x), float(s_ul_x), float(s_ll_x)));
#	xmax = str(min(float(r_ur_x), float(r_lr_x), float(s_ur_x), float(s_lr_x)));
#	ymin = str(max(float(r_ll_y), float(r_lr_y), float(s_ll_y), float(s_lr_y)));
#	ymax = str(min(float(r_ul_y), float(r_ur_y), float(s_ul_y), float(s_ur_y)));	

	xmin = str(float(r_ul_x) - math.floor((float(r_ul_x) - max(float(r_ul_x), float(s_ul_x))) / float(ref_res)) * float(ref_res));
	xmax = str(float(r_ur_x) - math.floor((float(r_ur_x) - min(float(r_ur_x), float(s_ur_x))) / float(ref_res)) * float(ref_res));
	ymin = str(float(r_ll_y) - math.floor((float(r_ll_y) - max(float(r_ll_y), float(s_ll_y))) / float(ref_res)) * float(ref_res));
	ymax = str(float(r_ul_y) - math.floor((float(r_ul_y) - min(float(r_ul_y), float(s_ul_y))) / float(ref_res)) * float(ref_res));	

#	print(xmin, xmax, ymin, ymax);

	cmd  = "\ngdalwarp -of GTiff -te " + xmin + " " + ymin + " " + xmax + " " + ymax + " -srcnodata \"" + ref_no_data + "\" -dstnodata \"nan\" " + ref_dem_tif_path + " temp_ref.tif\n";
	cmd += "\ngdalwarp -of GTiff -t_srs '+proj=utm +zone=" + ref_zone + " +datum=WGS84 +" + ref_ns + "' -te " + xmin + " " + ymin + " " + xmax + " " + ymax + " -tr " + ref_res + " " + ref_res + " -r near -srcnodata \"" + search_no_data + "\" -dstnodata \"nan\" " + search_dem_tif_path + " temp_search.tif\n";
	subprocess.call(cmd, shell=True);

	diff_before_tif_path  = "ast_" + search_name + "_diff_before.tif";
	diff_before_grd_path  = "ast_" + search_name + "_diff_before.grd";
	diff_before_hist_path = "ast_" + search_name + "_diff_before_hist.ps";

	cmd  = "\ngdal_calc.py -A temp_search.tif -B temp_ref.tif --outfile=" + diff_before_tif_path + " --calc=\"A-B\" --NoDataValue=-9999\n";
	cmd += "\ngdal_translate -of GMT " + diff_before_tif_path + " " + diff_before_grd_path + "\n"; 
	cmd += "\ngrdclip " + diff_before_grd_path + " -Sb-100/NaN -Sa100/NaN -Gtemp_diff1.grd\n";
	subprocess.call(cmd, shell=True);

	cmd  = "\ngrdinfo -L2 temp_diff1.grd\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	mean = info[re.search("mean:\s*", info).end(0) : re.search("mean:\s*\-*\d+\.*\d*", info).end(0)];
	sdev = info[re.search("stdev:\s*", info).end(0) : re.search("stdev:\s*\-*\d+\.*\d*", info).end(0)];

	cmd  = "\ngrdinfo -L1 temp_diff1.grd\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	median = info[re.search("median:\s*", info).end(0) : re.search("median:\s*\-*\d+\.*\d*", info).end(0)];

	plus_2sigma  = str(float(mean) + 2 * float(sdev));
	minus_2sigma = str(float(mean) - 2 * float(sdev));

	cmd = "\ngrdclip temp_diff1.grd -Sb" + minus_2sigma + "/NaN -Sa" + plus_2sigma + "/NaN -Gtemp_diff2.grd\n";
	subprocess.call(cmd, shell=True);

	cmd  = "\ngrdinfo -L2 temp_diff2.grd\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	mean_2sigma = info[re.search("mean:\s*", info).end(0) : re.search("mean:\s*\-*\d+\.*\d*", info).end(0)];
	sdev_2sigma = info[re.search("stdev:\s*", info).end(0) : re.search("stdev:\s*\-*\d+\.*\d*", info).end(0)];

	cmd  = "\ngrdinfo -L1 temp_diff2.grd\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	median_2sigma = info[re.search("median:\s*", info).end(0) : re.search("median:\s*\-*\d+\.*\d*", info).end(0)];

	cmd  = "\ngrd2xyz " + diff_before_grd_path + " | gawk '$0 !~ /a/ && 3 > -100 && $3 < 100 {print $3}' | pshistogram -JX10c -W1 -R-100/100/0/10000 -Ba20g10:\"Difference (m)\":/a2500g2500:\"# of points\":WeSn -Gblack --FONT_LABEL=14p,1,black --FONT_ANNOT_PRIMARY=14p,1,black --FONT_ANNOT_SECONDARY=14p,1,black -P -K > " + diff_before_hist_path + "\n";
	cmd += "\necho \"" + minus_2sigma + " 0\\n" + minus_2sigma + " 10000\" | psxy -J -R -W1p,cyan -O -K >> " + diff_before_hist_path + "\n";
	cmd += "\necho \"" + plus_2sigma + " 0\\n" + plus_2sigma + " 10000\" | psxy -J -R -W1p,cyan -O -K >> " + diff_before_hist_path + "\n";
	cmd += "\necho \"" + mean + " 0\\n" + mean + " 10000\" | psxy -J -R -W1p,red -O -K >> " + diff_before_hist_path + "\n";
	cmd += "\necho \"" + str(float(mean_2sigma) - 2 * float(sdev_2sigma)) + " 0\\n" + str(float(mean_2sigma) - 2 * float(sdev_2sigma)) + " 10000\" | psxy -J -R -W1p,blue -O -K >> " + diff_before_hist_path + "\n";
	cmd += "\necho \"" + str(float(mean_2sigma) + 2 * float(sdev_2sigma)) + " 0\\n" + str(float(mean_2sigma) + 2 * float(sdev_2sigma)) + " 10000\" | psxy -J -R -W1p,blue -O -K >> " + diff_before_hist_path + "\n";
	cmd += "\necho \"" + mean_2sigma + " 0\\n" + mean_2sigma + " 10000\" | psxy -J -R -W1p,maroon -O >> " + diff_before_hist_path + "\n";
	cmd += "\nps2raster -A -Tf " + diff_before_hist_path + "\n";
	subprocess.call(cmd, shell=True);

	os.remove("temp_diff1.grd");
	os.remove("temp_diff2.grd");
	os.remove(diff_before_grd_path);
	os.remove(diff_before_hist_path);

#	cmd  = "\ngdal_calc.py -A temp_ref.tif --outfile=temp1.tif --calc=\"A*(A>" + MIN_ELEV + ")*(A<" + MAX_ELEV + ")\" --NoDataValue=0\n";
#	cmd += "\ngdalwarp -srcnodata \"0\" -dstnodata \"nan\" temp1.tif temp_ref_clipped.tif\n";
#	subprocess.call(cmd,shell=True);

#	os.remove("temp_ref.tif");
#	os.remove("temp1.tif");

#	cmd  = "\ngdal_calc.py -A temp_search.tif --outfile=temp1.tif --calc=\"A*(A>" + MIN_ELEV + ")*(A<" + MAX_ELEV + ")\" --NoDataValue=0\n";
#	cmd += "\ngdalwarp -srcnodata \"0\" -dstnodata \"nan\" temp1.tif temp_search_clipped.tif\n";
#	subprocess.call(cmd, shell=True);

#	os.remove("temp_search.tif");
#	os.remove("temp1.tif");

#	cmd  = "\ngdal_calc.py -A temp_search_clipped.tif -B temp_ref_clipped.tif --outfile=temp1.tif --calc=\"A-B\" --NoDataValue=0\n";
#	cmd += "\ngdalwarp -srcnodata \"0\" -dstnodata \"nan\" temp1.tif temp_diff.tif\n";
#	subprocess.call(cmd, shell=True);

#	os.remove("temp1.tif");

#	cmd  = "\ngdal_calc.py -A temp_diff.tif -B temp_ref_clipped.tif --outfile=temp1.tif --calc=\"B*(A>=" + MIN_DIFF + ")*(A<=" + MAX_DIFF + ")\" --NoDataValue=0\n";
#	cmd += "\ngdalwarp -srcnodata \"0\" -dstnodata \"nan\" temp1.tif temp_ref_clipped_diff_masked.tif\n";
#	subprocess.call(cmd, shell=True);

#	os.remove("temp_diff.tif");
#	os.remove("temp1.tif");

	cmd  = "\ngdalwarp -of GTiff -srcnodata \"-9999\" -dstnodata \"nan\" " + search_dem_tif_path + " temp_search_nans.tif\n";
	subprocess.call(cmd, shell=True);

	ast_pc_path  = "ast_" + search_name + "_srtm_aligned_PC.tif";
	ast_tif_path = "ast_" + search_name + "_srtm_aligned_DEM.tif";

	if not os.path.exists(ast_tif_path):

		cmd  = "\n/home/akm26/Public/StereoPipeline-2.4.2-2014-10-06-x86_64-Linux-GLIBC-2.5/bin/pc_align --max-displacement 300 --highest-accuracy " + ref_dem_tif_path + " temp_search_nans.tif -o temp_search_aligned --save-transformed-source-points\n";
#		cmd  = "\n/home/akm26/Public/StereoPipeline-2.4.2-2014-10-06-x86_64-Linux-GLIBC-2.5/bin/pc_align --max-displacement 300 --highest-accuracy " + ref_dem_tif_path + " " + search_dem_tif_path + " -o temp_search_aligned --save-transformed-source-points\n";
		cmd += "\n/home/akm26/Public/StereoPipeline-2.4.2-2014-10-06-x86_64-Linux-GLIBC-2.5/bin/point2dem --nodata-value NaN --t_srs '+proj=utm +datum=WGS84 +zone=" + ref_zone + " +" + ref_ns + "' temp_search_aligned-trans_source.tif\n";
		cmd += "\ngdalwarp -of GTiff -te " + xmin + " " + ymin + " " + xmax + " " + ymax + " -tr " + ref_res + " " + ref_res + " -srcnodata \"nan\" -dstnodata \"nan\" temp_search_aligned-trans_source-DEM.tif " + ast_tif_path + "\n";
		subprocess.call(cmd, shell=True);

		os.rename("temp_search_aligned-trans_source.tif", ast_pc_path);
		os.remove("temp_search_aligned-trans_source-DEM.tif");

	diff_after_tif_path  = "ast_" + search_name + "_diff_after.tif";
	diff_after_grd_path  = "ast_" + search_name + "_diff_after.grd";
	diff_after_hist_path = "ast_" + search_name + "_diff_after_hist.ps";

	cmd  = "\ngdal_calc.py -A " + ast_tif_path + " -B temp_ref.tif --outfile=" + diff_after_tif_path + " --calc=\"A-B\" --NoDataValue=-9999\n";
	cmd += "\ngdal_translate -of GMT " + diff_after_tif_path + " " + diff_after_grd_path + "\n"; 
	cmd += "\ngrdclip " + diff_after_grd_path + " -Sb-100/NaN -Sa100/NaN -Gtemp_diff1.grd\n";
	subprocess.call(cmd, shell=True);

	cmd  = "\ngrdinfo -L2 temp_diff1.grd\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	a_mean = info[re.search("mean:\s*", info).end(0) : re.search("mean:\s*\-*\d+\.*\d*", info).end(0)];
	a_sdev = info[re.search("stdev:\s*", info).end(0) : re.search("stdev:\s*\-*\d+\.*\d*", info).end(0)];

	cmd  = "\ngrdinfo -L1 temp_diff1.grd\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	a_median = info[re.search("median:\s*", info).end(0) : re.search("median:\s*\-*\d+\.*\d*", info).end(0)];

	plus_2sigma  = str(float(a_mean) + 2 * float(a_sdev));
	minus_2sigma = str(float(a_mean) - 2 * float(a_sdev));

	cmd = "\ngrdclip temp_diff1.grd -Sb" + minus_2sigma + "/NaN -Sa" + plus_2sigma + "/NaN -Gtemp_diff2.grd\n";
	subprocess.call(cmd, shell=True);

	cmd  = "\ngrdinfo -L2 temp_diff2.grd\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	a_mean_2sigma = info[re.search("mean:\s*", info).end(0) : re.search("mean:\s*\-*\d+\.*\d*", info).end(0)];
	a_sdev_2sigma = info[re.search("stdev:\s*", info).end(0) : re.search("stdev:\s*\-*\d+\.*\d*", info).end(0)];

	cmd  = "\ngrdinfo -L1 temp_diff2.grd\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	a_median_2sigma = info[re.search("median:\s*", info).end(0) : re.search("median:\s*\-*\d+\.*\d*", info).end(0)];

	cmd  = "\ngrd2xyz " + diff_after_grd_path + " | gawk '$0 !~ /a/ && 3 > -100 && $3 < 100 {print $3}' | pshistogram -JX10c -W1 -R-100/100/0/10000 -Ba20g10:\"Difference (m)\":/a2500g2500:\"# of points\":WeSn -Gblack --FONT_LABEL=14p,1,black --FONT_ANNOT_PRIMARY=14p,1,black --FONT_ANNOT_SECONDARY=14p,1,black -P -K > " + diff_after_hist_path + "\n";
	cmd += "\necho \"" + minus_2sigma + " 0\\n" + minus_2sigma + " 10000\" | psxy -J -R -W1p,cyan -O -K >> " + diff_after_hist_path + "\n";
	cmd += "\necho \"" + plus_2sigma + " 0\\n" + plus_2sigma + " 10000\" | psxy -J -R -W1p,cyan -O -K >> " + diff_after_hist_path + "\n";
	cmd += "\necho \"" + a_mean + " 0\\n" + a_mean + " 10000\" | psxy -J -R -W1p,red -O -K >> " + diff_after_hist_path + "\n";
	cmd += "\necho \"" + str(float(a_mean_2sigma) - 2 * float(a_sdev_2sigma)) + " 0\\n" + str(float(a_mean_2sigma) - 2 * float(a_sdev_2sigma)) + " 10000\" | psxy -J -R -W1p,blue -O -K >> " + diff_after_hist_path + "\n";
	cmd += "\necho \"" + str(float(a_mean_2sigma) + 2 * float(a_sdev_2sigma)) + " 0\\n" + str(float(a_mean_2sigma) + 2 * float(a_sdev_2sigma)) + " 10000\" | psxy -J -R -W1p,blue -O -K >> " + diff_after_hist_path + "\n";
	cmd += "\necho \"" + a_mean_2sigma + " 0\\n" + a_mean_2sigma + " 10000\" | psxy -J -R -W1p,maroon -O >> " + diff_after_hist_path + "\n";
	cmd += "\nps2raster -A -Tf " + diff_after_hist_path + "\n";
	subprocess.call(cmd, shell=True);

	os.remove("temp_diff1.grd");
	os.remove("temp_diff2.grd");
	os.remove(diff_after_grd_path);
	os.remove(diff_after_hist_path);
	os.remove("temp_ref.tif");
	
	contents   = os.listdir(".");
	temp_files = [item for item in contents if re.search("^temp_search", item)];

	for temp_file in temp_files:
		os.remove(temp_file);

	outfile = open("ast_" + search_name + "_srtm_aligned_stats.txt", "w");
	outfile.write("Median, mean, stdev BEFORE alignment, clipped at +/- 100 m: " + median + " " + mean + " " + sdev + "\n");
	outfile.write("Median, mean, stdev BEFORE alignment, clipped at +/- 2 stdev: " + median_2sigma + " " + mean_2sigma + " " + sdev_2sigma + "\n");
	outfile.write("Median, mean, stdev AFTER alignment, clipped at +/- 100 m: " + a_median + " " + a_mean + " " + a_sdev + "\n");
	outfile.write("Median, mean, stdev AFTER alignment, clipped at +/- 2 stdev: " + a_median_2sigma + " " + a_mean_2sigma + " " + a_sdev_2sigma + "\n");
#	outfile.write("Median, mean, stdev AFTER ramp-removal: " + rr_median + " " + rr_mean + " " + rr_stdev + "\n");
	outfile.close();
	
	return;

#	Fit search DEM to reference grid

	ast_diff_tif_path         = "ast_" + search_name + "_srtm_diff.tif";
	ast_diff_grd_path         = "ast_" + search_name + "_srtm_diff.grd";
	ast_diff_ps_path          = "ast_" + search_name + "_srtm_diff.ps";
	ast_aligned_diff_tif_path = "ast_" + search_name + "_srtm_aligned_diff.tif";
	ast_aligned_diff_grd_path = "ast_" + search_name + "_srtm_aligned_diff.grd";
	ast_aligned_diff_ps_path  = "ast_" + search_name + "_srtm_aligned_diff.ps";
	ast_rr_tif_path           = "ast_" + search_name + "_srtm_aligned_DEM_rr.tif";
	ast_rr_grd_path           = "ast_" + search_name + "_srtm_aligned_DEM_rr.grd";
	ast_rr_diff_tif_path      = "ast_" + search_name + "_srtm_aligned_rr_diff.tif";
	ast_rr_diff_grd_path      = "ast_" + search_name + "_srtm_aligned_rr_diff.grd";
	ast_rr_diff_ps_path       = "ast_" + search_name + "_srtm_aligned_rr_diff.ps";

	cmd  = "\ngdal_translate -of GMT " + ast_tif_path + " " + ast_grd_path + "\n";
	cmd += "\ngdal_translate -of GMT " + ast_aligned_diff_tif_path + " " + ast_aligned_diff_grd_path + "\n";
	cmd += "\ngdal_translate -of GMT " + ast_diff_tif_path + " " + ast_diff_grd_path + "\n";
	cmd += "\ngrdclip " + ast_aligned_diff_grd_path + " -Sa30/NaN -Sb-30/NaN -Gtemp1.grd\n";
	subprocess.call(cmd, shell=True);

	removeTrendDEM(ast_grd_path, "temp1.grd");
	os.remove("temp1.grd");

	cmd  = "\ngrdmath " + ast_rr_grd_path + " 1 MUL --IO_NC4_CHUNK_SIZE=c = " + ast_rr_grd_path + "\n";
	cmd += "\ngdalwarp -of GTiff -t_srs '+proj=utm +datum=WGS84 +zone=" + ref_zone + " +" + ref_ns + "' -te " + xmin + " " + ymin + " " + xmax + " " + ymax + " -tr " + ref_res + " " + ref_res + " -r near -srcnodata \"nan\" -dstnodata \"nan\" " + ast_rr_grd_path + " " + ast_rr_tif_path + "\n";
	subprocess.call(cmd, shell=True);

	geoTiffDiff(ast_rr_tif_path, "temp_ref.tif", ".", ast_rr_diff_tif_path, NO_DATA);

	cmd = "\ngdal_translate -of GMT " + ast_rr_diff_tif_path + " " + ast_rr_diff_grd_path + "\n";
	subprocess.call(cmd, shell=True);


#	Get info on coregistered search DEM

	cmd  = "\ngrd2xyz " + ast_aligned_diff_grd_path + " | gawk '$0 !~ /a/ && 3 > -100 && $3 < 100 {print $3}' | pshistogram -JX10c -W1 -R-100/100/0/10000 -Ba20g10:\"Difference (m)\":/a500g500:\"# of points\":WeSn -Gblack -P --LABEL_FONT_SIZE=14 > " + ast_aligned_diff_ps_path + "\n";
	cmd += "\ngrd2xyz " + ast_rr_diff_grd_path + " | gawk '$0 !~ /a/ && 3 > -100 && $3 < 100 {print $3}' | pshistogram -JX10c -W1 -R-100/100/0/10000 -Ba20g10:\"Difference (m)\":/a500g500:\"# of points\":WeSn -Gblack -P --LABEL_FONT_SIZE=14 > " + ast_rr_diff_ps_path + "\n";
	cmd += "\ngrd2xyz " + ast_diff_grd_path + " | gawk '$0 !~ /a/ && 3 > -100 && $3 < 100 {print $3}' | pshistogram -JX10c -W1 -R-100/100/0/10000 -Ba20g10:\"Difference (m)\":/a500g500:\"# of points\":WeSn -Gblack -P --LABEL_FONT_SIZE=14 > " + ast_diff_ps_path + "\n";
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

	outfile = open("ast_" + search_name + "_srtm_aligned_stats.txt", "w");
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

