#!/usr/bin/python


# dhdtPointPlot.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def dhdtPointPlot(kml_path, points_path, ecrs_tif_path, ecrs_txt_path, ice_bounds_path, rock_bounds_path, utm_zone):

	min_year = "2000";
	
	import os;

	assert os.path.exists(kml_path), "\n***** ERROR: " + kml_path + " does not exist\n";
	assert os.path.exists(points_path), "\n***** ERROR: " + points_path + " does not exist\n";
	assert os.path.exists(ecrs_tif_path), "\n***** ERROR: " + ecrs_tif_path + " does not exist\n";
	assert os.path.exists(ecrs_txt_path), "\n***** ERROR: " + ecrs_txt_path + " does not exist\n";
	assert os.path.exists(ice_bounds_path), "\n***** ERROR: " + ice_bounds_path + " does not exist\n";
	assert os.path.exists(rock_bounds_path), "\n***** ERROR: " + rock_bounds_path + " does not exist\n";

	import re;

	pos_dev = ecrs_tif_path[re.search("p\d+m\d+", ecrs_tif_path).start(0) : re.search("p\d+m\d+", ecrs_tif_path).end(0)]
	neg_dev = pos_dev[re.search("m\d+", pos_dev).start(0) + 1 : re.search("m\d+", pos_dev).end(0)];
	pos_dev = pos_dev[re.search("p\d+", pos_dev).start(0) + 1 : re.search("p\d+", pos_dev).end(0)];
	
	import subprocess;

	cmd  = "\ngdalinfo " + ecrs_tif_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();

	ecrs_zone = info[re.search("UTM\s*zone\s*",info).end(0) : re.search("UTM\s*zone\s*\d+",info).end(0)];
	ecrs_type = info[re.search("Type\s*=\s*",info).end(0) : re.search("Type\s*=\s*\S+",info).end(0)].replace(",","");
	ecrs_res  = info[re.search("Pixel\s*Size\s*=\s*\(\s*",info).end(0) : re.search("Pixel\s*Size\s*=\s*\(\s*\d+\.*\d*",info).end(0)];

	if re.search("0+$", ecrs_res):
		ecrs_res  = ecrs_res[ : re.search("0+$",ecrs_res).start(0)];

	ecrs_no_data = info[re.search("NoData\s*Value\s*=\s*",info).end(0) : re.search("NoData\s*Value\s*=\s*\S+",info).end(0)];

	ecrs_ns   = info[re.search("UTM\s*zone\s*\d+",info).end(0) : re.search("UTM\s*zone\s*\d+[A-Z]",info).end(0)];

	if ecrs_ns.lower().find("n") > -1:
		ecrs_ns = "north";

	else:
		ecrs_ns = "south";

	ecrs_ul_x = info[re.search("Upper Left\s*\(\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	ecrs_ul_y = info[re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	ecrs_ur_x = info[re.search("Upper Right\s*\(\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	ecrs_ur_y = info[re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Upper Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	ecrs_lr_x = info[re.search("Lower Right\s*\(\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	ecrs_lr_y = info[re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Right\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];
	ecrs_ll_x = info[re.search("Lower Left\s*\(\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*",info).end(0)];
	ecrs_ll_y = info[re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*",info).end(0) : re.search("Lower Left\s*\(\s*\-*\d+\.*\d*,\s*\-*\d+\.*\d*",info).end(0)];

	cmd	 = "\ndate +\"%s\" -d \"1858-11-17 00:00:00\"\n";
	pipe	 = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	jul_secs = pipe.read().strip();
	pipe.close();

	coords_str = "";

	kml_file = open(kml_path,"r");

	while 1:

		line = kml_file.readline().strip();

		if not line:
			break;

		if re.search("\-*\d+\.*\d*\s*,\s*\-*\d+\.*\d*",line):
			coords_str = line + "\n";

	kml_file.close();

	coords_list = coords_str.replace(",0","").split();

	new_coords = {};

	for coord in coords_list:

		[input_x, input_y] = coord.split(",");

		cmd = "\necho \"" + input_x + " " + input_y + "\" | /usr/local/gmt/bin/mapproject -Ju" + ecrs_zone + "X/1:1 -F -C\n";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		info = pipe.read().strip();
		pipe.close();

		reproj_coords = info.split();

		input_x = reproj_coords[0];
		input_y = reproj_coords[1];

		new_x = str((float(ecrs_ul_x) - int(ecrs_res.replace(".","")) / 2) + int(abs(float(input_x) - (float(ecrs_ul_x) - int(ecrs_res.replace(".","")) / 2))) / int(ecrs_res.replace(".","")) * int(ecrs_res.replace(".","")));

		if float(input_x) - float(new_x) > int(ecrs_res.replace(".","")) / 2.:
			new_x = str(float(new_x) + int(ecrs_res.replace(".","")));

		new_y = str((float(ecrs_ll_y) - int(ecrs_res.replace(".","")) / 2) + int(abs(float(input_y) - (float(ecrs_ll_y) - int(ecrs_res.replace(".","")) / 2))) / int(ecrs_res.replace(".","")) * int(ecrs_res.replace(".","")));

		if float(input_y) - float(new_y) > int(ecrs_res.replace(".","")) / 2.:
			new_y = str(float(new_y) + int(ecrs_res.replace(".","")));

		new_coords[new_x + " " + new_y] = new_x + " " + new_y;

	points = {};

	selected_points_path = kml_path[kml_path.rfind("/") + 1 : kml_path.rfind(".")] + "_selected.txt";

	if os.path.exists(selected_points_path):
		points_path = selected_points_path;

	infile = open(points_path, "r");

	for line in infile:
	
		if line.find(">") > -1:
			continue;

		elements = line.split()
		x = elements[0];
		y = elements[1];

		if x + " " + y not in points:
			points[x + " " + y] = [];	
		
		points[x + " " + y].append(line.strip());	

	infile.close();

	if not os.path.exists(selected_points_path):

		outfile = open(selected_points_path, "w");

		for coord in new_coords:

			for line in points[coord]:

				outfile.write(line + "\n");
	
			outfile.write(">\n");

		outfile.close();

	dates     = {};
	elevs     = {};
	stdevs    = {};

	for coord in new_coords:

		dates[coord]  = {};
		elevs[coord]  = {};
		stdevs[coord] = {};

		for line in points[coord]:

			elements  = line.split();

			date = elements[3];

			dates[coord][date]  = date;
			elevs[coord][date]  = elements[2];
			stdevs[coord][date] = elements[4];

	ecrs      = {};
	ref_elevs = {};
	ref_dates = {};
	min_dates = {};
	max_dates = {};

	infile = open(ecrs_txt_path, "r");

	for line in infile:

		elements = line.split();
		coord    = elements[0] + " " + elements[1];
		ecrs[coord] = line.strip();

		if coord not in new_coords:
			continue;

		ref_elevs[elements[8]] = coord;
		ref_dates[elements[8]] = elements[7];
		min_dates[coord]       = elements[10];
		max_dates[coord]       = elements[12];
		
	infile.close();

	sorted_elevs = sorted(ref_elevs);

	print(sorted_elevs);
	#first_date = min(dates)[0:4] + "T";
	#last_date  = max(dates)[0:4] + "T";

#	first_date = "1950T";
	first_date = "2000T";
	last_date  = "2015T";

	count = 0;

	ps_path = kml_path[kml_path.rfind("/") + 1 : kml_path.rfind(".")] + ".ps";

	cmd  = "\nmakecpt -Cpaired -T0/" + str(len(new_coords)) + "/1  > points.cpt\n";

	for elev in sorted_elevs:

		coord = ref_elevs[elev];

		elements = ecrs[coord].split();

		ecr	  = elements[2];
		intercept = elements[4];
		interval  = elements[14];

		max_elev = "";
		min_elev = "";

		if float(ecr) > 0:
			min_elev = str(int(float(intercept) - float(intercept) % 50 - 50));
			max_elev = str(int(float(intercept) + float(interval) * float(ecr) - (float(intercept) + float(interval) * float(ecr)) % 50 + 100));
		
		else:
			min_elev = str(int(float(intercept) + float(interval) * float(ecr) - (float(intercept) + float(interval) * float(ecr)) % 50 - 50));
			max_elev = str(int(float(intercept) - float(intercept) % 50 + 100));

		if float(min_elev) < 0:
			min_elev = "0";
		
		#min_elev = min(elevs.values());
		#max_elev = max(elevs.values());

		X  = "";
		Y  = "-Y40c";
		KO = "-K >";

		if count > 0:

			KO = "-O -K >>";

			Y = "-Y-6.5";

			if count % 5 == 0:

				X = "-X7";
				Y = "-Y26";

		cmd += "\npsbasemap " + X + " " + Y + " -Ba10yf10yg10y:\"Year\":/a50f50g50:\"Elevation (m)\":WeSn -JX5c -R" + first_date + "/" + last_date + "/" + min_elev + "/" + max_elev + " --INPUT_DATE_FORMAT=yyyy-mm-dd --PLOT_DATE_FORMAT=yy -P --PAPER_MEDIA=A2 --ANNOT_FONT_SIZE_PRIMARY=9 --ANNOT_OFFSET_PRIMARY=0.05i --LABEL_FONT_SIZE=10 --LABEL_OFFSET=0.04i " + KO + " " + ps_path + "\n";

		for date in dates[coord]:

			upper_thresh = float(elev) + (float(date) - float(ref_dates[elev])) * float(pos_dev);
			lower_thresh = float(elev) - (float(date) - float(ref_dates[elev])) * float(neg_dev);

			if float(date) - float(ref_dates[elev]) < 0:
				temp         = upper_thresh;
				upper_thresh = lower_thresh;
				lower_thresh = temp;

			print(elev, elevs[coord][date], (float(date) - float(ref_dates[elev])), upper_thresh, lower_thresh);

			if float(elevs[coord][date]) > upper_thresh or float(elevs[coord][date]) < lower_thresh:
				cmd += "\necho \"" + date + " " + elevs[coord][date] + " " + str(count) + " " + stdevs[coord][date] + "\" | psxy -J -R -Ey -Ss0.3c -Cpoints.cpt -W0.1p,red -O -K >> " + ps_path + "\n";

			else:
				cmd += "\necho \"" + date + " " + elevs[coord][date] + " " + str(count) + " " + stdevs[coord][date] + "\" | psxy -J -R -Ey -Ss0.3c -Cpoints.cpt -W0.1p,black -O -K >> " + ps_path + "\n";
		
		cmd += "\necho \"" + min_dates[coord] + " " + intercept + "\\n" + max_dates[coord] + " " + str(float(intercept) + float(interval) * float(ecr)) + "\" | psxy -J -R -W2p,blue -O -K >> " + ps_path + "\n";
		cmd += "\necho \"0.5 9 12 0 1 BL " + str(int(count) + 1) + "\" | pstext -J -R0/10/0/10 -Gblack -Wwhiteo0.2p,black -O -K >> " + ps_path + "\n";
		cmd += "\necho \"2 9 10 0 1 BL dh/dt=" + str(round(float(ecr), 2)) + " m/yr\" | pstext -J -R0/10/0/10 -Gblack -Wwhiteo0.2p,black -O -K >> " + ps_path + "\n";

		count += 1;

	cmd  = cmd[ : cmd.rfind("-K") - 1] + cmd[cmd.rfind("-K") + 2 : ];
	cmd += "\nps2raster -A -Tf " + ps_path + "\n";

	subprocess.call(cmd,shell=True);


		#cmd += "\ngawk '{print $4\" \"$2\" " + str(count) + " \"$3}' bad_temp | psxy -J -R -Ey -Ss0.3c -Cpoints.cpt -W1.25p,red -O -K >> " + psname + "\n";
		#cmd += "\necho \"1963-04-01 186\\n1988-11-01 186\\n1988-11-01 163\\n1963-04-01 163\\n1963-04-01 186\" | psxy -J -R -W1p,black -Gwhite -O -K >> " + psname + "\n";
		#cmd += "\necho \"1965-10-01 181 " + str(count) + "\" | psxy -J -R -Ss0.3c -W1.25p,red -Cpoints.cpt -O -K >> " + psname + "\n";
		#cmd += "\necho \"1968-04-01 181 10 0 1 ML Excluded\" | pstext -J -R -Gblack -O -K >> " + psname + "\n";
		#cmd += "\necho \"1968-04-01 170 10 0 1 ML dh/dt\" | pstext -J -R -Gblack -O -K >> " + psname + "\n";
		#cmd += "\npsxy temp_out_1 -J -R -W1p,blue -O -K >> " + psname + "\n";

		#if len(elements) > 7:
#		cmd += "\npsxy temp_out_2 -J -R -W1p,blue -O -K >> " + psname + "\n";
		
		

	return;


if __name__ == "__main__":

	import os;
	import sys;
	
	assert len(sys.argv) > 7, "\n***** ERROR: dhdtPointPlot.py requires 7 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";
	assert os.path.exists(sys.argv[4]), "\n***** ERROR: " + sys.argv[4] + " does not exist\n";
	assert os.path.exists(sys.argv[5]), "\n***** ERROR: " + sys.argv[5] + " does not exist\n";
	assert os.path.exists(sys.argv[6]), "\n***** ERROR: " + sys.argv[6] + " does not exist\n";
	
	dhdtPointPlot(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7]);

	exit();

