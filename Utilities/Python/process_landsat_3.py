#!/usr/bin/python

# process_landsat.py
# Author: Andrew Kenneth Melkonian
# All rights reserved

import aropInput;
from getxyzs import *;
from imageAmpResults import *;
from motionElevCorrection import *;
import os;
import re;
import subprocess;
import sys;

ICE		= "/home/akm26/Documents/Russia/NovZ/Glaciers/NovZ_bounds_ice_sub_utm41x.gmt";
#IMAGE_DIR	= "/home/akm26/Documents/Russia/NovZ/Landsat/VIS/Images";
IMAGE_DIR	= "/home/akm26/Documents/Russia/NovZ/Landsat/pairs";
METADATA_DIR	= "/home/akm26/Documents/Russia/NovZ/Landsat/VIS/Images/";
PAIRS_DIR	= "/home/akm26/Documents/Russia/NovZ/Landsat/pairs";
#PAIRS		= "l7_pair_list.txt";
PAIRS		= "l8_pair_list.txt";
PROCESSORS	= "8";
RESOLUTION	= "15";
ROCK		= "/home/akm26/Documents/Russia/NovZ/Glaciers/NovZ_bounds_rock_sub_utm41x.gmt";
#SATELLITE	= "Landsat7";
SATELLITE	= "Landsat8";
SNR_CUTOFF	= "5";
SRTM_GRD	= "/home/akm26/Documents/Russia/NovZ/DEMs/NovZ_carto_dem_utm41x_clipped.grd";
UTM_ZONE	= "41";
UTM_LETTER	= "X";


step=sys.argv[1];


if step == "utm_change":

	cmd="\nls *_B8.TIF\n";
	pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	images=pipe.read().split();
	pipe.close();

	for image in images:

		cmd="\ngdalinfo "+image+"\n";
		pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		info=pipe.read();
		pipe.close();

		if info.find("40N") > -1:
			cmd="\ngdalwarp -of GTiff -t_srs '+proj=utm +zone=41 +datum=WGS84 +north' -tr " + RESOLUTION + " " + RESOLUTION + " -r cubic "+image+" "+image[:image.rfind(".")]+"_zone41.TIF\n";
			subprocess.call(cmd,shell=True);


elif step == "cut":

	cmd="\nls *_B8*.TIF\n";
	pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	images=pipe.read().split();
	pipe.close();

	for image in images:

		cmd="\n/home/akm26/Downloads/gdal-1.8.0/apps/gdal_translate -of ENVI -ot Float32 -projwin 577000 8494000 595000 8484000 "+image+" "+image[:image.rfind(".")]+"_Ino.img\n";
		subprocess.call(cmd,shell=True);


elif step == "setup1":

	infile=open(PAIRS,"r");

	for line in infile:

		elements = line.split();
		
		limage = elements[0];
		eimage = elements[1];

		cmd="\nfind /home/akm26/Documents/Russia/NovZ/Landsat/ -name \""+limage+"*TIF\"\n";
		pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		limage=pipe.read().split()[0];
		pipe.close(); 

		cmd="\nfind /home/akm26/Documents/Russia/NovZ/Landsat/ -name \""+eimage+"*TIF\"\n";
		pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		eimage=pipe.read().split()[0];
		pipe.close();

		pair = line.strip().replace(" ","_").replace("_B8","").replace(".TIF","").replace("_zone41","");
		pair_dir = PAIRS_DIR + "/" + pair;

		cmd = "\ngdalinfo " + limage + "\n";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		limage_info = pipe.read().strip();
		pipe.close();

		cmd = "\ngdalinfo " + eimage + "\n";
                pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
                eimage_info = pipe.read().strip();
                pipe.close();

		limage_utm = limage_info[re.search("UTM zone\s+",limage_info).end(0):re.search("UTM zone\s+\d+",limage_info).end(0)];
		limage_rez = limage_info[re.search("Pixel Size = \(",limage_info).end(0):re.search("Pixel Size = \(\d+",limage_info).end(0)]; 
		eimage_utm = eimage_info[re.search("UTM zone\s+",eimage_info).end(0):re.search("UTM zone\s+\d+",eimage_info).end(0)];
		eimage_rez = eimage_info[re.search("Pixel Size = \(",eimage_info).end(0):re.search("Pixel Size = \(\d+",eimage_info).end(0)]; 

		coreg_limage = pair_dir + "/coreg_" + limage[limage.rfind("/")+1:limage.rfind(".")] + ".img";

		#if not os.path.exists(pair_dir):

		#	cmd = "\nmkdir " + PAIRS_DIR + "/" + pair + "\n";

		arop_inp_path = pair_dir + "/" + pair + ".inp";

		if not os.path.exists(arop_inp_path):
			
			arop_inp = aropInput.AropInput();
			
			arop_inp.setBasePixelSize(eimage_rez);
			arop_inp.setBaseLandsat(eimage);
			arop_inp.setUTMZone(eimage_utm);
			arop_inp.setBaseSatellite(SATELLITE);

			arop_inp.setWarpFileType("GEOTIFF");
			arop_inp.setWarpNSample("-1");
			arop_inp.setWarpNLine("-1");
			arop_inp.setWarpUpperLeftCorner("-1, -1");
			arop_inp.setWarpSatellitePointingAngle("0");
			arop_inp.setWarpOrientationAngle("0");
			arop_inp.setWarpLandsatBand(limage);
			arop_inp.setWarpBaseMatchBand(limage);
		
			arop_inp.setWarpPixelSize(limage_rez);
			arop_inp.setWarpSatellite(SATELLITE);
			arop_inp.setWarpUTMZone(limage_utm);

			# Set output image parameters
			arop_inp.setOutPixelSize(eimage_rez);
			arop_inp.setResampleMethod("CC");
			arop_inp.setOutLandsatBand(coreg_limage);
			arop_inp.setOutBaseMatchBand(coreg_limage);

			#print(arop_inp_path);
			arop_inp.write_arop(arop_inp_path);


