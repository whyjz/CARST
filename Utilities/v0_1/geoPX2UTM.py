#!/usr/bin/python


# geoPX2UTM.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

# USAGE
# *****
# python geoPX2UTM.py /path/to/geo_azimuth_990102_990101.grd /path/to/geo_range_990102_990101.grd /path/to/geo_snr_990102_990101.grd /another/path/to/ice_outlines.gmt /another/path/to/rock_outlines.gmt interval utm_zone
#	/path/to/geo_azimuth_990102_990101.grd:	Path to netcdf grid of georeferenced (long/lat) azimuth offsets 
#	/path/to/geo_range_990102_990101.grd:	Path to netcdf grid of georeferenced (long/lat) range offsets
#	/path/to/geo_snr_990102_990101.grd:	Path to netcdf grid of georeferenced (long/lat) SNR values
#	/another/path/to/ice_outlines.gmt:	Path to GMT polygon-format ice outlines
#	/another/path/to/rock_outlines.gmt:	Path to GMT polygon-format rock outlines
#	interval:				Output resolution (in meters)
#	snr_thresh:				*snrfilt*.grd will be clipped below this threshold
#	utm_zone:				Valid UTM zone in the form \d\d[A-Z] desired for output

# OUTPUT
# ******
# The main output of this script are two grids (UTM E-W and N-S velocities in m/day) to the current working directory:
#	 19990102000000_19990101000000_eastxyz.grd 
#	 19990102000000_19990101000000_northxyz.grd 

# REQUIREMENTS
# ************
# This script requires GMT installed and in the default path, tested with GMT4 and python 2.7



def geoPX2UTM(azm_grd_path, rng_grd_path, snr_grd_path, ice_bounds_path, rock_bounds_path, interval, snr_thresh, utm_zone):

	import math;
	import re;
	import subprocess;
	import sys;

	azm_dir = ".";

	if azm_grd_path.rfind("/") > -1:
		azm_dir = azm_grd_path[ : azm_grd_path.rfind("/")];

	azm_name = azm_grd_path[azm_grd_path.rfind("/") + 1 : azm_grd_path.rfind(".")];
	rng_name = rng_grd_path[rng_grd_path.rfind("/") + 1 : rng_grd_path.rfind(".")];
	snr_name = snr_grd_path[snr_grd_path.rfind("/") + 1 : snr_grd_path.rfind(".")];

	cmd  = "\ngrdinfo " + azm_grd_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	azm_xmin = info[re.search("x_min: ",info).end(0) : re.search("x_min: -*\d+\.*\d*",info).end(0)];
	azm_xmax = info[re.search("x_max: ",info).end(0) : re.search("x_max: -*\d+\.*\d*",info).end(0)];
	azm_ymin = info[re.search("y_min: ",info).end(0) : re.search("y_min: -*\d+\.*\d*",info).end(0)];
	azm_ymax = info[re.search("y_max: ",info).end(0) : re.search("y_max: -*\d+\.*\d*",info).end(0)];
	inc      = info[re.search("x_inc: ",info).end(0) : re.search("x_inc: -*\d+\.*\d*",info).end(0)];

	cmd  = "\ngrdinfo " + rng_grd_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	rng_xmin = info[re.search("x_min: ",info).end(0) : re.search("x_min: -*\d+\.*\d*",info).end(0)];
	rng_xmax = info[re.search("x_max: ",info).end(0) : re.search("x_max: -*\d+\.*\d*",info).end(0)];
	rng_ymin = info[re.search("y_min: ",info).end(0) : re.search("y_min: -*\d+\.*\d*",info).end(0)];
	rng_ymax = info[re.search("y_max: ",info).end(0) : re.search("y_max: -*\d+\.*\d*",info).end(0)];

	xmin = azm_xmin;
	xmax = azm_xmax;
	ymin = azm_ymin;
	ymax = azm_ymax;

	if xmin < rng_xmin:
		xmin = rng_xmin;

	if xmax > rng_xmax:
		xmax = rng_xmax;

	if ymin < rng_ymin:
		ymin = rng_ymin;

	if ymax > rng_ymax:
		ymax = rng_ymax;

	R = "-R" + xmin + "/" + ymin + "/" + xmax + "/" + ymax + "r";

	azm_resamp_grd = azm_grd_path[azm_grd_path.rfind("/") + 1 : azm_grd_path.rfind(".")] + "_resamp.grd";
	rng_resamp_grd = rng_grd_path[rng_grd_path.rfind("/") + 1 : rng_grd_path.rfind(".")] + "_resamp.grd";
	snr_resamp_grd = snr_grd_path[snr_grd_path.rfind("/") + 1 : snr_grd_path.rfind(".")] + "_resamp.grd";

	cmd  = "\ngrdsample " + azm_grd_path + " -nn " + R + " -I" + inc + " -G" + azm_resamp_grd + "\n";
	cmd += "\ngrdsample " + rng_grd_path + " -nn " + R + " -I" + inc + " -G" + rng_resamp_grd + "\n";
	cmd += "\ngrdsample " + snr_grd_path + " -nn " + R + " -I" + inc + " -G" + snr_resamp_grd + "\n";	
	subprocess.call(cmd, shell=True);

	azm_grd_path = azm_resamp_grd;
	rng_grd_path = rng_resamp_grd;
	snr_grd_path = snr_resamp_grd;

	later_date   = azm_grd_path[re.search("\d{6}",azm_grd_path).start(0) : re.search("\d{6}",azm_grd_path).end(0)];
	earlier_date = azm_grd_path[re.search("\d{6}-",azm_grd_path).end(0) : re.search("\d{6}-\d{6}",azm_grd_path).end(0)];
	label        = azm_grd_path[re.search("r\d+x\d+",azm_grd_path).start(0) : re.search("s\d+x\d+",azm_grd_path).end(0)];

	heading = "";

	infile  = open(azm_dir + "/" + later_date + ".slc.rsc","r");

	for line in infile:

		if line.find("HEADING") > -1:
			elements = line.split();
			heading  = elements[1].strip();

	infile.close();

	cos_azm_grd = "cos_azimuth.grd";
	sin_azm_grd = "sin_azimuth.grd";
	cos_rng_grd = "cos_range.grd";
	sin_rng_grd = "sin_range.grd";

