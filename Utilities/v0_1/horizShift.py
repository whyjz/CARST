#!/usr/bin/python

# horizShift.py
# Author: Andrew Kenneth Melkonian (akm26)
# All rights reserved


def horizShift(pc_align_output):
	
	assert os.path.exists(pc_align_output), "\n***** ERROR: " + pc_align_output + " does not exist\n";

	dem_path = "";

	infile = open(pc_align_output, "r");

	for line in infile:
	
		if line.find("Reading") > -1:
			elements = line.split();
			dem_path = elements[1];

		elif line.find("Translation vector (meters)") > -1:
			print(line);

	infile.close();

	return;

	image_tif_path = "";
	resample_method = "";
	icesat_xyz_path = "";

	image_tif_dir = ".";	

	index = image_tif_path.rfind("/");

	if index > -1:
		image_tif_dir = image_tif_path[ : index];

	image_name     = image_tif_path[index + 1 : image_tif_path.rfind(".")];
	image_grd_path = image_tif_dir + "/" + image_name + ".grd";
	icesat_track   = image_name + "_icesat.gmt";


	cmd = "";

	import subprocess;

	if not os.path.exists(image_grd_path):
		cmd  += "\ngdal_translate -of GMT " + image_tif_path + " " + image_grd_path + "\n";

	cmd += "\ngrdtrack " + icesat_xyz_path + " -G" + image_grd_path + " -Q" + resample_method + " -m | gawk '$0 !~ /\-9999/ {print $0}' > temp\n";
	subprocess.call(cmd,shell=True);


	diffs = [];

	infile  = open("temp", "r");
	outfile = open(icesat_track, "w");

	for line in infile:

		if line.find(">") > -1:
			continue;

		elements = line.split();

		if float(elements[17]) < 5 or float(elements[5]) < 5:
			continue;

		diff = str(float(elements[17]) - float(elements[5]));

		if ell_or_ortho.lower().find("ortho"):
			diff = str(float(elements[17]) - (float(elements[5]) - float(elements[6])));

		out_line = "";

		for i in range(len(elements)):

			out_line += elements[i] + " ";

		out_line += diff + "\n";

		outfile.write(out_line);

		diffs.append(float(diff));

	infile.close();
	outfile.close();

	os.remove("temp");


	diffs = [i for i in diffs if i < 50 and i > -50];

	sorted_diffs = sorted(diffs);

	median_diff = sorted_diffs[len(diffs)/2];	

	mean_diff = sum(diffs)/float(len(diffs));

	import numpy;

	sorted_diffs = numpy.array(sorted_diffs);

	stdev_diff = (sum((sorted_diffs - mean_diff)**2)/float(len(sorted_diffs)))**0.5;

	print("Mean, median and standard deviation (m) BEFORE clipping: " + str(mean_diff) + " " + str(median_diff) + " " + str(stdev_diff));

	before_mean_diff = mean_diff;
	before_med_diff  = median_diff;
	before_stdev     = stdev_diff;


	sorted_diffs = sorted_diffs[sorted_diffs > (mean_diff - 2 * stdev_diff)];
	sorted_diffs = sorted_diffs[sorted_diffs < (mean_diff + 2 * stdev_diff)];

	mean_diff = sum(sorted_diffs)/float(len(sorted_diffs));
	stdev_diff = (sum((sorted_diffs - mean_diff)**2)/float(len(sorted_diffs)))**0.5;
	median_diff = sorted_diffs[len(sorted_diffs)/2];

	print("Mean, median and standard deviation (m) AFTER clipping at +/- 2 stdev: " + str(mean_diff) + " " + str(median_diff) + " " + str(stdev_diff));
	
	hist_ps_path = image_name + "_icesat_diff_hist.ps";

	cmd  = "\ngawk '{print $19}' " + icesat_track + " | pshistogram -JX12c -W0.5 -F -R-20/20/0/100 -Ba4g2:\"Difference\":/a10g5:\"Counts\":WeSn -Gblack --LABEL_FONT=1 -P -K > " + hist_ps_path + "\n";
	cmd += "\necho \"" + str(median_diff) + " 0\\n" + str(median_diff) + " 100\" | psxy -J -R -W1p,maroon -O -K >> " + hist_ps_path + "\n";
	cmd += "\necho \"" + str(2 * stdev_diff + mean_diff) + " 0\\n" + str(2 * stdev_diff + mean_diff) + " 100\" | psxy -J -R -W01p,blue -O -K >> " + hist_ps_path + "\n";
	cmd += "\necho \"" + str(-2 * stdev_diff + mean_diff) + " 0\\n" + str(-2 * stdev_diff + mean_diff) + " 100\" | psxy -J -R -W1p,blue -O >> " + hist_ps_path + "\n";
	cmd += "\nps2raster -A -Tf " + hist_ps_path + "\n";
	subprocess.call(cmd,shell=True);


#	Subtrack median difference from DEM

	shift_image_tif_path = image_name + "_icesat_medshift.tif";

	cmd = "\ngdal_calc.py -A " + image_tif_path + " --outfile=" + shift_image_tif_path + " --calc=\"A-" + str(median_diff) + "\"\n";
	subprocess.call(cmd,shell=True);


#	Output statistics to text file

	stats_path = image_name + "_icesat_stats.txt"

	stats_file = open(stats_path, "w");

	stats_file.write(image_name + " minus ICESat statistics\n");
	stats_file.write("Mean, median and standard deviation of differences (m) BEFORE clipping:\n");
	stats_file.write(str(before_mean_diff) + " " + str(before_med_diff) + " " + str(before_stdev) + "\n");
	stats_file.write("Mean, median and standard deviation of differences (m) AFTER clipping at +/- 2 stdev:\n");
	stats_file.write(str(mean_diff) + " " + str(median_diff) + " " + str(stdev_diff) + "\n");

	stats_file.close();


	return;


if __name__ == "__main__":

	import os;
	import sys;

	assert len(sys.argv) > 1, "\n***** ERROR: horizShift.py requires 1 argument, " + str(len(sys.argv)) + " given\n";
	
	horizShift(sys.argv[1]);

	exit();



