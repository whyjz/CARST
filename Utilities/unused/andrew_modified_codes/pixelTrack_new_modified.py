#!/usr/bin/python

# pixelTrack.py

# Author: Andrew Kenneth Melkonian
# All rights reserved

# Modified by Whyjay 2016/5/12


import calendar;
import fileinput;
import math;
import numpy;
import os;
from pxfuncs_modified import *;
import pylab;
import re;
import scipy;
import subprocess;
import sys;
import time;


PROGRAM_NAME="pixelTrack_new.py";







start_time = time.time();


params_path = "";
steps = "uncompress/preraw/makeraw/setup/baselines/offsets/ampcor/make_unw/affine/geocode/optical_raw/gausshp_filt/get_xyzs/profiles/kml/test";

if len(sys.argv) > 2:

	params_path = sys.argv[1];
	start = sys.argv[2];

	if not os.path.isfile(params_path):
		print("\n***** ERROR, parameter file \"" + params_path + "\" does not exist\n");
		sys.exit();

	if steps.find(start) == -1:
		print("\n***** ERROR, \"" + start + "\" is not a valid name for a step\nValid step names: " + steps + "\n");
		sys.exit();

	if len(sys.argv) > 3:
		end = sys.argv[3];

		if steps.find(end) == -1:
			print("\n***** ERROR, \"" + end + "\" is not a valid name for a step\nValid step names: " + steps + "\n");
			sys.exit();

	else:
		end = "";

else:

	if len(sys.argv) < 2:
		print("\n***** ERROR, please include parameter file as command line argument\n" + PROGRAM_NAME + " usage: $python " + PROGRAM_NAME + " parameter_file_path start_step [end_step]\n");
		sys.exit();

	else:
		print("\n***** ERROR, please include step to start at\n" + PROGRAM_NAME + " usage: $python " + PROGRAM_NAME + " parameter_file_path start_step [end_step]\n");
		sys.exit();



parameter_file = open(params_path,"r");

while 1:
	line = parameter_file.readline();

	if not line:
		break;

	line = line.strip();

	name = "";
	value = "";
	elements = line.split("=");

	if len(elements) < 2 or len(elements[0]) < 1 or len(elements[1]) < 1:
		print("\n***** ERROR, parameter file line format is \"name = value\", \"" + line + "\" does not conform to this format\n");
		sys.exit();

	name = elements[0].strip();
	value = elements[1].strip();
	vars()[name] = value;

parameter_file.close();


try: WorkPath
except NameError:
	print("\n***** ERROR, variable \"WorkPath\" not set in parameter file\n");
	sys.exit();

if not os.path.isdir(WorkPath):
	print("\n***** ERROR, raw-raw folder \"" + WorkPath + "\" does not exist\n");
	sys.exit();

elif len(os.listdir(WorkPath)) < 1:
	print("\n***** ERROR, raw-raw folder \"" + WorkPath + "\" is empty\n");
	sys.exit();


try: DataType
except NameError:
	print("\n***** WARNING, variable \"DataType\" not set in parameter file\nUsing ERS as data type");
	DataType = "ERS";

if re.search("ers", DataType.lower()) > -1:
	DataType = "ers";
	orbit = "PRC";

elif re.search("r\.*sat", DataType.lower()):
	DataType = "radarsat";
	orbit = "HDR";

elif re.search("envisat", DataType.lower()):
	DataType = "envisat";
	orbit = "DOR";

elif re.search("alos", DataType.lower()):
	DataType = "alos";
	orbit = "HDR";

elif re.search("tsx", DataType.lower()) or re.search("terrasarx", DataType.lower()):
	DataType = "tsx";
	orbit = "HDR";


try: Angle
except NameError:
	print("\n***** WARNING, variable \"Angle\" not set in parameter file\nUsing default value of 23 degrees (ERS)\n");
	Angle = "23";



# ***** STEP: uncompress *****
# Takes downloaded, compressed scenes, uncompresses them

