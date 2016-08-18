#!/usr/bin/python


# dhdtReport.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# DESCRIPTION
# ***********
# dhdtReport.py takes as input a list of paths to GMT polygon files defining glacier bounds and a list of paths to netCDF grid files containing dh/dt.
#		It returns a Latex-format table with glacier names as rows and glacier areas, as well as volume/average mass balance from each dh/dt grid as columns.


# USAGE
# *****
# python dhdtReport.py /path/to/glacier_polygon_list.txt /path/to/dhdt_grids.txt
#	/path/to/glacier_polygon_list.txt: Path to list of glacier GMT polygon files
#	/path/to/dhdt_grids.txt:	   Path to list of dh/dt grids


def dhdtReport(glacier_list_path, dhdt_grd_list_path, utm_zone):

	assert os.path.exists(glacier_list_path), "\n***** ERROR: " + glacier_list_path + " does not exist\n";
	assert os.path.exists(dhdt_grd_list_path), "\n***** ERROR: " + dhdt_grd_list_path + " does not exist\n";	

	corr_width = 1800.;

	glacier_paths  = {};
	glacier_bounds = {};
	glacier_types  = {};

	import re;
	import subprocess;

	dhdt_grd_paths = {};

	infile = open(dhdt_grd_list_path, "r");

	for line in infile:

		if line.find("#") > -1:
			continue;

		line 		     = line.strip();
		dhdt_grd_paths[line] = line;

		cmd  = "\ngrdinfo " + line + "\n";
		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		info = pipe.read().strip();
		pipe.close();

		dhdt_xmin = info[re.search("x_min\:\s+",info).end(0) : re.search("x_min\:\s+\-*\d*\.\d+",info).end(0)];
		dhdt_ymin = info[re.search("y_min\:\s+",info).end(0) : re.search("y_min\:\s+\-*\d*\.\d+",info).end(0)];
		dhdt_xmax = info[re.search("x_max\:\s+",info).end(0) : re.search("x_max\:\s+\-*\d*\.\d+",info).end(0)];
		dhdt_ymax = info[re.search("y_max\:\s+",info).end(0) : re.search("y_max\:\s+\-*\d*\.\d+",info).end(0)];	

	infile.close();

	infile = open(glacier_list_path, "r");

	for line in infile:

		if not os.path.exists(line.strip()):
			continue;

#		if line.find("Ino") < 0:
#			continue;

		line 		    = line.strip();
		glacier_paths[line] = line;

		infile = open(line, "r");

		while 1:

			bound_line = infile.readline();

			if not bound_line:
				break;

			if bound_line.find("DRG") > -1:
				elements = bound_line.split("|");
				glactype = elements[10];
				glacier_types[line] = glactype;
				break;

		infile.close();

		cmd  = "\ngmtinfo -C " + line + "\n";
		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		info = pipe.read().strip().split();
		pipe.close();

		xmin = info[0];
		xmax = info[1];
		ymin = info[2];
		ymax = info[3];

		cmd  = "\necho \"" + xmin + " " + ymin + "\n" + xmax + " " + ymax + "\" | mapproject -Ju" + utm_zone + "/1:1 -F -C\n";
		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		info = pipe.read().strip().split();
		pipe.close();

		xmin = info[0];
		ymin = info[1];
		xmax = info[2];
		ymax = info[3];

		glacier_bounds[line] = "-R" + xmin + "/" + ymin + "/" + xmax + "/" + ymax + "r";

	infile.close();

	ecrs = {};
	uncs = {};

	for dhdt_grd_path in dhdt_grd_paths:

		dhdt_label   = dhdt_grd_path[dhdt_grd_path.rfind("/") + 1 : dhdt_grd_path.rfind(".")];
		unc_grd_path = dhdt_grd_path.replace("dhdt", "uncs");

		for glacier_path in glacier_paths:

