#!/usr/bin/python


# removeRampNoOutlines.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# USAGE
# *****
# python removeRampNoOutlines.py /path/to/vel.grd /path/to/rock.grd min_vel max_vel
# 	vel.grd:  velocity grid (netcdf format) to remove ramp from
# 	rock.grd: NetCDF-grid that defines off-ice area, must be on the same grid and have the same bounds as "vel.grd"
#	min_vel:  velocities below "min_vel" will be clipped before the a ramp is fitted
#	max_vel:  velocities above "max_vel" will be clipped before the a ramp is fitted


# OUTPUT
# ******
# vel_rr.grd - ramp removed version of vel.grd, written to current working directory


# DESCRIPTION
# ***********
# removeRampNoOutlines.py fits a planar ramp to the area of "vel.grd" defined in "rock.grd", then remove this ramp from "vel.grd"


def removeRampNoOutlines(vel_grd_path, rock_grd_path, min_vel, max_vel):

	import os;
	import subprocess;

	assert os.path.exists(vel_grd_path), "\n***** ERROR: " + vel_grd_path + " does not exist\n";
	assert os.path.exists(rock_grd_path), "\n***** ERROR: " + rock_grd_path + " does not exist\n";

	vel_name = vel_grd_path[vel_grd_path.rfind("/") + 1 : vel_grd_path.rfind(".")];

	cmd  = "\ngrdmath " + vel_grd_path + " " + rock_grd_path + " OR = " + vel_name + "_off_ice.grd\n";
	cmd += "\ngrdclip " + vel_name + "_off_ice.grd -Sb" + min_vel + "/NaN -Sa" + max_vel + "/NaN -G" + vel_name + "_clipped.grd --IO_NC4_CHUNK_SIZE=c\n";
	cmd += "\ngrdtrend " + vel_name + "_clipped.grd -N4r -T" + vel_name + "_trend.grd\n";
#	cmd += "\ngrdmath " + vel_name + "_trend.grd 2 DIV = " + vel_name + "_trend.grd\n";
	cmd += "\ngrdmath " + vel_grd_path + " " + vel_name + "_trend.grd SUB = " + vel_name + "_rr.grd\n";
	cmd += "\ngrdmath " + vel_name + "_rr.grd 1 MUL --IO_NC4_CHUNK_SIZE=c = " + vel_name + "_rr.grd\n";
	cmd += "\ngrdmath " + vel_name + "_trend.grd 1 MUL --IO_NC4_CHUNK_SIZE=c = " + vel_name + "_trend.grd\n";
	subprocess.call(cmd, shell=True);

	os.remove(vel_name + "_off_ice.grd");
#	os.remove(vel_name + "_clipped.grd");
#	os.remove(vel_name + "_trend.grd");

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 4, "\n***** ERROR: removeRampNoOutlines.py requires one argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	removeRampNoOutlines(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]);

	exit();

