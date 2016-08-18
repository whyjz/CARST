#!/usr/bin/python


# removeTrend.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# USAGE
# *****
# python removeTrend.py /path/to/vel.grd /path/to/rock.grd min_vel max_vel
# 	vel.grd:  velocity grid (netcdf format) to remove ramp from
# 	rock.grd: NetCDF-grid that defines off-ice area, must be on the same grid and have the same bounds as "vel.grd"
#	min_vel:  velocities below "min_vel" will be clipped before the a ramp is fitted
#	max_vel:  velocities above "max_vel" will be clipped before the a ramp is fitted


# OUTPUT
# ******
# vel_rr.grd - ramp removed version of vel.grd, written to current working directory


# DESCRIPTION
# ***********
# removeTrend.py fits a planar ramp to the area of "vel.grd" defined in "rock.grd", then remove this ramp from "vel.grd"


def removeTrend(vel_grd_path, ice_path, rock_path, min_vel, max_vel):

	import os;
	import re;
	import subprocess;

	assert os.path.exists(vel_grd_path), "\n***** ERROR: " + vel_grd_path + " does not exist\n";
	assert os.path.exists(rock_grd_path), "\n***** ERROR: " + rock_grd_path + " does not exist\n";

	vel_name = vel_grd_path[vel_grd_path.rfind("/") + 1 : vel_grd_path.rfind(".")];

	cmd  = "\ngrdmask " + ice_path + " -R" + vel_grd_path + " -N1/NaN/NaN -G" + vel_name + "_outside_ice.grd\n";
	cmd += "\ngrdmask " + rock_path + " -R" + vel_grd_path + " -NNaN/NaN/1 -G" + vel_name + "_inside_rock.grd\n";
	cmd += "\ngrdmath " + vel_name + "_outside_ice.grd " + vel_name + "_inside_rock.grd OR

	cmd  = "\ngrdmath " + vel_grd_path + " " + rock_grd_path + " OR = " + vel_name + "_off_ice.grd\n";
	cmd += "\ngrdclip " + vel_name + "_off_ice.grd -Sb" + min_vel + "/NaN -Sa" + max_vel + "/NaN -G" + vel_name + "_clipped.grd --IO_NC4_CHUNK_SIZE=c\n";
	cmd += "\ngrd2xyz " + vel_name + "_clipped.grd | gawk '$0 !~ /a/ {print $0}' > " + vel_name + "_clipped.txt\n";
	subprocess.call(cmd, shell=True);

	cmd  = "\ntrend2d " + vel_name + "_clipped.txt -Fxyr -N3 -V > " + vel_name + "_clipped_trendremoved.txt\n";
	pipe = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE).stderr;
	info = pipe.read();
	pipe.close();

	coeffs = info[re.search("Model Coefficients: ", info).end(0) : ].split();

	cmd  = "\ngmtinfo -C " + vel_name + "_clipped.txt\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	xmin, xmax, ymin, ymax, zmin, zmax = pipe.read().split();
	pipe.close();

	x_int = str((float(xmax) - float(xmin)) / 2);
	y_int = str((float(ymax) - float(ymin)) / 2);

	os.remove(vel_name + "_off_ice.grd");
	os.remove(vel_name + "_clipped.grd");
	os.remove(vel_name + "_clipped.txt");
	os.remove(vel_name + "_clipped_trendremoved.txt");

	cmd  = "\ngrd2xyz " + vel_grd_path + " | gawk '$0 !~ /a/ {print $0}' > temp.txt\n";
	cmd += "\ngawk '{print $1\" \"$2\" \"$3-(" + coeffs[0] + "+(($1-" + xmin + ")/" + x_int + "-1)*" + coeffs[1] + "+(($2-" + ymin + ")/" + y_int + "-1)*" + coeffs[2] + ")}' temp.txt | xyz2grd -R" + vel_grd_path + " -G" + vel_name + "_rr.grd --IO_NC4_CHUNK_SIZE=c\n";
	subprocess.call(cmd, shell=True);

	os.remove("temp.txt");

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 4, "\n***** ERROR: removeTrend.py requires one argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	removeTrend(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]);

	exit();

