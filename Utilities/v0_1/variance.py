#!/usr/bin/python


# variance.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

# USAGE
# *****
# python variance.py /path/to/off_ice_dhdt.grd interval max_width
#	/path/to/off_ice_dhdt.grd: path to netcdf grid of off-ice dh/dt 
#	interval:		   interval in meters to perform variance calculation, typically resolution of "/path/to/off_ice_dhdt.grd" (e.g. "120")
#	max_width:		   variance calculation will not be performed past this width (e.g. "3600")
#	numproc:		   number of processors to use

# OUTPUT
# ******
# Two-column ASCII text file "off_ice_dhdt_variance.txt" (in current directory), first column is width, second is variance of input netcdf grid at that width

# FILES CREATED
# *************
# "var_#.cmd" files, where # is 0 through numproc minus 1, and "run_vars.cmd", these can be removed AFTER processing is finished (see NOTE below)

# NOTE: This script will take more time to run as the width increases. 
#	"run_vars.cmd" is run in the background, the script is NOT FINISHED until "off_ice_dhdt_variance.txt" is fully populated with all valid widths


def variance(grd_path, interval, max_width, numproc):

	import os;
	import subprocess;

	assert os.path.exists(grd_path), "\n***** ERROR: " + grd_path + " does not exist\n";

	out_txt = grd_path[grd_path.rfind("/") + 1 : grd_path.rfind(".")] + "_variance.txt";

	print("\nWriting variance results to: " + out_txt + " ...\n");

	cmds = {};
	i    = 0;

	for width in range(int(interval), int(max_width), int(interval)):

		# Calculate variance (NOTE: this step takes a long time for large widths

		cmd  = "\ngrdfilter " + grd_path + " -D0 -Fb" + str(width) + " -Gmean" + str(width) + ".grd\n";
		cmd += "\ngrdmath " + grd_path + " mean" + str(width) + ".grd SUB = diff" + str(width) + ".grd\n";
		cmd += "\ngrdmath diff" + str(width) + ".grd 2 POW = square" + str(width) + ".grd\n";
		cmd += "\ngrdfilter square" + str(width) + ".grd -D0 -Fb" + str(width) + " -Gmean" + str(width) + ".grd\n";
		cmd += "\ngrdvolume mean" + str(width) + ".grd | gawk '{print \"" + str(width) + " \"$4}' >> " + out_txt + "\n";
		cmd += "\nrm mean" + str(width) + ".grd square" + str(width) + ".grd diff" + str(width) + ".grd\n";

		if (i % int(numproc)) not in cmds:
			cmds[i % int(numproc)] = cmd;

		else:
			cmds[i % int(numproc)] += cmd;

		i += 1;

	cmds[0] = cmds[0].replace(">>", ">", 1);

	all_vars_cmdfile = open("run_vars.cmd", "w");

	for key in cmds:

		cmdfile = open("var_" + str(key) + ".cmd", "w");
		cmdfile.write(cmds[key]);
		cmdfile.close();

		os.chmod("var_" + str(key) + ".cmd", 0700);

		all_vars_cmdfile.write("./var_" + str(key) + ".cmd &\n");

	all_vars_cmdfile.close();

	os.chmod("run_vars.cmd", 0700);

	cmd = "./run_vars.cmd &";
	subprocess.call(cmd, shell=True);

	return;
		

if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 3, "\n***** ERROR: variance.py requires 3 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";

	numproc = "1";

	if len(sys.argv) > 4:
		numproc = sys.argv[4];
	
	variance(sys.argv[1], sys.argv[2], sys.argv[3], numproc);

	exit();