elif step == "setup":

	infile=open("l7_pair_list.txt","r");

	for line in infile:

		elements=line.split();
		limage=elements[0];
		eimage=elements[1];
		cmd="\nfind /home/akm26/Documents/Russia/NovZ/Landsat/ -name \""+limage+"*TIF*ghp_stretch\"\n";
		pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		limage=pipe.read().split()[0];
		pipe.close(); 
		cmd="\nfind /home/akm26/Documents/Russia/NovZ/Landsat/ -name \""+eimage+"*TIF*ghp_stretch\"\n";
		pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		eimage=pipe.read().split()[0];
		pipe.close();
		pair=line.replace(" ","_").replace("_B8","").replace(".TIF","").replace("_zone41","");

		if not os.path.exists("/home/akm26/Documents/Russia/NovZ/Landsat/pairs/"+pair):

			cmd="\nmkdir /home/akm26/Documents/Russia/NovZ/Landsat/pairs/"+pair+"\n";
			cmd+="\ncp -p /home/akm26/Documents/Russia/NovZ/Landsat/pairs/*.py /home/akm26/Documents/Russia/NovZ/Landsat/pairs/"+pair+"\n";
			cmd+="\ncd /home/akm26/Documents/Russia/NovZ/Landsat/pairs/"+pair+"\n";
			cmd+="\npython split_ampcor.py "+eimage+" "+limage+" 8\n";
			cmd+="\ncd /home/akm26/Documents/Russia/NovZ/Landsat/pairs\n";
			subprocess.call(cmd,shell=True);
			
			outfile=open("/home/akm26/Documents/Russia/NovZ/Landsat/pairs/"+pair.strip()+"/run_amp.cmd","w");
			outfile.write("ampcor ampcor_1.in rdf > ampcor_1.out &\n");
			outfile.write("ampcor ampcor_2.in rdf > ampcor_2.out &\n");
			outfile.write("ampcor ampcor_3.in rdf > ampcor_3.out &\n");
			outfile.write("ampcor ampcor_4.in rdf > ampcor_4.out &\n");
			outfile.write("ampcor ampcor_5.in rdf > ampcor_5.out &\n");
			outfile.write("ampcor ampcor_6.in rdf > ampcor_6.out &\n");
			outfile.write("ampcor ampcor_7.in rdf > ampcor_7.out &\n");
			outfile.write("ampcor ampcor_8.in rdf > ampcor_8.out &\n");
			outfile.close();

	infile.close();

	exit();


