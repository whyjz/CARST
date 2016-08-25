#!/usr/bin/python


# hypsometryDHDT.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def hypsometryDHDT(dhdt_txt_path):

	import os;

	assert os.path.exists(dhdt_txt_path), "\n***** ERROR: " + dhdt_txt_path + " does not exist\n";

	index        = dhdt_txt_path.rfind("/");
	dhdt_txt_dir = dhdt_txt_path[ : index];

	if index < 0:
		dhdt_txt_dir = ".";

#	px_area in m^2
	px_area = 120.**2;

	hypsometry_area = {};
	hypsometry_dhdt = {};
	hypsometry_unc  = {};

	import math;

	infile = open(dhdt_txt_path, "r");

	infile.readline();

	for line in infile:

		elements = line.split();
		dhdt     = float(elements[2]);
		unc      = float(elements[3]);
		ref_elev = math.floor(float(elements[8]));

		ref_elev = str(int(ref_elev - ref_elev % 10));

		if ref_elev not in hypsometry_area:
			hypsometry_area[ref_elev] = px_area;
			hypsometry_dhdt[ref_elev] = dhdt;
			hypsometry_unc[ref_elev]  = unc * px_area;

		else:
			hypsometry_area[ref_elev] += px_area;
			hypsometry_dhdt[ref_elev] += dhdt;
			hypsometry_unc[ref_elev]  += unc * px_area;

	infile.close();

	name = dhdt_txt_path[dhdt_txt_path.rfind("/") + 1 : dhdt_txt_path.rfind(".")];
	hypsometry_txt_path = name + "_hyp.txt";

	max_area = 0.0;
	max_elev = 0.0;
	max_dvdt = -100.0;
	min_dvdt = 100.0;
	min_dhdt = 10.0;
	max_dhdt = -10.0;

	outfile = open(hypsometry_txt_path, "w");

	outfile.write("Elevation(m)     Area(km2)     DVDT(km3/yr)     DVDT_UNC(km3/yr)     DHDT(m/yr)\n");

	for ref_elev in hypsometry_dhdt:

		area = hypsometry_area[ref_elev] / 1e6;
		dvdt = hypsometry_dhdt[ref_elev] * px_area / 1e9;
		unc  = 1.96 * hypsometry_unc[ref_elev] / ((hypsometry_area[ref_elev] / (960. * 960.))**0.5) / 1e9;
		dhdt = hypsometry_dhdt[ref_elev] * px_area / hypsometry_area[ref_elev];
		
		if float(ref_elev) > max_elev:
			max_elev = float(ref_elev);

		if area > max_area:
			max_area = area;

		if dvdt > max_dvdt:
			max_dvdt = dvdt;

		elif dvdt < min_dvdt:
			min_dvdt = dvdt;

		if dhdt > max_dhdt:
			max_dhdt = dhdt;

		elif dhdt < min_dhdt:
			min_dhdt = dhdt;

		outfile.write(ref_elev + " " + str(area) + " " + str(dvdt) + " " + str(unc) + " " + str(dhdt) + "\n");

	outfile.close();

	max_elev = int(round(max_elev, -2)) + 100;
#	print(min_dvdt, max_dvdt);
#	print(hypsometry_dhdt["590"], hypsometry_dhdt["600"], hypsometry_dhdt["610"], hypsometry_dhdt["620"], hypsometry_dhdt["630"], hypsometry_dhdt["640"], hypsometry_dhdt["650"], hypsometry_dhdt["660"], hypsometry_dhdt["670"], hypsometry_dhdt["680"]);

	cwd              = os.getcwd();
	hyp_ps_path      = hypsometry_txt_path.replace(".txt", ".ps");
	dhdt_hyp_ps_path = hyp_ps_path.replace(".ps", "_dhdt.ps");
	dvdt_hyp_ps_path = hyp_ps_path.replace(".ps", "_dvdt.ps");

	max_elev = 1300;
	min_dhdt = -5.0;
	max_dhdt = 1.0;

	import subprocess;

	cmd  = "\ngawk 'NR > 1 {print $1\" \"$2}' " + cwd + "/" + hypsometry_txt_path + " | psxy -X3c -Y30c -JX10c -R0/" + str(max_elev) + "/0/" + str(max_area) + " -Ss0.2c -Gdarkgreen -W0.3p,darkgray --PAPER_MEDIA=A3 -P -K > " + hyp_ps_path + "\n";
	cmd += "\npsbasemap -JX10c -R0/" + str(max_elev) + "/0/" + str(max_area) + " -Bf100a300g100:\"\":/a20g40:\"Area (km@+2@+)\"::,::.\"\":WeSn -O -K >> " + hyp_ps_path + "\n";
	cmd += "\ngawk 'NR > 1 {print $1\" \"$3}' " + cwd + "/" + hypsometry_txt_path + " | psxy -Y-11.2c -JX10c -R0/" + str(max_elev) + "/" + str(min_dvdt) + "/" + str(max_dvdt) + " -Ss0.2c -Gpurple -W0.3p,darkgray -O -K >> " + hyp_ps_path + "\n";
	cmd += "\npsbasemap -JX10c -R0/" + str(max_elev) + "/" + str(min_dvdt) + "/" + str(max_dvdt) + " -Bf100a300g100:\"\":/a0.02g0.01:\"dV/dt (km@+3@+)\"::,::.\"\":WeSn -O -K >> " + hyp_ps_path + "\n";
	cmd += "\necho \"0 0\\n" + str(max_elev) + " 0\" | psxy -JX10c -R0/" + str(max_elev) + "/" + str(min_dvdt) + "/" + str(max_dvdt) + " -W1p,black -O -K >> " + hyp_ps_path + "\n";
	cmd += "\ngawk 'NR > 1 {print $1\" \"$5}' " + cwd + "/" + hypsometry_txt_path + " | psxy -Y-11.2c -JX10c -R0/" + str(max_elev) + "/" + str(min_dhdt) + "/" + str(max_dhdt) + " -Ss0.2c -W0.3p,darkgray -Gred -O -K >> " + hyp_ps_path + "\n";
	cmd += "\npsbasemap -JX10c -R0/" + str(max_elev) + "/" + str(min_dhdt) + "/" + str(max_dhdt) + " -Bf100a300g100:\"Elevation (m)\":/a0.4g0.2:\"dh/dt (m yr@+-1@+)\"::,::.\"\":WeSn -O -K >> " + hyp_ps_path + "\n";	
	cmd += "\necho \"0 0\\n" + str(max_elev) + " 0\" | psxy -JX10c -R0/" + str(max_elev) + "/" + str(min_dhdt) + "/" + str(max_dhdt) + " -W1p,black -O >> " + hyp_ps_path + "\n";
	cmd += "\nps2raster -A -Tf " + hyp_ps_path + "\n";
	print(cmd);
	subprocess.call(cmd, shell=True);

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: hypsometryDHDT.py requires one argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	hypsometryDHDT(sys.argv[1]);

	exit();


