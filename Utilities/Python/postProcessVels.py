#!/usr/bin/python


# postProcessVels.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def postProcessVels(east_vels_list_path, ice_gmt_path, rock_gmt_path, dem_grd_path):

	import datetime;
	import os;
	import re;
	import subprocess;
	import sys;

	sys.path.append("/data/akm/Python");

	from season import *;

	assert os.path.exists(east_vels_list_path), "\n***** ERROR: \"" + east_vels_list_path + "\" not found, exiting...\n";
	assert os.path.exists(ice_gmt_path), "\n***** ERROR: \"" + ice_gmt_path + "\" not found, exiting...\n";
	assert os.path.exists(rock_gmt_path), "\n***** ERROR: \"" + rock_gmt_path + "\" not found, exiting...\n";
	assert os.path.exists(dem_grd_path), "\n***** ERROR: \"" + dem_grd_path + "\" not found, exiting...\n";	

	M_SCRIPTS_DIR = "/data/akm/MATLAB/Adam_Cleaner";
	REF_UTM_ZONE  = "41";
	UTM_LETTER    = "X";
	VEL_PATH_COL  = 0;
	REGION_COL    = 1;
	UTM_COL       = 2;
	SCALE         = "500000";

#	VEL_MAX       = "5";
#	TOL           = "0.2";
#	NUMDIF        = "2";

