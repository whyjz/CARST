#!/usr/bin/python


# elevProfile.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# Usage
# *****
# python elevProfile.py icesat_dem_elevs.gmt


def elevProfile(track_path, dem_grd_path, ice_bounds_path, rock_bounds_path, label):

	from distanceFromUTM import *;
	import os;
	import subprocess;

	assert os.path.exists(track_path), "\n***** ERROR: " + track_path + " does not exist\n";
	assert os.path.exists(dem_grd_path), "\n***** ERROR: " + dem_grd_path + " does not exist\n";

	output_profile_path = track_path[track_path.rfind("/") + 1 : track_path.rfind(".")] + "_" + dem_grd_path[dem_grd_path.rfind("/") + 1 : dem_grd_path.rfind(".")] + ".gmt";

	print(output_profile_path);

	cmd = "\ngrdtrack " + track_path + " -G" + dem_grd_path + " -nn | gawk '$0 !~ /a/ {print $0}' > temp.dat\n";
	subprocess.call(cmd, shell=True);

	distanceFromUTM("temp.dat", output_profile_path);
	os.remove("temp.dat");

	cmd  = "\ngmtinfo -C " + output_profile_path + "\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip().split();
	pipe.close();

	R = "-R" + str(float(info[4]) / 1000.) + "/" + str(float(info[5]) / 1000.) + "/" + info[6] + "/" + info[7];
	J = "-JX10c";
	B = "-Ba2f2g2:\"Distance Along Track (km)\":/a100f100g100:\"Elevation (m)\"::,::.\"Elevations from " + label + "\":WeSn";
	fonts = "--FONT_TITLE=18p,1,black --FONT_LABEL=14p,1,black --FONT_ANNOT_PRIMARY=12p,1,black --FONT_ANNOT_SECONDARY=12p,1,black";
	output_ps_path = output_profile_path.replace(".gmt", ".ps");

	cmd  = "\npsbasemap " + J + " " + R + " " + B + " " + fonts + " -P -K > " + output_ps_path + "\n";
	cmd += "\ngmtselect -F" + ice_bounds_path + " " + output_profile_path + " | gmtselect -If -F" + rock_bounds_path + " | gawk '{print $3/1000\" \"$4}' | psxy " + J + " " + R + " -Sc0.05c -Gblue -O -K >> " + output_ps_path + "\n";
	cmd += "\ngmtselect -If -F" + ice_bounds_path + " " + output_profile_path + " > temp.dat\n";
	cmd += "\ngmtselect -F" + rock_bounds_path + " " + output_profile_path + " >> temp.dat\n";
	cmd += "\ngawk '{print $3/1000\" \"$4}' temp.dat | psxy " + J + " " + R + " -Sc0.05c -Ggreen -O -K >> " + output_ps_path + "\n";
	cmd += "\necho \"1.4 9.9\\n4.9 9.9\\n4.9 8.5\\n1.4 8.5\" | psxy " + J + " -R0/10/0/10 -L -W1p,black -Gwhite -O -K >> " + output_ps_path + "\n";
	cmd += "\necho \"1.75 9.8 12p,1,black 0 LT DEM (ice)\" | pstext " + J + " -R0/10/0/10 -F+f+a+j -O -K >> " + output_ps_path + "\n";
	cmd += "\necho \"1.75 9.1 12p,1,black 0 LT DEM (off-ice)\" | pstext " + J + " -R0/10/0/10 -F+f+a+j -O -K >> " + output_ps_path + "\n";
	cmd += "\necho \"1.55 9.65\" | psxy " + J + " -R0/10/0/10 -Ss0.3c -Gblue -O -K >> " + output_ps_path + "\n";
	cmd += "\necho \"1.55 8.95\" | psxy " + J + " -R0/10/0/10 -Ss0.3c -Ggreen -O >> " + output_ps_path + "\n";
	cmd += "\nps2raster -A -Tf " + output_ps_path + "\n";
	subprocess.call(cmd, shell=True);

	os.remove(output_ps_path);
	os.remove("temp.dat");

	output_map_path = output_profile_path.replace(".gmt", "_map.ps");
	J = "-Jo62/75.5/135/1:1500000";
	R = "-R53.5/74.5/69.5/76.4r";

	cmd  = "\npscoast " + J + " " + R + " -G200/200/200 -Df -Swhite -W1.5p,black --PS_MEDIA=A3 -P -K > " + output_map_path + "\n";
	cmd += "\nmapproject -Ju41X/1:1 -F -C -I " + ice_bounds_path + " | psxy -J -R -W1p,blue -O -K >> " + output_map_path + "\n";
	cmd += "\nmapproject -Ju41X/1:1 -F -C -I " + rock_bounds_path + " | psxy -J -R -W1p,black -O -K >> " + output_map_path + "\n";
	cmd += "\nmapproject -Ju41X/1:1 -F -C -I " + output_profile_path + " | psxy -J -R -Sc0.2c -Gred -O -K >> " + output_map_path + "\n";
	cmd += "\npsbasemap -J -R -Lfx2.5c/3c/75.5/10k+l+jr --FONT_LABEL=20p,1,black --FONT_ANNOT_PRIMARY=20p,1,black -O -K >> " + output_map_path + "\n";
	cmd += "\npsbasemap -J -R -Bf2a2g2:\"Longitude\":/f1a1g1:\"Latitude\"::,::.\"\":wESn --FONT_LABEL=20p,1,black --FONT_ANNOT_PRIMARY=20p,1,black -O >> " + output_map_path + "\n";
	cmd += "\nps2raster -A -Tf " + output_map_path + "\n";
	subprocess.call(cmd, shell=True);

	os.remove(output_map_path);

	return;





if __name__ == "__main__":

	import os;
	import sys;

	assert len(sys.argv) > 5, "\n***** ERROR: elevProfile.py requires 5 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";
	assert os.path.exists(sys.argv[4]), "\n***** ERROR: " + sys.argv[4] + " does not exist\n";

	elevProfile(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]);

	exit();

