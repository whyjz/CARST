#!/usr/bin/python


# removeRamp.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# USAGE
# *****
# python removeRamp.py /path/to/vel.grd /path/to/ice.gmt /path/to/rock.gmt
# 	vel.grd:  velocity grid (netcdf format) to remove ramp from
#	ice.gmt:  GMT polygon file with ice outlines (area to EXCLUDE)
#	rock.gmt: GMT polygon file with rock outlines (area to INCLUDE)


# OUTPUT
# ******
# vel_rr.grd - ramp removed version of vel.grd, written to current working directory


# DESCRIPTION
# ***********
# "removeRamp.py" uses GMT commands to isolate off-ice areas of "vel.grd", fit a planar ramp to those, then remove this ramp from "vel.grd"
# "rock.gmt" is higher-priority than "ice.gmt", meaning that if a portion of rock.gmt is inside ice.gmt it will be included in the ramp calculation


def removeRamp(vel_grd_path, ice_gmt_path, rock_gmt_path):

	import os;
	import subprocess;

	assert os.path.exists(vel_grd_path), "\n***** ERROR: " + vel_grd_path + " does not exist\n";
	assert os.path.exists(ice_gmt_path), "\n***** ERROR: " + ice_gmt_path + " does not exist\n";
	assert os.path.exists(rock_gmt_path), "\n***** ERROR: " + rock_gmt_path + " does not exist\n";

	MIN_VEL = "-1.5";
	MAX_VEL = "1.5";

	vel_name = vel_grd_path[vel_grd_path.rfind("/") + 1 : vel_grd_path.rfind(".")];

	cmd  = "\ngrdmask " + ice_gmt_path + " -Goutside_ice.grd -N1/NaN/NaN -R" + vel_grd_path + "\n";
	cmd += "\ngrdmask " + rock_gmt_path + " -Ginside_rock.grd -NNaN/NaN/1 -R" + vel_grd_path + "\n";
	cmd += "\ngrdmath outside_ice.grd inside_rock.grd AND = off_ice.grd\n";
	cmd += "\ngrdmath " + vel_grd_path + " off_ice.grd OR = " + vel_name + "_off_ice.grd\n";
	cmd += "\ngrdclip " + vel_name + "_off_ice.grd -Sb" + MIN_VEL + "/NaN -Sa" + MAX_VEL + "/NaN -G" + vel_name + "_off_ice.grd\n";
	cmd += "\ngrdtrend " + vel_name + "_off_ice.grd -N3r -T" + vel_name + "_off_ice_trend.grd\n";
	cmd += "\ngrdmath " + vel_grd_path + " " + vel_name + "_off_ice_trend.grd SUB --IO_NC4_CHUNK_SIZE=c = " + vel_name + "_rr.grd\n";
	subprocess.call(cmd, shell=True);

	os.remove("outside_ice.grd");
	os.remove("inside_rock.grd");
	os.remove("off_ice.grd");
	os.remove(vel_name + "_off_ice.grd");
	os.remove(vel_name + "_off_ice_trend.grd");

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 3, "\n***** ERROR: removeRamp.py requires 3 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";
	
	removeRamp(sys.argv[1], sys.argv[2], sys.argv[3]);

	exit();

