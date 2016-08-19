#!/usr/bin/python

# splitAmpcor.py
# Author: Andrew Kenneth Melkonian

import os;
import subprocess;
import sys;


def splitAmpcor(ref_path, search_path, pair_dir, nproc, resolution, ref_x, ref_y, search_x, search_y, step):

	ref_hdr     = ref_path + ".hdr";

	if not os.path.exists(ref_hdr):
		ref_hdr = ref_path[ : ref_path.rfind(".")] + ".hdr";

	search_hdr  = search_path + ".hdr";
	
	if not os.path.exists(search_hdr):
		search_hdr = search_path[ : search_path.rfind(".")] + ".hdr";

	ref_samples = "";
	ref_lines   = "";
	
	infile = open(ref_hdr,"r");

	for line in infile:

		if line.find("samples") > -1:
			elements    = line.split();
			ref_samples = elements[len(elements)-1].strip();

		if line.find("lines") > -1:
			elements    = line.split();
			ref_lines   = elements[len(elements)-1].strip();

	infile.close();
	
	search_samples = "";
	search_lines   = "";
	
	infile = open(search_hdr,"r");

	for line in infile:

		if line.find("samples") > -1:
			elements       = line.split();
			search_samples = elements[len(elements)-1].strip();

		if line.find("lines") > -1:
			elements     = line.split();
			search_lines = elements[len(elements)-1].strip();

	infile.close();

	from findOffset import findOffset;
	
	output = findOffset(ref_hdr, search_hdr, resolution);
	
	mean_x = str(output[4]);
	mean_y = str(output[5]);

	label = "r" + ref_x + "x" + ref_y + "_s" + search_x + "x" + search_y;
	
	for i in range(1,int(nproc)+1):

		lines_proc = int(ref_lines) / int(nproc) / int(ref_y) * int(ref_y);
	
		yoffset = 0;

		if int(mean_y) < 0:
			yoffset = -1 * int(mean_y);
	
		firstline = str((i - 1) * lines_proc + 1 + yoffset);
		lastline  = str(int(firstline) + lines_proc - 1);

		if i == int(nproc):

			lastline = ref_lines;

			if int(mean_y) > 0:
				lastline = str(int(lastline) - int(mean_y));
	
		firstpix = "1";

		if int(mean_x) < 0:
			firstpix = str(1 - int(mean_x));
	
		outfile=open(pair_dir + "/ampcor_" + label + "_" + str(i) + ".in","w");
		outfile.write("                  AMPCOR INPUT FILE\n");
		outfile.write("\n");
		outfile.write("DATA TYPE\n");
		outfile.write("\n");
		outfile.write("Data Type for Reference Image Real or Complex                   (-)    =  Real   ![Complex , Real]\n");
		outfile.write("Data Type for Search Image Real or Complex                      (-)    =  Real   ![Complex , Real]\n");
		outfile.write("\n");
		outfile.write("INPUT/OUTPUT FILES\n");
		outfile.write("\n");
		outfile.write("Reference Image Input File                                      (-)    =  " + ref_path[ref_path.rfind("/") + 1 : ] + "\n");
		outfile.write("Search Image Input File                                         (-)    =  " + search_path[search_path.rfind("/") + 1 : ] + "\n");
		outfile.write("Match Output File                                               (-)    =  ampcor_" + label + "_" + str(i) + ".off\n");
		outfile.write("\n");
		outfile.write("MATCH REGION\n");
		outfile.write("\n");
		outfile.write("Number of Samples in Reference/Search Images                    (-)    =  " + ref_samples + " " + search_samples + "\n");
		outfile.write("Start, End and Skip Lines in Reference Image                    (-)    =  " + firstline + " " + lastline + " " + step + "\n");
		outfile.write("Start, End and Skip Samples in Reference Image                  (-)    =  " + firstpix + " " + ref_samples + " " + step + "\n");
		outfile.write("\n");
		outfile.write("MATCH PARAMETERS\n");
		outfile.write("\n");
		outfile.write("Reference Window Size Samples/Lines                             (-)    = " + ref_x + " " + ref_y + "\n");
		outfile.write("Search Pixels Samples/Lines                                     (-)    = " + search_x + " " + search_y + "\n");
		outfile.write("Pixel Averaging Samples/Lines                                   (-)    =  1 1\n");
		outfile.write("Covariance Surface Oversample Factor and Window Size            (-)    =  64 16\n");
		outfile.write("Mean Offset Between Reference and Search Images Samples/Lines   (-)    =  " + mean_x + " " + mean_y + "\n");
		outfile.write("\n");
		outfile.write("MATCH THRESHOLDS AND DEBUG DATA\n");
		outfile.write("\n");
		outfile.write("SNR and Covariance Thresholds                                   (-)    =  0 10000000000\n");
		outfile.write("Debug and Display Flags T/F                                     (-)    =  f f\n");
		outfile.close();

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: splitAmpcor.py requires 1 argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";
	
	splitAmpcor(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10]);

	exit();

