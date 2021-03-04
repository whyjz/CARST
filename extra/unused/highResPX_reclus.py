#!/usr/bin/python


# hirez_pixel_track.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def highResPX(ref_ntf_path, search_ntf_path, ref_dem_path, search_dem_path, pairs_dir, resolution, utm_zone, bounds_txt_path, num_proc, search_size, ref_size, step_size, dem_grd_path):

	import os;

	assert os.path.exists(ref_ntf_path), "\n***** ERROR: " + ref_ntf_path + " does not exist\n";
	assert os.path.exists(search_ntf_path), "\n***** ERROR: " + search_ntf_path + " does not exist\n";
	assert os.path.exists(ref_dem_path), "\n***** ERROR: " + ref_dem_path + " does not exist\n";
	assert os.path.exists(search_dem_path), "\n***** ERROR: " + search_dem_path + " does not exist\n";
	assert os.path.exists(pairs_dir), "\n***** ERROR: " + pairs_dir + " does not exist\n";
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

	ref_date = "";
	ref_year   = "";
	ref_month  = "";
	ref_day    = "";
	ref_hour   = "";
	ref_minute = "";
	ref_second = "";

	if ref_ntf_path.lower().find("wv") > -1:

		ref_date = ref_ntf_path[re.search("\d\d[A-Z][A-Z][A-Z]\d\d\d\d\d\d\d\d\d", ref_ntf_path).start(0) : re.search("\d\d[A-Z][A-Z][A-Z]\d\d\d\d\d\d\d\d\d", ref_ntf_path).end(0)];
	
		ref_year   = "20" + ref_date[0:2];
		ref_month  = months[ref_date[2:5]];
		ref_day    = ref_date[5:7];
		ref_hour   = ref_date[7:9];
		ref_minute = ref_date[9:11];
		ref_second = str(int(round(float(ref_date[11:13] + "." + ref_date[13]))));

	elif ref_ntf_path.lower().find("ge0") > -1:

		cmd  = "\ngdalinfo " + ref_ntf_path + "\n";
		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		info = pipe.read().strip();
		pipe.close();

		ref_date   = info[re.search("NITF_CSDIDA_TIME\s*=\s*", info).end(0) : re.search("NITF_CSDIDA_TIME\s*=\s*\d+", info).end(0)];
		ref_year   = ref_date[0:4];
		ref_month  = ref_date[4:6];
		ref_day    = ref_date[6:8];
		ref_hour   = ref_date[8:10];
		ref_minute = ref_date[10:12];
		ref_second = ref_date[12:14];

	if len(ref_second) < 2:
		ref_second = "0" + ref_second;

	ref_date = ref_year + ref_month + ref_day + ref_hour + ref_minute + ref_second;

	search_date = "";
	search_year   = "";
	search_month  = "";
	search_day    = "";
	search_hour   = "";
	search_minute = "";
	search_second = "";

	if search_ntf_path.lower().find("wv") > -1:

		search_date = search_ntf_path[re.search("\d\d[A-Z][A-Z][A-Z]\d\d\d\d\d\d\d\d\d", search_ntf_path).start(0) : re.search("\d\d[A-Z][A-Z][A-Z]\d\d\d\d\d\d\d\d\d", search_ntf_path).end(0)];
	
		search_year   = "20" + search_date[0:2];
		search_month  = months[search_date[2:5]];
		search_day    = search_date[5:7];
		search_hour   = search_date[7:9];
		search_minute = search_date[9:11];
		search_second = str(int(round(float(search_date[11:13] + "." + search_date[13]))));

	elif search_ntf_path.lower().find("ge0") > -1:

		cmd  = "\ngdalinfo " + search_ntf_path + "\n";
		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		info = pipe.read().strip();
		pipe.close();

		search_date   = info[re.search("NITF_CSDIDA_TIME\s*=\s*", info).end(0) : re.search("NITF_CSDIDA_TIME\s*=\s*\d+", info).end(0)];
		search_year   = search_date[0:4];
		search_month  = search_date[4:6];
		search_day    = search_date[6:8];
		search_hour   = search_date[8:10];
		search_minute = search_date[10:12];
		search_second = search_date[12:14];

	if len(search_second) < 2:
		search_second = "0" + search_second;

	search_date = search_year + search_month + search_day + search_hour + search_minute + search_second;

	pair = search_date + "_" + ref_date;

	pair_path = pairs_dir + "/" + pair;

	if not os.path.exists(pair_path):
		os.mkdir(pair);

	print(pair_path);

	ref_img_path    = pair_path + "/" + ref_ntf_path[ref_ntf_path.rfind("/") +1 : ref_ntf_path.rfind(".")] + "_orthod.img";
	search_img_path = pair_path + "/" + search_ntf_path[search_ntf_path.rfind("/") + 1 : search_ntf_path.rfind(".")] + "_orthod.img";

	if not os.path.exists(ref_img_path):
		cmd  = "\ngdalwarp -of ENVI -ot Float32 -t_srs '+proj=utm +zone=" + utm_zone + " +datum=WGS84 +north' -multi -et 0 -tr " + resolution + " " + resolution + " -te " + bounds_str + " -rpc -to RPC_DEM=" + ref_dem_path + " " + ref_ntf_path + " " + ref_img_path + "\n";
		cmd += "\ngdalwarp -of ENVI -ot Float32 -t_srs '+proj=utm +zone=" + utm_zone + " +datum=WGS84 +north' -multi -et 0 -tr " + resolution + " " + resolution + " -te " + bounds_str + " -rpc -to RPC_DEM=" + search_dem_path + " " + search_ntf_path + " " + search_img_path + "\n";
		#subprocess.call(cmd,shell=True);

	else:
		print("\n***** \"" + ref_img_path + "\" already exists, skipping orthorectification for " + pair + "...\n");

	import sys;

	sys.path.append("/home/akm/Python");

	from splitAmpcor import *;

	if not os.path.exists(pair_path + "/ampcor_1.in"):

		splitAmpcor(ref_img_path, search_img_path, pair_path, num_proc, resolution, ref_size, ref_size, search_size, search_size, step_size);

		outfile = open(pair_path + "/run_amp.cmd", "w");

		for i in range(1, int(num_proc) + 1):
			outfile.write("\nampcor ampcor_" + str(i) + ".in rdf > ampcor_" + str(i) + ".out &\n");

		outfile.close();

	else:
		print("\n***** \"ampcor_1.in\" already exists, skipping ampcor for " + pair + "...\n");

	assert os.path.exists(pair_path + "/ampcor_1.off"), "\n***** ERROR: \"ampcor_1.off\" does not exist in current directory, please cd to directory with ampcor results or run ampcor for " + pair + "...\n";

	ref_hdr_path = ref_img_path.replace("img","hdr");

	if not os.path.exists(ref_hdr_path):
		ref_hdr_path = ref_hdr_path.replace(".hdr", ".img.hdr");

	assert os.path.exists(ref_hdr_path), "\n***** ERROR: \"" + ref_hdr_path + "/" + ref_hdr_path.replace(".img.hdr", ".hdr") + "\" not found...\n";

	if not os.path.exists(pair_path + "/ampcor.off"):

		amp_offs = [item for item in os.listdir(pair_path) if ".off" in item and "ampcor" in item];

		cmd = "\ncat ";

		for amp_off in amp_offs:
			cmd += pair_path + "/" + amp_off + " ";

		cmd += " > " + pair_path + "/ampcor.off\n";

		subprocess.call(cmd,shell=True);

	ref_hdr_info = "";

	infile = open(ref_hdr_path, "r");

	for line in infile:

		ref_hdr_info += line;

	infile.close();

	ref_hdr_info = ref_hdr_info.lower();

	ref_samples = ref_hdr_info[re.search("samples\s*=\s*", ref_hdr_info).end(0) : re.search("samples\s*=\s*\d+", ref_hdr_info).end(0)];
	ref_lines   = ref_hdr_info[re.search("lines\s*=\s*", ref_hdr_info).end(0) : re.search("lines\s*=\s*\d+", ref_hdr_info).end(0)];

	from getxyzs import *;	

	e_txt_path  = pair_path + "/" + pair + "_eastxyz.txt";
	n_txt_path = pair_path + "/" + pair + "_northxyz.txt";

	if not os.path.exists(e_txt_path):
		getxyzs(pair_path, step_size, step_size, "1", resolution, ref_samples, ref_lines, ul_x, ul_y, pair);

	else:
		print("\n***** \"" + e_txt_path + " already exists, skipping \"getxyzs\" for " + pair + "...\n");

	n_grd_path   = pair_path + "/" + pair + "_northxyz.grd";
	e_grd_path   = pair_path + "/" + pair + "_eastxyz.grd";
	snr_grd_path = pair_path + "/" + pair + "_snr.grd";

	vel_res = str(int(float(resolution) * float(step_size)));

	import datetime;
	from datetime import timedelta;

	ref_time    = datetime.datetime(int(ref_year), int(ref_month), int(ref_day), int(ref_hour), int(ref_minute), int(ref_second));
	search_time = datetime.datetime(int(search_year), int(search_month), int(search_day), int(search_hour), int(search_minute), int(search_second));

	difference     = (search_time - ref_time).days + (search_time - ref_time).seconds / (60.0 * 60.0 * 24.0);
	mperday_factor = str(100.0 * difference);

	R = "-R" + ul_x + "/" + lr_y + "/" + lr_x + "/" + ul_y + "r";

	if not os.path.exists(e_grd_path):
	        cmd = "";
	        cmd += "\ngawk '$4 !~ /a/ {print $1\" \"$2\" \"$4}' " + n_txt_path + " | xyz2grd -I" + vel_res + "= -G" + snr_grd_path + " " + R + "\n";
	        cmd += "\nxyz2grd " + e_txt_path + " -I" + vel_res + "= -G" + e_grd_path + " " + R + "\n";
	        cmd += "\nxyz2grd " + n_txt_path + " -I" + vel_res + "= -G" + n_grd_path + " " + R + "\n";
	        cmd += "\ngrdmath " + e_grd_path + " " + mperday_factor + " DIV = " + e_grd_path + "\n";
	        cmd += "\ngrdmath " + n_grd_path + " " + mperday_factor + " DIV = " + n_grd_path + "\n";
	        subprocess.call(cmd,shell=True);

	else:
		print("\n***** \"" + e_grd_path + " already exists, skipping making E-W and N-S grids for " + pair + "...\n");

	n_corrected_grd_path = pair_path + "/" + pair + "_northxyz_corrected.grd";
	e_corrected_grd_path = pair_path + "/" + pair + "_eastxyz_corrected.grd";

	ICE	   = "/home/akm/Russia/NovZ/Boundaries/NovZ_bounds_ice_sub_utm41x.gmt";
	ROCK	   = "/home/akm/Russia/NovZ/Boundaries/NovZ_bounds_rock_sub_utm41x.gmt";
	SNR_CUTOFF = "1";

	from motionElevCorrection import *;

	if not os.path.exists(e_corrected_grd_path):
		#print("\npython /home/akm/Python/motionElevCorrection.py " + n_grd_path + " " + dem_grd + " " + ICE + " " + ROCK + " " + vel_res + " " + SNR_CUTOFF + "\n");
	        motionElevCorrection(n_grd_path, dem_grd_path, ICE, ROCK, vel_res, SNR_CUTOFF);
	        motionElevCorrection(e_grd_path, dem_grd_path, ICE, ROCK, vel_res, SNR_CUTOFF);

	else:
		print("\n***** \"" + e_corrected_grd_path + " already exists, skipping \"motionElevCorrection\" for " + pair + "...\n");

	mag_grd_path    = pair_path + "/" + pair + "_magnitude_corrected.grd";
	ratio           = "1000000";
	cscale          = "3";

	if not os.path.exists(mag_grd_path):

		from imageAmpResults import *;

	        print("\nCreating magnitude grid and image for " + pair_path + " ...\n");

		ratio = "200000";

	        imageAmpResults(pair_path, pair, n_corrected_grd_path, e_corrected_grd_path, [bounds[0], bounds[2], bounds[3], bounds[1]], ratio, cscale, utm_zone + "X", ICE, ROCK);


	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 13, "\n***** ERROR: highResPX.py requires 13 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";
	assert os.path.exists(sys.argv[4]), "\n***** ERROR: " + sys.argv[4] + " does not exist\n";
	assert os.path.exists(sys.argv[5]), "\n***** ERROR: " + sys.argv[5] + " does not exist\n";
	assert os.path.exists(sys.argv[8]), "\n***** ERROR: " + sys.argv[8] + " does not exist\n";
	assert os.path.exists(sys.argv[13]), "\n***** ERROR: " + sys.argv[13] + " does not exist\n";
	

	highResPX(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10], sys.argv[11], sys.argv[12], sys.argv[13]);


	exit();
