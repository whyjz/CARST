#!/usr/bin/python


# diffStats.py
# Author: Andrew Kenneth Melkonian
# All Rights Reserved


def diffStats(diff_tif_path):

	import os;
	import re;
	import subprocess;

	assert os.path.exists(diff_tif_path), "\n***** ERROR: " + diff_tif_path + " does not exist\n";

	cmd = "\ngdalinfo " + diff_tif_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	diff_no_data = info[re.search("NoData\s*Value\s*=\s*",info).end(0) : re.search("NoData\s*Value\s*=\s*\S+",info).end(0)];

	diff_name = diff_tif_path[ : diff_tif_path.rfind(".")];

	cmd  = "\ngdal_calc.py -A " + diff_tif_path + " --outfile=temp.tif --calc=\"(A*(A>-50))\" --NoDataValue=\"" + diff_no_data + "\"\n";
	cmd += "\ngdal_calc.py -A temp.tif --outfile=diff_clipped.tif --calc=\"(A*(A<50))\" --NoDataValue=\"" + diff_no_data + "\"\n";
	subprocess.call(cmd,shell=True);

	os.remove("temp.tif");

	if os.path.exists("temp.tif.aux.xml"):
		os.remove("temp.tif.aux.xml");

	cmd  = "\ngdal_translate -of GMT " + diff_tif_path + " diff.grd\n";
	cmd += "\ngrd2xyz diff.grd | gawk '$3 > -50 && $3 < 50 {print $3}' | pshistogram -JX10c -W1 -F -R-50/50/0/3000 -Ba10g10:\"Difference\":/a200g100:\"Counts\":WeSn -Gblack --FONT_LABEL=14p,1,black --FONT_ANNOT_PRIMARY=14p,1,black -P > " + diff_name + "_hist.ps\n";
	cmd += "\nps2raster -A -Tf " + diff_name + "_hist.ps\n";
	subprocess.call(cmd,shell=True);

	os.remove("diff.grd");

	if os.path.exists("diff.grd.aux.xml"):
		os.remove("diff.grd.aux.xml");

	os.remove(diff_name + "_hist.ps");

	cmd = "\ngdalinfo -stats diff_clipped.tif\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	os.remove("diff_clipped.tif");

	if os.path.exists("diff_clipped.tif.aux.xml"):
		os.remove("diff_clipped.tif.aux.xml");

	mean  = info[re.search("STATISTICS_MEAN\s*=\s*",info).end(0) : re.search("STATISTICS_MEAN\s*=\s*\-*\d+\.*\d*\e*\-*\d*",info).end(0)];
	stdev = info[re.search("STATISTICS_STDDEV\s*=\s*",info).end(0) : re.search("STATISTICS_STDDEV\s*=\s*\d+\.*\d*",info).end(0)];

	upper_bound = str(float(mean) + 2 * float(stdev));
	lower_bound = str(float(mean) - 2 * float(stdev));

	cmd  = "\ngdal_calc.py -A " + diff_tif_path + " --outfile=temp.tif --calc=\"(A*(A>" + lower_bound + "))\" --NoDataValue=\"" + diff_no_data + "\"\n";
	cmd += "\ngdal_calc.py -A temp.tif --outfile=diff_clipped.tif --calc=\"(A*(A<" + upper_bound + "))\" --NoDataValue=\"" + diff_no_data + "\"\n";
	subprocess.call(cmd,shell=True);

	os.remove("temp.tif");

	if os.path.exists("temp.tif.aux.xml"):
		os.remove("temp.tif.aux.xml");

	cmd = "\ngdalinfo -stats diff_clipped.tif\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	os.remove("diff_clipped.tif");

	if os.path.exists("diff_clipped.tif.aux.xml"):
		os.remove("diff_clipped.tif.aux.xml");

	a_stdev = info[re.search("STATISTICS_STDDEV\s*=\s*",info).end(0) : re.search("STATISTICS_STDDEV\s*=\s*\d+\.*\d*",info).end(0)];
	a_mean  = info[re.search("STATISTICS_MEAN\s*=\s*",info).end(0) : re.search("STATISTICS_MEAN\s*=\s*\-*\d+\.*\d*\e*\-*\d*",info).end(0)];

	outfile = open(diff_name + "_stats.txt", "w");
	outfile.write("Mean, stdev after clipping at +/- 50: " + mean + " " + stdev + "\n");
	outfile.write("Mean, stdev after clipping at +/- 50 AND then +/- 2 stdev: " + a_mean + " " + a_stdev + "\n");
	outfile.close();

	return;




if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: diffStats.py requires one argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	diffStats(sys.argv[1]);

	exit();