#	if float(heading) < 0:
#		heading = str(-1 * (float(heading) - 90.0));

#	else:
#		heading = str(90.0 - float(heading));

	heading = str(360. + float(heading));

	cos_heading = str(math.cos(math.radians(float(heading))));
	sin_heading = str(math.sin(math.radians(float(heading))));

	cmd  = "\ngrdmath " + azm_grd_path + " " + cos_heading + " MUL = " + cos_azm_grd + "\n";
	cmd += "\ngrdmath " + azm_grd_path + " " + sin_heading + " MUL = " + sin_azm_grd + "\n";
	cmd += "\ngrdmath " + rng_grd_path + " " + cos_heading + " MUL = " + cos_rng_grd + "\n";
	cmd += "\ngrdmath " + rng_grd_path + " " + str(-1*float(sin_heading)) + " MUL = " + sin_rng_grd + "\n";
	subprocess.call(cmd,shell=True);

	cmin  = "-200";
	cmax  = "200";
	scale = "1000000";

	cos_azm_ps = cos_azm_grd.replace("grd","ps");
	cos_rng_ps = cos_rng_grd.replace("grd","ps");
	sin_azm_ps = sin_azm_grd.replace("grd","ps");
	sin_rng_ps = sin_rng_grd.replace("grd","ps");

	cmd  = "\nmakecpt -Chaxby -T" + cmin + "/" + cmax + "/1 > vel_cm.cpt\n";
	cmd += "\ngrdimage " + cos_azm_grd + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -Cvel_cm.cpt -Q -P -K > " + cos_azm_ps + "\n";
	cmd += "\npsxy " + ice_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O -K >> " + cos_azm_ps + "\n";
	cmd += "\npsxy " + rock_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O >> " + cos_azm_ps + "\n";
	cmd += "\nps2raster -A -Tf " + cos_azm_ps + "\n";
