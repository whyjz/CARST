#!/usr/bin/python


# Author: Andrew Kenneth Melkonian
# All rights reserved

# modified by whyjay 2016/5/12

#import calendar;
#import fileinput;
from makeAzo import *;
import math;
import numpy;
import os;
#from pxfuncs import *;
import pylab;
import re;
import scipy;
import shutil;
import subprocess;
#import sys;
#import time;




def adjustPhase(radar_path, wavelength, width):

	radar_dir = ".";	

	index = radar_path.rfind("/");

	if index > -1:
		radar_dir = radar_path[ : index];

	radar_name = radar_path[index + 1 : ];

	new_radar_path = radar_dir + "/new_" + radar_name;
	
	infile         = open(radar_path, "rb");
	radar_unw_data = scipy.matrix(numpy.fromfile(infile,numpy.float32, -1)).reshape(int(width), -1);
	radar_unw_data = radar_unw_data * float(wavelength) / 4 / numpy.pi;
	infile.close();

	radar_unw_data = scipy.matrix(radar_unw_data,scipy.float32);
	radar_unw_data.tofile(new_radar_path);
	radar_unw_data = None;

	return(new_radar_path);



def ampcor(path, rwin, awin, search_x, search_y, wsamp, numproc):

	cwd = os.getcwd();

	import glob;

	cull_paths = glob.glob(path + "/int*/*_cull.off");

	for i in range(0,len(cull_paths)):

		cull_name = cull_paths[i].strip()[cull_paths[i].rfind("/")+1:];
		cull_dir = cull_paths[i][:cull_paths[i].rfind("/")];

		if not re.search("\d{6}",cull_name):
			continue;

		already_processed=False;

		contents=os.listdir(cull_dir);

		for item in contents:
			if re.search("azo_" + wsamp + "_r" + rwin + "x" + awin + "_s" + search_x + "x" + search_y,item) > -1:
				already_processed=True;
				break;

		if already_processed:
			print("\n***** WARNING, " + cull_dir + " contains \"" + item +"\", \"ampcor\" step already run, exiting...\n");
			continue;

		index1 = re.search("\d{6}",cull_name).start(0);
		index2 = re.search("\d{6}",cull_name).end(0);
		index3 = re.search("\d{6}",cull_name[index2:]).start(0)+index2;
		index4 = re.search("\d{6}",cull_name[index2:]).end(0)+index2;

		date2 = cull_name[index1:index2];
		date1 = cull_name[index3:index4];


		slc1 = path + "/" + date1 + "/" + date1 + ".slc";

		if not os.path.exists(slc1):
			print("\n***** ERROR, could not find \"" + date1 + ".slc\" in \"" + path + "/" + date1 + "/\"\n");
			break;


		slc2 = path + "/" + date2 + "/" + date2 + ".slc";

		if not os.path.exists(slc2):
			print("\n***** ERROR, could not find \"" + date2 + ".slc\" in \"" + path + "/" + date2 + "/\"\n");
			break;


		slc1_rsc_file = open(slc1 + ".rsc","r");

		while 1:

			line = slc1_rsc_file.readline();

			if not line:
				break;

			elif line.find("WIDTH") > -1:
				width = line.split()[1].strip();

		slc1_rsc_file.close();

		amp1 = cull_dir + "/" + date1 + ".amp";
		amp2 = cull_dir + "/" + date2 + ".amp";

		if not os.path.exists(amp1):
			cmd = "\ncpx2mag_phs " + slc1 + " " + cull_dir + "/" + date1 + ".amp " + cull_dir + "/" + date1 + ".phs " + width + "\n";
			cmd += "\ncp -pr " + slc1 + ".rsc " + cull_dir + "/" + date1 + ".amp.rsc\n";
			cmd += "\nrm " + cull_dir + "/" + date1 + ".phs\n";
			subprocess.call(cmd,shell=True);


		slc2_rsc_file = open(slc2 + ".rsc","r");

		while 1:

			line = slc2_rsc_file.readline();

			if not line:
				break;

			elif line.find("WIDTH") > -1:
				width = line.split()[1].strip();

		slc2_rsc_file.close();

		if not os.path.exists(amp2):
			cmd = "\ncpx2mag_phs " + slc2 + " " + cull_dir + "/" + date2 + ".amp " + cull_dir + "/" + date2 + ".phs " + width + "\n";
			cmd += "\ncp -pr " + slc2 + ".rsc " + cull_dir + "/" + date2 + ".amp.rsc\n";
			cmd += "\nrm " + cull_dir + "/" + date2 + ".phs\n";
			subprocess.call(cmd,shell=True);

		cmd = "\ncp -pr azo_real.pl " + cull_dir + "\n";
		subprocess.call(cmd,shell=True);

		cmd = "\ncd " + cull_dir + "\n";
		cmd += "\nperl azo_real.pl " + amp2 + " " + amp1 + " " + cull_name[0:cull_name.rfind(".")] + " " + cull_name[index1:index4] + "_azo_" + wsamp + " " + rwin + " " + awin + " " + search_x + " " + search_y + " " + wsamp + " " + numproc + " &\n";
		cmd += "\ncd " + cwd + "\n";
		print(cmd);
		#subprocess.call(cmd,shell=True);
	return;



