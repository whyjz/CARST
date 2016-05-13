#!/usr/bin/python


# dateInterval.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# Description
# ***********
# Reads filenames that contain dates, returns later date, earlier date, interval in days an mean date

# Usage
# *****
# python /path/to/filelist.txt


# Input
# *****
#	/path/to/filelist.txt - One-column ASCII text file containing filenames that have dates in them


# Output
# ******
# later_date, earlier_date, interval, middle_date
#	later_date - string representing later date as read in by the script from the filename
#	earlier_date - string representing earlier date as read in by the script from the filename
#	interval - interval between later_date and earlier_date in days
#	middle_date - date midway between later_date and earlier_date, outputted as "YYYY-MM-DD HH:MM:SS"



def dateInterval(file_list_path):

	import datetime;
	import re;

	dates = {};

	date1       = "";
	date2       = "";
	interval    = "";
	middle_date = "";

	infile = open(file_list_path, "r");

	for line in infile:

		if re.search("\d{14}_\d{14}", line):

			date1 = line[re.search("\d{14}_\d{14}", line).start(0) : re.search("\d{14}_\d{14}", line).start(0) + 14];
			date2 = line[re.search("\d{14}_\d{14}", line).start(0) + 15 : re.search("\d{14}_\d{14}", line).end(0)];

			if date1[0:2] != "19" and date1[0:2] != "20":
				date1 = date1[4:8] + date1[0:2] + date1[2:4] + date1[8:14];
				date2 = date2[4:8] + date2[0:2] + date2[2:4] + date2[8:14];

			datetime1   = datetime.datetime(int(date1[0:4]), int(date1[4:6]), int(date1[6:8]), int(date1[8:10]), int(date1[10:12]), int(date1[12:14]));
			datetime2   = datetime.datetime(int(date2[0:4]), int(date2[4:6]), int(date2[6:8]), int(date2[8:10]), int(date2[10:12]), int(date2[12:14]));
			interval    = str(abs((datetime1 - datetime2).total_seconds() / float(60. * 60. * 24.)));
			interval_td = (datetime1 - datetime2) // 2;
			datetime_m  = datetime2 + interval_td;

			datetime_m_year = datetime.datetime(datetime_m.year, 1, 1, 0, 0, 0);
			m_dec_year      = (datetime_m - datetime_m_year).total_seconds() / float(60. * 60. * 24. * 365.25);
			

			print(date1 + " " + date2 + " " + interval + " " + str(datetime_m.year + float(m_dec_year)) + " " + datetime_m.isoformat(" "));
			dates[date1 + " " + date2] = line.strip(), date1, date2, interval, datetime_m.isoformat(" ");

		elif re.search("\d{2}[A-Z]{3}\d{2}[_\-]\d{2}[A-Z]{3}\d{2}", line):

			months = {"JAN" : "01", "FEB" : "02", "MAR" : "03", "APR" : "04", "MAY" : "05", "JUN" : "06", "JUL" : "07", "AUG" : "08", "SEP" : "09", "OCT" : "10", "NOV" : "11", "DEC" : "12"};

			date2 = line[re.search("\d{2}[A-Z]{3}\d{2}[_\-]\d{2}[A-Z]{3}\d{2}", line).start(0) : re.search("\d{2}[A-Z]{3}\d{2}[_\-]\d{2}[A-Z]{3}\d{2}", line).start(0) + 7];
			date1 = line[re.search("\d{2}[A-Z]{3}\d{2}[_\-]\d{2}[A-Z]{3}\d{2}", line).start(0) + 8 : re.search("\d{2}[A-Z]{3}\d{2}[_\-]\d{2}[A-Z]{3}\d{2}", line).end(0)];

			date1 = "20" + date1[0:2] + months[date1[2:5]] + date1[5:7];
			date2 = "20" + date2[0:2] + months[date2[2:5]] + date2[5:7];

			datetime1   = datetime.datetime(int(date1[0:4]), int(date1[4:6]), int(date1[6:8]), 0, 0, 0);
			datetime2   = datetime.datetime(int(date2[0:4]), int(date2[4:6]), int(date2[6:8]), 0, 0, 0);
			interval    = str(abs((datetime1 - datetime2).total_seconds() / float(60. * 60. * 24.)));
			interval_td = (datetime1 - datetime2) // 2;
			datetime_m  = datetime2 + interval_td;

			print(date1, date2, interval, datetime_m.isoformat(" "));
			dates[date1 + " " + date2] = line.strip(), date1, date2, interval, datetime_m.isoformat(" ");

		elif re.search("L[A-Z]\d{14}[A-Z]{3}\d{2}_B\d{1}\.[A-Z]{3} L[A-Z]\d{14}[A-Z]{3}\d{2}_B\d{1}\.[A-Z]{3}", line):

			search_exp = "L[A-Z]\d{14}[A-Z]{3}\d{2}_B\d{1}\.[A-Z]{3} L[A-Z]\d{14}[A-Z]{3}\d{2}_B\d{1}\.[A-Z]{3}";

			date1  = line[re.search(search_exp, line).start(0) + 9 : re.search(search_exp, line).start(0) + 16];
			date2  = line[re.search(search_exp, line).start(0) + 38 : re.search(search_exp, line).start(0) + 45];

			datetime1   = datetime.datetime(int(date1[0:4]), 1, 1, 0, 0, 0) + datetime.timedelta(days=int(date1[4:7]));
			datetime2   = datetime.datetime(int(date2[0:4]), 1, 1, 0, 0, 0) + datetime.timedelta(days=int(date2[4:7]));
			interval    = str(abs((datetime1 - datetime2).total_seconds() / float(60. * 60. * 24.)));
			interval_td = (datetime1 - datetime2) // 2;
			datetime_m  = datetime2 + interval_td;

#			print(date1, date2, interval, datetime_m.isoformat(" "));
			dates[date1 + " " + date2] = line.strip(), date1, date2, interval, datetime_m.isoformat(" ");

	infile.close();

	return dates;


if __name__ == "__main__":

	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: dateInterval.py requires one argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";

	dateInterval(sys.argv[1]);

	exit();

