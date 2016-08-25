#!/usr/bin/python


# unwLOSToVel.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# DESCRIPTION
# ***********
# unwLOSToVel.py takes the path to a NetCDF-format georectified, unwrapped interferogram and the path to a NetCDF-format aspect (slope) file at the same gridspacing 
#		 and creates E-W and N-S velocity grids


# USAGE
# *****
# python unwLOSToVel.py /path/to/geo_unw.grd /path/to/aspect_slope.grd


def unwLOSToVel(unw_grd_path, aspect_grd_path):

	import os;

	assert os.path.exists(unw_grd_path), "\n***** ERROR: " + unw_grd_path + " does not exist\n";
	assert os.path.exists(aspect_grd_path), "\n***** ERROR: " + aspect_grd_path + " does not exist\n";

	unw_rsc_path = unw_grd_path.replace("grd", "unw.rsc");

	infile = open(unw_rsc_path, "r");

	for line in infile:

		if line.find("HEADING") > -1:
			break;

	infile.close();

	heading = float(line.split()[1]);
	los     = heading;

	if heading < 0:
		los = los - 90.
		los = 360. + los;

	else:
		los = los + 90.

	los = 360 - los;
	los = los + 90;

	if los > 360:
		los = los -360;

	import subprocess;

	cmd  = "\ngrdinfo " + unw_grd_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	import re;

	xmin1 = info[re.search("x_min: ",info).end(0):re.search("x_min: -*\d+\.*\d*",info).end(0)];
	xmax1 = info[re.search("x_max: ",info).end(0):re.search("x_max: -*\d+\.*\d*",info).end(0)];
	ymin1 = info[re.search("y_min: ",info).end(0):re.search("y_min: -*\d+\.*\d*",info).end(0)];
	ymax1 = info[re.search("y_max: ",info).end(0):re.search("y_max: -*\d+\.*\d*",info).end(0)];
	xinc = info[re.search("x_inc: ",info).end(0):re.search("x_inc: \-*\d+\.*\d*",info).end(0)];

#	Initialize global bounds to first grid's bounds

	min_x = xmin1;
	max_x = xmax1;
	min_y = ymin1;
	max_y = ymax1;

#	Find bounds of second grid

	cmd  = "\ngrdinfo " + aspect_grd_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	xmin2 = info[re.search("x_min: ",info).end(0):re.search("x_min: -*\d+\.*\d*",info).end(0)];
	xmax2 = info[re.search("x_max: ",info).end(0):re.search("x_max: -*\d+\.*\d*",info).end(0)];
	ymin2 = info[re.search("y_min: ",info).end(0):re.search("y_min: -*\d+\.*\d*",info).end(0)];
	ymax2 = info[re.search("y_max: ",info).end(0):re.search("y_max: -*\d+\.*\d*",info).end(0)];

#	Determine minimum bounds that encompass both grids

	if float(xmin2) > float(min_x):
		min_x = xmin2;

	if float(xmax2) < float(max_x):
		max_x = xmax2;

	if float(ymin2) > float(min_y):
		min_y = ymin2;

	if float(ymax2) < float(max_y):
		max_y = ymax2;

	min_x = str(float(min_x) + float(xinc)/100000);
	max_x = str(float(max_x) - float(xinc)/100000);
	min_y = str(float(min_y) + float(xinc)/100000);
	max_y = str(float(max_y) - float(xinc)/100000);
	

	R = "-R" + min_x + "/" + min_y + "/" + max_x + "/" + max_y + "r";

	cmd  = "\ngrdcut " + unw_grd_path + " " + R + " -Gtemp_unw.grd\n";
	cmd += "\ngrdcut " + aspect_grd_path + " " + R + " -Gtemp_aspect.grd\n";
#	cmd += "\ngrdmask " + ice_path + " -Rtemp_unw.grd -Gtemp_off_ice.grd -N1/NaN/NaN -m\n";
#	cmd += "\ngrdmask " + rock_path + " -Rtemp_unw.grd -Gtemp_internal_rock.grd -NNaN/NaN/1 -m\n";
#	cmd += "\ngrdmath temp_off_ice.grd temp_internal_rock.grd XOR = temp_rock.grd\n";
#	cmd += "\ngrdmath temp_unw.grd temp_rock.grd OR = temp_unw_rock.grd\n";
	subprocess.call(cmd,shell=True);

#	os.remove("temp_off_ice.grd");
#	os.remove("temp_internal_rock.grd");

	mag_grd_path   = unw_grd_path.replace(".grd", "_magnitude.grd");
	east_grd_path  = unw_grd_path.replace(".grd", "_east.grd");
	north_grd_path = unw_grd_path.replace(".grd", "_north.grd");
	mag_tif_path   = mag_grd_path.replace("grd", "tif");
	
	import subprocess;

	cmd  = "\ngrdmath temp_aspect.grd " + str(los) + " SUB = temp.grd\n";
	cmd += "\ngrdmath temp.grd COSD = temp2.grd\n";
	cmd += "\ngrdmath 1 temp2.grd DIV = temp3.grd\n";
	cmd += "\ngrdmath temp_unw.grd temp3.grd MUL = " + mag_grd_path + "\n";
	cmd += "\ngrdmath " + mag_grd_path + " ABS = " + mag_grd_path + "\n";
	cmd += "\ngdalwarp -of GTiff -t_srs '+proj=longlat +datum=WGS84' " + mag_grd_path + " " + mag_tif_path + "\n";
	subprocess.call(cmd,shell=True);

#	cmd  = "\ngrdclip temp_aspect.grd -Sb0/NaN -Sa90/NaN -Gtemp_aspect_90.grd\n";
#	cmd += "\ngrdclip temp_aspect.grd -Sb90.0001/NaN -Sa180/NaN -Gtemp_aspect_180.grd\n";
#	cmd += "\ngrdclip temp_aspect.grd -Sb180.0001/NaN -Sa270/NaN -Gtemp_aspect_270.grd\n";
#	cmd += "\ngrdclip temp_aspect.grd -Sb270.0001/NaN -Gtemp_aspect_360.grd\n";
	cmd  = "\ngrdmath temp_aspect.grd COSD = temp_cos_aspect.grd\n";
	cmd += "\ngrdmath temp_aspect.grd SIND = temp_sin_aspect.grd\n";
	cmd += "\ngrdmath temp_cos_aspect.grd " + mag_grd_path + " MUL = " + east_grd_path + "\n";
	cmd += "\ngrdmath temp_sin_aspect.grd " + mag_grd_path + " MUL = " + north_grd_path + "\n";
	subprocess.call(cmd,shell=True);

	os.remove("temp.grd");
	os.remove("temp2.grd");
	os.remove("temp3.grd");
	os.remove("temp_aspect.grd");
	os.remove("temp_cos_aspect.grd");
	os.remove("temp_sin_aspect.grd");

	if os.path.exists(mag_tif_path + ".aux.xml"):
		os.remove(mag_tif_path + ".aux.xml");

	return;


if __name__ == "__main__":

	import os;
	import sys;

	assert len(sys.argv) > 2, "\n***** ERROR: unwLOSToVel.py requires 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	unwLOSToVel(sys.argv[1], sys.argv[2]);

	exit();