#       For INO velocities
	VEL_MAX       = "5";
	TOL           = "0.2";
	NUMDIF        = "3";

	num_pairs = {};

	infile = open(east_vels_list_path, "r");

	for line in infile:

		if line[0] == "#":
			continue;

		elements = line.strip().split();

		east_vel_path  = elements[VEL_PATH_COL];
		north_vel_path = east_vel_path.replace("east", "north");
		utm_zone       = elements[UTM_COL];

		if not os.path.exists(east_vel_path):
			print("\n***** Warning: \"" + east_vel_path + "\" not found, skipping...\n");	
			continue;

		east_vel_name   = east_vel_path[east_vel_path.rfind("/") + 1 : ]; 
		pair_dates      = east_vel_name[re.search("\d{14}_\d{14}", east_vel_name).start(0) : re.search("\d{14}_\d{14}", east_vel_name).end(0)];
		east_pair_type  = east_vel_name[re.search("\d{14}_\d{14}", east_vel_name).end(0) + 1 : east_vel_name.rfind(".")];

		if pair_dates[0:2] != "19" and pair_dates[0:2] != "20":
			pair_dates = pair_dates[4:8] + pair_dates[0:2] + pair_dates[2:4] + pair_dates[8:14] + "_" + pair_dates[19:23] + pair_dates[15:17] + pair_dates[17:19] + pair_dates[23:29];

		key = pair_dates + "_" + east_pair_type;

		if key not in num_pairs:
			num_pairs[key] = 1;

		else:
			east_pair_type  = east_pair_type + "_" + str(num_pairs[key]);
			num_pairs[key] += 1;

		north_pair_type    = east_pair_type.replace("east", "north");
		mag_pair_type      = east_pair_type.replace("eastxyz", "mag");
		new_east_name      = pair_dates + "_" + east_pair_type;
		new_north_name     = pair_dates + "_" + north_pair_type;
		new_mag_name       = pair_dates + "_" + mag_pair_type;
		new_east_vel_path  = pair_dates + "_" + east_pair_type + ".grd";
		new_north_vel_path = pair_dates + "_" + north_pair_type + ".grd";

		if utm_zone == REF_UTM_ZONE:

			if not os.path.exists(new_east_vel_path):
				cmd  = "\ngdalwarp -of GTiff -srcnodata \"0\" -dstnodata \"nan\" " + east_vel_path + " temp_east.tif\n";
				cmd += "\ngdalwarp -of GTiff -srcnodata \"0\" -dstnodata \"nan\" " + north_vel_path + " temp_north.tif\n";
				cmd += "\ngdal_translate -of GMT -a_nodata \"nan\" temp_east.tif " + new_east_vel_path + "\n";
				cmd += "\ngdal_translate -of GMT -a_nodata \"nan\" temp_north.tif " + new_north_vel_path + "\n";
				cmd += "\ngrdsample -T " + new_east_vel_path + " -G" + new_east_vel_path + "\n";
				cmd += "\ngrdsample -T " + new_north_vel_path + " -G" + new_north_vel_path + "\n";
				subprocess.call(cmd,shell=True);

				os.remove("temp_east.tif");
				os.remove("temp_north.tif");

		else:

			if not os.path.exists(new_east_vel_path):
				cmd  = "\ngdalwarp -of GTiff -t_srs '+proj=utm +zone=" + utm_zone + " +datum=WGS84 +north' -srcnodata \"0\" -dstnodata \"nan\" " + east_vel_path + " temp_east.tif\n";
				cmd += "\ngdalwarp -of GTiff -t_srs '+proj=utm +zone=" + utm_zone + " +datum=WGS84 +north' -srcnodata \"0\" -dstnodata \"nan\" " + north_vel_path + " temp_north.tif\n";
				cmd += "\ngdalwarp -of GTiff -t_srs '+proj=utm +zone=" + REF_UTM_ZONE + " +datum=WGS84 +north' -srcnodata \"nan\" -dstnodata \"nan\" temp_east.tif temp_east_warp.tif\n";
				cmd += "\ngdalwarp -of GTiff -t_srs '+proj=utm +zone=" + REF_UTM_ZONE + " +datum=WGS84 +north' -srcnodata \"nan\" -dstnodata \"nan\" temp_north.tif temp_north_warp.tif\n";
				cmd += "\ngdal_translate -of GMT -a_nodata \"nan\" temp_east_warp.tif " + new_east_vel_path + "\n";
				cmd += "\ngdal_translate -of GMT -a_nodata \"nan\" temp_north_warp.tif " + new_north_vel_path + "\n";
				cmd += "\ngrdsample -T " + new_east_vel_path + " -G" + new_east_vel_path + "\n";
				cmd += "\ngrdsample -T " + new_north_vel_path + " -G" + new_north_vel_path + "\n";
				subprocess.call(cmd, shell=True);

				os.remove("temp_east.tif");
				os.remove("temp_north.tif");
				os.remove("temp_east_warp.tif");
				os.remove("temp_north_warp.tif");

		cmd  = "\ngrdinfo " + new_east_vel_path + "\n";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		info = pipe.read();
		pipe.close();

		min_x = info[re.search("x_min: ",info).end(0) : re.search("x_min: -*\d+\.*\d*",info).end(0)];
		max_x = info[re.search("x_max: ",info).end(0) : re.search("x_max: -*\d+\.*\d*",info).end(0)];
		min_y = info[re.search("y_min: ",info).end(0) : re.search("y_min: -*\d+\.*\d*",info).end(0)];
		max_y = info[re.search("y_max: ",info).end(0) : re.search("y_max: -*\d+\.*\d*",info).end(0)];

		cmd  = "\necho \"" + min_x + " " + max_y + "\\n" + max_x + " " + min_y + "\" | mapproject -Ju" + REF_UTM_ZONE + UTM_LETTER + "/1:1 -F -C -I\n";
                pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
                geo_ul_x, geo_ul_y, geo_lr_x, geo_lr_y = pipe.read().split();
                pipe.close();

		R    = "-R" + min_x + "/" + min_y + "/" + max_x + "/" + max_y + "r";
                geoR = "-R" + geo_ul_x + "/" + geo_lr_y + "/" + geo_lr_x + "/" + geo_ul_y + "r";
                J    = "-Jx1:" + SCALE;
                geoJ = "-Ju" + REF_UTM_ZONE + "/1:" + SCALE;

		rock_grd_path   = pair_dates + "_" + east_pair_type.replace("eastxyz","") + "_off_ice.grd";
		rock_grd_path   = rock_grd_path.replace("__","_")
		east_rr_path    = new_east_name + "_rr.grd";
		north_rr_path   = new_north_name + "_rr.grd";
		mag_rr_path     = new_mag_name + "_rr.grd";
		east_rock_path  = new_east_name + "_off_ice.grd";
		north_rock_path = new_north_name + "_off_ice.grd";
		east_filt_path  = new_east_name + "_filt.grd";
		north_filt_path = new_north_name + "_filt.grd";
		mag_filt_path   = new_mag_name + "_filt.grd";

		if not os.path.exists(east_rr_path):

			print("\n***** Removing ramp, creating \"" + east_rr_path + "\" and \"" + north_rr_path + "\"...\n");

			if not os.path.exists(rock_grd_path):
				cmd  = "\ngrdmask " + ice_gmt_path + " -N1/NaN/NaN -R" + new_east_vel_path + " -Gtemp_outside_ice.grd\n";
				cmd += "\ngrdmask " + rock_gmt_path + " -NNaN/NaN/1 -R" + new_east_vel_path + " -Gtemp_inside_rock.grd\n";
				cmd += "\ngrdmath temp_outside_ice.grd temp_inside_rock.grd AND = " + rock_grd_path + "\n";
				subprocess.call(cmd, shell=True);

				os.remove("temp_outside_ice.grd");
				os.remove("temp_inside_rock.grd");

			if not os.path.exists("noiseremoval.m"):
				os.symlink(M_SCRIPTS_DIR + "/noiseremoval.m", "noiseremoval.m");
				os.symlink(M_SCRIPTS_DIR + "/remloners.m", "remloners.m");
				os.symlink(M_SCRIPTS_DIR + "/remnoise.m", "remnoise.m");
				os.symlink(M_SCRIPTS_DIR + "/grdread2.m", "grdread2.m");
				os.symlink(M_SCRIPTS_DIR + "/grdwrite2.m", "grdwrite2.m");

			cmd  = "\nmatlab -nodesktop -nosplash -r \"noiseremoval(5,0.3,3,'" + new_east_vel_path + "','" + new_north_vel_path + "'); exit;\"\n";
			subprocess.call(cmd, shell=True);

			os.remove("noiseremoval.m");
			os.remove("remloners.m");
			os.remove("remnoise.m");
			os.remove("grdread2.m");
			os.remove("grdwrite2.m");
			
			cmd  = "\ngrdmath " + east_filt_path + " " + rock_grd_path + " OR = " + east_rock_path + "\n";
			cmd += "\ngrdmath " + north_filt_path + " " + rock_grd_path + " OR = " + north_rock_path + "\n";
			subprocess.call(cmd, shell=True);

			os.remove(east_filt_path);
			os.remove(north_filt_path);

			from removeTrendNoOutlines import *;

			removeTrendNoOutlines(new_east_vel_path, east_rock_path, "-2", "2");
			removeTrendNoOutlines(new_north_vel_path, north_rock_path, "-2", "2");