def makeUNW(path, rwin, awin, search_x, search_y, wsamp, angle, data_type):

	cmd = "\nfind " + path + " -name \"*azo_" + wsamp + "_r" + rwin + "x" + awin + "_s" + search_x + "x" + search_y + "*.off\" -print\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	ampoff_paths = pipe.read().split();
	pipe.close();

	ampoff_dirs={};
	cat_cmds={};

	angles = {};
	max_inc_angle = "";
	min_inc_angle = "";

	if data_type.lower().find("tsx") > -1:

		cmd = "\nfind " + path + " -name \"T*X*.xml\"\n";
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


	for i in range(0,len(ampoff_paths)):
	
		ampoff_dir = ampoff_paths[i].strip()[0:ampoff_paths[i].strip().rfind("/")];

		if ampoff_dir not in ampoff_dirs:
			ampoff_dirs[ampoff_dir] = ampoff_paths[i];
			cat_cmds[ampoff_dir] = "\ncat " + ampoff_paths[i];

		else:
			cat_cmds[ampoff_dir] += " " + ampoff_paths[i];

	
	for ampoff_dir in cat_cmds:

		cmd = cat_cmds[ampoff_dir];
		elements = cmd.split();

		if len(elements) < 3:
			continue;

		else:
			if not re.search("_\d\.off",elements[1]):
				ampoff_dirs[ampoff_dir] = elements[1];
				continue;

			else:
				composite_ampoff_path = elements[1][:re.search("_\d\.off",elements[1]).start(0)] + ".off";
				ampoff_dirs[ampoff_dir]=composite_ampoff_path;
				
				if os.path.exists(composite_ampoff_path):
					continue;

				cat_cmds[ampoff_dir] += " > " + composite_ampoff_path + "\n";
				print("\n***** pixelTrack - step \"make_unw\" - running cat to compose ampcor results into single file...\n");
				subprocess.call(cat_cmds[ampoff_dir],shell=True);


	for ampoff_dir in ampoff_dirs:

		ampoff_dir_contents = os.listdir(ampoff_dir);

		already_done = False;
		item="";

		for i in range(0,len(ampoff_dir_contents)):

			item = ampoff_dir_contents[i];

			if re.search(".*azimuth_r" + rwin + "x" + awin + "_s" + search_x + "x" + search_y + "_" + str(int(rwin)/int(wsamp)) + "rlks.unw",item) or \
			   re.search(".*range_r" + rwin + "x" + awin + "_s" + search_x + "x" + search_y + "_" + str(int(rwin)/int(wsamp)) + "rlks.unw",item):
				already_done=True;
				break;

		if already_done:
			print("\n****** \"" + item +"\" already exists in \"" + ampoff_dir + "\", make_unw step likely already done for this directory, skipping...\n");
			continue;

		ampoff_path = ampoff_dirs[ampoff_dir];

		date = ampoff_path[re.search("/\d{6}[\-_]\d{6}",ampoff_path).start(0) + 1 : re.search("/\d{6}[\-_]\d{6}", ampoff_path).start(0) + 7];

		cmd = "\nls " + ampoff_path[0:ampoff_path.rfind("azo")+3]+"*.off.rsc\n";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		ampoff_rsc_paths = pipe.read().split();
		pipe.close();

		if len(ampoff_rsc_paths) < 1:
			print("\n***** WARNING, could not find any azo rsc file in \"" + amcporDir + "\", skipping these results\n");
			break; 

		ampoff_rsc_path = ampoff_rsc_paths[0];

		da_p = "";
		r_e = "";
		p_h = "";
		dr = "";
		endRefSample = "";
		endRefLine = "";

		ampoff_rsc_file = open(ampoff_rsc_path,"r");

		while 1:

			line = ampoff_rsc_file.readline();

			if not line:
				break;

			elif line.find("RANGE_PIXEL_SIZE") > -1:
				dr = line.split()[1].strip();

			elif line.find("FILE_LENGTH") > -1:
				endRefLine = line.split()[1].strip();

			elif line.find("WIDTH") > -1:
				endRefSample = line.split()[1].strip();

			elif line.find("EARTH_RADIUS") > -1:
				r_e = line.split()[1].strip();

			elif re.search("^HEIGHT\s+",line):
				p_h = line.split()[1].strip();

			elif line.find("AZIMUTH_PIXEL_SIZE") > -1:
				da_p = line.split()[1].strip();

		ampoff_rsc_file.close();

		if da_p == "":
			print("\n***** WARNING, could not find parameter \"FILE_LENGTH\" in \"" + ampoff_rsc_path[0].strip() + "\", skipping these results\n");
			break;

		if da_p == "":
			print("\n***** WARNING, could not find parameter \"WIDTH\" in \"" + ampoff_rsc_path[0].strip() + "\", skipping these results\n");
			break;

		if da_p == "":
			print("\n***** WARNING, could not find parameter \"AZIMUTH_PIXEL_SIZE\" in \"" + ampoff_rsc_path[0].strip() + "\", skipping these results\n");
			break;

		if r_e == "":
			print("\n***** WARNING, could not find parameter \"EARTH_RADIUS\" in \"" + ampoff_rsc_path[0].strip() + "\", skipping these results\n");
			break;

		if p_h == "":
			print("\n***** WARNING, could not find parameter \"HEIGHT\" in \"" + ampoff_rsc_path[0].strip() + "\", skipping these results\n");
			break;

		if dr == "":
			print("\n***** WARNING, could not find parameter \"RANGE_PIXEL_SIZE\" in \"" + ampoff_rsc_path[0].strip() + "\", skipping these results\n");
			break;

		input_angle = angle;

		if data_type.lower().find("tsx") > -1:
			input_angle = angles[date];

		print("\n***** pixelTrack - step \"make_unw\" - running makeAzo in " + ampoff_dir + " to generate azimuth and range unw files ...\n");

		makeAzo(ampoff_path, float(da_p), float(r_e), float(p_h), float(dr), float(input_angle), int(wsamp), int(rwin), int(awin), search_x, search_y, int(endRefSample), int(endRefLine));

		cwd = os.getcwd();

		if not os.path.exists(ampoff_dir+"/azimuth_" + rwin + "x" + awin + "_" + str(int(rwin)/int(wsamp)) + "rlks.unw.rsc"):
			date = ampoff_path[re.search("/\d{6}[\-_]\d{6}",ampoff_path).start(0)+1:re.search("/\d{6}[\-_]\d{6}",ampoff_path).start(0)+7];
			cmd = "";

			if not os.path.exists(ampoff_dir + "/" + date + "_" + str(int(rwin)/int(wsamp)) + "rlks.slc.rsc"):
				cmd += "\nlook.pl " + ampoff_dir + "/" + date + ".slc " + str(int(rwin)/int(wsamp)) + " " + str(int(awin)/int(wsamp)) + "\n";

			cmd += "\ncp -p " + ampoff_dir + "/" + date + "_" + str(int(rwin)/int(wsamp)) + "rlks.slc.rsc " + ampoff_dir + "/azimuth_r" + rwin + "x" + awin + "_s" + search_x + "x" + search_y + "_" + str(int(rwin)/int(wsamp)) + "rlks.unw.rsc\n";
			cmd += "\ncp -p " + ampoff_dir + "/" + date + "_" + str(int(rwin)/int(wsamp)) + "rlks.slc.rsc " + ampoff_dir + "/range_r" + rwin + "x" + awin + "_s" + search_x + "x" + search_y + "_" + str(int(rwin)/int(wsamp)) + "rlks.unw.rsc\n";
			cmd += "\ncp -p " + ampoff_dir + "/" + date + "_" + str(int(rwin)/int(wsamp)) + "rlks.slc.rsc " + ampoff_dir + "/snr_r" + rwin + "x" + awin + "_s" + search_x + "x" + search_y + "_" + str(int(rwin)/int(wsamp)) + "rlks.unw.rsc\n";
			subprocess.call(cmd,shell=True);

	return;



