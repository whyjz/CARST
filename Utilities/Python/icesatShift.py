#!/usr/bin/python

# icesatShift.py
# Author: Andrew Kenneth Melkonian (akm26)
# All rights reserved


def icesatShift(image_tif_path, icesat_xyz_path, resample_method, ell_or_ortho):
	
	assert os.path.exists(image_tif_path), "\n***** ERROR: " + image_tif_path + " does not exist\n";
	assert os.path.exists(icesat_xyz_path), "\n***** ERROR: " + icesat_xyz_path + " does not exist\n";

	import re;

	assert re.search(".tif$",image_tif_path.lower()), "\n***** ERROR: " + image_tif_path + " does not appear to be valid GeoTiff file, does not have \".tif\" extension\n";

	ICESAT_UTM_ZONE = "41";
	ICESAT_UTM_LET  = "X";

#	Carto parameters
	MIN_COUNT = 700;
	CUTOFF    = 75;
	MAX_Y     = "1500";
	Y_INT	  = "300";
	X_INT	  = "15";

#	ASTER parameters
	MIN_COUNT = 700;
        CUTOFF    = 75;
        MAX_Y     = "80";
        Y_INT     = "10";
        X_INT     = "5";


	image_tif_dir = ".";	

	index = image_tif_path.rfind("/");

	if index > -1:
		image_tif_dir = image_tif_path[ : index];

	image_name     = image_tif_path[index + 1 : image_tif_path.rfind(".")];
	image_grd_path = image_tif_dir + "/" + image_name + ".grd";
	icesat_track   = image_name + "_icesat.gmt";

	shift_image_tif_path = image_name + "_icesat_medshift.tif";

	assert not os.path.exists(shift_image_tif_path), "\n***** ERROR: " + shift_image_tif_path + " already exists\n";


	cmd = "";

	import subprocess;

	if not os.path.exists(image_grd_path):
		cmd  += "\ngdal_translate -of GMT " + image_tif_path + " " + image_grd_path + "\n";

	info_cmd  = "\ngdalinfo " + image_tif_path + "\n";
	pipe      = subprocess.Popen(info_cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info      = pipe.read();
	pipe.close();

	zone = info[re.search("UTM\s*zone\s*",info).end(0) : re.search("UTM\s*zone\s*\d+",info).end(0)];

	if zone != ICESAT_UTM_ZONE:
		cmd += "\n/usr/local/gmt/bin/mapproject " + icesat_xyz_path + " -Ju" + ICESAT_UTM_ZONE + ICESAT_UTM_LET + "/1:1 -F -C -I -m | /usr/local/gmt/bin/mapproject -Ju" + zone + ICESAT_UTM_LET + "/1:1 -F -C -m | grdtrack -G" + image_grd_path + " -Q" + resample_method + " -m | gawk '$0 !~ /\-9999/ {print $0}' > temp\n";

	else:
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


	diffs = [i for i in diffs if i < CUTOFF and i > (-1*CUTOFF)];

	sorted_diffs = sorted(diffs);

	if len(sorted_diffs) < MIN_COUNT:
		os.remove(image_grd_path);
		os.remove(icesat_track);
		return;
		

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

	cmd  = "\ngawk '{print $19}' " + icesat_track + " | pshistogram -X5c -JX12c -W0.5 -F -R-50/50/0/" + MAX_Y + " -Ba" + X_INT + "g" + X_INT + ":\"Difference\":/a" + Y_INT + "g" + Y_INT + ":\"Counts\":WeSn -Gblack --LABEL_FONT=1 -P -K > " + hist_ps_path + "\n";
	cmd += "\necho \"" + str(median_diff) + " 0\\n" + str(median_diff) + " " + MAX_Y + "\" | psxy -J -R -W1p,maroon -O -K >> " + hist_ps_path + "\n";
	cmd += "\necho \"" + str(2 * stdev_diff + mean_diff) + " 0\\n" + str(2 * stdev_diff + mean_diff) + " " + MAX_Y + "\" | psxy -J -R -W01p,blue -O -K >> " + hist_ps_path + "\n";
	cmd += "\necho \"" + str(-2 * stdev_diff + mean_diff) + " 0\\n" + str(-2 * stdev_diff + mean_diff) + " " + MAX_Y + "\" | psxy -J -R -W1p,blue -O >> " + hist_ps_path + "\n";
	cmd += "\nps2raster -A -Tf " + hist_ps_path + "\n";
	subprocess.call(cmd,shell=True);


#	Subtract median difference from DEM

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


#	Output icesat elevations clipped at mean+/-2stdevs for us with pc_align

	icesat_track_clipped = image_name + "_icesat_clipped.csv"; 

	cmd = "\ngawk '$19 > " + str(-2 * stdev_diff + mean_diff) + " && $19 < " + str(2 * stdev_diff + mean_diff) + " && $0 !~ />/ {print $5\",\"$4\",\"$6}' " + icesat_track + " > " + icesat_track_clipped + "\n";
	subprocess.call(cmd,shell=True);

	return;


if __name__ == "__main__":

	import os;
	import sys;

	assert len(sys.argv) > 2, "\n***** ERROR: icesatShift.py requires 2 arguments, " + str(len(sys.argv)) + " given\n";
	
	resample_method = "n";

	if len(sys.argv) == 4:
		resample_method = sys.argv[3];

	ell_or_ortho = "ell";

	if len(sys.argv) == 5:
		ell_or_ortho = sys.argv[4];

	icesatShift(sys.argv[1], sys.argv[2], resample_method, ell_or_ortho);

	exit();



