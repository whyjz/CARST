#!/usr/bin/python


# plotICESatTrack.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# Usage
# *****
# python plotICESatTrack.py icesat_dem_elevs.gmt


def plotICESatTrack(icesat_path, dem_grd_path, ice_bounds_path, rock_bounds_path, input_track_num):

	from distanceFromUTM import *;
	import os;
	import subprocess;

	assert os.path.exists(icesat_path), "\n***** ERROR: " + icesat_path + " does not exist\n";
	assert os.path.exists(dem_grd_path), "\n***** ERROR: " + dem_grd_path + " does not exist\n";

	track = 0;

	try:
		track = int(input_track_num);
	except ValueError:
		print("\n***** ERROR: \"" + input_track_num + "\" is not a vaild integer, please re-run command with valid integer\n");
		return;

	track_dir = "Track" + str(track);

	UTM_E_COL        = 0;
	UTM_N_COL        = 1;
	GEOID_HEIGHT_COL = 6;
	STRIP_NUM_COL    = 13;
	TRACK_NUM_COL    = 14;	
	ORTHO_ELEV_COL   = 15;

	track_gmt_path = track_dir + "/track_" + str(track) + "_map.gmt";

	cmd = "gawk 'NR !~ /#/ && $" + str(TRACK_NUM_COL + 1) + " == " + str(track) + " {print $" + str(UTM_E_COL + 1) + "\" \"$" + str(UTM_N_COL + 1) + "\" \"$" + str(ORTHO_ELEV_COL + 1)  + "\" \"$" + str(GEOID_HEIGHT_COL + 1) + "\" \"$" + str(TRACK_NUM_COL + 1) + "\" \"$" + str(STRIP_NUM_COL + 1) + "}' " + icesat_path + " | grdtrack -G" + dem_grd_path + " -nn | gawk '$0 !~ /a/ {print $0}' > " + track_gmt_path + "\n";
	subprocess.call(cmd, shell=True);

	strips = {};

	infile = open(track_gmt_path);

	for line in infile:

		elements = line.split();
		strip    = elements[len(elements) - 2].replace("-", "");

		if strip not in strips:
			strips[strip] = line;
		else:
			strips[strip] += line;
			
	infile.close();

	if not os.path.exists(track_dir):
		os.mkdir(track_dir);

	for strip in strips:

		temp_strip_path = track_dir + "/temp_" + strip + ".txt";
		strip_path      = track_dir + "/strip_" + strip + ".gmt";

		outfile = open(temp_strip_path, "w");
		outfile.write(strips[strip]);
		outfile.close();

		distanceFromUTM(temp_strip_path, strip_path);

		os.remove(temp_strip_path);

		cmd  = "\ngmtinfo -C " + strip_path + "\n";
		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		info = pipe.read().strip().split();
		pipe.close();

		if info[14].lower().find("a") > -1:
			continue;

		R = "-R" + str(float(info[4]) / 1000.) + "/" + str(float(info[5]) / 1000.) + "/" + str(min(float(info[6]), float(info[14]))) + "/" + str(max(float(info[7]), float(info[15])));
		J = "-JX10c";
		B = "-Ba10f10g10:\"Distance Along Track (km)\":/a100f100g100:\"Elevation (m)\"::,::.\"Track " + str(track) + " Strip " + strip + " Elevations\":WeSn";
		fonts = "--FONT_TITLE=18p,1,black --FONT_LABEL=14p,1,black --FONT_ANNOT_PRIMARY=12p,1,black --FONT_ANNOT_SECONDARY=12p,1,black";
		strip_ps_path  = strip_path.replace(".gmt", ".ps");
		strip_cmd_path = strip_path.replace(".gmt", ".cmd");

		cmd  = "\npsbasemap " + J + " " + R + " " + B + " " + fonts + " -P -K > " + strip_ps_path + "\n";
		cmd += "\ngmtselect -F" + ice_bounds_path + " " + strip_path + " | gmtselect -If -F" + rock_bounds_path + " | gawk '{print $3/1000\" \"$4}' | psxy " + J + " " + R + " -Sc0.05c -Gblue -O -K >> " + strip_ps_path + "\n";
		cmd += "\ngmtselect -If -F" + ice_bounds_path + " " + strip_path + " > " + track_dir + "/temp\n";
		cmd += "\ngmtselect -F" + rock_bounds_path + " " + strip_path + " >> " + track_dir + "/temp\n";
		cmd += "\ngawk '{print $3/1000\" \"$4}' " + track_dir + "/temp | psxy " + J + " " + R + " -Sc0.05c -Ggreen -O -K >> " + strip_ps_path + "\n";
		cmd += "\ngawk '{print $3/1000\" \"$8}' " + strip_path + " | psxy " + J + " " + R + " -Sc0.05c -Gred -O -K >> " + strip_ps_path + "\n";
		cmd += "\necho \"6.4 9.9\\n9.9 9.9\\n9.9 7.9\\n6.4 7.9\" | psxy " + J + " -R0/10/0/10 -L -W1p,black -Gwhite -O -K >> " + strip_ps_path + "\n";
		cmd += "\necho \"6.75 9.8 12p,1,black 0 LT ICESat (ice)\" | pstext " + J + " -R0/10/0/10 -F+f+a+j -O -K >> " + strip_ps_path + "\n";
		cmd += "\necho \"6.75 9.1 12p,1,black 0 LT ICESat (off-ice)\" | pstext " + J + " -R0/10/0/10 -F+f+a+j -O -K >> " + strip_ps_path + "\n";
		cmd += "\necho \"6.75 8.4 12p,1,black 0 LT DEM\" | pstext " + J + " -R0/10/0/10 -F+f+a+j -O -K >> " + strip_ps_path + "\n";
		cmd += "\necho \"6.55 9.65\" | psxy " + J + " -R0/10/0/10 -Ss0.3c -Gblue -O -K >> " + strip_ps_path + "\n";
		cmd += "\necho \"6.55 8.95\" | psxy " + J + " -R0/10/0/10 -Ss0.3c -Ggreen -O -K >> " + strip_ps_path + "\n";
		cmd += "\necho \"6.55 8.25\" | psxy " + J + " -R0/10/0/10 -Ss0.3c -Gred -O >> " + strip_ps_path + "\n";
		cmd += "\nps2raster -A -Tf " + strip_ps_path + "\n";
		subprocess.call(cmd, shell=True);

		outfile = open(strip_cmd_path, "w");
		outfile.write(cmd);
		outfile.close();

		os.remove(strip_ps_path);
		os.remove(track_dir + "/temp");

	track_map_path = track_dir + "/track_" + str(track) + "_map.ps";
	track_cmd_path = track_dir + "/track_" + str(track) + "_map.cmd";
	J = "-Jo62/75.5/135/1:1500000";
	R = "-R53.5/74.5/69.5/76.4r";

	cmd  = "\npscoast " + J + " " + R + " -G200/200/200 -Df -Swhite -W1.5p,black --PS_MEDIA=A3 -P -K > " + track_map_path + "\n";
	cmd += "\nmapproject -Ju41X/1:1 -F -C -I " + ice_bounds_path + " | psxy -J -R -W1p,blue -O -K >> " + track_map_path + "\n";
	cmd += "\nmapproject -Ju41X/1:1 -F -C -I " + rock_bounds_path + " | psxy -J -R -W1p,black -O -K >> " + track_map_path + "\n";
	cmd += "\nmapproject -Ju41X/1:1 -F -C -I " + track_gmt_path + " | psxy -J -R -Sc0.2c -Gred -O -K >> " + track_map_path + "\n";
	cmd += "\npsbasemap -J -R -Lfx2.5c/3c/75.5/10k+l+jr --FONT_LABEL=20p,1,black --FONT_ANNOT_PRIMARY=20p,1,black -O -K >> " + track_map_path + "\n";
	cmd += "\npsbasemap -J -R -Bf2a2g2:\"Longitude\":/f1a1g1:\"Latitude\"::,::.\"\":wESn --FONT_LABEL=20p,1,black --FONT_ANNOT_PRIMARY=20p,1,black -O >> " + track_map_path + "\n";
	cmd += "\nps2raster -A -Tf " + track_map_path + "\n";
	subprocess.call(cmd, shell=True);

	outfile = open(track_cmd_path, "w");
	outfile.write(cmd);
	outfile.close();

	os.remove(track_map_path);

	return;





if __name__ == "__main__":

	import os;
	import sys;

	assert len(sys.argv) > 3, "\n***** ERROR: plotICESatTrack.py requires 5 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";
	assert os.path.exists(sys.argv[4]), "\n***** ERROR: " + sys.argv[4] + " does not exist\n";

	plotICESatTrack(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]);

	exit();