if start == "uncompress":

	cwd = os.getcwd();

#	Find compressed, raw files

	if not os.path.exists(WorkPath + "/ARCHIVE"):
		os.mkdir(WorkPath + "/ARCHIVE");

	prefix = "";

	if DataType == "tsx":
		prefix = "dims";

	elif DataType == "ers":
		prefix = "ER0";


	cmd = "\nfind " + WorkPath + " \( -name \"" + prefix + "*.bz2\" -o -name \"" + prefix + "*.bzip2\" -o -name \"" + prefix + "*.tar\" -o -name \"" + prefix + "*.zip\" -o -name \"" + prefix + "*.gz\" -o -name \"" + prefix + "*.gzip\" -o -name \"" + prefix + "*.tgz\" \) -print\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	compressed_file_list = pipe.read().split();
	pipe.close();

#	When none are found (or tar files already untarred), break out of loop  
	
	if len(compressed_file_list) < 1:
		print("\n***** WARNING, no uncompressed data files found, exiting...\n");
		exit();

#	When compressed files found, check extension and uncompress using appropriate program

	extensions = {};
	extensions["\.tar"] = "tar xvf";
	extensions["\.bz2"] = "bunzip2";
	extensions["\.tgz"] = "gunzip";
	extensions["\.gz"]  = "gunzip";
	extensions["\.zip"] = "unzip";

	all_extensions = ["\.tar|\.bz2|\.tgz|\.gz|\.zip"];


	for path in compressed_file_list:

		compressed_file_name = path[path.rfind("/") + 1 : ];
		compressed_file_dir  = path[path.rfind("/") + 1 : path.find(".")];

		print(compressed_file_dir);

#		Do not uncompress files that have already been uncompressed

		if os.path.exists(compressed_file_dir):
			print("\n***** Directory " + compressed_file_dir + " already exists, skipping...\n");
			continue;

#		Do not uncompress files that have been archived   

		if re.search("ARCHIVE/",path):
			print("\n***** File " + path + " contained in ARCHIVE folder, skipping...\n");
			continue;

		cmd = "\ncp -p " + path + " " + WorkPath + "/ARCHIVE\n";
		subprocess.call(cmd,shell=True);

		cmds = {};

		if DataType == "ers":
			date = path[re.search("0P_\d{8}", path).start(0) + 3 : re.search("0P_\d{8}", path).end(0)];
			os.mkdir(path[path.rfind("/") + 1 : path.find(".")]);
			os.chdir(path[path.rfind("/") + 1 : path.find(".")]);
#			cmds[-1]   = "\ncd " + cwd + "\n";


		for key in extensions:	

			if re.search(key,path):	
				
				cmds[re.search(key,path).end(0)] = "\n" + extensions[key] + " " + path[ : re.search(key,path).end(0)] + "\n";

				if key.find("tar") > -1:
					cmds[0] = "\nrm " + path[ : re.search(key,path).end(0)] + "\n";

			if path.rfind("tgz") > -1:
				cmds[1] = "\ntar xvf " + path[ : path.rfind(".tgz")] + ".tar\n";
				cmds[0] = "\nrm " + path[ : re.search(key,path).end(0)] + "\n";

		for index in sorted(cmds,reverse=True):
			subprocess.call(cmds[index],shell=True);


		if DataType == "ers":
			os.chdir(cwd);

	start = "preraw";

	if start == end:
		logFile = open("pxlog.txt","a");
		logFile.write("\n***** pixelTrack.py for parameters \""+params_path+"\" - Started at \""+start+"\", ended at \""+end+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-start_time)));
		logFile.close();
		print("\nReached end step \"" + end + "\", exiting...\n");
		sys.exit();



# ***** STEP: preraw *****
# Creates separate date directories and places files in appropriated date directories, prepares for "makeraw" step

