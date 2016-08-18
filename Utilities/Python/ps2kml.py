#!/usr/bin/python

# ps2kml.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


import math;
import os;
import re;
import subprocess;
import sys;


def ps2kml(pspath, utm_zone):

	assert os.path.exists(pspath), "\n***** ERROR: " + pspath + " does not exist\n";

	cmd  = "\ngrep \"grdvector\" " + pspath + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	xmin = info[re.search("-R",info).end(0):re.search("-R\d+\.*\d*",info).end(0)].strip();
	ymin = info[re.search("-R\d+\.*\d*/",info).end(0):re.search("-R\d+\.*\d*/\d+\.*\d*",info).end(0)].strip();
	xmax = info[re.search("-R\d+\.*\d*/\d+\.*\d*/",info).end(0):re.search("-R\d+\.*\d*/\d+\.*\d*/\d+\.*\d*",info).end(0)].strip();
	ymax = info[re.search("-R\d+\.*\d*/\d+\.*\d*/\d+\.*\d*/",info).end(0):re.search("-R\d+\.*\d*/\d+\.*\d*/\d+\.*\d*/\d+\.*\d*",info).end(0)].strip();

	ul_lat  = ymax;
	ul_long = xmin;
	ll_lat  = ymin;
	ll_long = ul_long;
	lr_lat  = ll_lat;
	lr_long = xmax;
	ur_lat  = ul_lat;
	ur_long = lr_long;

	geo_coords = [ul_long, ul_lat, ll_long, ll_lat, lr_long, lr_lat, ur_long, ur_lat];

	if utm_zone.lower().find("none") < 0:
		cmd = "\necho \"" + ul_long + " " + ul_lat + "\n" + ll_long + " " + ll_lat + "\n" + lr_long + " " + lr_lat + "\n" + ur_long + " " + ur_lat + "\" | mapproject -Ju" + utm_zone + "/1:1 -F -C -I\n";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		geo_coords = pipe.read().split();
		pipe.close();

	print(geo_coords);


	index = pspath.rfind("/");

	psdir = pspath[ : index];

	if index == -1:
		psdir = ".";
		
	psname = pspath[ index + 1 : pspath.rfind(".ps")];

	kml_file = open(psdir + "/" + psname + ".kml","w");
	kml_file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
	kml_file.write("<kml xmlns=\"http://earth.google.com/kml/2.1\"\n");
	kml_file.write(" xmlns:gx=\"http://www.google.com/kml/ext/2.2\">\n");
	kml_file.write("<Document>\n");
	kml_file.write("<name>" + psname + "</name>\n");
	kml_file.write("<open>1</open>\n");
	kml_file.write("<GroundOverlay>\n");
	kml_file.write("<name>" + psname + "</name>\n");
	kml_file.write("<description>" + psname + "</description>\n");
	kml_file.write("<Icon>\n");
	kml_file.write("<href>" + psname + ".png</href>\n");
	kml_file.write("<viewBoundScale>0.75</viewBoundScale>\n");
	kml_file.write("</Icon>\n");
	kml_file.write("<gx:LatLonQuad>\n");

	cmd  = "\ngrep \" -P\" " + pspath + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	if info.find(" -P") > -1:
		if float(geo_coords[2]) > 180.0:
			kml_file.write("<coordinates>" + str(-360.0 + float(geo_coords[2])) + "," + geo_coords[3] + " " + str(-360.0 + float(geo_coords[4])) + "," + geo_coords[5] + " " + str(-360.0 + float(geo_coords[6])) + "," + geo_coords[7] + " " + str(-360.0 + float(geo_coords[0])) + "," + geo_coords[1] + "</coordinates>\n");
		else:
			kml_file.write("<coordinates>" + geo_coords[2] + "," + geo_coords[3] + " " + geo_coords[4] + "," + geo_coords[5] + " " + geo_coords[6] + "," + geo_coords[7] + " " + geo_coords[0] + "," + geo_coords[1] + "</coordinates>\n");
	else:
		if float(geo_coords[2]) > 180.0:
			kml_file.write("<coordinates>" + str(-360.0 + float(geo_coords[0])) + "," + geo_coords[1] + " " + str(-360.0 + float(geo_coords[2])) + "," + geo_coords[3] + " " + str(-360.0 + float(geo_coords[4])) + "," + geo_coords[5] + " " + str(-360.0 + float(geo_coords[6])) + "," + geo_coords[7] + "</coordinates>\n");
		else:
			kml_file.write("<coordinates>" + geo_coords[0] + "," + geo_coords[1] + " " + geo_coords[2] + "," + geo_coords[3] + " " + geo_coords[4] + "," + geo_coords[5] + " " + geo_coords[6] + "," + geo_coords[7] + "</coordinates>\n");

	kml_file.write("</gx:LatLonQuad>\n");
	kml_file.write("</GroundOverlay>\n");
	kml_file.write("</Document>\n");
	kml_file.write("</kml>\n");
	kml_file.close();

	cmd = "";

	if info.find(" -P") > -1:
		cmd = "\nps2raster -A -P -TG " + pspath + "\n";
	else:
		cmd = "\nps2raster -A -TG " + pspath + "\n";

	subprocess.call(cmd,shell=True);

	return;


if __name__ == "__main__":

	import os;
	import sys;

	assert len(sys.argv) > 1, "\n***** ERROR: ps2kml.py requires at least 1 argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";

	if len(sys.argv) < 3:
		ps2kml(sys.argv[1],"none");

	else:
		ps2kml(sys.argv[1],sys.argv[2]);

	exit();