#			if glacier_path.find("Ino") < 0:
#				continue;

			glacier_label        = glacier_path[glacier_path.rfind("/") + 1 : glacier_path.rfind("_ice")];
			grid_path            = glacier_label + "_" + dhdt_label + ".grd";
			pdf_path             = glacier_label + "_ice_only.pdf";
			ice_only_grd_path    = glacier_label + "_utm" + utm_zone.lower() + "_ice_only.grd";
			glacier_ecr_grd_path = glacier_label + "_" + dhdt_label + "_utm" + utm_zone.lower() + ".grd";
			glacier_unc_grd_path = glacier_ecr_grd_path.replace("dhdt", "uncs");

			glacier_types[glacier_label] = glacier_types[glacier_path];

			if os.path.exists(glacier_ecr_grd_path) and os.path.exists(glacier_unc_grd_path):

				if glacier_label in ecrs:
					ecrs[glacier_label] += " " + glacier_ecr_grd_path;
					uncs[glacier_label] += " " + glacier_unc_grd_path;

				else:
					ecrs[glacier_label] = glacier_ecr_grd_path;
					uncs[glacier_label] = glacier_unc_grd_path;

				continue;

			cmd  = "\nmapproject " + glacier_path + " -Ju" + utm_zone + "/1:1 -F -C > temp_ice.gmt\n";
			cmd += "\ngrdmask temp_ice.gmt -R" + dhdt_grd_path + " -Gice.grd -NNaN/NaN/1\n";
			subprocess.call(cmd,shell=True);

			os.remove("temp_ice.gmt");

			cmd  = "\ngrdvolume ice.grd\n";
			pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
			info = pipe.read().split();
			pipe.close();

			area = info[1];	