if start == "preraw":

	cmd = "";

	if DataType.lower().find("alos") > -1:
		cmd = "\nfind " + WorkPath + " -name \"LED*\" -print\n";

	elif DataType.lower().find("envisat") > -1:
		cmd = "\nfind " + WorkPath + " -name \"*.N1*\" -print\n";

	elif DataType.lower().find("ers") > -1:
		cmd = "\nfind " + WorkPath + " \( -name \"*.ldr\" -o -name \"LEA*.001\" \) -print\n";

	elif DataType.lower().find("tsx") > -1:
		#cmd = "\nfind " + WorkPath + " -name \"TDX*.xml\"\n";    # whyjay modified
		cmd = "\nfind " + WorkPath + " -name \"TSX*.xml\"\n";

	else:
		cmd = "\nfind " + WorkPath + " -name \"*.ldr\" -print\n";

	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	leader_file_paths = pipe.read().split();
	pipe.close();

	if DataType.lower().find("alos") > -1:
		setupALOS(WorkPath,leader_file_paths);

	elif DataType.lower().find("envisat") > -1:
		setupENVISAT(WorkPath,leader_file_paths);

	elif DataType.lower().find("ers") > -1:
		setupERS(WorkPath,leader_file_paths);

	elif DataType.lower().find("tsx") > -1:
		print("Here: setup TSX")     # whyjay modified
		setupTSX(WorkPath,leader_file_paths);	

	else:
		setupERS(WorkPath,leader_file_paths);

	searchExp = "\s\d\d\d\d\d\d\d\d";

	if DataType.lower().find("alos") > -1:
		searchExp = "\s\d{20}\s";

	elif re.search("envisat",DataType.lower()):
		searchExp = "SENSING_START";

	start = "makeraw";

	if start == end:
		logFile = open("pxlog.txt","a");
		logFile.write("\n***** pixelTrack.py for parameters \""+params_path+"\" - Started at \""+start+"\", ended at \""+end+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-start_time)));
		logFile.close();
		print("\nReached end step \"" + end + "\", exiting...\n");
		sys.exit();



# ***** STEP: makeraw *****
# Runs appropriate makeraw script depending on sensor type

if start == "makeraw":

	if re.search(".*ers.*",DataType.lower()):
		makeRawERS(WorkPath, orbit);

	elif re.search("r.*sat",DataType.lower()):
		makeRawERS(WorkPath, orbit);

	elif re.search("envisat",DataType.lower()):
		makeRawENVISAT(WorkPath, orbit); 

	elif re.search("alos",DataType.lower()):
		makeRawALOS(WorkPath);

	elif re.search("tsx",DataType.lower()):
		makeRawTSX(WorkPath);

	start = "setup";

	if start == end:
		logFile = open("pxlog.txt","a");
		logFile.write("\n***** pixelTrack.py for parameters \""+params_path+"\" - Started at \""+start+"\", ended at \""+end+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-start_time)));
		logFile.close();
		print("\nReached end step \"" + end + "\", exiting...\n");
		sys.exit();



# ***** STEP: make_int_dirs_and_procs *****
# Makes interferogram directories and .proc files consistent with criteria provided in parameters file

