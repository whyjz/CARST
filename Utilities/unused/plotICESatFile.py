#!/usr/bin/python


# plotICESatFile.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# Usage
# *****
# python plotICESatFile.py icesat_dem_elevs.gmt


def plotICESatFile(icesat_path, dem_grd_path, ice_bounds_path, rock_bounds_path):

	from distanceFromUTM import *;
	import os;
	import subprocess;

	assert os.path.exists(icesat_path), "\n***** ERROR: " + icesat_path + " does not exist\n";
	assert os.path.exists(dem_grd_path), "\n***** ERROR: " + dem_grd_path + " does not exist\n";

	UTM_E_COL        = 0;
	UTM_N_COL        = 1;
	ELL_ELEV_COL     = 2;
	GEOID_HEIGHT_COL = 3;

	icesat_name = icesat_path[icesat_path.rfind("/") + 1 : icesat_path.rfind(".")];
	icesat_dem_gmt_path = icesat_name + "_dem.gmt";

	print(icesat_path);

	cmd = "gawk '{print $" + str(UTM_E_COL + 1) + "\" \"$" + str(UTM_N_COL + 1) + "\" \"$" + str(ELL_ELEV_COL + 1)  + "\" \"$" + str(GEOID_HEIGHT_COL + 1) + "\" \"$5\" \"$6\" \"$7}' " + icesat_path + " | grdtrack -G" + dem_grd_path + " -nn | gawk '$0 !~ /a/ {print $0}' > temp\n";
	subprocess.call(cmd, shell=True);

	if os.path.getsize("temp") == 0:
		print("\n***** WARNING: ICESat file \"" + icesat_path + "\" does not appear to overlap the DEM \"" + dem_grd_path + "\", skipping...\n");
		os.remove("temp");
		return;

	distanceFromUTM("temp", icesat_dem_gmt_path);

	print("HELLO");

	os.remove("temp");

	cmd  = "\ngmtinfo -C " + icesat_dem_gmt_path + "\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip().split();
	pipe.close();

	if info[16].lower().find("a") > -1:
		return;

	R = "-R" + str(float(info[4]) / 1000.) + "/" + str(float(info[5]) / 1000.) + "/" + str(min(float(info[6]), float(info[16]))) + "/" + str(max(float(info[7]), float(info[17])));
	J = "-JX10c";
	B = "-Ba10f10g10:\"Distance Along Track (km)\":/a100f100g100:\"Elevation (m)\"::,::.\"" + icesat_path + " Elevations\":WeSn";
	fonts = "--FONT_TITLE=18p,1,black --FONT_LABEL=14p,1,black --FONT_ANNOT_PRIMARY=12p,1,black --FONT_ANNOT_SECONDARY=12p,1,black";
	track_ps_path  = icesat_dem_gmt_path.replace(".gmt", ".ps");
	track_cmd_path = icesat_dem_gmt_path.replace(".gmt", ".cmd");

	cmd  = "\npsbasemap " + J + " " + R + " " + B + " " + fonts + " -P -K > " + track_ps_path + "\n";
	cmd += "\ngmtselect -F" + ice_bounds_path + " " + icesat_dem_gmt_path + " | gmtselect -If -F" + rock_bounds_path + " | gawk '{print $3/1000\" \"$4}' | psxy " + J + " " + R + " -Sc0.05c -Gblue -O -K >> " + track_ps_path + "\n";
	cmd += "\ngmtselect -If -F" + ice_bounds_path + " " + icesat_dem_gmt_path + " > temp\n";
	cmd += "\ngmtselect -F" + rock_bounds_path + " " + icesat_dem_gmt_path + " >> temp\n";
	cmd += "\ngawk '{print $3/1000\" \"$4}' temp | psxy " + J + " " + R + " -Sc0.05c -Ggreen -O -K >> " + track_ps_path + "\n";
	cmd += "\ngawk '{print $3/1000\" \"$9}' " + icesat_dem_gmt_path + " | psxy " + J + " " + R + " -Sc0.05c -Gred -O -K >> " + track_ps_path + "\n";
	cmd += "\necho \"6.4 9.9\\n9.9 9.9\\n9.9 7.9\\n6.4 7.9\" | psxy " + J + " -R0/10/0/10 -L -W1p,black -Gwhite -O -K >> " + track_ps_path + "\n";
	cmd += "\necho \"6.75 9.8 12p,1,black 0 LT ICESat (ice)\" | pstext " + J + " -R0/10/0/10 -F+f+a+j -O -K >> " + track_ps_path + "\n";
	cmd += "\necho \"6.75 9.1 12p,1,black 0 LT ICESat (off-ice)\" | pstext " + J + " -R0/10/0/10 -F+f+a+j -O -K >> " + track_ps_path + "\n";
	cmd += "\necho \"6.75 8.4 12p,1,black 0 LT DEM\" | pstext " + J + " -R0/10/0/10 -F+f+a+j -O -K >> " + track_ps_path + "\n";
	cmd += "\necho \"6.55 9.65\" | psxy " + J + " -R0/10/0/10 -Ss0.3c -Gblue -O -K >> " + track_ps_path + "\n";
	cmd += "\necho \"6.55 8.95\" | psxy " + J + " -R0/10/0/10 -Ss0.3c -Ggreen -O -K >> " + track_ps_path + "\n";
	cmd += "\necho \"6.55 8.25\" | psxy " + J + " -R0/10/0/10 -Ss0.3c -Gred -O >> " + track_ps_path + "\n";
	cmd += "\nps2raster -A -Tf " + track_ps_path + "\n";
	subprocess.call(cmd, shell=True);

	outfile = open(track_cmd_path, "w");
	outfile.write(cmd);
	outfile.close();

	os.remove(track_ps_path);
	os.remove("temp");

	map_ps_path  = icesat_dem_gmt_path.replace(".gmt", "_map.ps");
	map_cmd_path = icesat_dem_gmt_path.replace(".gmt", "_map.cmd");