elif step == "results":

	pairs = {};
	pair_images = {};
	images = {};

	infile=open(PAIRS,"r");

	for line in infile:

		elements = line.split();
		image1 = elements[0];
		image1 = image1[image1.rfind("/") + 1 : ];

		index  = image1.find("_");

		if index < 0:
			index = len(image1);

		image1 = image1[ : index];

		image2 = elements[1];
		image2 = image2[image2.rfind("/") + 1 : ];

		index  = image2.find("_");

		if index < 0:
			index = len(image2);

		image2 = image2[ : index];

		if image1 not in pair_images:
			pair_images[image1] = image1;

		if image2 not in pair_images:
			pair_images[image2] = image2;

		pair = image1 + "_" + image2;
		
		if pair not in pairs:
			pairs[pair] = pair;

	infile.close();

	contents = os.listdir(IMAGE_DIR);

	for item in contents:

		item = item.strip(); 

		if not re.search("B8.TIF$",item) and not re.search("B8_zone" + UTM_ZONE + ".TIF$",item):
			continue;

		label = item[item.rfind("/") + 1 :]
		label = label[: label.find("_")];

		if label in pair_images:
			images[label] = IMAGE_DIR + "/" + item;
		

	for pair in pairs:

		print("\nCurrent pair is " + pair + "\n");

		pair_dir = PAIRS_DIR + "/" + pair;

		elements = pair.split("_");
		limage = elements[0];
		eimage = elements[1];
		limage_path = images[limage];
		eimage_path = images[eimage];

		later_date = "";

		limage_metfile = open(METADATA_DIR + "/" + limage + "_MTL.txt","r"); 

		for line in limage_metfile:

			if line.find("DATE_ACQUIRED") > -1:
				elements = line.split();
				date = elements[2];
				later_date = later_date + date[5:7] + date[8:] + date[0:4];

			elif line.find("SCENE_CENTER_TIME") > -1:
				elements = line.split();
				time = elements[2];
				seconds = str(int(time[6:8])+int(round(float(time[8:11]))));

				if len(seconds) < 2:
					seconds = "0" + seconds;

				later_date = later_date + time[0:2] + time[3:5] + seconds;

		limage_metfile.close();

		earlier_date = "";
		
		eimage_metfile=open(METADATA_DIR + "/" + eimage + "_MTL.txt","r");

		for line in eimage_metfile:

			if line.find("DATE_ACQUIRED") > -1:
				elements = line.split();
				date = elements[2];
				earlier_date = earlier_date + date[5:7] + date[8:] + date[0:4];

			elif line.find("SCENE_CENTER_TIME") > -1:
				elements = line.split();
				time = elements[2];
				seconds = str(int(time[6:8])+int(round(float(time[8:11]))));

				if len(seconds) < 2:
					seconds = "0" + seconds;

				earlier_date = earlier_date + time[0:2] + time[3:5] + seconds;

		eimage_metfile.close();

		pair_label = later_date + "_" + earlier_date;

		if not os.path.exists(pair_dir + "/ampcor_1.off"):
			continue;

		cat_cmd = "\ncat ";
		contents = os.listdir(pair_dir);

		for item in contents:

			if re.search("ampcor_\d\.off",item):
				cat_cmd += pair_dir + "/" + item.strip() + " ";

		cat_cmd += "> " + pair_dir + "/ampcor.off\n";
		subprocess.call(cat_cmd,shell=True);

		rwin = "";
		awin = "";
		input_res = "";
		input_width = "";
		input_length = "";
		utm_z = "";
		ns = "";
		ul_lat = "";
		ul_lon = "";
		
		infile = open(pair_dir + "/ampcor_1.in");

		for line in infile:

			if line.find("Reference Image Input File") > -1:

				elements = line.split();

				hdr_path = elements[len(elements) - 1] + ".hdr";

				if hdr_path.find("/") < 0:
					hdr_path = pair_dir + "/" + hdr_path;

				hdr_file = open(hdr_path, "r");

				for hdr_line in hdr_file:

					if hdr_line.find("samples") > -1:
						hdr_elements  = hdr_line.split();
						input_width = hdr_elements[len(hdr_elements)-1].strip();

					elif hdr_line.find("lines") > -1:
						hdr_elements  = hdr_line.split();
						input_length = hdr_elements[len(hdr_elements)-1].strip();

					elif hdr_line.find("map") > -1:
						hdr_elements = hdr_line.split();
						ul_long = hdr_elements[6].strip().replace(",","");
						ul_lat = hdr_elements[7].strip().replace(",","");
						input_res = str(int(float(hdr_elements[8].strip().replace(",",""))));
						utm_z = hdr_elements[10].strip().replace(",","");
						ns = hdr_elements[11].strip().replace(",","");

				hdr_file.close();

			elif line.find("Start, End and Skip Lines in Reference Image") > -1:
				elements = line.split();
				awin = elements[len(elements) - 1].strip();

			elif line.find("Start, End and Skip Samples in Reference Image") > -1:
				elements = line.split();
				rwin = elements[len(elements) - 1].strip();

		infile.close();

		if not os.path.exists(pair_dir + "/" + pair_label + "_eastxyz.txt"):
			getxyzs(pair_dir, rwin, awin, "1", input_res, input_width, input_length, ul_long, ul_lat, pair_label);

		later_date_str	 = later_date[6:8] + "-" + later_date[0:2] + "-" + later_date[2:4] + " " + later_date[8:10] + ":" + later_date[10:12] + ":" + later_date[12:14];
		earlier_date_str = earlier_date[6:8] + "-" + earlier_date[0:2] + "-" + earlier_date[2:4] + " " + earlier_date[8:10] + ":" + earlier_date[10:12] + ":" + earlier_date[12:14];

		cmd="\ndate +\"%s\" -d \"" + later_date_str + "\"\n";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		later_seconds = pipe.read().strip();
		pipe.close();

		cmd="\ndate +\"%s\" -d \"" + earlier_date_str + "\"";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		earlier_seconds = pipe.read().strip();
		pipe.close();

		day_diff=abs(float(later_seconds)/(60*60*24) - float(earlier_seconds)/(60*60*24));
		mperday_factor = str(day_diff * 100.0);

		cmd="\nminmax -C " + pair_dir + "/" + pair_label + "_northxyz.txt\n";
		pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
		bounds = pipe.read().split();
		pipe.close();

		bounds	= bounds[0:4];
		min_x	= bounds[0];
		max_x	= bounds[1];
		min_y	= bounds[2];
		max_y	= bounds[3];
		R	= "-R" + min_x + "/" + min_y + "/" + max_x + "/" + max_y + "r";

		n_grd = pair_dir + "/" + pair_label + "_northxyz.grd";
		e_grd = pair_dir + "/" + pair_label + "_eastxyz.grd";

		if not os.path.exists(n_grd):
			cmd = "";
			cmd += "\ngawk '$4 !~ /a/ {print $1\" \"$2\" \"$4}' " + pair_dir + "/" + pair_label + "_northxyz.txt | xyz2grd -I" + str(int(input_res) * int(rwin)) + "= -G" + pair_dir + "/" + pair_label + "_snr.grd " + R + "\n"; 
			cmd += "\nxyz2grd " + pair_dir + "/" + pair_label + "_eastxyz.txt -I120= -G" + pair_dir + "/" + pair_label + "_eastxyz.grd " + R + "\n";
			cmd += "\nxyz2grd " + pair_dir + "/" + pair_label + "_northxyz.txt -I120= -G" + pair_dir + "/" + pair_label + "_northxyz.grd " + R + "\n";
			cmd += "\ngrdmath " + pair_dir + "/" + pair_label + "_eastxyz.grd " + mperday_factor + " DIV = " + pair_dir + "/" + pair_label + "_eastxyz.grd\n";
			cmd += "\ngrdmath " + pair_dir + "/" + pair_label + "_northxyz.grd " + mperday_factor + " DIV = " + pair_dir + "/" + pair_label + "_northxyz.grd\n";
			subprocess.call(cmd,shell=True);

		n_corrected_grd	= pair_dir + "/" + pair_label + "_northxyz_corrected.grd";
		e_corrected_grd	= pair_dir + "/" + pair_label + "_eastxyz_corrected.grd";

		if not os.path.exists(n_corrected_grd):
			motionElevCorrection(n_grd, SRTM_GRD, ICE, ROCK, SNR_CUTOFF);
			motionElevCorrection(e_grd, SRTM_GRD, ICE, ROCK, SNR_CUTOFF);

		mag_grd		= pair_dir + "/" + pair_label + "_magnitude_corrected.grd";
		ratio		= "1000000";
		cscale		= "3";

		if not os.path.exists(mag_grd):
			print("\nCreating magnitude grid and image for " + pair_dir + " ...\n");
			imageAmpResults(pair_dir, pair_label, n_corrected_grd, e_corrected_grd, bounds, ratio, cscale, utm_z + UTM_LETTER, IMAGE_DIR, ICE, ROCK);



exit();