if start == "setup":

	try: MinDateInterval
	except NameError:
		print("\nMinDateInterval not set in parameter file, using 1\n");
		MinDateInterval = "1";

	try: MaxDateInterval
	except NameError:
		print("\nMaxDateInterval not set in parameter file, using 72\n");
		MaxDateInterval = "72";

	try: DEM
	except NameError:
		print("\n***** WARNING, variable \"DEM\" not set in parameter file\n");
		DEM = "";

	angles = {};
	max_inc_angle = "";
	min_inc_angle = "";

	if DataType.lower().find("tsx") > -1:

		# cmd = "\nfind " + WorkPath + " -name \"TDX*.xml\"\n";    # whyjay modified
		cmd = "\nfind " + WorkPath + " -name \"TSX*.xml\"\n";      # whyjay modified
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		leader_file_paths = pipe.read().split();
		pipe.close();

		for path in leader_file_paths:

			date = "";

			infile = open(path,"r");

			for line in infile:

				if line.find("timeUTC") > -1:
					index = re.search("timeUTC>",line).end(0);
					year  = line[index + 2 : index + 4];
					month = line[index + 5 : index + 7];
					day   = line[index + 8 : index + 10];
					date  = year + month + day;

				elif line.find("coverageRegionMin incidenceAngle") > -1:
					min_inc_angle = line[re.search("\">",line).end(0) : re.search("</",line).start(0)];

				elif line.find("coverageRegionMax incidenceAngle") > -1:
					max_inc_angle = line[re.search("\">",line).end(0) : re.search("</",line).start(0)];

			infile.close();

			angles[date] = str((float(max_inc_angle) + float(min_inc_angle)) / 2.);

	contents = os.listdir(WorkPath);
	dates    = [item for item in contents if re.search("^\d\d\d\d\d\d$", item)];

	for i in range(0,len(dates)):

		for j in range(i+1,len(dates)):

			year_i = "";
			year_j = "";

			if int(dates[i][0:2]) > 70:
				year_i = "19" + dates[i][0:2];
			else:
				year_i = "20" + dates[i][0:2];

			if int(dates[j][0:2]) > 70:
				year_j = "19" + dates[j][0:2];
			else:
				year_j = "20" + dates[j][0:2];

			month_i = dates[i][2:4];
			month_j = dates[j][2:4];
			day_i = dates[i][4:6];
			day_j = dates[j][4:6];

			date_i_cmd = "\ndate +\"%s\" -d \"" + year_i + "-" + month_i + "-" + day_i + " 00:00:00\"\n";
			pipe = subprocess.Popen(date_i_cmd,shell=True,stdout=subprocess.PIPE).stdout;
			date_i_seconds = pipe.read().strip();
			pipe.close();

			date_j_cmd = "\ndate +\"%s\" -d \"" + year_j + "-" + month_j + "-" + day_j + " 00:00:00\"\n";
			pipe = subprocess.Popen(date_j_cmd,shell=True,stdout=subprocess.PIPE).stdout;
			date_j_seconds = pipe.read().strip();
			pipe.close();

			seconds_difference = int(date_j_seconds) - int(date_i_seconds);
			days_difference = seconds_difference / (60. * 60. * 24.);

			later_date   = dates[i];
			earlier_date = dates[j];

			if int(date_j_seconds) > int(date_i_seconds):
				later_date   = dates[j];
				earlier_date = dates[i];

			if abs(days_difference) >= int(MinDateInterval) and abs(days_difference) <= int(MaxDateInterval):

				int_path = WorkPath + "/int_" + later_date + "_" + earlier_date;
				print(int_path);

				if not os.path.exists(int_path):
					os.mkdir(int_path);

				if DataType.lower().find("tsx") > -1: 
					# print(angles)    # whyjay modified
					Angle = str((float(angles[dates[i]]) + float(angles[dates[j]]))/2.);

				if not os.path.exists(int_path + ".proc"):
					makeProcFile(WorkPath, later_date, earlier_date, Angle, DEM, orbit);

	start = "baselines";

	if start == end:
		logFile = open("pxlog.txt","a");
		logFile.write("\n***** pixelTrack.py for parameters \""+params_path+"\" - Started at \""+start+"\", ended at \""+end+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-start_time)));
		logFile.close();
		print("\nReached end step \"" + end + "\", exiting...\n");
		sys.exit();



# ***** STEP: baselines *****
# Runs ROI_PAC's process_2pass from raw to orbbase to calculate perpendicular baselines for all interferogram directories in the work folder