def beamTable():

	beam_angle["ST1"] = "23.7";
	beam_angle["ST2"] = "27.7";
	beam_angle["ST3"] = "33.7";
	beam_angle["ST4"] = "36.6";
	beam_angle["ST5"] = "39.4";
	beam_angle["ST6"] = "44.0";
	beam_angle["ST7"] = "47.2";
	beam_angle["F1"]  = "38.5";
	beam_angle["F2"]  = "40.8";
	beam_angle["F3"]  = "42.9";
	beam_angle["F4"]  = "44.8";
	beam_angle["F5"]  = "46.6";
	
	return;


#def densifyAmpmag(path, date):
#
#	if 
#
#	return;


def findAzimuthPixelSize(path, date, orbit):

	cwd = os.getcwd();

	cmd = "find " + path + " -name \"" + date + ".slc.rsc\" -print";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	slc_rsc_paths = pipe.read().split();
	pipe.close();

	slc_rsc_path = "";

	if len(slc_rsc_paths) < 1:

		cmd = "find " + path + " -name \"" + date + ".raw\" -print";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		raw_paths = pipe.read().split();
		pipe.close();

		cmd = "find " + path + " -name \"hdr*"+date+"*.rsc\" -print";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		hdr_paths = pipe.read().split();
		pipe.close();

		if len(raw_paths) < 1:
			print("\n***** WARNING, could not find \"" + date + ".raw\", necessary to determine azimuth pixel size\n");
			return "-1";

		raw_path = raw_paths[0];

		if not os.path.exists(raw_path + ".rsc"):
			print("\n***** WARNING, could not find \"" + date + ".raw.rsc\", necessary to determine azimuth pixel size\n");
			return "-1";

		if len(hdr_paths) < 1:
			print("\n***** WARNING, could not find \"hdr*" + date + "*.rsc\", necessary to determine azimuth pixel size\n");
			return "-1";

		hdr_path = hdr_paths[0];

		cmd  = "\nmkdir " + path + "/" + date + "_APS\n";
		cmd += "\ncd " + path + "/" + date + "_APS\n";
		cmd += "\nln -s " + raw_path + " " + raw_path[raw_path.rfind("/") + 1 : ] + "\n";
		cmd += "\nln -s " + raw_path + ".rsc " + raw_path[raw_path.rfind("/") + 1 : ] + ".rsc\n";
		cmd += "\nln -s " + hdr_path + " " + hdr_path[hdr_path.rfind("/") + 1 : ]+"\n";
		cmd += "\ndopav.pl . . " + date + " " + date + " \"\"\n";
		cmd += "\nroi_prep.pl " + date + " " + orbit + " " + date + "-" + date + "\n";
		cmd += "\ncd " + cwd + "\n";
		subprocess.call(cmd,shell=True);
		
		slc_rsc_path = path + "/" + date + "_APS/" + date + ".slc.rsc";

	else:
		slc_rsc_path = slc_rsc_paths[0];


	slc_rsc_file = open(slc_rsc_path,"r");

	while 1:

		line = slc_rsc_file.readline();

		if not line:
			break;

		if line.find("AZIMUTH_PIXEL_SIZE") > -1:

			slc_rsc_file.close();

			if os.path.exists(path + "/" + date + "_APS"):
				shutil.rmtree(path + "/" + date + "_APS");

			return line[re.search("\d+\.*\d*",line).start(0) : re.search("\d+\.*\d*",line).end(0)];

	slc_rsc_file.close();
	
	print("\n***** WARNING, unable to determine azimuth pixel size, using default value of \"5\"\n");
	shutil.rmtree(path + "/" + date + "_APS");

	return "-1";



def GCF(num):
	temp = num[0];
	for i in range(len(num)-1):
		num1 = temp;
		num2 = num[i+1];
		if num1 < num2:
			num1,num2=num2,num1;
		while num1 - num2:
			num3 = num1 - num2;
			num1 = max(num2,num3);
			num2 = min(num2,num3);
		temp = num1;
	return num1;



def has_value(self, value):
	return value in self.values();



def LCM(num):
	temp = num[0];
	for i in range(len(num)-1):
		num1 = temp;
		num2 = num[i+1];
		t_gcf = GCF([num1,num2]);
		temp = t_gcf * num1/t_gcf * num2/t_gcf;
	return temp;



def makeProcFile(path, date2, date1, angle, dem, orbit):

	proc_file_path = path + "/int_" + date2 + "_" + date1 + ".proc";

	print(proc_file_path);

	if os.path.exists(proc_file_path):
		print("\n\"" + proc_file_path + "\" already exists, skipping\n");
		return;

	int_path = path + "/int_" + date2 + "_" + date1;

	proc_file = open(proc_file_path,"w");
	proc_file.write("SarDir1=" + path + "/" + date2 + "\n");
	proc_file.write("SarDir2=" + path + "/" + date1 + "\n");
	proc_file.write("IntDir=" + int_path + "\n");
	proc_file.write("SimDir=" + int_path + "/SIM\n");
	proc_file.write("GeoDir=" + int_path + "/GEO\n");
	proc_file.write("flattening=orbit\n");
	proc_file.write("DEM=" + dem + "\n");
	proc_file.write("OrbitType=" + orbit + "\n");
	proc_file.write("Rlooks_sim=1\n");
	proc_file.write("Rlooks_unw=1\n");
	proc_file.write("Rlooks_geo=1\n");
	proc_file.write("Rlooks_int=1\n");
	pixelRatio = "-1";

	if re.search("\d+", angle):

		azimuth_pixel_size = findAzimuthPixelSize(path, date1, orbit);
		range_pixel_size = "-1";

		if azimuth_pixel_size != "-1":

			cmd = "\nfind " + path + " -name \"" + date1 + ".raw.rsc\" -print\n";
			pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
			raw_rsc_paths = pipe.read().split();
			pipe.close();

			if len(raw_rsc_paths) > 0:

				raw_rsc_file = open(raw_rsc_paths[0],"r");

				while 1:

					line = raw_rsc_file.readline();

					if not line:
						break;

					if line.find("RANGE_PIXEL_SIZE") > -1:
						raw_rsc_file.close();
						range_pixel_size = line[re.search("\d+\.*\d*",line).start(0) : re.search("\d+\.*\d*",line).end(0)];
						pixel_ratio = str(round(float(range_pixel_size) / math.sin(math.radians(float(angle))) / float(azimuth_pixel_size)));
						pixel_ratio = pixel_ratio[0 : pixel_ratio.rfind(".")];
						break;

				raw_rsc_file.close();

	if pixel_ratio != "-1":
		proc_file.write("pixel_ratio=" + pixel_ratio + "\n");

	proc_file.close();