#	subprocess.call(cmd,shell=True);

	cmd  = "";
	cmd += "\ngrdimage " + cos_rng_grd + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -Cvel_cm.cpt -Q -P -K > " + cos_rng_ps + "\n";
	cmd += "\npsxy " + ice_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O -K >> " + cos_rng_ps + "\n";
	cmd += "\npsxy " + rock_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O >> " + cos_rng_ps + "\n";
	cmd += "\nps2raster -A -Tf " + cos_rng_ps + "\n";
#	subprocess.call(cmd,shell=True);

	cmd  = "";
	cmd += "\ngrdimage " + sin_azm_grd + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -Cvel_cm.cpt -Q -P -K > " + sin_azm_ps + "\n";
	cmd += "\npsxy " + ice_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O -K >> " + sin_azm_ps + "\n";
	cmd += "\npsxy " + rock_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O >> " + sin_azm_ps + "\n";
	cmd += "\nps2raster -A -Tf " + sin_azm_ps + "\n";
#	subprocess.call(cmd,shell=True);

	cmd  = "";
	cmd += "\ngrdimage " + sin_rng_grd + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -Cvel_cm.cpt -Q -P -K > " + sin_rng_ps + "\n";
	cmd += "\npsxy " + ice_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O -K >> " + sin_rng_ps + "\n";
	cmd += "\npsxy " + rock_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O >> " + cos_rng_ps + "\n";
	cmd += "\nps2raster -A -Tf " + sin_rng_ps + "\n";
#	subprocess.call(cmd,shell=True);

#	os.remove(sin_azm_ps);
#	os.remove(sin_rng_ps);
#	os.remove(cos_azm_ps);
#	os.remove(cos_rng_ps);

	sar_dates = {};
	int_date  = azm_grd_path[re.search("\d{6}-\d{6}", azm_grd_path).start(0) : re.search("\d{6}-\d{6}", azm_grd_path).end(0)];

#	Code to find scene date+time specific to TerraSARX

#	***** TerraSARX date+time code START *****

#	cmd  = "\nfind .. -name \"TDX*.xml\"\n";
#	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
#	leader_file_paths = pipe.read().split();
#	pipe.close();

#	for path in leader_file_paths:

#		infile = open(path,"r");

#		for line in infile:

#			if line.find("timeUTC") > -1:

#				index  = re.search("timeUTC>",line).end(0);
#				year   = line[index : index + 4];
#				month  = line[index + 5 : index + 7];
#				day    = line[index + 8 : index + 10];
#				hour   = line[index + 11 : index + 13];
#				minute = line[index + 14 : index + 16];
#				second = line[index + 17 : index + 19];

#				ymd  = year[2:4] + month + day;
#				date = year + month + day + hour + minute + second;

#				sar_dates[ymd] = date;

#				break;

#		infile.close();


#	***** TerraSARX date+time code END *****

	datesum = 0;

	year   = "";
	month  = "";
	day    = "";
	hour   = "";
	minute = "";
	second = "";	

	infile  = open(azm_dir + "/" + later_date + ".slc.rsc","r");

	for line in infile:

#		if line.find("FIRST_FRAME_SCENE_CENTER_TIME") > -1:

#			elements          = line.split();
#			scene_center_time = elements[1];

#			year   = scene_center_time[0:4];
#			month  = scene_center_time[4:6];
#			day    = scene_center_time[6:8];
#			hour   = scene_center_time[8:10];
#			minute = scene_center_time[10:12];
#			second = scene_center_time[12:14];
#			ymd    = year[2:4] + month + day;
#			date   = year + month + day + hour + minute + second;

#			sar_dates[ymd] = date;

