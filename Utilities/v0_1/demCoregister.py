#!/usr/bin/python


# demCoregister.py
# Author: Andrew Kenneth Melkonian
# All rights reserved



def demCoregister(dem_tif_path):
	

	import os;

	assert os.path.exists(dem_tif_path), "\n***** ERROR: " + dem_tif_path + " does not exist\n";

	DATE_LENGTH = "14";
	DATE_ADJ    = int(DATE_LENGTH) - 14;
	HIGH_BOUND  = "1520";
	INTERVAL    = "120";
	LOW_BOUND   = "1";
	ICE	    = "/home/akm26/Documents/Russia/NovZ/Glaciers/NovZ_bounds_ice_sub_utm41x.gmt";
	ROCK	    = "/home/akm26/Documents/Russia/NovZ/Glaciers/NovZ_bounds_rock_sub_utm41x.gmt";
	REF_DEM	    = "/home/akm26/Documents/Russia/NovZ/DEMs/NovZ_carto_dem_utm41x_hillshade_rock_ones.img";
	REF_DEM_RAW = "/home/akm26/Documents/Russia/NovZ/DEMs/NovZ_carto_dem_utm41x_clipped_rock.img";
	REF_DEM_GRD = "/home/akm26/Documents/Russia/NovZ/DEMs/NovZ_carto_dem_utm41x_clipped_rock.grd";
	UTM_ZONE    = "41";
	UTM_NS      = "North";
	
	
	import re;

	dem_ast_name	    = dem_tif_path[dem_tif_path.rfind("/") + 1 : dem_tif_path.rfind(".")];
	dem_grd		    = dem_ast_name + ".grd";
	date		    = dem_tif_path[re.search("\d{" + DATE_LENGTH + "}",dem_tif_path).start(0) + DATE_ADJ : re.search("\d{" + DATE_LENGTH + "}",dem_tif_path).end(0)];
	dem_clip	    = date + "_clip.grd";
	dem_resamp	    = date + "_resamp_DEM.grd";
	dem_img		    = dem_resamp.replace("grd","img");
	ref_resamp	    = date + "_ref_resamp.grd";
	off_ice_mask	    = date + "_off_ice.grd";
	dem_off_ice	    = date + "_resamp_DEM_off_ice.grd";
	dem_off_ice_img     = date + "_resamp_DEM_off_ice.img";
	dem_hillshade	    = date + "_resamp_DEM_off_ice_hillshade.img";
	dem_hillshade_float = date + "_resamp_DEM_off_ice_hillshade_float.img";
	

	print(date);

	import subprocess;

	cmd  = "\ngdalinfo " + dem_tif_path + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	zone		= info[re.search("UTM\s*zone\s*",info).end(0) : re.search("UTM\s*zone\s*\d+",info).end(0)];
	dem_zone41_path = dem_tif_path[dem_tif_path.rfind("/") + 1 : dem_tif_path.rfind(".")] + "_zone41.tif";

	if zone != "41":
		cmd  = "\ngdalwarp -t_srs '+proj=utm +zone=41 +datum=WGS84 +" + UTM_NS.lower() + "' -of GTiff " + dem_tif_path + " " + dem_zone41_path + "\n"
		subprocess.call(cmd,shell=True);
		dem_tif_path = dem_zone41_path;

	
	cmd = "\ngrdinfo " + REF_DEM_GRD + "\n";
	pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info=pipe.read().strip();
	pipe.close();
	
	ref_min_x = info[re.search("x_min\:\s+",info).end(0) : re.search("x_min\:\s+\-*\d*\.\d+",info).end(0)];
	ref_min_y = info[re.search("y_min\:\s+",info).end(0) : re.search("y_min\:\s+\-*\d*\.\d+",info).end(0)];
	ref_max_x = info[re.search("x_max\:\s+",info).end(0) : re.search("x_max\:\s+\-*\d*\.\d+",info).end(0)];
	ref_max_y = info[re.search("y_max\:\s+",info).end(0) : re.search("y_max\:\s+\-*\d*\.\d+",info).end(0)];
		
	map_info = "map info = {UTM, 1, 1, x_min, y_min, " + INTERVAL + ", " + INTERVAL + ", " + UTM_ZONE + ", " + UTM_NS + ", WGS-84, units=Meters}";
	
	if not os.path.exists(dem_grd):
		cmd = "\n/home/akm26/Downloads/gdal-1.8.0/apps/gdal_translate -of GMT " + dem_tif_path + " " + dem_grd + "\n";
		print(cmd);
		subprocess.call(cmd,shell=True);
	
	cmd  = "\ngrdinfo " + dem_grd + "\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	info = pipe.read().strip();
	pipe.close();
	
	aster_min_x = str(float(info[re.search("x_min\:\s+",info).end(0) : re.search("x_min\:\s+\-*\d*\.\d+",info).end(0)]) + 15);
	aster_min_y = str(float(info[re.search("y_min\:\s+",info).end(0) : re.search("y_min\:\s+\-*\d*\.\d+",info).end(0)]) + 15);
	aster_max_x = str(float(info[re.search("x_max\:\s+",info).end(0) : re.search("x_max\:\s+\-*\d*\.\d+",info).end(0)]) - 15);
	aster_max_y = str(float(info[re.search("y_max\:\s+",info).end(0) : re.search("y_max\:\s+\-*\d*\.\d+",info).end(0)]) - 15);
	
	cut = 0;

	if float(aster_min_x) < float(ref_min_x):
		aster_min_x = str(float(ref_min_x) + 30);
		cut = 1;

	if float(aster_min_y) < float(ref_min_y):
		aster_min_y = str(float(ref_min_y) + 30);
		cut = 1;

	if float(aster_max_x) > float(ref_max_x):
		aster_max_x = str(float(ref_max_x) - 30);
		cut = 1;

	if float(aster_max_y) > float(ref_max_y):
		aster_max_y = str(float(ref_max_y) - 30);
		cut = 1;
	
	R = "-R" + aster_min_x + "/" + aster_max_x + "/" + aster_min_y + "/" + aster_max_y;
	
	if cut:
		cmd = "\ngrdcut " + dem_grd + " " + R + " -G" + dem_grd + "\n";
		subprocess.call(cmd,shell=True);
	
	if not os.path.exists(dem_clip):
		cmd = "\ngrdclip " + dem_grd + " -G" + dem_clip + " -Sa" + HIGH_BOUND + "/NaN -Sb" + LOW_BOUND + "/NaN\n";
		subprocess.call(cmd,shell=True);
	
	if not os.path.exists(dem_resamp):
		cmd = "\ngrdfilter -I" + INTERVAL + " " + dem_clip + " -D0 -Fg" + INTERVAL + " -G" + dem_resamp + "\n";
		subprocess.call(cmd,shell=True);
	
	if not os.path.exists(ref_resamp):
		cmd = "\ngrdsample -Qn " + REF_DEM_GRD + " -R" + dem_resamp + " -G" + ref_resamp + "\n";
		subprocess.call(cmd,shell=True);
	
	if not os.path.exists(dem_img):
		cmd = "\n/home/akm26/Downloads/gdal-1.8.0/apps/gdal_translate -of ENVI -ot Float32 " + dem_resamp + " " + dem_img + "\n";
		subprocess.call(cmd,shell=True);
	
	if not os.path.exists(off_ice_mask):
		cmd = "\ngrdmask -R" + dem_resamp + " " + ICE + " -m -G" + off_ice_mask + " -N1/NaN/NaN\n";

		if len(ROCK) > 0:
			cmd += "\ngrdmask -R" + dem_resamp + " " + ROCK + " -m -Gtemp.grd -NNaN/NaN/1\n";
			cmd += "\ngrdmath " + off_ice_mask + " temp.grd XOR = " + off_ice_mask + "\n"; 

		subprocess.call(cmd,shell=True);
	
	if not os.path.exists(dem_off_ice):
		cmd = "\ngrdmath " + dem_resamp + " " + off_ice_mask + " MUL = " + dem_off_ice + "\n";
		subprocess.call(cmd,shell=True);
	
	if not os.path.exists(dem_off_ice_img):
		cmd = "\n/home/akm26/Downloads/gdal-1.8.0/apps/gdal_translate -of ENVI " + dem_off_ice + " " + dem_off_ice_img + "\n";
		subprocess.call(cmd,shell=True);
	
	if not os.path.exists(date + "_hist.ps"):
		cmd  = "\ngrdmath " + ref_resamp + " " + dem_off_ice + " SUB = diff.grd\n";
		cmd += "\nmakecpt -Crainbow -T-50/50/1 > diff.cpt\n";
		cmd += "\ngrd2xyz diff.grd | gawk '$0 !~ /a/ {print $3}' | pshistogram -JX10c -W1 -R-75/75/0/3000 -Ba15g15:\"Difference (m)\":/a1000g1000:\"# of points\":WeSn -Gblack -P --LABEL_FONT_SIZE=14 > " + date + "_hist.ps\n";
		cmd += "\ngrdclip diff.grd -Sb-50/NaN -Sa50/NaN -Gdiff.grd\n";
		cmd += "\ngrdinfo -L2 diff.grd\n";
		cmd += "\ngrdimage diff.grd -Jx1:1000000 -R" + dem_off_ice + " -Q -P -Cdiff.cpt > " + date + "_diff.ps\n";
		cmd += "\nps2raster -A -Tf " + date + "_diff.ps\n";
		cmd += "\nps2raster -A -Tf " + date + "_hist.ps\n";
		cmd += "\ncp -p diff.grd " + date + "_old_diff_clip.grd\n";
		cmd += "\nrm diff.grd\n";
		subprocess.call(cmd,shell=True);
	
	dem_map_info = "";

	infile = open(dem_off_ice_img.replace("img","hdr"),"r");

	while 1:

		line = infile.readline().strip();

		if not line:
			break

		if line.find("map info") > -1:
			dem_map_info = line.split();
			break;

	infile.close();
	
	ul_lon = dem_map_info[6].replace(",","");
	ul_lat = dem_map_info[7].replace(",","");
	
	map_info = map_info.replace("x_min",ul_lon);
	map_info = map_info.replace("y_min",ul_lat);
	
	if not os.path.exists(dem_hillshade):
		cmd = "\n/home/akm26/Downloads/gdal-1.8.0/apps/gdaldem hillshade -of ENVI " + dem_off_ice_img + " " + dem_hillshade + "\n";
		subprocess.call(cmd,shell=True);
	
	outfile = open(dem_hillshade.replace("img","hdr"),"a");
	outfile.write(map_info + "\n");
	outfile.close();
	
	if not os.path.exists(dem_hillshade_float):
		cmd  = "\n/home/akm26/Downloads/gdal-1.8.0/apps/gdal_translate -of ENVI -ot Float32 " + dem_hillshade + " temp\n";
		cmd += "\ngdalwarp -of ENVI -srcnodata \"0\" -dstnodata \"1\" temp " + dem_hillshade_float + "\n";
		cmd += "\nmv temp.hdr " + dem_hillshade_float.replace("img","hdr") + "\n";
		cmd += "\nrm temp*\n";
		subprocess.call(cmd,shell=True);
	
	info_present = False;

	infile = open(dem_hillshade_float.replace("img","hdr"),"r");

	for line in infile:

		if line.find("map info") > -1:
			info_present = True;

	infile.close();
	
	if not info_present:
		outfile = open(dem_hillshade_float.replace("img","hdr"),"a");
		outfile.write(map_info + "\n");
		outfile.close();
	
	ampoff_path    = date + "_amp.off";
	ref_samps      = "";
	search_samps   = "";
	ref_lines      = "";
	search_lines   = "";
	ref_start_samp = "";
	ref_end_samp   = "";
	ref_start_line = "";
	ref_end_line   = "";
	step_size      = "2";
	ref_size       = "32";
        search_size     = "8";
	mean_off_samp  = "";
	mean_off_line  = "";
	

	from findOffsetDEMs import *;

	[ref_samps, search_samps, ref_lines, search_lines, ref_start_line, ref_end_line, ref_start_samp, ref_end_samp, mean_off_samp, mean_off_line] = findOffsetDEMs(REF_DEM.replace("img","hdr"), dem_hillshade_float.replace("img","hdr"), "120");


	from makeAmpcorInput import *;
	
	makeAmpcorInput(REF_DEM, dem_hillshade_float, date + "_amp.in", ampoff_path, ref_samps, search_samps, ref_start_line, ref_end_line, ref_start_samp, ref_end_samp, step_size, ref_size, search_size, mean_off_samp, mean_off_line);
	
	
	if not os.path.exists(date + "_amp.out"):
		cmd = "\nampcor " + date + "_amp.in rdf > " + date + "_amp.out\n";
		subprocess.call(cmd,shell=True);
	
	if not os.path.exists(date + "_amp_cull.out"):
		cmd = "$INT_BIN/fitoff " + date + "_amp.off " + date + "_amp_cull.off 1.5 .1 50 > " + date + "_amp_cull.out\n";
		subprocess.call(cmd,shell=True);
	
	cmd  = "\n$INT_SCR/find_affine.pl " + date + "_amp_cull.out\n";
	pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
	[m11, m12, m21, m22, t1, t2] = pipe.read().split();
	pipe.close();
	
	dem_rmg	    = dem_hillshade_float.replace("img","rmg");
	dem_img_rmg = dem_img.replace("img","rmg");
	
	if not os.path.exists(dem_rmg):
		cmd = "\nmag_phs2rmg " + dem_hillshade_float + " " + dem_hillshade_float + " " + dem_rmg + " " + search_samps + "\n";
		subprocess.call(cmd,shell=True);
	
	if not os.path.exists(dem_img_rmg):
		cmd = "\nmag_phs2rmg " + dem_img + " " + dem_img + " " + dem_img_rmg + " " + search_samps + "\n";
		subprocess.call(cmd,shell=True);
	
	coreg_dem_hillshade_rmg = "coreg_" + dem_rmg;
	coreg_dem_rmg		= "coreg_" + dem_img_rmg;
	
	if not os.path.exists(date + "_rect.in"):
		outfile = open(date + "_rect.in","w");
		outfile.write("Input Image File Name  (-) = " + dem_rmg + "      ! dimension of file to be rectified\n");
		outfile.write("Output Image File Name (-) = " + coreg_dem_hillshade_rmg + " ! dimension of output\n");
		outfile.write("Input Dimensions       (-) = " + search_samps + " " + search_lines + "  ! across, down\n");
		outfile.write("Output Dimensions      (-) = " + ref_samps + " " + ref_lines + "  ! across, down\n");
		outfile.write("Affine Matrix Row 1    (-) = " + m11 + " " + m12 + "       ! a b\n");
		outfile.write("Affine Matrix Row 2    (-) = " + m21 + " " + m22 + "       ! c d\n");
		outfile.write("Affine Offset Vector   (-) = " + t1 + " " + t2 + "         ! e f\n");
		outfile.write("File Type              (-) = RMG            ! [RMG, COMPLEX]\n");
		outfile.write("Interpolation Method   (-) = NN        ! [NN, Bilinear, Sinc]\n");
		outfile.close();
	
	if not os.path.exists(date + "_rect_dem.in"):
		outfile = open(date + "_rect_dem.in","w");
		outfile.write("Input Image File Name  (-) = " + dem_img_rmg + "      ! dimension of file to be rectified\n");
		outfile.write("Output Image File Name (-) = " + coreg_dem_rmg + " ! dimension of output\n");
		outfile.write("Input Dimensions       (-) = " + search_samps + " " + search_lines + "  ! across, down\n");
		outfile.write("Output Dimensions      (-) = " + ref_samps + " " + ref_lines + "  ! across, down\n");
		outfile.write("Affine Matrix Row 1    (-) = " + m11 + " " + m12 + "       ! a b\n");
		outfile.write("Affine Matrix Row 2    (-) = " + m21 + " " + m22 + "       ! c d\n");
		outfile.write("Affine Offset Vector   (-) = " + t1 + " " + t2 + "         ! e f\n");
		outfile.write("File Type              (-) = RMG            ! [RMG, COMPLEX]\n");
		outfile.write("Interpolation Method   (-) = NN        ! [NN, Bilinear, Sinc]\n");
		outfile.close();
	
	if not os.path.exists(coreg_dem_hillshade_rmg):
		cmd = "\nrect " + date + "_rect.in\n";
		subprocess.call(cmd,shell=True);
	
	if not os.path.exists(coreg_dem_rmg):
		cmd = "\nrect " + date + "_rect_dem.in\n";
		subprocess.call(cmd,shell=True);
	
	coreg_dem_hillshade = coreg_dem_hillshade_rmg.replace("rmg","img");
	coreg_dem	    = coreg_dem_rmg.replace("rmg","img");
	
	if not os.path.exists(coreg_dem_hillshade):
		cmd  = "\nrmg2mag_phs " + coreg_dem_hillshade_rmg + " " + coreg_dem_hillshade + " " + coreg_dem_hillshade.replace("img","phs") + " " + ref_samps + "\n";
		cmd += "\nrm " + coreg_dem_hillshade.replace("img","phs") + "\n";
		cmd += "\ncp -p " + REF_DEM.replace("img","hdr") + " " + coreg_dem_hillshade.replace("img","hdr") + "\n";
		subprocess.call(cmd,shell=True);
	
	if not os.path.exists(coreg_dem):
		cmd  = "\nrmg2mag_phs " + coreg_dem_rmg + " " + coreg_dem + " " + coreg_dem.replace("img","phs") + " " + ref_samps + "\n";
		cmd += "\nrm " + coreg_dem.replace("img","phs") + "\n";
		cmd += "\ncp -p " + REF_DEM.replace("img","hdr") + " " + coreg_dem.replace("img","hdr") + "\n";
		subprocess.call(cmd,shell=True);
	
	coreg_dem_grd = coreg_dem_rmg.replace("rmg","grd");
	
	if not os.path.exists(coreg_dem_grd):
		cmd  = "\n/home/akm26/Downloads/gdal-1.8.0/apps/gdal_translate -of GMT " + coreg_dem + " " + coreg_dem_grd + "\n";
		cmd += "\ngrdclip " + coreg_dem_grd + " -Sb1/NaN -G" + coreg_dem_grd + "\n";
		subprocess.call(cmd,shell=True);
	
	if not os.path.exists(date + "_new_hist.ps"):
		cmd  = "\ngrdmath " + REF_DEM_GRD + " " + coreg_dem_grd + " SUB = diff.grd\n";
		cmd += "\ngrd2xyz diff.grd | gawk '$0 !~ /a/ {print $3}' | pshistogram -JX10c -W1 -R-75/75/0/3000 -Ba15g15:\"Difference (m)\":/a1000g1000:\"# of points\":WeSn -Gblack -P --LABEL_FONT_SIZE=14 > " + date + "_new_hist.ps\n";
		cmd += "\ngrdclip diff.grd -Sb-50/NaN -Sa50/NaN -Gdiff.grd\n";
		cmd += "\ngrdinfo -L2 diff.grd\n";
		cmd += "\ngrdimage diff.grd -Jx1:1000000 -R" + dem_off_ice + " -Q -P -Cdiff.cpt > " + date + "_new_diff.ps\n";
		cmd += "\nps2raster -A -Tf " + date + "_new_diff.ps\n";
		cmd += "\nps2raster -A -Tf " + date + "_new_hist.ps\n";
		cmd += "\ncp -p diff.grd " + date + "_new_diff_clip.grd\n";
		cmd += "\nrm diff.grd\n";
		subprocess.call(cmd,shell=True);

	if os.path.exists(dem_zone41_path):
		os.remove(dem_zone41_path);

	os.remove(dem_rmg);
	os.remove(dem_img_rmg);
	os.remove(coreg_dem_hillshade_rmg);
	os.remove(coreg_dem_rmg);


	return;


if __name__ == "__main__":
	
	import os;
	import sys;

	
	assert len(sys.argv) > 1, "\n***** ERROR: demCoregister.py requires 1 argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	demCoregister(sys.argv[1]);

	exit();








