#!/usr/bin/python


# ampoffToUNW.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def ampoffToUNW(ampoff_path, slc_rsc_path, mean_x_off, mean_y_off, ref_x, ref_y, search_x, search_y, step_x, step_y):

	import math;
	import scipy;

	width  = "";
	length = "";
	da_p   = "";
	r_e    = "";
	p_h    = "";
	dr     = "";
	angle  = "";

	infile = open(slc_rsc_path, "r");

	for line in infile:

		if line.find("WIDTH") > -1:
			width = line.split()[1];

		elif line.find("RANGE_PIXEL_SIZE") > -1:
			dr = line.split()[1];

		elif line.find("FILE_LENGTH") > -1:
			length = line.split()[1];

		elif line.find("HEIGHT") > -1 and line.find("_") < 0:
			p_h = line.split()[1];

		elif line.find("EARTH_RADIUS") > -1:
			r_e = line.split()[1];

		elif line.find("AZIMUTH_PIXEL_SIZE") > -1:
			da_p = line.split()[1];

		elif line.find("BEAM") > -1:
			angle = line.split()[1];

	infile.close();

	print(width, length, da_p, r_e, p_h, dr, angle);

	r_p  = float(r_e) + float(p_h);        #platform radius
        da_e = float(da_p) * float(r_e) / r_p * 100; #az pixel size at earth surface, cm    
        #dr   = ; #range pixel size
        la   =  float(angle) * math.pi / 180;      #look angle
        dr_g = float(dr) / math.sin(la) * 100;  #g

	unw_width  = str(int(width) / int(step_x));
	unw_length = str(int(length) / int(step_y));

	azimuth_path = "azimuth_noaffine_r" + ref_x + "x" + ref_y + "_s" + search_x + "x" + search_y + "_" + step_x + "rlks.unw";
	range_path   = "range_noaffine_r" + ref_x + "x" + ref_y + "_s" + search_x + "x" + search_y + "_" + step_x + "rlks.unw";
	snr_path     = "snr_noaffine_r" + ref_x + "x" + ref_y + "_s" + search_x + "x" + search_y + "_" + step_x + "rlks.unw";

	if not os.path.exists(azimuth_path):

#		dxg  = scipy.zeros((int(unw_width), int(unw_length)));
#		dyg  = scipy.zeros((int(unw_width), int(unw_length)));
#		snrg = scipy.zeros((int(unw_width), int(unw_length)));

		dxg  = scipy.zeros((int(unw_length), int(unw_width)));
		dyg  = scipy.zeros((int(unw_length), int(unw_width)));
		snrg = scipy.zeros((int(unw_length), int(unw_width)));

		infile = open(ampoff_path,"r");

		for line in infile:

			elements = line.split();

#			dxg[int(elements[0])/int(step_x), int(elements[2])/int(step_y)] = float(elements[1]) - float(mean_x_off);
#			dyg[int(elements[0])/int(step_x), int(elements[2])/int(step_y)] = float(elements[3]) - float(mean_y_off);
#			snrg[int(elements[0])/int(step_x), int(elements[2])/int(step_y)] = float(elements[4]);

			dxg[int(elements[2])/int(step_y), int(elements[0])/int(step_x)] = (float(elements[1]) - float(mean_x_off)) * dr_g;
			dyg[int(elements[2])/int(step_y), int(elements[0])/int(step_x)] = (float(elements[3]) - float(mean_y_off)) * da_e;
			snrg[int(elements[2])/int(step_y), int(elements[0])/int(step_x)] = float(elements[4]);

#		for i in range(0, scipy.size(dxg, 0) - 1):

#			for j in range(0, scipy.size(dxg, 1) - 1):

#				low_x  = i - 50;
#				high_x = i + 50;
#				low_y  = j - 50;
#				high_y = j + 50;

#				if low_x < 0:
#					low_x  = 0;
#					high_x = 100;

#				if high_x > scipy.size(dxg, 0) - 1:
#					high_x = scipy.size(dxg, 0) - 1;
#					low_x  = (scipy.size(dxg, 0) - 100) - 1;

#				if low_y < 0:
#					low_y  = 0;
#					high_y = 100;

#				if high_y > scipy.size(dxg, 1) - 1:
#					high_y = scipy.size(dxg, 1) - 1;
#					low_y  = (scipy.size(dxg, 1) - 100) - 1;