def getPixelRatios(path):
	return; 



def readProcFile(path,date2,date1):
	procCmd = "find " + path + " -name \"*" + date2 + "*" + date1 + "*.proc\" -print";
	procStream = subprocess.Popen(procCmd);
	procOutput = procStream.read();
	procFilePath = procOutput.strip().split();
	if len(procFilePath) < 1:
		print("\n***** ERROR, no proc file found for dates \"" + date2 + ", " + date1 + "\" in \"" + path + "\"\n");
		sys.exit();
	if len(procFilePath) > 1:
		print("\n***** WARNING, found more than one proc file for dates \"" + date2 + ", " + date1 + "\", using \"" + procFilePath[0] + "\"\n");
	procStream.close();
	procFile = open(procFilePath[0],"r");
	procHash = {};
	while 1:
		line = procFile.readline();
		if not line:
			break;
		line = line.strip();
		name = "";
		value = "";
		elements = line.split("=");
		if len(elements) < 2 or len(elements[0]) < 1 or len(elements[1]) < 1:
			print("\n***** ERROR, proc file line format is \"varName=varValue\", \"" + line + "\" does not conform to this format\n");
			sys.exit();
		procHash[elements[0]] = elements[1];
	procFile.close();
	return procHash;

def gausshpfilt(data,kernel):
		padSize = numpy.size(kernel,axis=0) / 2;
		temp = numpy.zeros((numpy.size(data,axis=0)+2*padSize,numpy.size(data,axis=1)+2*padSize));
		#fill temp with data values
		for i in range(padSize,numpy.size(temp,axis=0)-padSize):
			for j in range(padSize,numpy.size(temp,axis=1)-padSize):
				temp[i,j] = data[i-padSize,j-padSize];
		#pad left
		for i in range(0,padSize):
			for j in range(padSize,padSize+numpy.size(data,axis=0)):
				temp[j,padSize-1-i] = data[j-padSize,i];
		#pad top
		for i in range(0,padSize):
			for j in range(padSize,padSize+numpy.size(data,axis=1)):
				temp[padSize-1-i,j] = data[i,j-padSize]; 
		#pad right
		for i in range(0,padSize):
			for j in range(padSize,padSize+numpy.size(data,axis=0)):
				temp[j,numpy.size(temp,axis=1)-padSize+i] = data[j-padSize,numpy.size(data,axis=1)-1-i];
		#pad bottom
		for i in range(0,padSize):
			for j in range(padSize,padSize+numpy.size(data,axis=1)):
				temp[numpy.size(temp,axis=0)-padSize+i,j] = data[numpy.size(data,axis=0)-1-i,j-padSize];
		#fill top-left corner
		for i in range(0,padSize):
			for j in range(0, padSize):
				temp[padSize-i-1,padSize-j-1] = int((temp[padSize-i-1,padSize-j] + temp[padSize-i,padSize-j-1]) / 2);
		#fill top-right corner
		for i in range(0,padSize):
			for j in range(0, padSize):
				temp[padSize-i-1,numpy.size(temp,axis=1)-padSize+j] = int((temp[padSize-i-1,numpy.size(temp,axis=1)-padSize+j-1] + temp[padSize-i,numpy.size(temp,axis=1)-padSize+j]) / 2);
		#fill bottom-right corner
		for i in range(0,padSize):
			for j in range(0, padSize):
				temp[numpy.size(temp,axis=0)-padSize+i,numpy.size(temp,axis=1)-padSize+j] = int((temp[numpy.size(temp,axis=0)-padSize+i,numpy.size(temp,axis=1)-padSize+j-1] + temp[numpy.size(temp,axis=0)-padSize+i-1,numpy.size(temp,axis=1)-padSize+j]) / 2);
		#fill bottom-left corner
		for i in range(0,padSize):
			for j in range(0, padSize):
				temp[numpy.size(temp,axis=0)-padSize+i,padSize-j-1] = (temp[numpy.size(temp,axis=0)-padSize+i,padSize-j] + temp[numpy.size(temp,axis=0)-padSize+i-1,padSize-j-1]) / 2;
		#perform convolution
		ghp_data = numpy.zeros((numpy.size(data,axis=0),numpy.size(data,axis=1)));
		for i in range(numpy.size(ghp_data,axis=0)):
			for j in range(numpy.size(ghp_data,axis=1)):
				ghp_data[i,j] = numpy.sum(kernel*temp[i:i+numpy.size(kernel,axis=0),j:j+numpy.size(kernel,axis=1)]);
		return ghp_data;



