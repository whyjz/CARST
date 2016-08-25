#!/usr/bin/python


# season.py
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



def season(pair):

	import datetime;
	import re;

	season_days       = [0.0, 0.0, 0.0, 0.0];
	last_day_of_month = {2 : 28, 5 : 31, 8 : 31, 11 : 30};

	date2 = pair[re.search("\d{14}_\d{14}", pair).start(0) : re.search("\d{14}_\d{14}", pair).start(0) + 14];
	date1 = pair[re.search("\d{14}_\d{14}", pair).start(0) + 15 : re.search("\d{14}_\d{14}", pair).end(0)];

	year1  = int(date1[0:4]);
	month1 = int(date1[4:6]);
	day1   = int(date1[6:8]);
	
	year2  = int(date2[0:4]);
	month2 = int(date2[4:6]);
	day2   = int(date2[6:8]);	

	cur_year  = year1;
	cur_month = month1;

	datetime1    = datetime.datetime(int(date1[0:4]), int(date1[4:6]), int(date1[6:8]), int(date1[8:10]), int(date1[10:12]), int(date1[12:14]));
	current_dt   = datetime.datetime(int(date1[0:4]), int(date1[4:6]), int(date1[6:8]), int(date1[8:10]), int(date1[10:12]), int(date1[12:14]));
	datetime2    = datetime.datetime(int(date2[0:4]), int(date2[4:6]), int(date2[6:8]), int(date2[8:10]), int(date2[10:12]), int(date2[12:14]));
	start_season = datetime.datetime(int(year1), 9, 1, 0, 0, 0);
	end_season   = datetime.datetime(int(year1), 11, 30, 11, 59, 59);
	cur_season   = 3;

	if month1 > 11:
		start_season = datetime.datetime(int(year1), 12, 1, 0, 0, 0);
		end_season   = datetime.datetime(int(year1) + 1, 2, 28, 11, 59, 59);
		cur_season   = 0;

	elif month1 > 2 and cur_month < 6:
		start_season = datetime.datetime(int(year1), 3, 1, 0, 0, 0);
		end_season   = datetime.datetime(int(year1), 5, 31, 11, 59, 59);
		cur_season   = 1;

	elif month1 > 5 and cur_month < 9:
		start_season = datetime.datetime(int(year1), 6, 1, 0, 0, 0);
		end_season   = datetime.datetime(int(year1), 8, 31, 11, 59, 59);
		cur_season   = 2;

	while end_season < datetime2:

		interval = (end_season - current_dt).total_seconds() / float(60. * 60. * 24.);
		season_days[cur_season] += interval;

		if cur_month > 11:
			cur_year     += 1;
			cur_month     = 3;
			start_season  = datetime.datetime(int(cur_year), 3, 1, 0, 0, 0);
			current_dt    = datetime.datetime(int(cur_year), 3, 1, 0, 0, 0);
			end_season    = datetime.datetime(int(cur_year), 5, 31, 11, 59, 59);
			cur_season    = 1;

		elif cur_month > 2 and cur_month < 6:
			cur_month     = 6;
			start_season  = datetime.datetime(int(cur_year), 6, 1, 0, 0, 0);
			current_dt    = datetime.datetime(int(cur_year), 6, 1, 0, 0, 0);
			end_season    = datetime.datetime(int(cur_year), 8, 31, 11, 59, 59);
			cur_season    = 2;

		elif cur_month > 5 and cur_month < 9:
			cur_month     = 9;
			start_season  = datetime.datetime(int(cur_year), 9, 1, 0, 0, 0);
			current_dt    = datetime.datetime(int(cur_year), 9, 1, 0, 0, 0);
			end_season    = datetime.datetime(int(cur_year), 11, 30, 11, 59, 59);
			cur_season    = 3;

		else:
			cur_month    = 12;
			start_season = datetime.datetime(int(cur_year), 12, 1, 0, 0, 0);
			current_dt   = datetime.datetime(int(cur_year), 12, 1, 0, 0, 0);
			end_season   = datetime.datetime(int(cur_year) + 1, 2, 28, 11, 59, 59);
			cur_season   = 0;

	interval = (datetime2 - current_dt).total_seconds() / float(60. * 60. * 24.);
	season_days[cur_season] += interval;

	return season_days;


if __name__ == "__main__":

	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: season.py requires one argument, " + str(len(sys.argv) - 1) + " given\n";

	season(sys.argv[1]);

	exit();

