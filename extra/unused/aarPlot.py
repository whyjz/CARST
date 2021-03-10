#!/usr/bin/python


# aarPlot.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

# Produces graph of AAR (x-axis) versus elevation in directory where run

# Usage
# *****
# python aarPlot.py /path/to/glacier_elevation_grid.grd ela1 ela2 ela3
#	/path/to/glacier_elevation_grid.grd is the path to the grid containing elevations for the glacier
#	ela1 is a number denoting the minimum ELA to plot as a circle on the graph
#	ela2 is a number denoting the "actual" ELA to plot as a circle on the graph
#	ela3 is a number denoting the maximum ELA to plot as a circle on the graph



def aarPlot(elev_grd_path, ela1, ela2, ela3):


#	Check elev_grd_path exists

	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";

#	Get minimum and maximum elevations using "grdinfo" command

	import re;
	import subprocess;

	cmd  = "\ngrdinfo " + elev_grd_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	zmin = info[re.search("z_min:\s*",info).end(0) : re.search("z_min:\s*\-*\d+\.*\d*",info).end(0)];
	zmax = info[re.search("z_max:\s*",info).end(0) : re.search("z_max:\s*\-*\d+\.*\d*",info).end(0)];

#	Round zmin down to nearest multiple of 10, round zmax up to nearest multiple of 10

	zmin = str(int(float(zmin) - (float(zmin) % 10)));
	zmax = str(int(float(zmax) + (10 - (float(zmax) % 10))));

#	Find area of the glacier basin

	cmd  = "\ngrdvolume " + elev_grd_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().split();
	pipe.close();

	glacier_area = info[1];

#	If AAR file does NOT exist: iteratively clip glacier elevation grid in 10 m elevation increments and store elevation and AAR as columns in output file
#	If AAR file DOES exist: read AAR file

	elev_aar = {};

	name     = elev_grd_path[elev_grd_path.rfind("/") + 1: elev_grd_path.rfind(".")];
	aar_path = name + "_AAR.txt";

	if not os.path.exists(aar_path):

		outfile = open(aar_path, "w");

		outfile.write("Elevation_Threshold_(m) AAR_(%_of_total_area)\n");

		for i in range(int(zmin), int(zmax), 10):
	
			cmd = "\ngrdclip " + elev_grd_path + " -Sb" + str(i) + "/NaN -Gtemp.grd\n";
			subprocess.call(cmd,shell=True);

			cmd  = "\ngrdvolume temp.grd\n";
			pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
        		info = pipe.read().split();
        		pipe.close();

			area = info[1];
			aar  = str(float(area)/float(glacier_area));

			outfile.write(str(i) + " " + aar + "\n");

			elev_aar[str(i)] = aar;

		outfile.close();

	else:

		infile = open(aar_path, "r");

		for line in infile:

			if line.find("a") > -1:
				continue;
	
			elements = line.split();

			elev = elements[0];
			aar  = elements[1];

			elev_aar[elev] = aar;

		infile.close();

#	Adjust zmin and zmax for plotting to closest multiple 50 below zmin and closest multiple of 50 above zmax

	zmin = str(int(float(zmin) - (float(zmin) % 50)));
	zmax = str(int(float(zmax) + (50 - (float(zmax) % 50))));

#	Make AAR vs. elevation plot

	index = name.find("_");

	if index < 0:
		index = len(name);

	title = name[ : index] + " Glacier AAR vs. Elevation";

	ps_path = name + "_AAR.ps";

	cmd  = "\npsbasemap -JX16c/10c -R0/100/" + zmin + "/" + zmax + " -Ba10f10g20:\"AAR (% of total area)\":/a200f100g200:\"Elevation (m)\"::,::.\"" + title + "\":WS --D_FORMAT=%.12lg --LABEL_FONT=1 --LABEL_FONT_SIZE=14 --ANNOT_FONT_PRIMARY=1 --ANNOT_FONT_SIZE_PRIMARY=12 --ANNOT_FONT_SECONDARY=1 --ANNOT_FONT_SIZE_SECONDARY=10 --HEADER_FONT=1 --HEADER_FONT_SIZE=18 -P -K > " + ps_path + "\n"; 
	cmd += "\ngawk 'NR > 1 {print 100*$2\" \"$1}' " + aar_path + " | psxy -J -R -W1p,black -O -K >> " + ps_path + "\n";
	cmd += "\necho \"" + str(100 * float(elev_aar[str(int(ela1) - int(ela1) % 10)])) + " " + str(int(ela1) - int(ela1) % 10) + "\" | psxy -J -R -Sc0.35c -Gblue -O -K >> " + ps_path + "\n";
	cmd += "\necho \"" + str(100 * float(elev_aar[str(int(ela2) - int(ela2) % 10)])) + " " + str(int(ela2) - int(ela2) % 10) + "\" | psxy -J -R -Sc0.35c -Gdarkgreen -O -K >> " + ps_path + "\n";
	cmd += "\necho \"" + str(100 * float(elev_aar[str(int(ela3) - int(ela3) % 10)])) + " " + str(int(ela3) - int(ela3) % 10) + "\" | psxy -J -R -Sc0.35c -Gred -O -K >> " + ps_path + "\n";
	cmd += "\necho \"6.7 7.55\\n6.7 9.45\\n9.75 9.45\\n9.75 7.55\" | psxy -J -R0/10/0/10 -W1p,black -Gwhite -O -K >> " + ps_path + "\n";
	cmd += "\necho \"6.9 9.1\" | psxy -J -R -Sc0.35c -Gred -O -K >> " + ps_path + "\n";
	cmd += "\necho \"6.9 8.5\" | psxy -J -R -Sc0.35c -Gdarkgreen -O -K >> " + ps_path + "\n";
	cmd += "\necho \"6.9 7.9\" | psxy -J -R -Sc0.35c -Gblue -O -K >> " + ps_path + "\n";
	cmd += "\necho \"7.1 9.1 12 0 1 ML AAR at " + str(int(ela3) - int(ela3) % 10) + " m\" | pstext -J -R -Gblack -O -K >> " + ps_path + "\n";
	cmd += "\necho \"7.1 8.5 12 0 1 ML AAR at ELA (" + str(int(ela2) - int(ela2) % 10) + " m)\" | pstext -J -R -Gblack -O -K >> " + ps_path + "\n";
	cmd += "\necho \"7.1 7.9 12 0 1 ML AAR at " + str(int(ela1) - int(ela1) % 10) + " m\" | pstext -J -R -Gblack -O >> " + ps_path + "\n";
	print(cmd);
	cmd += "\nps2raster -A -Tf " + ps_path + "\n";
	subprocess.call(cmd,shell=True);


	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 4, "\n***** ERROR: aarPlot.py requires 4 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	aarPlot(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]);

	exit();