def geocode(path, rwin, awin, search_x, search_y, wsamp, orbit, dem_path):

	import fnmatch;

	cwd = os.getcwd();

	azo_unw_paths = [];

	for root, dirnames, filenames in os.walk(path):

		for filename in fnmatch.filter(filenames, "*.unw"):

			if re.search("r" + rwin + "x" + awin + "_s" + search_x + "x" + search_y + "_" + str(int(rwin) / int(wsamp)), filename):
				azo_unw_paths.append(root + "/" + filename);

	ld_range   = str(int(rwin) / int(wsamp));
	ld_azimuth = str(int(awin) / int(wsamp));

	for azo_unw_path in azo_unw_paths:

		index      = re.search("\d{6}_\d{6}", azo_unw_path).start(0);
		later_date = azo_unw_path[index : index + 6];
		early_date = azo_unw_path[index + 7 : index + 13];

		print(azo_unw_path);

		azo_unw_dir = ".";

		index = azo_unw_path.rfind("/");

		if index > -1:
			azo_unw_dir = azo_unw_path[ : index];

		azo_unw_name = azo_unw_path[index + 1 : ];

		os.chdir(azo_unw_dir);

		geo_unw     = "geo_" + azo_unw_name[ : azo_unw_name.find("_")] + "_" + later_date + "-" + early_date + "_r" + rwin + "x" + awin + "_s" + search_x + "x" + search_y + "_" + ld_range + "rlks.unw";

		if os.path.exists(geo_unw):
			print("\n**** WARNING, \"" + geo_unw + "\" already exists in \"" + azo_unw_dir + "\", skipping " + azo_unw_name + "...\n");

		elif geo_unw.find("range") > -1 and os.path.exists(geo_unw.replace("range", "adj_range")):
			print("\n**** WARNING, \"" + geo_unw.replace("range", "adj_range") + "\" already exists in \"" + azo_unw_dir + "\", skipping " + azo_unw_name + "...\n");
			
		radar_name     = "radar_" + orbit + ".unw";
		radar_rsc_name = radar_name + ".rsc";

		if not os.path.exists(radar_name):
			print("\n**** WARNING, \"" + radar_name + "\" not found in \"" + azo_unw_dir + "\", skipping range ramp-removal for this pair...\n");

		if not os.path.exists(radar_rsc_name):
			print("\n***** WARNING, \"" + radar_rsc_name + "\" not found in \"" + azo_unw_dir + "\", skipping range ramp-removal for this pair...\n");

		if re.search("^blalbalbrange", azo_unw_name) and os.path.exists(radar_name) and os.path.exists(radar_name + ".rsc"):

			cmd = "\nlook.pl " + radar_name + " " + ld_range + " " + ld_azimuth + "\n";
			subprocess.call(cmd, shell=True);

			radar_ld_name = "radar_" + orbit + "_" + ld_range + "rlks";
			radar_ld_unw  = "radar_" + orbit + "_" + ld_range + "rlks.unw";

			width      = "";
			wavelength = "";

			radar_rsc_file = open(radar_ld_unw + ".rsc", "r");

			while 1:

				line = radar_rsc_file.readline();

				if not line:
					break;

				if line.find("WIDTH") > -1:

					elements = line.split();
					width    = elements[1];

				if line.find("WAVELENGTH") > -1:

					elements   = line.split();
					wavelength = elements[1];

			radar_rsc_file.close();

			if width == "":
				print("\n***** WARNING, could not find \"WIDTH\" in \"" + radar_ld_unw + ".rsc\", skipping range ramp-removal for \"" + azo_unw_dir + "\"...\n");
				continue;

			if wavelength == "":
				print("\n***** WARNING, could not find \"WAVELENGTH\" in \"" + radar_ld_unw + ".rsc\", skipping range ramp-removal for \"" + azo_unw_dir + "\"...\n");
				continue;

			cmd = "\nrmg2mag_phs " + radar_ld_unw + " " + radar_ld_name + ".mag " + radar_ld_name + ".phs " + width + "\n";
			subprocess.call(cmd, shell=True);

			adj_radar_ld_phs = adjustPhase(radar_ld_name + ".phs", str(100 * float(wavelength)), width);

			cmd = "\nmag_phs2rmg " + radar_ld_name + ".mag " + adj_radar_ld_phs + " " + radar_ld_unw + " " + width + "\n";
			subprocess.call(cmd, shell=True);

			adj_range_unw_name = "adj_" + azo_unw_name;

			cmd = "\nadd_rmg.pl " + azo_unw_name + " " + radar_ld_unw + " " + adj_range_unw_name + " -1 1\n";
			subprocess.call(cmd, shell=True);

			azo_unw_name = adj_range_unw_name;

		cmd = "";

		if not os.path.exists(azo_unw_dir + "/" + later_date + "_" + ld_range + "rlks.slc.rsc"):
			cmd += "\nlook.pl " + later_date + ".slc " + ld_range + " " + ld_azimuth + "\n";

		cmd += "\ncp -pr " + later_date + "_" + ld_range + "rlks.slc.rsc " + azo_unw_path + ".rsc\n";


		cmd += "\nmake_geomap.pl ./GEO " + azo_unw_name + " azm.trans " + orbit + " " + dem_path + " " + later_date + "-" + early_date + "_SIM.aff " + ld_range + " " + later_date + " yes ../SIM\n";
		cmd += "\ngeocode.pl ./GEO/azm.trans " + azo_unw_name  + " geo_" + azo_unw_name[ : azo_unw_name.find("_")] + "_" + later_date + "-" + early_date + "_r" + rwin + "x" + awin + "_s" + search_x + "x" + search_y + "_" + ld_range + "rlks.unw\n";
		print(cmd)        # whyjay modified
		subprocess.call(cmd,shell=True);

		os.chdir(cwd);

	return;



def generateProfiles(path):
	currentDir = os.getcwd();
	profilesCmd = "find " + path + " -name \"*.distance\" -print";
	profilesStream = subprocess.Popen(profilesCmd);
	profilesOutput = profilesStream.read();
	profilesStream.close();
	profiles = profilesOutput.split();
	xyzCmd = "find " + path + " -name \"northxyz.txt\" -print";
	xyzStream = subprocess.Popen(xyzCmd);
	xyzOutput = xyzStream.read();
	xyzStream.close();
	xyzCmd = "find " + path + " -name \"eastxyz.txt\" -print";
	xyzStream = subprocess.Popen(xyzCmd);
	xyzOutput = xyzOutput + xyzStream.read();
	xyzStream.close();
	xyzCmd = "find " + path + " -name \"magxyz.txt\" -print";
	xyzStream = subprocess.Popen(xyzCmd);
	xyzOutput = xyzOutput + xyzStream.read();
	xyzStream.close();
	xyzFileList = xyzOutput.split();
	for i in range(0,len(xyzFileList)):
		xyzPath = xyzFileList[i].strip()[0:xyzFileList[i].strip().rfind("/")];
		xyzFileName = xyzFileList[i].strip()[xyzFileList[i].strip().rfind("/")+1:];
		xyzName = xyzFileName[0:xyzFileName.find(".")];
		gridCmd = "";
		if not os.path.exists(xyzPath + "/" + xyzName + ".grd"):
			gridCmd = gridCmd + "\npython grid.py " + xyzFileList[i].strip() + "\n";
			gridCmdStream = subprocess.Popen(gridCmd);
			gridCmdOutput = gridCmdStream.read();
			gridCmdStream.close();
		#for i in range(0,len(profiles)):
		# genProfileCmd = "\ncd " + xyzPath + "\ngrdtrack " + profiles[i] + " -G" + xyzName + ".grd > " + profiles[i][profiles[i].rfind("/")+1:profiles[i].find(".")] + "_" + xyzName + ".txt\ncd " + currentDir + "\n";
		# print(genProfileCmd);
			#genProfileStream = subprocess.Popen(genProfileCmd);
			#genProfileStream.close();