#			removeTrendNoOutlines(new_east_vel_path, east_rock_path, "-10", "10");
#			removeTrendNoOutlines(new_north_vel_path, north_rock_path, "-10", "10");

			os.remove(east_rock_path);
			os.remove(north_rock_path);

			cmd = "\ngrdmath " + east_rr_path + " " + north_rr_path + " HYPOT --IO_NC4_CHUNK_SIZE=c = " + mag_rr_path + "\n";
			subprocess.call(cmd, shell=True);

		else:
			print("\n***** \"" + east_rr_path + "\" already exists, assuming results already ramp-removed...\n");

		mag_rr_ps_path = new_mag_name + "_rr.ps";

		cmd  = "\nmakecpt -Cjet -T0/" + VEL_MAX + "/0.01 --COLOR_BACKGROUND=white --COLOR_NAN=white --COLOR_FOREGROUND=white > mag.cpt\n";
                cmd += "\ngrdimage " + mag_rr_path + " " + J + " " + R + " -Cmag.cpt -P -K > " + mag_rr_ps_path + "\n";
		cmd += "\npsxy " + ice_gmt_path + " " + J + " " + R + " -W1p,black -O -K >> " + mag_rr_ps_path + "\n";
		cmd += "\npsxy " + rock_gmt_path + " " + J + " " + R + " -W1p,black -O -K >> " + mag_rr_ps_path + "\n";
		cmd += "\npsbasemap " + geoJ + " " + geoR + " -Bf1a1g1:\"Longitude\":/a0.5g0.5:\"\"::,::.\"\":WeSn --MAP_FRAME_TYPE=inside --FORMAT_GEO_MAP=ddd:mmF --FONT_ANNOT_PRIMARY=12p,1,black --MAP_GRID_PEN_PRIMARY=0.25p,100/100/100,- -O -K >> " + mag_rr_ps_path + "\n";
		cmd += "\npsbasemap " + geoJ + " " + geoR + " -Lfx3c/2c/76/5k+jr+u+p0.5,black+gwhite --FONT_ANNOT_PRIMARY=12p,1,black --FONT_LABEL=12p,1,black -O -K >> " + mag_rr_ps_path + "\n";
		cmd += "\npsscale -D3c/4c/3c/0.1c -Cmag.cpt -B1:\"Speed\":/:\"m day@+-1@+\": --FONT_ANNOT_PRIMARY=12p,1,black --FONT_LABEL=12p,1,black -O >> " + mag_rr_ps_path + "\n";
		cmd += "\nps2raster -A -Tf " + mag_rr_ps_path + "\n";
		subprocess.call(cmd, shell=True);

		os.remove(mag_rr_ps_path);

		east_filt_path  = east_rr_path[ : east_rr_path.rfind(".")] + "_filt.grd";
		north_filt_path = north_rr_path[ : north_rr_path.rfind(".")] + "_filt.grd";
		mag_filt_path   = mag_rr_path[ : mag_rr_path.rfind(".")] + "_filt.grd";

		if not os.path.exists(east_filt_path):

			print("\n***** Filtering results, creating \"" + east_filt_path + "\" and \"" + north_filt_path + "\"...\n");

			if not os.path.exists("noiseremoval.m"):
				os.symlink(M_SCRIPTS_DIR + "/noiseremoval.m", "noiseremoval.m");
				os.symlink(M_SCRIPTS_DIR + "/remloners.m", "remloners.m");
				os.symlink(M_SCRIPTS_DIR + "/remnoise.m", "remnoise.m");
				os.symlink(M_SCRIPTS_DIR + "/grdread2.m", "grdread2.m");
				os.symlink(M_SCRIPTS_DIR + "/grdwrite2.m", "grdwrite2.m");

			cmd  = "\nmatlab -nodesktop -nosplash -r \"noiseremoval(" + \
			       VEL_MAX + "," + TOL + "," + NUMDIF + ",'" + east_rr_path + "','" + north_rr_path + "'); exit;\"\n";
			cmd += "\ngrdmath " + east_filt_path + " " + north_filt_path + " HYPOT --IO_NC4_CHUNK_SIZE=c = " + mag_filt_path + "\n";
			subprocess.call(cmd, shell=True);

			os.remove("noiseremoval.m");
			os.remove("remloners.m");
			os.remove("remnoise.m");
			os.remove("grdread2.m");
			os.remove("grdwrite2.m");

		else:
			print("\n***** \"" + east_filt_path + "\" already exists, assuming results already filtered...\n");

		mag_filt_ps_path = new_mag_name + "_rr_filt.ps";

		cmd  = "\nmakecpt -Chaxby -T0/" + VEL_MAX + "/0.01 --COLOR_BACKGROUND=white --COLOR_NAN=white --COLOR_FOREGROUND=white > mag.cpt\n";
                cmd += "\ngrdimage " + mag_filt_path + " " + J + " " + R + " -Cmag.cpt -P -K > " + mag_filt_ps_path + "\n";
		cmd += "\npsxy " + ice_gmt_path + " " + J + " " + R + " -W1p,black -O -K >> " + mag_filt_ps_path + "\n";
		cmd += "\npsxy " + rock_gmt_path + " " + J + " " + R + " -W1p,black -O -K >> " + mag_filt_ps_path + "\n";
		cmd += "\npsbasemap " + geoJ + " " + geoR + " -Bf1a1g1:\"Longitude\":/a0.5g0.5:\"\"::,::.\"\":WeSn --MAP_FRAME_TYPE=inside --FORMAT_GEO_MAP=ddd:mmF --FONT_ANNOT_PRIMARY=12p,1,black --MAP_GRID_PEN_PRIMARY=0.25p,100/100/100,- -O -K >> " + mag_filt_ps_path + "\n";
		cmd += "\npsbasemap " + geoJ + " " + geoR + " -Lfx3c/2c/76/5k+jr+u+p0.5,black+gwhite --FONT_ANNOT_PRIMARY=12p,1,black --FONT_LABEL=12p,1,black -O -K >> " + mag_filt_ps_path + "\n";
		cmd += "\npsscale -D3c/4c/3c/0.1c -Cmag.cpt -B1:\"Speed\":/:\"m day@+-1@+\": --FONT_ANNOT_PRIMARY=12p,1,black --FONT_LABEL=12p,1,black -O >> " + mag_filt_ps_path + "\n";
		cmd += "\nps2raster -A -Tf " + mag_filt_ps_path + "\n";
		subprocess.call(cmd, shell=True);

		os.remove(mag_filt_ps_path);

		mag_txt_path   = mag_filt_path[ : mag_filt_path.rfind(".")] + ".txt";

		if not os.path.exists(mag_txt_path):

			season_days = season(pair_dates);

			date1 = pair_dates[re.search("\d{14}_\d{14}", pair_dates).start(0) : re.search("\d{14}_\d{14}", pair_dates).start(0) + 14];
			date2 = pair_dates[re.search("\d{14}_\d{14}", pair_dates).start(0) + 15 : re.search("\d{14}_\d{14}", pair_dates).end(0)];

			if date1[0:2] != "19" and date1[0:2] != "20":
				date1 = date1[4:8] + date1[0:2] + date1[2:4] + date1[8:14];
				date2 = date2[4:8] + date2[0:2] + date2[2:4] + date2[8:14];

			datetime1   = datetime.datetime(int(date1[0:4]), int(date1[4:6]), int(date1[6:8]), int(date1[8:10]), int(date1[10:12]), int(date1[12:14]));
			datetime2   = datetime.datetime(int(date2[0:4]), int(date2[4:6]), int(date2[6:8]), int(date2[8:10]), int(date2[10:12]), int(date2[12:14]));
			interval    = str(abs((datetime1 - datetime2).total_seconds() / float(60. * 60. * 24.)));
			interval_td = (datetime1 - datetime2) // 2;
			datetime_m  = datetime2 + interval_td;

			datetime_m_year = datetime.datetime(datetime_m.year, 1, 1, 0, 0, 0);
			m_dec_year      = (datetime_m - datetime_m_year).total_seconds() / float(60. * 60. * 24. * 365.25);
			
			cmd = "\ngrdmath " + mag_filt_path + " " + rock_grd_path + " OR = temp.grd\n";
			subprocess.call(cmd, shell=True);

			cmd  = "\ngrdinfo -L2 temp.grd\n";
			pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
			info = pipe.read();
			pipe.close();

			stdev = info[re.search("stdev:\s*", info).end(0) : re.search("stdev:\s*\d+\.*\d*", info).end(0)];
			mean  = info[re.search("mean:\s*", info).end(0) : re.search("mean:\s*\-*\d+\.*\d*", info).end(0)];

			upper = str(float(mean) + 2 * float(stdev));
			lower = str(float(mean) - 2 * float(stdev));

			cmd = "\ngrdclip temp.grd -Sb" + lower + "/NaN -Sa" + upper + "/NaN -Gclipped.grd\n";
			subprocess.call(cmd,shell=True);

			cmd  = "\ngrdinfo -L2 clipped.grd\n";
			pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
			info = pipe.read();
			pipe.close();

			stdev = info[re.search("stdev:\s*", info).end(0) : re.search("stdev:\s*\d+\.*\d*", info).end(0)];
			mean  = info[re.search("mean:\s*", info).end(0) : re.search("mean:\s*\-*\d+\.*\d*", info).end(0)];

			cmd  = "\ngrdinfo -L1 clipped.grd\n";
			pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
			info = pipe.read();
			pipe.close();

			median  = info[re.search("median:\s*", info).end(0) : re.search("median:\s*\-*\d+\.*\d*", info).end(0)];

			cmd = "\ngrd2xyz " + mag_filt_path + " | gawk '$0 !~ /a/ {print $1\" \"$2\" \"$3\" " + median + " " + mean + " " + stdev + " " + interval + " " + str(season_days[0]) + " " + str(season_days[1]) + " " + str(season_days[2]) + " " + str(season_days[3]) + " " + str(datetime_m.year + float(m_dec_year)) + "\"}' > " + mag_txt_path + "\n";
			subprocess.call(cmd, shell=True);

			os.remove("temp.grd");
			os.remove("clipped.grd");
		