#	J = "-Jo62/75.5/135/1:1500000";
	J = "-Ju8V/1:1000000";
	R = "-R-134.27/56.65/-131.1/58.76r";

	cmd  = "\npscoast " + J + " " + R + " -G200/200/200 -Df -Swhite -W1.5p,black --PS_MEDIA=A3 -P -K > " + map_ps_path + "\n";
	cmd += "\nmapproject -Ju8V/1:1 -F -C -I " + ice_bounds_path + " | psxy -J -R -W1p,blue -O -K >> " + map_ps_path + "\n";
	cmd += "\nmapproject -Ju8V/1:1 -F -C -I " + rock_bounds_path + " | psxy -J -R -W1p,black -O -K >> " + map_ps_path + "\n";
	cmd += "\nmapproject -Ju8V/1:1 -F -C -I " + icesat_path + " | psxy -J -R -Sc0.2c -Gred -O -K >> " + map_ps_path + "\n";
	cmd += "\npsbasemap -J -R -Lfx2.5c/3c/75.5/10k+l+jr --FONT_LABEL=20p,1,black --FONT_ANNOT_PRIMARY=20p,1,black -O -K >> " + map_ps_path + "\n";
	cmd += "\npsbasemap -J -R -Bf2a2g2:\"Longitude\":/f1a1g1:\"Latitude\"::,::.\"\":wESn --FONT_LABEL=20p,1,black --FONT_ANNOT_PRIMARY=20p,1,black -O >> " + map_ps_path + "\n";
	cmd += "\nps2raster -A -Tf " + map_ps_path + "\n";
	subprocess.call(cmd, shell=True);

	outfile = open(map_cmd_path, "w");
	outfile.write(cmd);
	outfile.close();

	os.remove(map_ps_path);

	return;



if __name__ == "__main__":

	import os;
	import sys;

	assert len(sys.argv) > 4, "\n***** ERROR: plotICESatFile.py requires 5 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";
	assert os.path.exists(sys.argv[4]), "\n***** ERROR: " + sys.argv[4] + " does not exist\n";

	plotICESatFile(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]);

	exit();

