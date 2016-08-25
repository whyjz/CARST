#!/usr/bin/python


# verticalCoreg.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def verticalCoreg(search_dem_tif_path, ref_dem_tif_path, ice_bounds_path, rock_bounds_path, upper_bound, lower_bound, resolution):

	assert os.path.exists(ref_dem_tif_path), "\n***** ERROR: " + ref_dem_tif_path + " does not exist\n";
	assert os.path.exists(search_dem_tif_path), "\n***** ERROR: " + search_dem_tif_path + " does not exist\n";
	assert os.path.exists(ice_bounds_path), "\n***** ERROR: " + ice_bounds_path + " does not exist\n";
	assert os.path.exists(rock_bounds_path), "\n***** ERROR: " + rock_bounds_path + " does not exist\n";

	import subprocess;

	cmd  = "\ngdalinfo " + ref_dem_tif_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	import re;

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

	
	cmd  = "\ngdalinfo " + search_dem_tif_path + "\n";
        pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
        info = pipe.read().strip();
        pipe.close();

        import re;

	search_zone = info[re.search("UTM\s*zone\s*",info).end(0) : re.search("UTM\s*zone\s*\d+",info).end(0)];
	search_type = info[re.search("Type\s*=\s*",info).end(0) : re.search("Type\s*=\s*\S+",info).end(0)].replace(",","");
        search_res  = info[re.search("Pixel\s*Size\s*=\s*\(\s*",info).end(0) : re.search("Pixel\s*Size\s*=\s*\(\s*\d+\.*\d*",info).end(0)];
        search_res  = search_res[ : re.search("0+$",search_res).start(0)];

	NO_DATA = "-9999";

	search_no_data = NO_DATA;

	if not re.search("NoData",info):
		cmd = "\ngdal_edit.py " + search_dem_tif_path + " -a_nodata " + NO_DATA + "\n";
		subprocess.call(cmd,shell=True);

	else:
		search_no_data = info[re.search("NoData\s*Value\s*=\s*",info).end(0) : re.search("NoData\s*Value\s*=\s*\S+",info).end(0)];

	search_ns = info[re.search("UTM\s*zone\s*\d+",info).end(0) : re.search("UTM\s*zone\s*\d+[A-Z]",info).end(0)];

	if search_ns.lower().find("n") > -1:
		search_ns = "north";

	else:
		search_ns = "south";

        search_ul_x = info[re.search("Upper Left\s*\(\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
        search_ul_y = info[re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
        search_ur_x = info[re.search("Upper Right\s*\(\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
        search_ur_y = info[re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
        search_lr_x = info[re.search("Lower Right\s*\(\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
        search_lr_y = info[re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
        search_ll_x = info[re.search("Lower Left\s*\(\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
        search_ll_y = info[re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	cmd = "";

	if search_zone != ref_zone:
		cmd = "\ngdalwarp -ot Float32 -te " + search_ll_x + " " + search_ll_y + " " + search_ur_x + " " + search_ur_y + " -tr " + search_res + " " + search_res + " -r cubic -t_srs '+proj=utm +zone=" + search_zone + " +" + search_ns + " +datum=WGS84' -srcnodata \"" + ref_no_data + "\" -dstnodata \"" + NO_DATA + "\" -of GTiff " + ref_dem_tif_path + " ref.tif\n";

	else:
		cmd = "\ngdalwarp -ot Float32 -te " + search_ll_x + " " + search_ll_y + " " + search_ur_x + " " + search_ur_y + " -tr " + search_res + " " + search_res + " -r cubic -srcnodata \"" + ref_no_data + "\" -dstnodata \"" + NO_DATA + "\" -of GTiff " + ref_dem_tif_path + " ref.tif\n";

	cmd += "\ngdal_translate -of GTiff -ot Float32 " + search_dem_tif_path + " temp.tif\n";
	cmd += "\ngdal_calc.py -A temp.tif --outfile=search.tif --calc=\"(A*(A>0))\" --NoDataValue=\"" + NO_DATA + "\"\n";
	subprocess.call(cmd,shell=True);

	os.remove("temp.tif");

	if os.path.exists("temp.tif.aux.xml"):
		os.remove("temp.tif.aux.xml");
	
	from geoTiffDiff import *;

	geoTiffDiff("search.tif", "ref.tif", ".", "diff.tif", NO_DATA);

	cmd  = "\ngdal_calc.py -A diff.tif --outfile=temp.tif --calc=\"(A*(A>-100))\" --NoDataValue=\"" + NO_DATA + "\"\n";
	cmd += "\ngdal_calc.py -A temp.tif --outfile=diff_clipped.tif --calc=\"(A*(A<100))\" --NoDataValue=\"" + NO_DATA + "\"\n";
	subprocess.call(cmd,shell=True);

	os.remove("temp.tif");

	if os.path.exists("temp.tif.aux.xml"):
		os.remove("temp.tif.aux.xml");
		
	search_name = search_dem_tif_path[search_dem_tif_path.rfind("/") + 1 : search_dem_tif_path.rfind(".")];

	cmd  = "\ngdal_translate -of GMT diff.tif diff.grd\n";
	cmd += "\ngrd2xyz diff.grd | gawk '$3 > -100 && $3 < 100 {print $3}' | pshistogram -X5c -JX12c -W1 -F -R-100/100/0/10000 -Ba20g10:\"Difference\":/a200g100:\"Counts\":WeSn -Gblack --LABEL_FONT=1 -P -K > " + search_name + "_minus_carto.ps\n";
	cmd += "\nps2raster -A -Tf " + search_name + "_minus_carto.ps\n";
	subprocess.call(cmd,shell=True);

	os.remove("diff.grd");

	if os.path.exists("diff.grd.aux.xml"):
		os.remove("diff.grd.aux.xml");

	os.remove(search_name + "_minus_carto.ps");

	cmd = "\ngdalinfo -stats diff_clipped.tif\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	os.remove("diff_clipped.tif");

	if os.path.exists("diff_clipped.tif.aux.xml"):
		os.remove("diff_clipped.tif.aux.xml");

	mean  = info[re.search("STATISTICS_MEAN\s*=\s*",info).end(0) : re.search("STATISTICS_MEAN\s*=\s*\-*\d+\.*\d*\e*\-*\d*",info).end(0)];

	cmd  = "\ngdal_calc.py -A diff.tif --outfile=temp.tif --calc=\"A-" + mean + "\" --NoDataValue=\"" + NO_DATA + "\"\n";
	subprocess.call(cmd,shell=True);

	os.rename("temp.tif","diff.tif");

	cmd = "\ncp -p diff.tif " + search_name + "_mean_diff_removed.tif\n";
	subprocess.call(cmd,shell=True);

	cmd  = "\ngdal_translate -of GMT diff.tif diff.grd\n";
	cmd += "\ngrd2xyz diff.grd | gawk '$3 > -100 && $3 < 100 {print $3}' | pshistogram -X5c -JX12c -W1 -F -R-100/100/0/10000 -Ba20g10:\"Difference\":/a200g100:\"Counts\":WeSn -Gblack --LABEL_FONT=1 -P -K > " + search_name + "_mean_diff_removed.ps\n";
	cmd += "\nps2raster -A -Tf " + search_name + "_mean_diff_removed.ps\n";
	subprocess.call(cmd,shell=True);

	os.remove("diff.grd");

	if os.path.exists("diff.grd.aux.xml"):
		os.remove("diff.grd.aux.xml");

	os.remove(search_name + "_mean_diff_removed.ps");

	cmd  = "\ngdal_calc.py -A diff.tif --outfile=temp.tif --calc=\"(A*(A>-100))\" --NoDataValue=\"" + NO_DATA + "\"\n";
	cmd += "\ngdal_calc.py -A temp.tif --outfile=diff_clipped.tif --calc=\"(A*(A<100))\" --NoDataValue=\"" + NO_DATA + "\"\n";
	subprocess.call(cmd,shell=True);

	os.remove("temp.tif");

	if os.path.exists("temp.tif.aux.xml"):
		os.remove("temp.tif.aux.xml");
		
	cmd = "\ngdalinfo -stats diff_clipped.tif\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	stdev = info[re.search("STATISTICS_STDDEV\s*=\s*",info).end(0) : re.search("STATISTICS_STDDEV\s*=\s*\d+\.*\d*",info).end(0)];
	mean  = info[re.search("STATISTICS_MEAN\s*=\s*",info).end(0) : re.search("STATISTICS_MEAN\s*=\s*\-*\d+\.*\d*\e*\-*\d*",info).end(0)];

	#upper_bound = str(float(mean) + 2 * float(stdev));
	#lower_bound = str(float(mean) - 2 * float(stdev));

	#os.remove("diff_clipped.tif");
	os.rename("diff_clipped.tif","current_diff.tif");

	if os.path.exists("diff_clipped.tif.aux.xml"):
		os.remove("diff_clipped.tif.aux.xml");

	#cmd  = "\ngdal_calc.py -A diff.tif --outfile=temp.tif --calc=\"(A*(A>" + lower_bound + "))\" --NoDataValue=\"" + NO_DATA + "\"\n";
	#cmd += "\ngdal_calc.py -A temp.tif --outfile=diff_clipped.tif --calc=\"(A*(A<" + upper_bound + "))\" --NoDataValue=\"" + NO_DATA + "\"\n";
	#subprocess.call(cmd,shell=True);

	#os.remove("temp.tif");

	#if os.path.exists("temp.tif.aux.xml"):
	#	os.remove("temp.tif.aux.xml");
		
	#cmd  = "\ngdalinfo -stats diff_clipped.tif\n";
	#pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	#info = pipe.read().strip();
	#pipe.close();

	#stdev = info[re.search("STATISTICS_STDDEV\s*=\s*",info).end(0) : re.search("STATISTICS_STDDEV\s*=\s*\d+\.*\d*",info).end(0)];
	#mean  = info[re.search("STATISTICS_MEAN\s*=\s*",info).end(0) : re.search("STATISTICS_MEAN\s*=\s*\-*\d+\.*\d*\e*\-*\d*",info).end(0)];

	prev_stdev = stdev;

	#os.rename("diff_clipped.tif","current_diff.tif");
	#os.remove("diff_clipped.tif");

	#if os.path.exists("diff_clipped.tif.aux.xml"):
	#	os.remove("diff_clipped.tif.aux.xml");


	for i in range(0, 10):

		cmd  = "\ngdal_translate -of GMT current_diff.tif current_diff.grd\n";
		cmd += "\ngrdclip -Sb-100/NaN -Sa100/NaN current_diff.grd -Gcurrent_diff.grd\n";
    		cmd += "\ngrdtrend current_diff.grd -N3 -Ttrend.grd -V\n";
		cmd += "\ngdal_translate -a_srs '+proj=utm +datum=WGS84 +zone=" + search_zone + " +" + search_ns + "' -a_nodata " + NO_DATA + " -of GTiff trend.grd trend.tif\n";
		subprocess.call(cmd,shell=True);

		if not os.path.exists("fit.tif"):
			cmd = "\ncp -p trend.tif temp_fit.tif\n";
			subprocess.call(cmd,shell=True);

		else:
			cmd = "\ngdal_calc.py -A fit.tif -B trend.tif --outfile=temp_fit.tif --calc=\"A+B\" --NoDataValue=\"" + NO_DATA + "\"\n";
			subprocess.call(cmd,shell=True);
		
		cmd = "\ngdal_calc.py -A diff.tif -B temp_fit.tif --outfile=result.tif --calc=\"A-B\" --NoDataValue=\"" + NO_DATA + "\"\n";
		subprocess.call(cmd,shell=True);

		cmd = "\ngdal_calc.py -A current_diff.tif -B temp_fit.tif --outfile=temp.tif --calc=\"A-B\" --NoDataValue=\"" + NO_DATA + "\"\n";
		subprocess.call(cmd,shell=True);

		cmd  = "\ngdalinfo -stats temp.tif\n";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		info = pipe.read().strip();
		pipe.close();

		stdev = info[re.search("STATISTICS_STDDEV\s*=\s*",info).end(0) : re.search("STATISTICS_STDDEV\s*=\s*\d+\.*\d*",info).end(0)];
		mean  = info[re.search("STATISTICS_MEAN\s*=\s*",info).end(0) : re.search("STATISTICS_MEAN\s*=\s*\-*\d+\.*\d*\e*\-*\d*",info).end(0)];

		upper_bound = str(float(mean) + 2 * float(stdev));
		lower_bound = str(float(mean) - 2 * float(stdev));

		os.remove("current_diff.tif");

		if os.path.exists("current_diff.tif.aux.xml"):
			os.remove("current_diff.tif.aux.xml");

		cmd  = "\ngdal_calc.py -A temp.tif --outfile=temp2.tif --calc=\"(A*(A>" + lower_bound + "))\" --NoDataValue=\"" + NO_DATA + "\"\n";
		cmd += "\ngdal_calc.py -A temp2.tif --outfile=current_diff.tif --calc=\"(A*(A<" + upper_bound + "))\" --NoDataValue=\"" + NO_DATA + "\"\n";
		subprocess.call(cmd,shell=True);

		os.remove("temp.tif");

		if os.path.exists("temp.tif.aux.xml"):
			os.remove("temp.tif.aux.xml");

		os.remove("temp2.tif");

		if os.path.exists("temp2.tif.aux.xml"):
			os.remove("temp2.tif.aux.xml");

		os.remove("current_diff.grd");

		if os.path.exists("current_diff.grd.aux.xml"):
			os.remove("current_diff.grd.aux.xml");

		os.remove("trend.grd");

		if os.path.exists("trend.grd.aux.xml"):
			os.remove("trend.grd.aux.xml");

		if os.path.exists("trend.tif.aux.xml"):
			os.remove("trend.tif.aux.xml");

		os.remove("temp_fit.tif");

		if os.path.exists("temp_fit.tif.aux.xml"):
			os.remove("temp_fit.tif.aux.xml");

		cmd  = "\ngdal_calc.py -A result.tif --outfile=temp.tif --calc=\"(A*(A>-100))\" --NoDataValue=\"" + NO_DATA + "\"\n";
		cmd += "\ngdal_calc.py -A temp.tif --outfile=diff_clipped.tif --calc=\"(A*(A<100))\" --NoDataValue=\"" + NO_DATA + "\"\n";
		subprocess.call(cmd,shell=True);

		os.remove("temp.tif");

		if os.path.exists("temp.tif.aux.xml"):
			os.remove("temp.tif.aux.xml");
		
		cmd  = "\ngdalinfo -stats diff_clipped.tif\n";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		info = pipe.read().strip();
		pipe.close();

		stdev = info[re.search("STATISTICS_STDDEV\s*=\s*",info).end(0) : re.search("STATISTICS_STDDEV\s*=\s*\d+\.*\d*",info).end(0)];
		mean  = info[re.search("STATISTICS_MEAN\s*=\s*",info).end(0) : re.search("STATISTICS_MEAN\s*=\s*\-*\d+\.*\d*\e*\-*\d*",info).end(0)];

		upper_bound = str(float(mean) + 2 * float(stdev));
		lower_bound = str(float(mean) - 2 * float(stdev));

		os.remove("diff_clipped.tif");

		if os.path.exists("diff_clipped.tif.aux.xml"):
			os.remove("diff_clipped.tif.aux.xml");

		cmd  = "\ngdal_calc.py -A result.tif --outfile=temp.tif --calc=\"(A*(A>" + lower_bound + "))\" --NoDataValue=\"" + NO_DATA + "\"\n";
		cmd += "\ngdal_calc.py -A temp.tif --outfile=diff_clipped.tif --calc=\"(A*(A<" + upper_bound + "))\" --NoDataValue=\"" + NO_DATA + "\"\n";
		subprocess.call(cmd,shell=True);

		os.remove("temp.tif");

		if os.path.exists("temp.tif.aux.xml"):
			os.remove("temp.tif.aux.xml");
		
		cmd  = "\ngdalinfo -stats diff_clipped.tif\n";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		info = pipe.read().strip();
		pipe.close();

		stdev = info[re.search("STATISTICS_STDDEV\s*=\s*",info).end(0) : re.search("STATISTICS_STDDEV\s*=\s*\d+\.*\d*",info).end(0)];
		mean  = info[re.search("STATISTICS_MEAN\s*=\s*",info).end(0) : re.search("STATISTICS_MEAN\s*=\s*\-*\d+\.*\d*\e*\-*\d*",info).end(0)];

		print(prev_stdev);
		print(stdev);

		#if abs(float(prev_stdev) - float(stdev)) < 0.05:
		if float(prev_stdev) < float(stdev):
     			break;

		os.remove("diff_clipped.tif");

		if os.path.exists("diff_clipped.tif.aux.xml"):
			os.remove("diff_clipped.tif.aux.xml");

		if not os.path.exists("fit.tif"):
			os.rename("trend.tif","fit.tif");

		else:

			cmd  = "\ngdal_calc.py -A fit.tif -B trend.tif --outfile=temp.tif --calc=\"A+B\"\n";
			subprocess.call(cmd,shell=True);

			os.rename("temp.tif","fit.tif");

			if os.path.exists("temp.tif.aux.xml"):
				os.remove("temp.tif.aux.xml");

			os.remove("trend.tif");

		if os.path.exists("trend.tif.aux.xml"):
			os.remove("trend.tif.aux.xml");

		os.rename("result.tif","diff.tif");

		if os.path.exists("result.tif.aux.xml"):
			os.remove("result.tif.aux.xml");

		prev_stdev = stdev;


	if os.path.exists("current_diff.tif"):
		os.remove("current_diff.tif");

	if os.path.exists("current_diff.tif.aux.xml"):
		os.remove("current_diff.tif.aux.xml");

	if os.path.exists("trend.tif"):
		os.remove("trend.tif");

	if os.path.exists("trend.tif.aux.xml"):
		os.remove("trend.tif.aux.xml");

	if os.path.exists("result.tif"):
		os.remove("result.tif");

	if os.path.exists("result.tif.aux.xml"):
		os.remove("result.tif.aux.xml");

	os.remove("diff.tif");

	if os.path.exists("diff.tif.aux.xml"):
		os.remove("diff.tif.aux.xml");
	
	os.remove("diff_clipped.tif");

	if os.path.exists("diff_clipped.tif.aux.xml"):
		os.remove("diff_clipped.tif.aux.xml");

	if os.path.exists("fit.tif"):

		cmd  = "\ngdal_calc.py -A search.tif -B fit.tif --outfile=" + search_name + "_trend_removed.tif --calc=\"A-B\" --NoDataValue=\"" + NO_DATA + "\"\n";
		cmd += "\ngdal_calc.py -A " + search_name + "_trend_removed.tif -B ref.tif --outfile=" + search_name + "_trend_removed_diff.tif --calc=\"A-B\" --NoDataValue=\"" + NO_DATA + "\"\n";
		cmd += "\ngdal_translate -of GMT " + search_name + "_trend_removed_diff.tif " + search_name + "_trend_removed_diff.grd\n";
		cmd += "\ngrd2xyz " + search_name + "_trend_removed_diff.grd | gawk '$3 > -100 && $3 < 100 {print $3}' | pshistogram -X5c -JX12c -W1 -F -R-100/100/0/10000 -Ba20g10:\"Difference\":/a200g100:\"Counts\":WeSn -Gblack --LABEL_FONT=1 -P -K > " + search_name + "_trend_removed_diff.ps\n";
		cmd += "\nps2raster -A -Tf " + search_name + "_trend_removed_diff.ps\n";
		subprocess.call(cmd,shell=True);

		os.remove(search_name + "_trend_removed_diff.grd");

		if os.path.exists(search_name + "_trend_removed_diff.grd.aux.xml"):
			os.remove(search_name + "_trend_removed_diff.grd.aux.xml");

		if os.path.exists(search_name + "_trend_removed.tif.aux.xml"):
			os.remove(search_name + "_trend_removed.tif.aux.xml");

		os.remove(search_name + "_trend_removed_diff.ps");

		os.rename("fit.tif", search_name + "_fit.tif");

		if os.path.exists("fit.tif.aux.xml"):
			os.remove("fit.tif.aux.xml");
		
	os.remove("ref.tif");

	if os.path.exists("ref.tif.aux.xml"):
		os.remove("ref.tif.aux.xml");

	os.remove("search.tif");

	if os.path.exists("search.tif.aux.xml"):
		os.remove("search.tif.aux.xml");


	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 7, "\n***** ERROR: verticalCoreg.py requires 7 arguments, " + str(len(sys.argv)) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";
	assert os.path.exists(sys.argv[4]), "\n***** ERROR: " + sys.argv[4] + " does not exist\n";
	
	verticalCoreg(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7]);

	exit();


