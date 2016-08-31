#!/usr/bin/python

# splitAmpcor.py
# Author: Andrew Kenneth Melkonian
# modified by: Joey Durkin and Whyjay Zheng
# last edit: Aug 31, 2016 by Whyjay Zheng

import os
import subprocess
import sys
from UtilTIF import SingleTIF
# from findOffset import findOffset

def splitAmpcor(ref_path, search_path, pair_dir='.', nproc=8, ref_x=32, ref_y=32, search_x=32, search_y=32, step=8):

	ref_img = SingleTIF(ref_path)
	ref_samples = ref_img.GetRasterXSize()
	ref_lines = ref_img.GetRasterYSize()
	ref_ulx, ref_xres, _, ref_uly, _, ref_yres = ref_img.GetGeoTransform()
	search_img = SingleTIF(search_path)
	search_samples = search_img.GetRasterXSize()
	search_lines = search_img.GetRasterXSize()
	search_ulx, _, _, search_uly, _, _ = ref_img.GetGeoTransform()

	# here we use the resolution from ref image.
	# some problems may happen if the resolution of ref and search img are not the same.
	# this replaces findOffset.py, since we only need to get the ul and res, which can be found in an image itself
	# without header files.
	mean_x = round((ref_ulx - search_ulx) / ref_xres)
	mean_y = round((search_uly - ref_uly) / ref_yres)
	# It is now integer
	# print(type(round((ref_ulx - search_ulx) / ref_xres)))
	# print(mean_x)


	# output = findOffset(ref_hdr, search_hdr, resolution);
	# print(output)
	# mean_x = str(output[4]);
	# mean_y = str(output[5]);

	ampcor_label = "r{:d}x{:d}_s{:d}x{:d}".format(ref_x, ref_y, search_x, search_y)
	
	for i in range(1, nproc + 1):

		# lines_proc = ref_lines // nproc // ref_y * ref_y
		lines_proc = ref_lines // nproc

		firstpix = 1           if mean_x >= 0 else 1 - mean_x
		finalpix = ref_samples if mean_x <= 0 else ref_samples - mean_x

		yoffset = 0 if mean_y >= 0 else -mean_y
		firstline = (i - 1) * lines_proc + 1 + yoffset
		lastline  = firstline + lines_proc - 1    # WhyJ
		if i == nproc:
			lastline = ref_lines if mean_y <= 0 else ref_lines - mean_y

		ampcor_in_file  = pair_dir + "/ampcor_" + ampcor_label + "_" + str(i) + ".in"
		ampcor_off_file =             "ampcor_" + ampcor_label + "_" + str(i) + ".off"
		with open(ampcor_in_file, "w") as outfile:
			outfile.write("                  AMPCOR INPUT FILE\n")
			outfile.write("\n")
			outfile.write("DATA TYPE\n")
			outfile.write("\n")
			outfile.write("Data Type for Reference Image Real or Complex                   (-)    =  Real   ![Complex , Real]\n")
			outfile.write("Data Type for Search Image Real or Complex                      (-)    =  Real   ![Complex , Real]\n")
			outfile.write("\n")
			outfile.write("INPUT/OUTPUT FILES\n")
			outfile.write("\n")
			outfile.write("Reference Image Input File                                      (-)    =  " + ref_path.split('/')[-1] + "\n")
			outfile.write("Search Image Input File                                         (-)    =  " + search_path.split('/')[-1] + "\n")
			outfile.write("Match Output File                                               (-)    =  " + ampcor_off_file + "\n")
			outfile.write("\n")
			outfile.write("MATCH REGION\n")
			outfile.write("\n")
			outfile.write("Number of Samples in Reference/Search Images                    (-)    =  {:d} {:d}\n".format(ref_samples, search_samples))
			outfile.write("Start, End and Skip Lines in Reference Image                    (-)    =  {:d} {:d} {:d}\n".format(firstline, lastline, step))
			outfile.write("Start, End and Skip Samples in Reference Image                  (-)    =  {:d} {:d} {:d}\n".format(firstpix, finalpix, step))
			outfile.write("\n")
			outfile.write("MATCH PARAMETERS\n")
			outfile.write("\n")
			outfile.write("Reference Window Size Samples/Lines                             (-)    =  {:d} {:d}\n".format(ref_x, ref_y))
			outfile.write("Search Pixels Samples/Lines                                     (-)    =  {:d} {:d}\n".format(search_x, search_y))
			outfile.write("Pixel Averaging Samples/Lines                                   (-)    =  1 1\n")
			outfile.write("Covariance Surface Oversample Factor and Window Size            (-)    =  64 16\n")
			outfile.write("Mean Offset Between Reference and Search Images Samples/Lines   (-)    =  {:d} {:d}\n".format(mean_x, mean_y))
			outfile.write("\n")
			outfile.write("MATCH THRESHOLDS AND DEBUG DATA\n")
			outfile.write("\n")
			outfile.write("SNR and Covariance Thresholds                                   (-)    =  0 10000000000\n")
			outfile.write("Debug and Display Flags T/F                                     (-)    =  f f\n")
	return ampcor_label

def ampcor_cmd(ampcor_label, pair_dir='.', nproc=8):

	with open(pair_dir + "/amps_complete.txt", 'w') as amps_complete:
		pass 
	with open(pair_dir + "/run_amp.cmd", 'w') as amp_file:
		for i in range(1, nproc + 1):
			amp_file.write("(ampcor " + "ampcor_" + ampcor_label + "_" + str(i) + ".in rdf > " + "ampcor_" + ampcor_label + "_" + str(i) + ".out; echo " + str(i) + " >> amps_complete.txt) &\n")

if __name__ == "__main__":
	
	assert len(sys.argv) > 2, "\n***** ERROR: splitAmpcor.py requires at least 2 argument, " + str(len(sys.argv) - 1) + " given\n"
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n"
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n"
	if len(sys.argv) > 3:
		assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n"

	ampcor_label = splitAmpcor(*sys.argv[1:])
	ampcor_cmd(ampcor_label, *sys.argv[3:])