#				median_range = scipy.median(dxg[low_x : high_x][low_y : high_y]);
#				dxg[i][j]    = dxg[i][j] - median_range;

#				median_azimuth = scipy.median(dyg[low_x : high_x][low_y : high_y]);
#				dyg[i][j]    = dyg[i][j] - median_azimuth;

		infile.close();

		outg = scipy.hstack((abs(dyg),dyg));

		outfile = open(azimuth_path, "wb");
		outg = scipy.matrix(outg,scipy.float32);
		outg.tofile(outfile);
		outfile.close();

		outg = ""

		outr = scipy.hstack((dxg,dxg));

		outfile = open(range_path, "wb");
		outr = scipy.matrix(outr,scipy.float32);
		outr.tofile(outfile);
		outfile.close();

		outr = "";

		outsnr = scipy.hstack((snrg,snrg));

		outfile = open(snr_path, "wb");
		outsnr = scipy.matrix(outsnr,scipy.float32);
		outsnr.tofile(outfile);
		outfile.close();

		outsnr = "";

	return;

"""
	ramp_ld_unw  = ramp_unw_path[ramp_unw_path.rfind("/") + 1 : ramp_unw_path.rfind(".")] + "_" + step_x + "rlks.unw";
	radar_ld     = radar_unw_path[radar_unw_path.rfind("/") + 1 : radar_unw_path.rfind(".")] + "_" + step_x + "rlks";
	radar_ld_unw = radar_ld + ".unw";
	wavelength   = "0.0565646";

	import subprocess;

	if not os.path.exists(ramp_ld_unw):
		cmd  = "\nlook.pl " + ramp_unw_path + " " + step_x + " " + step_y + "\n";
#		print(cmd);
		subprocess.call(cmd,shell=True);

	if not os.path.exists(radar_ld_unw):
		cmd  = "\nlook.pl " + radar_unw_path + " " + step_x + " " + step_y + "\n";
#		print(cmd);
		subprocess.call(cmd,shell=True);
		
	cmd  = "\nadd_rmg.pl " + radar_ld_unw + " " + ramp_ld_unw + " rr_" + radar_ld_unw + " -1 1\n";
	cmd += "\nrmg2mag_phs rr_" + radar_ld_unw + " " + radar_ld + ".mag " + radar_ld + ".phs " + unw_width + "\n";
#	print(cmd);
	subprocess.call(cmd,shell=True);

	infile = open(radar_ld + ".phs", "rb");

	phs = scipy.matrix(scipy.fromfile(infile,scipy.float32,-1)).reshape(int(unw_width),-1);
	phs = phs * float(wavelength) / 4. / scipy.pi;

	infile.close();

	phs = scipy.matrix(phs,scipy.float32);
	phs.tofile("adj_" + radar_ld + ".phs");

	cmd  = "\nmag_phs2rmg " + radar_ld + ".mag adj_" + radar_ld + ".phs adj_" + radar_ld_unw + " " + unw_width + "\n";
	cmd += "\ncp -p " + radar_ld_unw + ".rsc adj_" + radar_ld + ".unw.rsc\n";
	cmd += "\nrm " + radar_ld + ".mag " + radar_ld + ".phs adj_" + radar_ld + ".phs\n";
	cmd += "\nadd_rmg.pl range_" + step_x + "rlks.unw adj_" + radar_ld_unw + " adj_range_" + step_x + "rlks.unw -1 1\n";
	cmd += "\nrm rr_" + radar_ld_unw + " rr_" + radar_ld_unw + ".rsc" + " adj_" + radar_ld_unw + " adj_" + radar_ld_unw + ".rsc " + radar_ld_unw + " " + radar_ld_unw + ".rsc " + radar_ld_unw + ".rsc.hst " + ramp_ld_unw + " " + ramp_ld_unw + ".rsc " + ramp_ld_unw + ".rsc.hst\n";
#	print(cmd);
	subprocess.call(cmd,shell=True);

#	import matplotlib;
#	import matplotlib.pyplot;

#	matplotlib.pyplot.imshow(scipy.array(dxg),interpolation='nearest',origin='lower');
#	matplotlib.pyplot.show();

	return;
"""


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 10, "\n***** ERROR: ampoffToUNW.py requires 10 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
#	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";
	
	ampoffToUNW(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10]);

	exit();