#		try: dem_grd_path
#		except NameError:
#			print("\n***** WARNING: dem_grd_path not set in \"" + params_path + "\", skipping motion-elevation correction...\n");
#			continue;

#		if not os.path.exists(dem_grd_path):
#			print("\n***** ERROR: dem_grd_path \"" + dem_grd_path + "\" not found, skipping motion-elevation correction...\n");
#			continue;

#		east_filt_txt_path  = east_filt_path[ : east_filt_path.rfind(".")] + ".txt";
#		north_filt_txt_path = north_filt_path[ : north_filt_path.rfind(".")] + ".txt";

#		if not os.path.exists(east_filt_txt_path):
#			print("***** Creating \"" + east_filt_txt_path + "\" and \"" + north_filt_txt_path + "\" from filtered grids...\n");
#			cmd  = "\ngrd2xyz " + east_filt_path + " | gawk '$0 !~ /a/ && $3 != 0 {print $0}' > " + east_filt_txt_path + "\n";
#			cmd += "\ngrd2xyz " + north_filt_path + " | gawk '$0 !~ /a/ && $3 != 0 {print $0}' > " + north_filt_txt_path + "\n";
#			subprocess.call(cmd, shell=True);

#		else:
#			print("***** \"" + east_filt_txt_path + "\" already exists, assuming current E-W and N-S filtered offsets already converted to ASCII files...\n");