def generatePNGs(path):
	currentDir = os.getcwd();
	findGRDsCmd = "find " + path + " -name \"*.grd\" -print";
	findGRDsStream = subprocess.Popen(findGRDsCmd);
	findGRDsOutput = findGRDsStream.read().split();
	findGRDsStream.close();
	pngCmd = "";
	for i in range(0,len(findGRDsOutput)):
		psName = findGRDsOutput[i][0:findGRDsOutput[i].rfind(".")] + ".ps";
		psPath = findGRDsOutput[i][0:findGRDsOutput[i].rfind("/")];
		pngName = findGRDsOutput[i][0:findGRDsOutput[i].rfind(".")] + ".png";
		if os.path.exists(psName) and not os.path.exists(pngName):
			pngCmd += "\ncd " + psPath + "\nps2raster -A -TG " + psName + "\ncd " + currentDir + "\n";
	if pngCmd != "":
		pngStream = subprocess.Popen(pngCmd);
		pngStream.close();



def getAffineTrans(path):

	cwd = os.getcwd();

	contents = os.listdir(path);
	proc_paths = [item for item in contents if ".proc" in item];

	if len(proc_paths) < 1:
		print("\n***** WARNING, no *.proc files found in " + path + ", not running \"affine\" step...\n");
		return;

	cmd = "";

	for proc_path in proc_paths:

		int_vars = readIntProcFile(proc_path);

		date1   = int_vars["SarDir1"];
		date2   = int_vars["SarDir2"];
		int_dir = int_vars["IntDir"];
		rlooks  = int_vars["Rlooks_geo"];

		aff_path = path + "/" + int_dir + "/" + date1 + "-" + date2 + "_" + rlooks + "rlks_SIM.aff";

		if os.path.exists(aff_path):
			print("\n***** WARNING, " + aff_path + " already exists in " + int_dir + ", skipping...\n");
			continue;

		cmd += "\ncd " + path + "\n";        # whyjay modified
		cmd += "\nexport LC_ALL=C\n"         # whyjay modified
		#cmd += "\ncd " + path + "/" + proc_path + "\n";    # whyjay modfied
		cmd += "\nprocess_2pass_glac.pl " + proc_path + " offsets done_sim_removal &\n";
		cmd += "\ncd " + cwd + "\n";

	print(cmd);
	#subprocess.call(cmd,shell=True);    # whyjay modified

	return;



def getGRDCorners(path):
	currentDir = os.getcwd();
	findGRDsCmd = "find " + path + " -name \"*.grd\" -print";
	findGRDsStream = subprocess.Popen(findGRDsCmd);
	findGRDsOutput = findGRDsStream.read().split();
	findGRDsStream.close();
	for i in range(0,len(findGRDsOutput)):
		grdPath = findGRDsOutput[i][0:findGRDsOutput[i].rfind("/")];
		grdName = findGRDsOutput[i][findGRDsOutput[i].rfind("/")+1:findGRDsOutput[i].rfind(".")];
		if not os.path.exists(grdPath + "/" + grdName + "_corners.dat"):
			grdinfoCmd = "\ngrdinfo " + findGRDsOutput[i].strip() + "\n";
			grdinfoStream = subprocess.Popen(grdinfoCmd);
			grdinfoOutput = grdinfoStream.read();
			grdinfoStream.close();
			x_min = grdinfoOutput[grdinfoOutput.find("x_min:")+6:grdinfoOutput.find("x_max:")].strip();
			x_max = grdinfoOutput[grdinfoOutput.find("x_max:")+6:grdinfoOutput.find("x_inc:")].strip();
			y_min = grdinfoOutput[grdinfoOutput.find("y_min:")+6:grdinfoOutput.find("y_max:")].strip();
			y_max = grdinfoOutput[grdinfoOutput.find("y_max:")+6:grdinfoOutput.find("y_inc:")].strip();
			cornersFileName = grdPath + "/" + grdName + "_corners.dat";
			cornersFile = open(cornersFileName,"w");
			cornersFile.write(x_min + " " + y_min + " LL\n");
			cornersFile.write(x_max + " " + y_max + " TR\n");
			cornersFile.write(x_min + " " + y_max + " TL\n");
			cornersFile.write(x_max + " " + y_min + " LR\n");
			cornersFile.close()



def generateKML(path):
	findPNGsCmd = "find " + path + " -name \"*.png\" -print";
	findPNGsStream = subprocess.Popen(findPNGsCmd);
	findPNGsOutput = findPNGsStream.read().split();
	findPNGsStream.close();



def createMatlabGetXYZ(matlabPath,ampcorInFilePath):
	startRefSample = "";
	endRefSample = "";
	skipRefSample = ""; 
	startRefLine = "";
	endRefLine = "";
	skipRefLine = "";
	ampcorInFile = open(ampcorInFilePath,"r");
	ampoff_dir = ampcorInFilePath[0:ampcorInFilePath.rfind("/")];
	ampoff_name = ampcorInFilePath[0:ampcorInFilePath.rfind(".")];
	cornersFilePath = ampoff_dir + "/corners.dat";
	cornersFile = open(cornersFilePath,"r");
	ul_long = "";
	ul_lat = "";
	while 1:
		line = cornersFile.readline();
		if not line:
			break;
		line = line.strip();
		if line.find("ul_long") > -1:
			ul_long = line.split("=")[1];
		elif line.find("ul_lat") > -1:
			ul_lat = line.split("=")[1];
	cornersFile.close();
	while 1:
		line = ampcorInFile.readline();
		if not line:
			break;
		if line.find("Start, End and Skip Samples in Reference Image") > -1:
			line = line.strip().split("=");
			sampleInfo = line[1].split();
			startRefSample = sampleInfo[0];
			endRefSample = sampleInfo[1];
			skipRefSample = sampleInfo[2];
		elif line.find("Start, End and Skip Lines in Reference Image") > -1:
			line = line.strip().split("=");
			lineInfo = line[1].split();
			startRefLine = lineInfo[0];
			endRefLine = lineInfo[1];
			skipRefLine = lineInfo[2];
	ampcorInFile.close();
	matlabFile = open(matlabPath,"r");
	outputMatlabFile = open(ampoff_dir + "/getxyzs.m","w");
	while 1:
		line = matlabFile.readline();
		if not line:
			break;
		elif re.search("rwin\s*=\s*;",line):
			outputMatlabFile.write(line.replace(";",skipRefSample+";"));
			break;
		else:
			outputMatlabFile.write(line);
	while 1:
		line = matlabFile.readline();
		if not line:
			break;
		elif re.search("awin\s*=\s*;",line):
			outputMatlabFile.write(line.replace(";",skipRefLine+";"));
			break;
		else:
			outputMatlabFile.write(line);
	while 1:
		line = matlabFile.readline();
		if not line:
			break;
		elif re.search("load\s*;",line):
			outputMatlabFile.write(line.replace(";",ampoff_name[ampoff_name.rfind("/")+1:]+".off;"));
			break;
		else:
			outputMatlabFile.write(line);
	while 1:
		line = matlabFile.readline();
		if not line:
			break;
		elif re.search("indat\s*=\s*;",line):
			outputMatlabFile.write(line.replace(";",ampoff_name[ampoff_name.rfind("/")+1:]+";"));
			break;
		else:
			outputMatlabFile.write(line);
	while 1:
		line = matlabFile.readline();
		if not line:
			break;
		elif re.search("width0\s*=\s*;",line):
			outputMatlabFile.write(line.replace(";",endRefSample+";"));
			break;
		else:
			outputMatlabFile.write(line);
	while 1:
		line = matlabFile.readline();
		if not line:
			break;
		elif re.search("length0\s*=\s*;",line):
			outputMatlabFile.write(line.replace(";",endRefLine+";"));
			break;
		else:
			outputMatlabFile.write(line);
	while 1:
		line = matlabFile.readline();
		if not line:
			break;
		elif re.search("ul_long\s*=\s*;",line):
			outputMatlabFile.write(line.replace(";",ul_long+";"));
			break;
		else:
			outputMatlabFile.write(line);
	while 1:
		line = matlabFile.readline();
		if not line:
			break;
		elif re.search("ul_lat\s*=\s*;",line):
			outputMatlabFile.write(line.replace(";",ul_lat+";"));
			break;
		else:
			outputMatlabFile.write(line);
	while 1:
		line = matlabFile.readline();
		if not line:
			break;
		elif re.search("x_step\s*=\s*;",line):
			outputMatlabFile.write(line.replace(";",str(15*int(skipRefSample))+";"));
			break;
		else:
			outputMatlabFile.write(line);
	while 1:
		line = matlabFile.readline();
		if not line:
			break;
		elif re.search("y_step\s*=\s*",line):
			outputMatlabFile.write(line.replace(";",str(15*int(skipRefLine))+";"));
		else:
			outputMatlabFile.write(line);
	outputMatlabFile.close();
	matlabFile.close();
	currentDir = os.getcwd();
	getXYZCmd = "\ncd " + ampoff_dir + "\nmatlab -nodesktop -nosplash -r getxyzs\ncd " + currentDir;
	getXYZCmdStream = subprocess.Popen(getXYZCmd);
	getXYZCmdStream.close();