if start == "baselines":

	cwd = os.getcwd();

	proc_file_paths = [];

	contents = os.listdir(WorkPath);

	proc_files = [item for item in contents if ".proc" in item];

	cmd = "\ncd " + WorkPath + "\n";

	for proc_file in proc_files:
		if DataType.lower().find("tsx") > -1:
			cmd += "\nprocess_2pass.pl " + proc_file + " roi_prep orbbase\n";
		else:
			cmd += "\nprocess_2pass.pl " + proc_file + " raw orbbase\n"; 

	cmd += "\ncd " + cwd + "\n";

	subprocess.call(cmd,shell=True);

	start = "offsets";

	if start == end:
		logFile = open("pxlog.txt","a");
		logFile.write("\n***** pixelTrack.py for parameters \""+params_path+"\" - Started at \""+start+"\", ended at \""+end+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-start_time)));
		logFile.close();
		print("\nReached end step \"" + end + "\", exiting...\n");
		sys.exit();



# ***** STEP: offsets *****
# Runs ROI_PAC's process_2pass from orbbase to offsets for all interferogram directories in the work folder to find mean offset between the slcs for each pair

if start == "offsets":

	try: MaxBaseline
	except NameError:
		print("\nMaxBaseline not set in parameter file, using +/-500\n");
		MaxBaseline = "500";

	cwd = os.getcwd();

	cmd = "find " + WorkPath + " -name \"*baseline*.rsc\" -print";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	baseline_files = pipe.read().split();
	pipe.close();

	cmd = "";

	for i in range(0, len(baseline_files)):

		baseline_file = open(baseline_files[i].strip(),"r");

		while 1:

			line = baseline_file.readline();

			if not line:
				break;

			if line.find("P_BASE") > -1:

				baseline = line.split()[1];

				if abs(float(baseline)) > abs(float(MaxBaseline)):
					break;

				line = baseline_file.readline();

				if line and line.find("P_BASE") > -1:

					baseline = line.split()[1].strip();

					if not re.search("[^\.\d]", baseline):

						if abs(float(baseline)) > abs(float(MaxBaseline)):
							break;

				cmd += "\ncd " + WorkPath + "\n";

				if DataType.lower().find("tsx") > -1:
					cmd += "\nprocess_2pass.pl " + baseline_files[i].strip()[ : baseline_files[i].rfind("/")] + ".proc slcs offsets &\n";

				else:
					cmd += "\nprocess_2pass.pl " + baseline_files[i].strip()[ : baseline_files[i].rfind("/")] + ".proc orbbase offsets &\n";

				cmd += "\ncd " + cwd + "\n";

		baseline_file.close();

	subprocess.call(cmd,shell=True);

	start = "ampcor";

	if start == end:
		logFile = open("pxlog.txt","a");
		logFile.write("\n***** pixelTrack.py for parameters \""+params_path+"\" - Started at \""+start+"\", ended at \""+end+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-start_time)));
		logFile.close();
		print("\nReached end step \"" + end + "\", exiting...\n");
		sys.exit();



# ***** STEP: ampcor *****
# Pixel-tracking step, finds offsets between the two slcs for all interferogram directories in the work folder according to the criteria in the parameters file

if start == "ampcor": 

	try: rwin
	except NameError:
		print("\n***** WARNING, variable \"rwin\" not set in parameter file\nUsing default value of \"40\"");
		rwin = "40";

	try: awin
	except NameError:
		print("\n***** WARNING, variable \"awin\" not set in parameter file\nUsing default value of \"40\"");
		awin = "40";

	try: search_x
	except NameError:
		print("\n***** WARNING, variable \"search_x\" not set in parameter file\nUsing default value of \"40\"");
		search_x = "16";

	try: search_y
	except NameError:
		print("\n***** WARNING, variable \"search_y\" not set in parameter file\nUsing default value of \"40\"");
		search_y = "16";

	try: wsamp
	except NameError:
		print("\n***** WARNING, variable \"wsamp\" not set in parameter file\nUsing default value of \"4\"");
		wsamp = "4";

	try: numproc
	except NameError:
		print("\n***** WARNING, variable \"numproc\" not set in parameter file\nUsing default value of \"1\"");
		numproc = "1"; 

	ampcor(WorkPath, rwin, awin, search_x, search_y, wsamp, numproc);

	start = "make_unw"; 

	if start == end:
		logFile = open("pxlog.txt","a");
		logFile.write("\n***** pixelTrack.py for parameters \""+params_path+"\" - Started at \""+start+"\", ended at \""+end+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-start_time)));
		logFile.close();
		print("\nReached end step \"" + end + "\", exiting...\n");
		sys.exit();