#		east_corr_path  = east_filt_path[ : east_filt_path.rfind(".")] + "_corrected.grd";
#		north_corr_path = north_filt_path[ : north_filt_path.rfind(".")] + "_corrected.grd";
#		mag_corr_path   = mag_filt_path[ : mag_filt_path.rfind(".")] + "_corrected.grd";

#		if os.path.exists(east_corr_path):
#			print("***** \"" + east_corr_path + "\" already exists, assuming motion-elevation correction performed on most recent results...\n");

#		else:
#			motionElevCorrection(east_filt_path, dem_grd_path, ice_gmt_path, rock_gmt_path, str(int(RESOLUTION) * int(STEP)), SNR_CUTOFF);
#			motionElevCorrection(north_filt_path, dem_grd_path, ice_gmt_path, rock_gmt_path, str(int(RESOLUTION) * int(STEP)), SNR_CUTOFF);
#			cmd = "\ngrdmath " + east_corr_path + " " + north_corr_path + " HYPOT --IO_NC4_CHUNK_SIZE=c = " + mag_corr_path + "\n";
#			subprocess.call(cmd, shell=True);

#		mag_corr_ps_path = new_mag_name + "_rr_filt_corrected.ps";

#		cmd  = "\nmakecpt -Chaxby -T0/" + VEL_MAX + "/0.01 --COLOR_BACKGROUND=white --COLOR_NAN=white --COLOR_FOREGROUND=white > mag.cpt\n";
#                cmd += "\ngrdimage " + mag_corr_path + " " + J + " " + R + " -Cmag.cpt -Q -P -K > " + mag_corr_ps_path + "\n";
#		cmd += "\npsxy " + ice_gmt_path + " " + J + " " + R + " -W1p,black -O -K >> " + mag_corr_ps_path + "\n";
#		cmd += "\npsxy " + rock_gmt_path + " " + J + " " + R + " -W1p,black -O -K >> " + mag_corr_ps_path + "\n";
#		cmd += "\npsbasemap " + geoJ + " " + geoR + " -Bf1a1g1:\"Longitude\":/a0.5g0.5:\"\"::,::.\"\":WeSn --MAP_FRAME_TYPE=inside --FORMAT_GEO_MAP=ddd:mmF --FONT_ANNOT_PRIMARY=1
#2p,1,black --MAP_GRID_PEN_PRIMARY=0.25p,100/100/100,- -O -K >> " + mag_corr_ps_path + "\n";
#		cmd += "\npsbasemap " + geoJ + " " + geoR + " -Lfx3c/2c/60.5/40k+jr+u+p0.5,black+gwhite --FONT_ANNOT_PRIMARY=12p,1,black --FONT_LABEL=12p,1,black -O -K >> " + mag_corr_ps
#_path + "\n";
#		cmd += "\npsscale -D3c/4c/3c/0.1c -Cmag.cpt -B1:\"Speed\":/:\"m day@+-1@+\": --FONT_ANNOT_PRIMARY=12p,1,black --FONT_LABEL=12p,1,black -O >> " + mag_cor
#r_ps_path + "\n";
#		cmd += "\nps2raster -A -Tf " + mag_corr_ps_path + "\n";
#                subprocess.call(cmd, shell=True);

#		os.remove(mag_corr_ps_path);

	infile.close();

	return;




if __name__ == "__main__":

	import os;
	import sys;

	assert len(sys.argv) > 4, "\n***** ERROR: postProcessVels.py requires 4 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: \"" + sys.argv[1] + "\" not found, exiting...\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: \"" + sys.argv[2] + "\" not found, exiting...\n";
	assert os.path.exists(sys.argv[3]), "\n***** ERROR: \"" + sys.argv[3] + "\" not found, exiting...\n";
	assert os.path.exists(sys.argv[4]), "\n***** ERROR: \"" + sys.argv[4] + "\" not found, exiting...\n";

	east_vels_list_path = sys.argv[1];
	ice_gmt_path   = sys.argv[2];
	rock_gmt_path  = sys.argv[3];
	dem_grd_path   = sys.argv[4];

	postProcessVels(east_vels_list_path, ice_gmt_path, rock_gmt_path, dem_grd_path);

	exit();