#			break;

		if line.find("FIRST_LINE_YEAR") > -1:
			elements = line.split();
			year     = elements[1];
			datesum += 1;

		elif line.find("FIRST_LINE_MONTH_OF_YEAR") > -1:
			elements = line.split();
			month    = elements[1];

			if len(month) < 2:
				month = "0" + month;

			datesum += 1;

		elif line.find("FIRST_LINE_DAY_OF_MONTH") > -1:
			elements = line.split();
			day      = elements[1];

			if len(day) < 2:
				day = "0" + day;

			datesum += 1;

		elif line.find("FIRST_CENTER_HOUR_OF_DAY") > -1:
			elements = line.split();
			hour     = elements[1];

			if len(hour) < 2:
				hour = "0" + hour;

			datesum += 1;

		elif line.find("FIRST_CENTER_MN_OF_HOUR") > -1:
			elements = line.split();
			minute   = elements[1];

			if len(minute) < 2:
				minute = "0" + minute;

			datesum += 1;

		elif line.find("FIRST_CENTER_S_OF_MN") > -1:
			elements = line.split();
			second   = elements[1];

			if len(second) < 2:
				second = "0" + second;

			datesum += 1;

		if datesum == 6:
			ymd            = year[2:4] + month + day;
			date           = year + month + day + hour + minute + second;
			sar_dates[ymd] = date;
			break;

	infile.close();

	datesum = 0;

	year   = "";
	month  = "";
	day    = "";
	hour   = "";
	minute = "";
	second = "";	

	infile  = open(azm_dir + "/" + earlier_date + ".slc.rsc","r");

	for line in infile:

#		if line.find("FIRST_FRAME_SCENE_CENTER_TIME") > -1:

#			elements          = line.split();
#			scene_center_time = elements[1];

#			year   = scene_center_time[0:4];
#			month  = scene_center_time[4:6];
#			day    = scene_center_time[6:8];
#			hour   = scene_center_time[8:10];
#			minute = scene_center_time[10:12];
#			second = scene_center_time[12:14];
#			ymd    = year[2:4] + month + day;
#			date   = year + month + day + hour + minute + second;

#			sar_dates[ymd] = date;

#			break;

		if line.find("FIRST_LINE_YEAR") > -1:
			elements = line.split();
			year     = elements[1];
			datesum += 1;

		elif line.find("FIRST_LINE_MONTH_OF_YEAR") > -1:
			elements = line.split();
			month    = elements[1];

			if len(month) < 2:
				month = "0" + month;

			datesum += 1;

		elif line.find("FIRST_LINE_DAY_OF_MONTH") > -1:
			elements = line.split();
			day      = elements[1];

			if len(day) < 2:
				day = "0" + day;

			datesum += 1;

		elif line.find("FIRST_CENTER_HOUR_OF_DAY") > -1:
			elements = line.split();
			hour     = elements[1];

			if len(hour) < 2:
				hour = "0" + hour;

			datesum += 1;

		elif line.find("FIRST_CENTER_MN_OF_HOUR") > -1:
			elements = line.split();
			minute   = elements[1];

			if len(minute) < 2:
				minute = "0" + minute;

			datesum += 1;

		elif line.find("FIRST_CENTER_S_OF_MN") > -1:
			elements = line.split();
			second   = elements[1];

			if len(second) < 2:
				second = "0" + second;

			datesum += 1;

		if datesum == 6:
			ymd            = year[2:4] + month + day;
			date           = year + month + day + hour + minute + second;
			sar_dates[ymd] = date;
			break;

	infile.close();

	year   = int_date[0:2];
	month  = int_date[2:4];
	day    = int_date[4:6];
	ymd_l  = year + month + day;
	date_l = sar_dates[ymd_l];
	year   = date_l[0:4];
	hour   = date_l[8:10];
	minute = date_l[10:12];
	second = date_l[12:14];

	cmd  = "\ndate +\"%s\" -d \"" + year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second + "\"\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	seconds_l = pipe.read().strip();
	pipe.close();

	year   = int_date[7:9];
	month  = int_date[9:11];
	day    = int_date[11:13];
	ymd_e  = year + month + day;
	date_e = sar_dates[ymd_e];
	year   = date_e[0:4];
	hour   = date_e[8:10];
	minute = date_e[10:12];
	second = date_e[12:14];

	cmd  = "\ndate +\"%s\" -d \"" + year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second + "\"\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	seconds_e = pipe.read().strip();
	pipe.close();

	time_difference_days = str( (float(seconds_l) - float(seconds_e)) / (60.*60.*24.) * 100. );

	north_grd = azm_name.replace("azimuth","north") + ".grd";
	east_grd  = azm_name.replace("azimuth","east") + ".grd";

	cmd  = "\ngrdmath " + cos_azm_grd + " " + sin_rng_grd + " ADD = " + north_grd + "\n";
	cmd += "\ngrdmath " + cos_rng_grd + " " + sin_azm_grd + " ADD = " + east_grd + "\n";
	cmd += "\ngrdmath " + north_grd + " " + time_difference_days + " DIV = " + north_grd + "\n";
	cmd += "\ngrdmath " + east_grd + " " + time_difference_days + " DIV = " + east_grd + "\n";
	subprocess.call(cmd,shell=True);

	os.remove(cos_azm_grd);
	os.remove(sin_azm_grd);
	os.remove(cos_rng_grd);
	os.remove(sin_rng_grd);

	north_ps = north_grd.replace("grd","ps");
	east_ps  = east_grd.replace("grd","ps");
	azm_ps   = azm_name + ".ps";
	rng_ps   = rng_name + ".ps";

	cmd  = "\nmakecpt -Chaxby -T" + str(round(float(cmin) / 100.)) + "/" + str(round(float(cmax) / 100.)) + "/0.01 > vel.cpt\n";
	cmd += "\ngrdimage " + north_grd + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -Cvel.cpt -Q -P -K > " + north_ps + "\n";
	cmd += "\npsxy " + ice_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O -K >> " + north_ps + "\n";
	cmd += "\npsxy " + rock_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O >> " + north_ps + "\n";
	cmd += "\nps2raster -A -Tf " + north_ps + "\n";