# ***** STEP: make_unw *****
# Creates azimuth*.unw and range*.unw from the raw azimuth and range offsets generated by the ampcor step for all applicable interferogram directories in WorkPath, these results can be viewed using mdx

if start == "make_unw":

	try: rwin
	except NameError:
		print("\n***** WARNING, variable \"rwin\" not set in parameter file\nUsing default value of \"40\"");
		rwin = "40";

	try: awin
	except NameError:
		print("\n***** WARNING, variable \"awin\" not set in parameter file\nUsing default value of \"40\"");
		awin = "40";

	try: search_x
	except NameError:
		print("\n***** WARNING, variable \"search_x\" not set in parameter file\nUsing default value of \"40\"");
		search_x = "16";

	try: search_y
	except NameError:
		print("\n***** WARNING, variable \"search_y\" not set in parameter file\nUsing default value of \"40\"");
		search_y = "16";

	try: wsamp
	except NameError:
		print("\n***** WARNING, variable \"wsamp\" not set in parameter file\nUsing default value of \"4\"");
		wsamp = "4";

	try: numproc
	except NameError:
		print("\n***** WARNING, variable \"numproc\" not set in parameter file\nUsing default value of \"1\"");
		numproc = "1";

	makeUNW(WorkPath,rwin,awin,search_x,search_y,wsamp,Angle,DataType);

	start = "affine";

	if start == end:
		logFile = open("pxlog.txt","a");
		logFile.write("\n***** pixelTrack.py for parameters \""+params_path+"\" - Started at \""+start+"\", ended at \""+end+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-start_time)));
		logFile.close();
		print("\nReached end step \"" + end + "\", exiting...\n");
		sys.exit();



# ***** STEP: affine *****
# Runs ROI_PAC's make_geomap.pl to calculate the best-fit affine transformation between the SAR pairs and provided DEM for each applicable interferogram in WorkPath

if start == "affine":

	getAffineTrans(WorkPath);

	start = "geocode";

	if start == end:
		logFile = open("pxlog.txt","a");
		logFile.write("\n***** pixelTrack.py for parameters \""+params_path+"\" - Started at \""+start+"\", ended at \""+end+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-start_time)));
		logFile.close();
		print("\nReached end step \"" + end + "\", exiting...\n");
		sys.exit();



# ***** STEP: geocode *****
# Runs ROI_PAC's "geocode.pl" to use affine transformation calculated in "affine" step to geocode the azimuth*.unw and range*.unw files for all applicable pairs in WorkPath

if start == "geocode":

	geocode(WorkPath, rwin, awin, search_x, search_y, wsamp, orbit, DEM); 

	start = "";

	if start == end:
		logFile = open("pxlog.txt","a");
		logFile.write("\n***** pixelTrack.py for parameters \""+params_path+"\" - Started at \""+start+"\", ended at \""+end+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-start_time)));
		logFile.close();
		print("\nReached end step \"" + end + "\", exiting...\n");  
		sys.exit();


#*****OPTICAL*****

