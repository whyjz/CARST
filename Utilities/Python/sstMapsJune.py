#!/usr/bin/python


# sstMaps.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# USAGE
# *****
# python sstMaps.py /path/to/grid_list.txt /another/path/to/kml_bounds.kml
#		grid_list.txt:  one-column ASCII text file with paths to grids that will be sampled
#		kml_bounds.kml: kml file defining bounds over which the grids in grid_list will be sampled


def sstMaps(grid_list_path):

	import datetime;
	import os;
	import re;
	import shutil;
	import subprocess;

	assert os.path.exists(grid_list_path), "\n***** ERROR: " + grid_list_path + " does not exist\n";

	ICE_BOUNDS  = "/data/akm/NovZ/Boundaries/NovZ_bounds_ice_sub.gmt";
	ROCK_BOUNDS = "/data/akm/NovZ/Boundaries/NovZ_bounds_rock_sub.gmt";

	out_grds     = {};
	out_grd_days = {};

	infile  = open(grid_list_path, "r");
	
	for grid_path in infile:

		grid_path = grid_path.strip();
		grid_name = grid_path[grid_path.rfind("/") + 1 : ];
		date      = grid_name[re.search("^\d{6}", grid_name).start(0) : re.search("^\d{6}", grid_name).end(0)];

		year  = date[0:4];
		month = int(date[4:6]);
		day   = date[6:8];

		if month != 6:
			continue;

		out_name   = year + "_june_sst";
		out_grd    = out_name + ".grd";

		if out_grd not in out_grds:
			out_grds[out_grd]       = out_grd;
			out_grd_days[out_grd]   = 1;

		else:
			out_grd_days[out_grd]   += 1;

		if not os.path.exists(out_grd) and not os.path.exists(out_name + ".pdf"):
			shutil.copy(grid_path, out_grd);	

		elif not os.path.exists(out_name + ".pdf"):
			cmd  = "\ngrdclip " + grid_path + " -Sb-50/NaN -Gtemp.grd\n";
			cmd += "\ngrdmath temp.grd " + out_grd + " ADD = " + out_grd + "\n";
			subprocess.call(cmd, shell=True);
			os.remove("temp.grd");

	infile.close();

	for out_grd in out_grds:

		out_name = out_grd[ : out_grd.rfind(".")];

		if not os.path.exists(out_name + ".pdf"):
			cmd = "\ngrdmath " + out_grd + " " + str(out_grd_days[out_grd]) + " DIV = " + out_grd + "\n";
			subprocess.call(cmd, shell=True);

		ps_path = out_grd[ : out_grd.rfind(".")] + ".ps";
		J       = "-Jm0.75c";
		R       = "-R50/70/70/78r";

		cmd  = "\ngrdimage -Y2c " + out_grd + " " + J + " " + R + " -Ba5g5/a2g2::wESn -Csst.cpt --PS_MEDIA=A3 -P -K > " + ps_path + "\n";
		cmd += "\ngrdcontour " + out_grd + " " + J + " " + R + " -A0.25+f12p,1,black -C0.25 -O -K >> " + ps_path + "\n";
		cmd += "\npsxy " + ICE_BOUNDS + " " + J + " " + R + " -W1p,white -O -K >> " + ps_path + "\n";
		cmd += "\npsxy " + ROCK_BOUNDS + " " + J + " " + R + " -W1p,white -O -K >> " + ps_path + "\n";
		cmd += "\npsbasemap " + J + " " + R + " -Lfx13.1c/2c/71/100k+jr+u+p0.5,black+gwhite --FONT_ANNOT_PRIMARY=10p,1,black --FONT_LABEL=10p,1,black -O -K >> " + ps_path + "\n";
		cmd += "\necho \"50.5 77.8 24p,1,black 0 ML " + out_grd[out_grd.find("_") + 1 : out_grd.rfind("_sst")].capitalize() + " " + out_grd[0:4] + "\" | pstext " + J + " " + R + " -F+f+a+j -W1p,black -Gwhite -O -K >> " + ps_path + "\n";
		cmd += "\necho \"51 77 12p,3,black 0 ML Barents Sea\" | pstext -Jm0.75c -R50/70/70/78r -F+f+a+j -W1p,black -Gwhite -O -K >> " + ps_path + "\n";
		cmd += "\necho \"65 75 12p,3,black 0 ML Kara Sea\" | pstext -Jm0.75c -R50/70/70/78r -F+f+a+j -W1p,black -Gwhite -O -K >> " + ps_path + "\n";
		cmd += "\npsscale -D13c/6c/5c/0.2c -B1:\"SST (C)\": -Csst.cpt -T+p1p,black+gwhite --FONT_ANNOT_PRIMARY=12p,1,black --FONT_LABEL=12p,1,black --FONT_ANNOT_SECONDARY=12p,1,black -O >> " + ps_path + "\n";
		cmd += "\nps2raster -A -Tf " + ps_path + "\n";
		subprocess.call(cmd, shell=True);

		os.remove(ps_path);

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: sstMaps.py requires 1 argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	sstMaps(sys.argv[1]);

	exit();