#	subprocess.call(cmd,shell=True);

	cmd  = "";
	cmd += "\ngrdimage " + east_grd + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -Cvel.cpt -Q -P -K > " + east_ps + "\n";
	cmd += "\npsxy " + ice_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O -K >> " + east_ps + "\n";
	cmd += "\npsxy " + rock_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O >> " + east_ps + "\n";
	cmd += "\nps2raster -A -Tf " + east_ps + "\n";
#	subprocess.call(cmd,shell=True);

	cmd  = "";
	cmd += "\ngrdimage " + azm_grd_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -Cvel_cm.cpt -Q -P -K > " + azm_ps + "\n";
	cmd += "\npsxy " + ice_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O -K >> " + azm_ps + "\n";
	cmd += "\npsxy " + rock_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O >> " + azm_ps + "\n";
	cmd += "\nps2raster -A -Tf " + azm_ps + "\n";
#	subprocess.call(cmd,shell=True);

	cmd  = "";
	cmd += "\ngrdimage " + rng_grd_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -Cvel_cm.cpt -Q -P -K > " + rng_ps + "\n";
	cmd += "\npsxy " + ice_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O -K >> " + rng_ps + "\n";
	cmd += "\npsxy " + rock_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O >> " + rng_ps + "\n";
	cmd += "\nps2raster -A -Tf " + rng_ps + "\n";
#	subprocess.call(cmd,shell=True);

#	os.remove(north_ps);
#	os.remove(east_ps);
#	os.remove(azm_ps);
#	os.remove(rng_ps);

	mag_grd         = north_grd.replace("north","magnitude");
	mag_snrfilt_grd = north_grd.replace("north","magnitude_snrfilt");
	mag_ps          = mag_grd.replace("grd","ps");
	mag_snrfilt_ps  = mag_snrfilt_grd.replace("grd","ps");

	cmd  = "\ngrdclip " + snr_grd_path + " -Sb" + snr_thresh + "/NaN -Gtemp.grd\n";
	cmd += "\ngrdmath " + north_grd + " 2 POW = nsq.grd\n";
	cmd += "\ngrdmath " + east_grd + " 2 POW = esq.grd\n";
	cmd += "\ngrdmath nsq.grd esq.grd ADD = sum.grd\n";
	cmd += "\ngrdmath sum.grd SQRT = " + mag_grd + "\n";
	cmd += "\ngrdmath " + mag_grd + " temp.grd OR = " + mag_snrfilt_grd + "\n";