if start == "optical_raw":
	try:
		import pyhdf.SD;
		try: Band
		except NameError:
			print("\n***** WARNING, variable \"Band\" not set in parameter file\nUsing default band \"3N\"\n");
			Band = "3N";
		findHDFCmd = "\nfind "+WorkPath+" -name \"*.hdf\" -print\n";
		findHDFStream = subprocess.Popen(findHDFCmd);
		findHDFOutput = findHDFStream.read().split();
		findHDFStream.close();
		for fileName in findHDFOutput: 
			hdfFile = pyhdf.SD.SD(fileName);
			num_datasets = hdfFile.info()[0];
			for i in range(0,int(num_datasets)):
				ds = hdfFile.select(i);
				if ds.info()[0].find("ImageData") > -1:
					dim = ds.dim(0);
					samples = str(dim.info()[1]);
					dim2 = ds.dim(1);
					lines = str(dim2.info()[1]);
					if dim.info()[0].find("Band"+Band) > -1:
						out = ds[:];
						if not os.path.exists(WorkPath+"/band"+Band):
							os.mkdir(WorkPath+"/band"+Band);
						print(WorkPath+"/band"+Band+"/"+fileName[fileName.rfind("/"):fileName.rfind(".hdf")]+".b"+Band);
						outfile = open(WorkPath+"/band"+Band+fileName[fileName.rfind("/"):fileName.rfind(".hdf")]+".b"+Band, 'wb');
						out = numpy.array(out,numpy.float32);
						out.tofile(outfile);
						outfile.close();
						outfile = open(WorkPath+"/band"+Band+fileName[fileName.rfind("/"):fileName.rfind(".hdf")]+".b"+Band+".met","w");
						outfile.write("samples="+samples+"\n");
						outfile.write("lines="+lines+"\n");
						outfile.close();
				ds.endaccess()
			hdfFile.end();
	except ImportError:
		print("\n***** ERROR, \"pyhdf\" module not found, cannot perform this step\n"); 
	start = "";
	if start == end:
		logFile = open("pxlog.txt","a");
		logFile.write("\n***** pixelTrack.py for parameters \""+params_path+"\" - Started at \""+start+"\", ended at \""+end+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-start_time)));
		logFile.close();
		print("\nReached end step \"" + end + "\", exiting...\n");
		sys.exit();

if start == "gausshp_filt":
	bandDirsCmd = "\nfind " + WorkPath + " -name \"band*\" -print\n";
	bandDirsStream = subprocess.Popen(bandDirsCmd);
	bandDirs = bandDirsStream.read().split();
	bandDirsStream.close();
	bandFiles = [];
	for bandDir in bandDirs:
		if os.path.isdir(bandDir):
			bandDirFiles = os.listdir(bandDir);
			for bandFile in bandDirFiles:
				if re.search("\.b.*\.met",bandFile) > -1:
					bandFiles.append(bandDir+"/"+bandFile[0:bandFile.rfind(".met")]);
	for fileName in bandFiles:
		samples = "";
		lines = "";
		metfile = open(fileName+".met","r");
		for line in metfile:
			if line.find("samples") > -1:
				samples = line.strip().split("=")[1];
			if line.find("lines") > -1:
				lines = line.strip().split("=")[1];
		metfile.close();
		infile = open(fileName,"rb");
		indat = scipy.fromfile(infile,scipy.float32,-1).reshape(int(samples),int(lines));
		infile.close();
		gausshpkernel = numpy.asarray([[-0.0000,-0.0007,-0.0024,-0.0007,-0.0000],[-0.0007,-0.0314,-0.1131,-0.0314,-0.0007],[-0.0024,-0.1131,0.5933,-0.1131,-0.0024],[-0.0007,-0.0314,-0.1131,-0.0314,-0.0007],[-0.0000,-0.0007,-0.0024,-0.0007,-0.0000]]);
		#gausshpkernel = numpy.asarray([[-0.0000,-0.0000,-0.0000,-0.0000,-0.0000],[-0.0000,-0.0000,1.0000,-0.0000,-0.0000],[-0.0000,1.0000,-4.0000,1.0000,-0.0000],[-0.0000,-0.0000,1.0000,-0.0000,-0.0000],[-0.0000,-0.0000,-0.0000,-0.0000,-0.0000]]);
		temp = gausshpfilt(indat,gausshpkernel);
		outfile = open(fileName[0:fileName.rfind(".b")]+"_ghp"+fileName[fileName.rfind(".b"):], 'wb');
		out = numpy.array(temp,numpy.float32);
		out.tofile(outfile);
		outfile.close();
	start = "";
	if start == end:
		logFile = open("pxlog.txt","a");
		logFile.write("\n***** pixelTrack.py for parameters \""+params_path+"\" - Started at \""+start+"\", ended at \""+end+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-start_time)));
		logFile.close();
		print("\nReached end step \"" + end + "\", exiting...\n");
		sys.exit();


