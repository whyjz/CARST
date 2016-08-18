#!/usr/bin/python


# datePlot.py
# Author: Andrew Kennethm Melkonian
# All rights reserved


# Usage
# *****
# python datePlot.py /path/to/input_dates.txt
#	input_dates.txt - ASCII column-file with dates in YYYYMMDDHHMMSS format



def datePlot(input_dates_path):

#	Read dates, total scenes for each month into hashtable

	dates = {};
	seasons = {"01" : 0, "02" : 0, "03" : 0, "04" : 0, "05" : 0, "06" : 0, "07" : 0, "08" : 0, "09" : 0, "10" : 0, "11" : 0, "12" : 0};

	infile = open(input_dates_path,"r");

	for line in infile:

		year   = line[0:4];
		month  = line[4:6];
		day    = line[6:8];
		hour   = line[8:10];
		minute = line[10:12];
		second = line[12:14];

		dates[line.strip()] = line.strip();

		seasons[line[4:6]] += 1;

	infile.close();

	min_year = str(int(min(dates)[0:4]));
	max_year = str(int(max(dates)[0:4]) + 1);

#	Sort the dates, restore as list
	
	dates = sorted(dates);

#	Write dates to file for plotting using GMT

	i = 0;

	outfile = open("temp.txt","w");

	for date in dates:

		elements = date.split();

		outfile.write(date[0:4] + "-" + date[4:6] + "-" + date[6:8] + " " + str(i) + "\n");

		
		i += 1;

	outfile.close();

#	Plot the dates

	ps_name = "aster_dates_2014_04_08.ps";

	import subprocess;	

	cmd  = "\npsbasemap -JX10c/6.25c -R" + min_year + "-01-01T00:00:00/" + max_year + "-01-01T00:00:00/0/" + str(len(dates) + 1) + " -Bsa2Yf1Yg1Y/WS -Bpf1o:Date:/a10f10g88WS:\"# of Images\"::.\"\": --D_FORMAT=%.12lg --LABEL_FONT=1 --LABEL_FONT_SIZE=14 --ANNOT_FONT_PRIMARY=1 --ANNOT_FONT_SIZE_PRIMARY=8 --ANNOT_FONT_SECONDARY=1 --ANNOT_FONT_SIZE_SECONDARY=10 --HEADER_FONT=1 --HEADER_FONT_SIZE=18 -P -K > " + ps_name + "\n";
	cmd += "\npsxy temp.txt -JX10c/6.25c -R" + min_year + "-01-01T00:00:00/" + max_year + "-01-01T00:00:00/0/" + str(len(dates) + 1) + " -Sc0.2c -Gred -O >> " + ps_name + "\n";
	cmd += "\nps2raster -A -Tf " + ps_name + "\n";
	cmd += "\nrm temp.txt\n";
	subprocess.call(cmd,shell=True);

#	Plot the total number of scenes for each month

	ps_path = "aster_monthly_dem_totals_2014_04_08.ps";

	cmd  = "\npsbasemap -JX10c/6.25c -R0/12/0/20 -Bf1:\"Month\":/a5f5g5:\"# of DEMs\"::,::.\"ASTER Monthly DEM Totals\":WS --D_FORMAT=%.12lg --LABEL_FONT=1 --LABEL_FONT_SIZE=14 --ANNOT_FONT_PRIMARY=1 --ANNOT_FONT_SIZE_PRIMARY=12 --ANNOT_FONT_SECONDARY=1 --ANNOT_FONT_SIZE_SECONDARY=10 --HEADER_FONT=1 --HEADER_FONT_SIZE=18 -P -K > " + ps_path + "\n";

	cmd += "\necho \"0.5 0 10 0 1 BC 1\" | pstext -Y-0.4c -J -R -Gblack -O -K >> " + ps_path + "\n";

	for i in range(1, 13):
		cmd += "\necho \"" + str(i - 0.5) + " 0 10 0 1 BC " + str(i) + "\" | pstext -J -R -Gblack -O -K >> " + ps_path + "\n";

	for month in seasons:
	
		cmd += "\necho \"" + str(int(month)) + " 0\\n" + str(int(month)) + " " + str(seasons[month]) + "\\n" + str(int(month) + 1) + " " + str(seasons[month]) + "\\n" + str(int(month) + 1) + " 0\" | psxy -J -R -Gred -W0.5p,black -O -K >> " + ps_path + "\n";

	cmd  = cmd.replace("psxy","psxy -Y0.4c",1);
	cmd  = cmd[ : cmd.rfind(" -K")] + " >> " + ps_path + "\n";
	cmd += "\nps2raster -A -Tf " + ps_path + "\n";
	subprocess.call(cmd,shell=True);

	return;



if __name__ == "__main__":

        import os;
        import sys;

        assert len(sys.argv) > 1, "\n***** ERROR: datePlot.py requires 1 argument, " + str(len(sys.argv) - 1) + " given\n";
        assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";

        datePlot(sys.argv[1]);

        exit();