def makeRawALOS(WorkPath):

	contents = os.listdir(WorkPath);

	cmd = "";

	for i in range(0, len(contents)):

		if re.search("^\d\d\d\d\d\d$", contents[i]):

			date_contents = os.listdir(WorkPath + "/" + contents[i]);

			for item in date_contents:

				if item.find("LED") > -1:

					fbd2fbs = "NO";

					img_path      = item.replace("LED", "IMG-HH");
					img_full_path = os.readlink(WorkPath + "/" + contents[i] + "/" + img_path);
					img_alt_path  = img_full_path.replace("HH","HV");

					if os.path.exists(img_alt_path):
						fbd2fbs = "FBD2FBS";

					cwd = os.getcwd();

					cmd = cmd + "\ncd " + WorkPath + "/" + contents[i] + "\nmake_raw_alos.pl IMG " + contents[i] + " " + fbd2fbs + "\ncd " + cwd + "\n";

					break;

	subprocess.call(cmd,shell=True);

	return;


def makeRawENVISAT(WorkPath, orbit):

	contents = os.listdir(WorkPath);

	cmd = "";

	for i in range(0, len(contents)):

		if re.search("^\d\d\d\d\d\d$", contents[i]):

			date_contents = os.listdir(WorkPath + "/" + contents[i]);

			for item in date_contents:

				if item.find("ASA_") > -1:

					cwd = os.getcwd();

					cmd = cmd + "\ncd " + WorkPath + "/" + contents[i] + "\nmake_raw_envi.pl " + item + " " + orbit + " " + contents[i] + "\ncd " + cwd + "\n";

					break;

	subprocess.call(cmd,shell=True);

	return;


def makeRawERS(WorkPath, orbit):

	contents = os.listdir(WorkPath);

	cmd = "";

	for i in range(0, len(contents)):

		if re.search("^\d\d\d\d\d\d$", contents[i]):

			date_contents = os.listdir(WorkPath + "/" + contents[i]);

			for item in date_contents:

				if item.find("SARLEADER") > -1:

					cwd = os.getcwd();

#					cmd = cmd + "\ncd " + WorkPath + "/" + contents[i] + "\nmake_raw_ASF.pl " + orbit + " " + item + " " + contents[i] + "\ncd " + cwd + "\n";
					cmd = cmd + "\ncd " + WorkPath + "/" + contents[i] + "\nmake_raw.pl " + orbit + " " + item + " " + contents[i] + "\ncd " + cwd + "\n";

					break;

	subprocess.call(cmd,shell=True);

	return;


def makeRawTSX(WorkPath):

	cwd = os.getcwd();

	#cmd = "\nfind " + WorkPath + " -name \"TDX*.xml\"\n";    # whyjay modified
	cmd = "\nfind " + WorkPath + " -name \"TSX*.xml\"\n";     # whyjay modified
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	leader_file_paths = pipe.read().split();
	pipe.close();

	dates = {};
	
	for path in leader_file_paths:

		infile = open(path,"r");

		for line in infile:

			if line.find("timeUTC") > -1:

				index = re.search("timeUTC>",line).end(0);
				year  = line[index + 2 : index + 4];
				month = line[index + 5 : index + 7];
				day   = line[index + 8 : index + 10];

				date  = year + month + day;

				dates[date] = path;

				break;

		infile.close();


	for date in dates:

		cmd  = "\ncd " + WorkPath + "/" + date + "\n";
		#cmd += "\nmake_slc_tsx.csh " + dates[date] + " " + date + "\n";   # whyjay modified
		cmd += "\n/13t1/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/tsx_trbshoot/make_slc_tsx.csh " + dates[date] + " " + date + "\n";    # whyjay modified
		cmd += "\ncp -p " + WorkPath + "/" + date + "/" + date + ".slc.rsc " + WorkPath + "/" + date + "/" + date + ".raw.rsc\n";
		cmd += "\ntouch " + WorkPath + "/" + date + "/" + date + ".raw\n";
		cmd += "\ncd " + cwd + "\n";
		subprocess.call(cmd,shell=True);

	return;