if start == "get_xyzs":
	try: MATLAB
	except NameError:
		print("\n***** ERROR, variable \"MATLAB\" not set in parameter file\nMust specify MATLAB directory\n");
		sys.exit();
	findAmpcorFilesCmd = "find " + WorkPath + " -name \"*mp*.in\" -print";
	findAmpcorCmdStream = subprocess.Popen(findAmpcorFilesCmd);
	findAmpcorOutput = findAmpcorCmdStream.read();
	findAmpcorCmdStream.close();
	ampcorFiles = findAmpcorOutput.split();
	confirmedAmpcorFiles = [];
	for i in range(0,len(ampcorFiles)):
		ampcorFile = open(ampcorFiles[i],"r");
		ampcorFileName = ampcorFiles[i][0:ampcorFiles[i].rfind(".")];
		ampcorPath = ampcorFiles[i][0:ampcorFiles[i].rfind("/")];
		if not (os.path.exists(ampcorFileName + ".off")):
			continue;
		while 1:
			line = ampcorFile.readline();
			if not line:
				break;
			if line.lower().find("ampcor") > -1:
				confirmedAmpcorFiles.append(ampcorFiles[i]);
				sedCmd = "sed -e '/\*/d' " + ampcorFileName + ".off > " + ampcorPath + "/temp";
				sedCmdStream = subprocess.Popen(sedCmd);
				sedCmdStream.close();
				diffCmd = "diff " + ampcorFileName + ".off " + ampcorPath + "/temp";
				diffCmdStream = subprocess.Popen(diffCmd);
				diffCmdOutput = diffCmdStream.read();
				diffCmdStream.close();
				if diffCmdOutput == "":
					removeTmpCmd = "rm " + ampcorPath + "/temp";
					removeTmpCmdStream = subprocess.Popen(removeTmpCmd);
					removeTmpCmdStream.close();
				else:
					mvCmd = "\nmv " + ampcorFileName + ".off " + ampcorFileName + ".off.old\nmv " + ampcorPath + "/temp " + ampcorFileName + ".off\n";
					mvCmdStream = subprocess.Popen(mvCmd);
					mvCmdStream.close();
				createMatlabGetXYZ(MATLAB + "/generic_getxyzs.m",ampcorFiles[i]);
				break;
	start = "";
	if start == end:
		logFile = open("pxlog.txt","a");
		logFile.write("\n***** pixelTrack.py for parameters \""+params_path+"\" - Started at \""+start+"\", ended at \""+end+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-start_time)));
		logFile.close();
		print("\nReached end step \"" + end + "\", exiting...\n");
		sys.exit();

if start == "profiles":
	start = "";
	generateProfiles(WorkPath);
	if start == end:
		logFile = open("pxlog.txt","a");
		logFile.write("\n***** pixelTrack.py for parameters \""+params_path+"\" - Started at \""+start+"\", ended at \""+end+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-start_time)));
		logFile.close();
		print("\nReached end step \"" + end + "\", exiting...\n");
		sys.exit();

if start == "kml":
	start = "";
	generatePNGs(WorkPath);
	getGRDCorners(WorkPath);
	generateKML(WorkPath);
	if start == end:
		logFile = open("pxlog.txt","a");
		logFile.write("\n***** pixelTrack.py for parameters \""+params_path+"\" - Started at \""+start+"\", ended at \""+end+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-start_time)));
		logFile.close();
		print("\nReached end step \"" + end + "\", exiting...\n");
		sys.exit();


