#!/usr/bin/python


# velUnc.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def velUnc(mag_grd_path, ice_bounds_path, rock_bounds_path):

	import datetime;
	import os;
	import re;
	import subprocess;

	sys.path.append("/data/akm/Python");

        from season import *;

	assert os.path.exists(mag_grd_path), "\n***** ERROR: " + mag_grd_path + " does not exist\n";
	assert os.path.exists(ice_bounds_path), "\n***** ERROR: " + ice_bounds_path + " does not exist\n";
	assert os.path.exists(rock_bounds_path), "\n***** ERROR: " + rock_bounds_path + " does not exist\n";

	north_grd_path = mag_grd_path.replace("mag", "northxyz");
	east_grd_path  = mag_grd_path.replace("mag", "eastxyz");

	pair = mag_grd_path[mag_grd_path.rfind("/") + 1 : mag_grd_path.lower().find("_mag")];

	if not re.search("^20", pair) and not re.search("^19", pair):
		pair = pair[4:8] + pair[0:4] + pair[8:14] + "_" + pair[19:23] + pair[15:19] + pair[23:29];

	season_days = season(pair);

	date1 = pair[re.search("\d{14}_\d{14}", pair).start(0) : re.search("\d{14}_\d{14}", pair).start(0) + 14];
	date2 = pair[re.search("\d{14}_\d{14}", pair).start(0) + 15 : re.search("\d{14}_\d{14}", pair).end(0)];

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

	cmd  = "\ngrdinfo " + mag_grd_path + "\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	mag_xinc = info[re.search("x_inc: ",info).end(0):re.search("x_inc: \-*\d+\.*\d*",info).end(0)];
	mag_xmin = info[re.search("x_min: ",info).end(0):re.search("x_min: \-*\d+\.*\d*",info).end(0)];
	mag_xmax = info[re.search("x_max: ",info).end(0):re.search("x_max: \-*\d+\.*\d*",info).end(0)];
	mag_ymin = info[re.search("y_min: ",info).end(0):re.search("y_min: \-*\d+\.*\d*",info).end(0)];
	mag_ymax = info[re.search("y_max: ",info).end(0):re.search("y_max: \-*\d+\.*\d*",info).end(0)];

	xmin = mag_xmin;
	xmax = mag_xmax;
	ymin = mag_ymin;
	ymax = mag_ymax;

	pair_off_ice_grd = mag_grd_path[mag_grd_path.rfind("/") + 1 : mag_grd_path.rfind(".")] + "_off_ice.grd";
	clipped_grd      = mag_grd_path[mag_grd_path.rfind("/") + 1 : mag_grd_path.rfind(".")] + "_off_ice_clipped.grd";

	if not os.path.exists(clipped_grd):

		cmd  = "\ngrdmask " + ice_bounds_path + " -R" + mag_grd_path + " -Goutside_ice.grd -N1/NaN/NaN\n";
		cmd += "\ngrdmask " + ice_bounds_path + " -R" + mag_grd_path + " -Gedge_ice.grd -S600 -N1/NaN/NaN\n";
		cmd += "\ngrdmask " + rock_bounds_path + " -R" + mag_grd_path + " -Ginside_rock.grd -NNaN/NaN/1\n";
		cmd += "\ngrdmask " + rock_bounds_path + " -R" + mag_grd_path + " -Grock_edge.grd -S600 -N1/NaN/NaN\n";
		cmd += "\ngrdmath inside_rock.grd rock_edge.grd OR = internal_rock.grd\n";
		cmd += "\ngrdmath outside_ice.grd edge_ice.grd OR = beyond_ice.grd\n";
		cmd += "\ngrdmath beyond_ice.grd internal_rock.grd AND = off_ice.grd\n";
		cmd += "\ngrdmath " + mag_grd_path + " off_ice.grd OR = " + pair_off_ice_grd + "\n";
		cmd += "\ngrdclip " + pair_off_ice_grd + " -Sb0.00001/NaN -G" + pair_off_ice_grd + "\n";
		subprocess.call(cmd,shell=True);

		os.remove("outside_ice.grd");
		os.remove("edge_ice.grd");
		os.remove("inside_rock.grd");
		os.remove("rock_edge.grd");
		os.remove("internal_rock.grd");
		os.remove("beyond_ice.grd");
		os.remove("off_ice.grd");

		cmd  = "\ngrdinfo -L2 " + pair_off_ice_grd + "\n";
		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		info = pipe.read();
		pipe.close();

		stdev = info[re.search("stdev:\s*", info).end(0) : re.search("stdev:\s*\d+\.*\d*", info).end(0)];
		mean  = info[re.search("mean:\s*", info).end(0) : re.search("mean:\s*\-*\d+\.*\d*", info).end(0)];

		upper = str(float(mean) + 2 * float(stdev));
		lower = str(float(mean) - 2 * float(stdev));

		cmd = "\ngrdclip " + pair_off_ice_grd + " -Sb" + lower + "/NaN -Sa" + upper + "/NaN -G" + clipped_grd + "\n";
		subprocess.call(cmd,shell=True);

	cmd  = "\ngrdinfo -L2 " + clipped_grd + "\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	stdev = info[re.search("stdev:\s*", info).end(0) : re.search("stdev:\s*\d+\.*\d*", info).end(0)];
	mean  = info[re.search("mean:\s*", info).end(0) : re.search("mean:\s*\-*\d+\.*\d*", info).end(0)];

	cmd  = "\ngrdinfo -L1 " + clipped_grd + "\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	median  = info[re.search("median:\s*", info).end(0) : re.search("median:\s*\-*\d+\.*\d*", info).end(0)];

	print(mag_grd_path + " " + pair + " " + median + " " + mean + " " + stdev);

	mag_txt_path = mag_grd_path[mag_grd_path.rfind("/") + 1 : mag_grd_path.rfind(".")] + ".txt";

	cmd = "\ngrd2xyz " + mag_grd_path + " | gawk '$0 !~ /a/ {print $1\" \"$2\" \"$3\" " + median + " " + mean + " " + stdev + " " + interval + " " + str(season_days[0]) + " " + str(season_days[1]) + " " + str(season_days[2]) + " " + str(season_days[3]) + " " + str(datetime_m.year + float(m_dec_year)) + "\"}' > " + mag_txt_path + "\n"
	subprocess.call(cmd, shell=True);

	ps_path = pair + "_off_ice.ps";

	cmd  = "\nmakecpt -Crainbow -T0/3/0.01 > unc.cpt\n";
	cmd += "\ngrdimage " + clipped_grd + " -Jx1:2000000 -R" + xmin + "/" + ymin + "/" + xmax + "/" + ymax + "r -Cunc.cpt -Q -P -K > " + ps_path + "\n";
	cmd += "\npsxy " + ice_bounds_path + " -Jx1:2000000 -R" + xmin + "/" + ymin + "/" + xmax + "/" + ymax + "r -W1p,black -O -K >> " + ps_path + "\n";
	cmd += "\npsxy " + rock_bounds_path + " -Jx1:2000000 -R" + xmin + "/" + ymin + "/" + xmax + "/" + ymax + "r -W1p,black -O -K >> " + ps_path + "\n";
	cmd += "\npsscale -D2c/4c/5c/0.2c -Cunc.cpt -B1:\"Speed\":/:\"m day@+-1@+\": -O >> " + ps_path + "\n";
	cmd += "\nps2raster -A -Tf " + ps_path + "\n";
	subprocess.call(cmd,shell=True);

	os.remove("unc.cpt");
	os.remove(ps_path);
	
	return;


if __name__ == "__main__":

	import os;
	import sys;

	assert len(sys.argv) > 3, "\n***** ERROR: velUnc.py requires 3 arguments, " + str(len(sys.argv)) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";

	velUnc(sys.argv[1], sys.argv[2], sys.argv[3]);

	exit();