#	cmd += "\nmakecpt -Chaxby -T0/" + str(round(float(cmax) / 100.)) + "/0.01 > mag.cpt\n";
#	cmd += "\ngrdimage " + mag_grd + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -Cmag.cpt -Q -P -K > " + mag_ps + "\n";
#	cmd += "\npsxy " + ice_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O -K >> " + mag_ps + "\n";
#	cmd += "\npsxy " + rock_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O >> " + mag_ps + "\n";
#	cmd += "\nps2raster -A -Tf " + mag_ps + "\n";
#	cmd += "\ngrdimage " + mag_snrfilt_grd + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -Cmag.cpt -Q -P -K > " + mag_snrfilt_ps + "\n";
#	cmd += "\npsxy " + ice_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O -K >> " + mag_snrfilt_ps + "\n";
#	cmd += "\npsxy " + rock_bounds_path + " -Ju" + utm_zone + "/1:" + scale + " " + R + " -W0.5p,black -O >> " + mag_snrfilt_ps + "\n";
#	cmd += "\nps2raster -A -Tf " + mag_snrfilt_ps + "\n";
	subprocess.call(cmd,shell=True);

	cmd += "\nrm temp.grd nsq.grd esq.grd sum.grd\n";
	os.remove("temp.grd");
	os.remove("nsq.grd");
	os.remove("esq.grd");
	os.remove("sum.grd");
#	os.remove(mag_ps);
#	os.remove(mag_snrfilt_ps);

	utm_north_grd = date_l + "_" + date_e + "_" + label + "_northxyz.grd";
	utm_north_txt = utm_north_grd.replace("grd","txt");
	utm_east_grd  = utm_north_grd.replace("north","east");
	utm_east_txt  = utm_east_grd.replace("grd","txt");
	utm_snr_grd   = utm_north_grd.replace("north","snr");
	utm_snr_txt   = utm_snr_grd.replace("grd","txt");

	print(utm_north_grd, utm_north_txt, utm_east_grd, utm_east_txt, utm_snr_grd, utm_snr_txt);

	cmd  = "\ngrd2xyz " + north_grd + " | mapproject -Ju" + utm_zone + "/1:1 -F -C > " + utm_north_txt + "\n";
	cmd += "\ngrd2xyz " + east_grd + " | mapproject -Ju" + utm_zone + "/1:1 -F -C > " + utm_east_txt + "\n";
	cmd += "\ngrd2xyz " + snr_grd_path + " | mapproject -Ju" + utm_zone + "/1:1 -F -C > " + utm_snr_txt + "\n";
	subprocess.call(cmd,shell=True);

	cmd  = "\nminmax -C " + utm_north_txt + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().split();
	pipe.close();

	xmin = info[0].strip();
	xmax = info[1].strip();
	ymin = info[2].strip();
	ymax = info[3].strip();
	R    = "-R" + xmin + "/" + ymin + "/" + xmax + "/" + ymax + "r";

	cmd  = "\nxyz2grd " + utm_north_txt + " " + R + " -G" + utm_north_grd + " -I" + interval + "=\n";
	cmd += "\nxyz2grd " + utm_east_txt + " " + R + " -G" + utm_east_grd + " -I" + interval + "=\n";
	cmd += "\nxyz2grd " + utm_snr_txt + " " + R + " -G" + utm_snr_grd + " -I" + interval + "=\n";
	subprocess.call(cmd,shell=True);

	os.remove(azm_resamp_grd);
	os.remove(rng_resamp_grd);

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 8, "\n***** ERROR: geoPX2UTM.py requires 8 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";
	assert os.path.exists(sys.argv[4]), "\n***** ERROR: " + sys.argv[4] + " does not exist\n";
	assert os.path.exists(sys.argv[5]), "\n***** ERROR: " + sys.argv[5] + " does not exist\n";
	
	geoPX2UTM(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8]);

	exit();


