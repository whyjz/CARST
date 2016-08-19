#!/usr/bin/python


def climateDataFormat(input_path):

	import os;
	import re;
	from scipy.interpolate import interp1d;
	import subprocess;

	assert os.path.exists(input_path), "\n***** ERROR: " + input_path + " does not exist\n"

	minyear = "9999";
	maxyear = "0";
	tod     = 6./24.;

	day_counts  = {};
	days        = [];
	precips     = {};
	temps       = {};
	avg_temps   = {};
	avg_precips = {};

	infile = open(input_path, "r");

	infile.readline();
	infile.readline();

	print("year     day     time     airtemp     relhumidity     windspeed     winddir     global_rad     reflected     netradiation     longwave_in     Longwave_out     precip     discharge");

	for line in infile:

		datetime = line[102:110];
		precip_r = line[394:400];
		ground_s = line[464:472];
		precip_s = line[534:543];
		max_temp = line[606:614];
		min_temp = line[676:685];
		obs_temp = line[747:756];

#		precip_r = line[111:118];
#		ground_s = line[180:190];
#		precip_s = line[250:260];
#		max_temp = line[322:331];
#		min_temp = line[392:403];
#		obs_temp = line[462:471];

		elements = line.strip().split();

		year  = datetime[0:4];
		month = datetime[4:6];
		day   = datetime[6:];

		cmd  = "\ndate -d \"" + year + "/" + month + "/" + day + "\" +%j\n";
		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		julian_day = pipe.read().strip();
		pipe.close();

		for i in range(0, 3 - len(julian_day)):
			julian_day = "0" + julian_day;

		if float(minyear) > float(year):
			minyear = year;

		if float(maxyear) < float(year):
			maxyear = year;

		if precip_s.find("999") > -1:
			precip_s = "0";

		if precip_r.find("999") > -1:
			precip_r = "0";

		total_precip = str(0.2 * float(precip_s) + float(precip_r) / 10);

		temp = obs_temp;
		
		if obs_temp.find("999") > -1:
			if re.search("\d", max_temp) and max_temp.find("9999") < 0:
				temp = max_temp[re.search("\-*\d+", max_temp).start(0) : re.search("\-*\d+", max_temp).end(0)];
				temp = str(float(temp) / 10);
			elif re.search("\d", min_temp) and min_temp.find("9999") < 0:
				temp = min_temp[re.search("\-*\d+", min_temp).start(0) : re.search("\-*\d+", min_temp).end(0)];
				temp = str(float(temp) / 10);
			else:
				temp = "-9999";
		else:
			temp = str(float(obs_temp) / 10);

		if julian_day not in day_counts:
			day_counts[int(julian_day)]   = 1;
		else:
			day_counts[int(julian_day)]  += 1;

		if julian_day not in avg_temps:
			avg_temps[int(julian_day)]    = float(temp);
		else:
			avg_temps[int(julian_day)]   += float(temp);

		if julian_day not in avg_precips:
			avg_precips[int(julian_day)]  = float(total_precip);
		else:
			avg_precips[int(julian_day)] += float(total_precip);

		days.append(year + julian_day);
		temps[year + julian_day]   = temp;
		precips[year + julian_day] = total_precip;

	infile.close();


	first_day = days[0][4:7];
	last_day  = days[len(days) - 1][4:7];

	days_input     = [];
	days_output    = [];
	temps_output   = [];
	precips_output = [];
	days_in_year   = 365;

	for year in range(int(minyear), int(minyear) + 1):

		if year % 4 != 0:
                        days_in_year = 365;
                elif year % 100 != 0:
                        days_in_year = 366;
                elif year % 400 != 0:
                        days_in_year = 365;
                else:
                        days_in_year = 366;

		for day in range(int(first_day), days_in_year + 1): 

			date = str(year) + str(day);

			if date not in temps or temps[date].find("999") > -1:
				temps[date] = str(avg_temps[day] / day_counts[day]);

			if date not in precips or precips[date].find("999") > -1:
				precips[date] = str(avg_precips[day] / day_counts[day]);

			print(str(year) + "     " + str(day) + "     6     " + temps[date] + "     -9999     -9999     -9999     -9999     -9999     -9999     -9999     -9999     " + precips[date] + "     -9999");


	if minyear == maxyear:
		return;


	for year in range(int(minyear) + 1, int(maxyear)):

		if year % 4 != 0:
                        days_in_year = 365;
                elif year % 100 != 0:
                        days_in_year = 366;
                elif year % 400 != 0:
                        days_in_year = 365;
                else:
                        days_in_year = 366;

		for day in range(1, days_in_year + 1): 

			date = str(year) + str(day);

			if date not in temps or temps[date].find("999") > -1:
				temps[date] = str(avg_temps[day] / day_counts[day]);

			if date not in precips or precips[date].find("999") > -1:
				precips[date] = str(avg_precips[day] / day_counts[day]);

			print(str(year) + "     " + str(day) + "     6     " + temps[date] + "     -9999     -9999     -9999     -9999     -9999     -9999     -9999     -9999     " + precips[date] + "     -9999");


	for year in range(int(maxyear), int(maxyear) + 1):

		days_in_year = 365;

		if year % 4 != 0: 
			days_in_year = 365;
		elif year % 100 != 0:
			days_in_year = 366;
		elif year % 400 != 0:
			days_in_year = 365;
		else:
			days_in_year = 366;
			 
		for day in range(1, int(last_day) + 1): 

			date = str(year) + str(day);

			if date not in temps or temps[date].find("999") > -1:
				temps[date] = str(avg_temps[day] / day_counts[day]);

			if date not in precips or precips[date].find("999") > -1:
				precips[date] = str(avg_precips[day] / day_counts[day]);

			print(str(year) + "     " + str(day) + "     6     " + temps[date] + "     -9999     -9999     -9999     -9999     -9999     -9999     -9999     -9999     " + precips[date] + "     -9999");


	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: climateDataFormat.py requires one argument, " + str(len(sys.argv)) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	climateDataFormat(sys.argv[1]);