#			if area == "0":
#				os.remove(glacier_path);
#				os.remove("ice.grd");
#				continue;

			if os.path.exists(glacier_path.replace("ice", "rock")):

				cmd  = "\nmapproject " + glacier_path.replace("ice", "rock") + " -Ju" + utm_zone + "/1:1 -F -C > temp_rock.gmt\n";
				cmd += "\ngrdmask temp_rock.gmt -R" + dhdt_grd_path + " -Grock.grd -N1/NaN/NaN\n";
				cmd += "\ngrdmath ice.grd rock.grd OR = " + ice_only_grd_path + "\n";
				subprocess.call(cmd, shell=True);

				os.remove("temp_rock.gmt");
				os.remove("rock.grd");
				os.remove("ice.grd");

			else:
				os.rename("ice.grd", ice_only_grd_path);

			cmd  = "\ngrdmath " + dhdt_grd_path + " " + ice_only_grd_path + " OR = " + glacier_ecr_grd_path + "\n";
			cmd += "\ngrdmath " + unc_grd_path + " " + ice_only_grd_path + " OR = " + glacier_unc_grd_path + "\n";
			cmd += "\ngrdcut " + ice_only_grd_path + " " + glacier_bounds[glacier_path] + " -G" + ice_only_grd_path + "\n";
			cmd += "\ngrdcut " + glacier_ecr_grd_path + " " + glacier_bounds[glacier_path] + " -G" + glacier_ecr_grd_path + "\n";
			cmd += "\ngrdcut " + glacier_unc_grd_path + " " + glacier_bounds[glacier_path] + " -G" + glacier_unc_grd_path + "\n";

			if not os.path.exists(pdf_path):
				ps_path = pdf_path.replace("pdf", "ps");
				cmd += "\nmakecpt -Crainbow -T0/2/1 > mask.cpt\n";
				cmd += "\ngrdimage " + ice_only_grd_path + " -Jx1:200000 " + glacier_bounds[glacier_path] + " -Cmask.cpt -Q -P > " + ps_path + "\n";
				cmd += "\nps2raster -A -Tf " + ps_path + "\n";

			subprocess.call(cmd, shell=True);

			if glacier_label in ecrs:
				ecrs[glacier_label] += " " + glacier_ecr_grd_path;
				uncs[glacier_label] += " " + glacier_unc_grd_path;

			else:
				ecrs[glacier_label] = glacier_ecr_grd_path;
				uncs[glacier_label] = glacier_unc_grd_path;	

	tw_areas          = {};
	tw_volumes        = {};
	tw_uncs           = {};
	common_tw_areas   = {};
	common_tw_volumes = {};
	common_tw_uncs    = {};

	land_areas          = {};
	land_volumes        = {};
	land_uncs           = {};
	common_land_areas   = {};
	common_land_volumes = {};
	common_land_uncs    = {};
	

	output = "Glacier     1952-2013 DH/DT Area     1952-2013 DV/DT     1952-2013 DH/DT     2012-2014 DH/DT Area     1952-2013 DV/DT     1952-2013 DH/DT     2012-2014 DH/DT Area     2012-2014 DV/DT     2012-2014 DH/DT\n";

	for glacier in ecrs:

		ecr_grds = ecrs[glacier].split();
		unc_grds = uncs[glacier].split();

		if len(ecr_grds) > 1:

			cmd = "\ngrdmath " + ecr_grds[0] + " " + ecr_grds[1] + " OR = temp.grd\n";

			for i in range(2, len(ecr_grds)):

				cmd += "\ngrdmath temp.grd " + ecr_grds[i] + " OR = temp.grd\n";

			subprocess.call(cmd, shell=True);

		output += glacier + " " + glacier_types[glacier];

		for i in range(0, len(ecr_grds)):

			cmd  = "\ngrdvolume " + ecr_grds[i] + "\n";
			pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
			info = pipe.read().split();
			pipe.close();

			area   = info[1];
			volume = info[2];
			dhdt   = info[3];

			if area == "0":
				continue;

			cmd  = "\ngrdvolume " + unc_grds[i] + "\n";
			pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
			info = pipe.read().split();
			pipe.close();

			unc_area   = info[1];
			unc_volume = info[2];
			unc_dhdt   = info[3];
			unc_dmdt   = str(round(1.96 * float(unc_volume) / ((float(unc_area) / (corr_width**2))**0.5) / 1e9 * 0.9, 2));
			unc_dhdt   = str(round(1.96 * float(unc_volume) / ((float(unc_area) / (corr_width**2))**0.5) / float(unc_area) * 0.9, 2));

			output += " " + str(round(float(area) / 1e6, 2)) + " " + str(round(float(volume) / 1e9 * 0.9, 2)) + "+/-" + unc_dmdt + " " + str(round(float(dhdt) * 0.9, 2)) + "+/-" + unc_dhdt;

			if glacier_types[glacier] == "0100":

				if i not in tw_areas:
					tw_areas[i]   = float(area);
					tw_volumes[i] = float(volume);
					tw_uncs[i]    = float(unc_volume);

				else:
					tw_areas[i]   += float(area);
					tw_volumes[i] += float(volume);
					tw_uncs[i]    += float(unc_volume);

			elif glacier_types[glacier] == "0000":

				if i not in land_areas:
					land_areas[i]   = float(area);
					land_volumes[i] = float(volume);
					land_uncs[i]     = float(unc_volume);

				else:
					land_areas[i]   += float(area);
					land_volumes[i] += float(volume);
					land_uncs[i]    += float(unc_volume);

			if not os.path.exists("temp.grd"):
				continue;

			cmd = "\ngrdmath " + ecr_grds[i] + " temp.grd OR = temp2.grd\n";
			subprocess.call(cmd, shell=True);

			cmd = "\ngrdmath " + unc_grds[i] + " temp.grd OR = temp3.grd\n";
			subprocess.call(cmd, shell=True);

			cmd  = "\ngrdvolume temp2.grd\n";
			pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
			info = pipe.read().split();
			pipe.close();

			common_area   = info[1];
			common_volume = info[2];
			common_dhdt   = info[3];

			if common_area == "0":
				continue;

			cmd  = "\ngrdvolume temp3.grd\n";
			pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
			info = pipe.read().split();
			pipe.close();

			unc_common_area   = info[1];
			unc_common_volume = info[2];
			unc_common_dhdt   = info[3];
			unc_common_dmdt   = str(round(1.96 * float(unc_common_volume) / ((float(unc_common_area) / (corr_width**2))**0.5) / 1e9 * 0.9, 2));
			unc_common_dhdt   = str(round(1.96 * float(unc_common_volume) / ((float(unc_common_area) / (corr_width**2))**0.5) / float(unc_common_area) * 0.9, 2));

			if area != common_area:
				output += " " + str(round(float(common_area) / 1e6, 2)) + " " + str(round(float(common_volume) / 1e9 * 0.9, 2)) + "+/-" + unc_common_dmdt + " " + str(round(float(common_dhdt) * 0.9, 2)) + "+/-" + unc_common_dhdt;

			if glacier_types[glacier] == "0100":

				if i not in common_tw_areas:
					common_tw_areas[i]   = float(common_area);
					common_tw_volumes[i] = float(common_volume);
					common_tw_uncs[i]    = float(unc_common_volume);

				else:
					common_tw_areas[i]   += float(common_area);
					common_tw_volumes[i] += float(common_volume);
					common_tw_uncs[i]    += float(unc_common_volume);

			elif glacier_types[glacier] == "0000":

				if i not in common_land_areas:
					common_land_areas[i]   = float(common_area);
					common_land_volumes[i] = float(common_volume);
					common_land_uncs[i]    = float(unc_common_volume);

				else:
					common_land_areas[i]   += float(common_area);
					common_land_volumes[i] += float(common_volume);
					common_land_uncs[i]    += float(unc_common_volume);

			os.remove("temp2.grd");

		if os.path.exists("temp.grd"):
			os.remove("temp.grd");

		output  = output.strip();
		output += "\n";

	output += "Tidewater 0100";

	for i in tw_volumes:

		unc_tw_dvdt = str(round(1.96 * tw_uncs[i] / ((tw_areas[i] / (corr_width**2))**0.5) / 1e9, 2));
		unc_tw_dhdt = str(round(1.96 * tw_uncs[i] / ((tw_areas[i] / (corr_width**2))**0.5) / tw_areas[i] * 0.9, 2));
		unc_common_tw_dmdt = str(round(1.96 * common_tw_uncs[i] / ((common_tw_areas[i] / (corr_width**2))**0.5) / 1e9 * 0.9, 2));
		unc_common_tw_dhdt = str(round(1.96 * common_tw_uncs[i] / ((common_tw_areas[i] / (corr_width**2))**0.5) / common_tw_areas[i] * 0.9, 2));	

		output += " " + str(round(tw_areas[i] / 1e6, 2)) + " " + str(round(tw_volumes[i] / 1e9 * 0.9, 2)) + "+/-" + unc_tw_dvdt + " " + str(round(tw_volumes[i] / tw_areas[i] * 0.9, 2)) + "+/-" + unc_tw_dhdt;

		if common_tw_areas[i] != tw_areas[i]:
			output += " " + str(round(common_tw_areas[i] / 1e6, 2)) + " " + str(round(common_tw_volumes[i] / 1e9 * 0.9, 2)) + "+/-" + unc_common_tw_dmdt + " " + str(round(common_tw_volumes[i] / common_tw_areas[i] * 0.9, 2)) + "+/-" + unc_common_tw_dhdt;

	output += "\nLand 0000";

	for i in land_volumes:

		unc_land_dvdt = str(round(1.96 * land_uncs[i] / ((land_areas[i] / (corr_width**2))**0.5) / 1e9, 2));
		unc_land_dhdt = str(round(1.96 * land_uncs[i] / ((land_areas[i] / (corr_width**2))**0.5) / land_areas[i] * 0.9, 2));
		unc_common_land_dmdt = str(round(1.96 * common_land_uncs[i] / ((common_land_areas[i] / (corr_width**2))**0.5) / 1e9 * 0.9, 2));
		unc_common_land_dhdt = str(round(1.96 * common_land_uncs[i] / ((common_land_areas[i] / (corr_width**2))**0.5) / common_land_areas[i] * 0.9, 2));	

		output += " " + str(round(land_areas[i] / 1e6, 2)) + " " + str(round(land_volumes[i] / 1e9 * 0.9, 2)) + "+/-" + unc_land_dvdt + " " + str(round(land_volumes[i] / land_areas[i] * 0.9, 2)) + "+/-" + unc_land_dhdt;

		if common_land_areas[i] != land_areas[i]:
			output += " " + str(round(common_land_areas[i] / 1e6, 2)) + " " + str(round(common_land_volumes[i] / 1e9 * 0.9, 2)) + "+/-" + unc_common_land_dmdt + " " + str(round(common_land_volumes[i] / common_land_areas[i] * 0.9, 2)) + "+/-" + unc_common_land_dhdt;

	print(output);

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 3, "\n***** ERROR: dhdtReport.py requires 3 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	dhdtReport(sys.argv[1], sys.argv[2], sys.argv[3]);

	exit();