def readIntProcFile(proc_path):

	assert os.path.exists(proc_path), "***** ERROR: " + proc_path + " not found, cannot read proc file\n";

	int_vars = {};

	proc_file = open(proc_path,"r");

	while 1:

		line = proc_file.readline();

		if not line:
			break;

		line = line.strip();

		if not line:
			continue;

		name = "";
		value = "";
		elements = line.split("=");

		if len(elements) < 2 or len(elements[0]) < 1 or len(elements[1]) < 1:
			print("\n***** ERROR, proc file line format is \"name = value\", \"" + line + "\" does not conform to this format\n");
			sys.exit();

		name  = elements[0].strip();
		value = elements[1].strip();
		int_vars[name] = value;

	proc_file.close();

	return int_vars;



def setupALOS(WorkPath, leader_file_paths):
	
	for leader_path in leader_file_paths:

		existingSARLeaderFiles = {};
		sarNumber              = {};
		dateName               = "";
		extension              = leader_path[leader_path.rfind("."):];
		leader_name            = leader_path[leader_path.rfind("/") + 1 : ];

		leaderFile             = open(leader_path,"rb");

		while 1:

			line = leaderFile.readline();

			if not line:
				break;

			searchExp = "\s\d\d\d\d\d\d\d\d";

			if re.search(searchExp,line):

				index = re.search(searchExp,line).start(0);

				dateName = line[index:index+9].strip();
				dateName = dateName[2:8];

				if not os.path.isdir(WorkPath + "/" + dateName):
					cmd = "mkdir " + WorkPath + "/" + dateName;
					subprocess.call(cmd,shell=True);

				if not existingSARLeaderFiles.has_key(leader_path):

					leader_link_path = WorkPath + "/" + dateName + "/" + leader_name;

					os.symlink(leader_path, leader_link_path);
					existingSARLeaderFiles[leader_path] = leader_link_path;

				break;

		leaderFile.close();

		if re.search("LED-A",leader_path):

			raw_path     = leader_path.replace("LED","IMG-HH");
			raw_alt_path = leader_path.replace("LED","IMG-HV");
			raw_name     = raw_path[raw_path.rfind("IMG") : ];
			raw_alt_name = raw_alt_path[raw_alt_path.rfind("IMG") : ];

			raw_link_path     = WorkPath + "/" + dateName + "/" + raw_name;
			raw_alt_link_path = WorkPath + "/" + dateName + "/" + raw_alt_name;
			
			if os.path.exists(raw_path) and not os.path.exists(raw_link_path):
				os.symlink(raw_path, raw_link_path);

#			if os.path.exists(raw_alt_path) and not os.path.exists(raw_alt_link_path):
#				os.symlink(raw_alt_path, raw_alt_link_path);

			if not os.path.exists(raw_path):
				print("\n***** WARNING, could not find corresponding raw file for leader file \"" + leader_path + "\"\nPlease make sure the raw file is in the same directory and is named \"IMG-HH*"+leader_path.replace("LED","")+"\"\n");

			continue;

	return;



def setupTSX(WorkPath, leader_file_paths):
	
	for path in leader_file_paths:

		infile = open(path,"r");

	for path in leader_file_paths:

		print(path);

	return;



def setupENVISAT(WorkPath, leader_file_paths):
	
	for path in leader_file_paths:

		print(path);

	return;



def setupERS(WorkPath, leader_file_paths):
	
	for path in leader_file_paths:

		existingSARLeaderFiles = {};
		sarNumber              = {};
		dateName               = "";
		extension              = path[path.rfind("."):];
		leaderFile             = open(path,"rb");

		while 1:

			line = leaderFile.readline();

			if not line:
				break;

			searchExp = "\s\d\d\d\d\d\d\d\d";

			if re.search(searchExp,line):

				index = re.search(searchExp,line).start(0);

				dateName = line[index:index+9].strip();
				dateName = dateName[2:8];

				if not os.path.isdir(WorkPath + "/" + dateName):
					cmd = "mkdir " + WorkPath + "/" + dateName;
					subprocess.call(cmd,shell=True);

				if not existingSARLeaderFiles.has_key(path):

					if not sarNumber.has_key(dateName):
						sarNumber[dateName] = 1;
					else:
						sarNumber[dateName] = sarNumber[dateName] + 1;

					sarNumberStr = str(sarNumber[dateName])

					if sarNumber[dateName] < 10:
						sarNumberStr = "0" + sarNumberStr;

					tempPath = WorkPath + "/" + dateName + "/SARLEADER" + sarNumberStr;

					while has_value(existingSARLeaderFiles,tempPath):

						sarNumber[dateName] = sarNumber[dateName] + 1;
						sarNumberStr = str(sarNumber[dateName]);

						if sarNumber[dateName] < 10:
							sarNumberStr = "0" + sarNumberStr;

						tempPath = WorkPath + "/" + dateName + "/SARLEADER" + sarNumberStr;

					os.symlink(path,tempPath);
					existingSARLeaderFiles[path] = tempPath;

				break;

		leaderFile.close();

		rawFileName = "rawness";

		if re.search("LEA.*\.001",path):
			rawFileName =  path.replace("LEA","DAT");

		else:
			rawFileName = path[0:path.find(".ldr")] + ".raw";

			if not os.path.exists(rawFileName):
				rawFileName = rawFileName[0:rawFileName.find(".raw")] + ".RAW";

				if not os.path.exists(rawFileName):
					rawFileName = rawFileName[0:rawFileName.find(".RAW")] + ".Raw";

		if not os.path.exists(rawFileName):

			if DataType.lower().find("alos") > -1:
				print("\n***** WARNING, could not find corresponding raw file for leader file \"" + path + "\"\nPlease make sure the raw file is in the same directory and is named \"IMG*"+path.replace("LED","")+"\"\n");
			else:
				print("\n***** WARNING, could not find corresponding raw file for leader file \"" + path + "\"\nPlease make sure the raw file is in the same directory and has the extension \".raw\"\n");
			continue;

		tempImagePath = "";

		if re.search("SARLEADER", existingSARLeaderFiles[path]):
			tempImagePath = existingSARLeaderFiles[path].replace("SARLEADER","IMAGERY");

		if not os.path.exists(tempImagePath):
			os.symlink(rawFileName, tempImagePath);

	return;



def setupTSX(WorkPath, leader_file_paths):
	
	for path in leader_file_paths:

		infile = open(path,"r");

		for line in infile:

			if line.find("timeUTC") > -1:

				index = re.search("timeUTC>",line).end(0);
				year  = line[index + 2 : index + 4];
				month = line[index + 5 : index + 7];
				day   = line[index + 8 : index + 10];

				date  = year + month + day;

				if not os.path.exists(date):
					os.mkdir(WorkPath + "/" + date);

				break;

		infile.close();

	return;


