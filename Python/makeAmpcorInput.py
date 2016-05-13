#!/usr/bin/python


# makeAmpcorInput.py
# Author: Andrew Kenneth Melkonian
# All rights reserved



def makeAmpcorInput(ref_img_path, search_img_path, out_path, ampoff_path, ref_samps, search_samps, ref_start_line, ref_end_line, ref_start_samp, ref_end_samp, step_size, ref_size, search_size, mean_off_samp, mean_off_line):

	import sys;

	outfile = open(out_path, "w");

	outfile.write("                 AMPCOR INPUT FILE\n");
	outfile.write("\n");
	outfile.write("DATA TYPE\n");
	outfile.write("\n");
	outfile.write("Data Type for Reference Image Real or Complex                   (-)    =  Real   ![Complex , Real]\n");
	outfile.write("Data Type for Search Image Real or Complex                      (-)    =  Real   ![Complex , Real]\n");
	outfile.write("\n");
	outfile.write("INPUT/OUTPUT FILES\n");
	outfile.write("\n");
	outfile.write("Reference Image Input File                                      (-)    =  " + ref_img_path + "\n");
	outfile.write("Search Image Input File                                         (-)    =  " + search_img_path + "\n");
	outfile.write("Match Output File                                               (-)    =  " + ampoff_path + "\n");
	outfile.write("\n");
	outfile.write("MATCH REGION\n");
	outfile.write("\n");
	outfile.write("Number of Samples in Reference/Search Images                    (-)    =  " + ref_samps + " " + search_samps + "\n");
	outfile.write("Start, End and Skip Lines in Reference Image                    (-)    =  " + ref_start_line + " " + ref_end_line + " " + step_size + "\n");
	outfile.write("Start, End and Skip Samples in Reference Image                  (-)    =  " + ref_start_samp + " " + ref_end_samp + " " + step_size + "\n");
	outfile.write("\n");
	outfile.write("MATCH PARAMETERS\n");
	outfile.write("\n");
	outfile.write("Reference Window Size Samples/Lines                             (-)    =  " + ref_size + " " + ref_size + "\n");
	outfile.write("Search Pixels Samples/Lines                                     (-)    =  " + search_size + " " + search_size + "\n");
	outfile.write("Pixel Averaging Samples/Lines                                   (-)    =  1 1\n");
	outfile.write("Covariance Surface Oversample Factor and Window Size            (-)    =  64 16\n");
	outfile.write("Mean Offset Between Reference and Search Images Samples/Lines   (-)    =  " + mean_off_samp + " " + mean_off_line + "\n");
	outfile.write("Matching Scale for Sample/Line Directions                       (-)    = 1. 1.\n");
	outfile.write("\n");
	outfile.write("MATCH THRESHOLDS AND DEBUG DATA\n");
	outfile.write("\n");
	outfile.write("SNR and Covariance Thresholds                                   (-)    =  0 100\n");
	outfile.write("Debug and Display Flags T/F                                     (-)    =  f f\n");

	outfile.close();


	return;

	

if __name__ == "__main__":
	
	import sys;
	
	assert len(sys.argv) > 15, "\n***** ERROR: makeAmpcorInput.py requires 15 arguments, " + str(len(sys.argv) - 1) + " given\n";
	
	makeAmpcorInput(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10], sys.argv[11], sys.argv[12], sys.argv[13], sys.argv[14], sys.argv[15]);

	exit();
