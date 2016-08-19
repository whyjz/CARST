#!/usr/bin/python


def velHyp(x_y_elev_vel_txt_path):

	import math;
	import os;
	import subprocess;

	assert os.path.exists(x_y_elev_vel_txt_path), "\n***** ERROR: \"" + x_y_elev_vel_txt_path + "\" not found, exiting...\n";

	BIN_SIZE = 10;
	T_WEIGHT = True;

	vels   = {};
	uncs   = {};
	times  = {};
	counts = {};

	vels_w   = {};
	uncs_w   = {};
	times_w  = {};
	counts_w = {};

	vels_sp   = {};
	uncs_sp   = {};
	times_sp  = {};
	counts_sp = {};

	vels_su   = {};
	uncs_su   = {};
	times_su  = {};
	counts_su = {};

	vels_a   = {};
	uncs_a   = {};
	times_a  = {};
	counts_a = {};

	infile = open(x_y_elev_vel_txt_path, "r");

	for line in infile:

		x, y, elev, median, mean, stdev, interval, winter_days, spring_days, summer_days, autumn_days, dec_year, vel = line.strip().split();

		bin_elev =  str(math.floor(float(elev) / BIN_SIZE));

		if bin_elev not in vels:

			vels[bin_elev]   = [];
			uncs[bin_elev]   = [];
			times[bin_elev]  = 0.0;
			counts[bin_elev] = 0;

			vels_w[bin_elev]   = [];
			uncs_w[bin_elev]   = [];
			times_w[bin_elev]  = 0.0;
			counts_w[bin_elev] = 0;
		
			vels_sp[bin_elev]   = [];
			uncs_sp[bin_elev]   = [];
			times_sp[bin_elev]  = 0.0;
			counts_sp[bin_elev] = 0;

			vels_su[bin_elev]   = [];
			uncs_su[bin_elev]   = [];
			times_su[bin_elev]  = 0.0;
			counts_su[bin_elev] = 0;

			vels_a[bin_elev]   = [];
			uncs_a[bin_elev]   = [];
			times_a[bin_elev]  = 0.0;
			counts_a[bin_elev] = 0;

		times[bin_elev]  += math.ceil(float(interval));
		counts[bin_elev] += 1;

		if T_WEIGHT:
			vels[bin_elev] += ([float(vel)] * int(math.ceil(float(interval))));
			uncs[bin_elev] += ([float(median)**2] * int(math.ceil(float(interval))));

		else:
			vels[bin_elev].append(float(vel));
			uncs[bin_elev].append(float(median)**2);

		if float(winter_days) > 0:
			times_w[bin_elev]  += math.ceil(float(winter_days));
			counts_w[bin_elev] += 1;

			if T_WEIGHT:
				vels_w[bin_elev] += ([float(vel)] * int(math.ceil(float(winter_days))));
				uncs_w[bin_elev] += ([float(median)**2] * int(math.ceil(float(winter_days))));

			else:
				vels_w[bin_elev].append(float(vel));
				uncs_w[bin_elev].append(float(median)**2);

		if float(spring_days) > 0:
			times_sp[bin_elev]  += math.ceil(float(spring_days));
			counts_sp[bin_elev] += 1;

			if T_WEIGHT:
				vels_sp[bin_elev] += ([float(vel)] * int(math.ceil(float(spring_days))));
				uncs_sp[bin_elev] += ([float(median)**2] * int(math.ceil(float(spring_days))));

			else:
				vels_sp[bin_elev].append(float(vel));
				uncs_sp[bin_elev].append(float(median)**2);

		if float(summer_days) > 0:
			times_su[bin_elev]  += math.ceil(float(summer_days));
			counts_su[bin_elev] += 1;

			if T_WEIGHT:
				vels_su[bin_elev] += ([float(vel)] * int(math.ceil(float(summer_days))));
				uncs_su[bin_elev] += ([float(median)**2] * int(math.ceil(float(summer_days))));

			else:
				vels_su[bin_elev].append(float(vel));
				uncs_su[bin_elev].append(float(median)**2);

		if float(autumn_days) > 0:
			times_a[bin_elev]  += math.ceil(float(autumn_days));
			counts_a[bin_elev] += 1;

			if T_WEIGHT:
				vels_a[bin_elev] += ([float(vel)] * int(math.ceil(float(autumn_days))));
				uncs_a[bin_elev] += ([float(median)**2] * int(math.ceil(float(autumn_days))));

			else:
				vels_a[bin_elev].append(float(vel));
				uncs_a[bin_elev].append(float(median)**2);

	infile.close();

	out_name    = x_y_elev_vel_txt_path[ : x_y_elev_vel_txt_path.rfind(".")] + "_hyp.txt";
	out_name_w  = x_y_elev_vel_txt_path[ : x_y_elev_vel_txt_path.rfind(".")] + "_winter_hyp.txt";
	out_name_sp = x_y_elev_vel_txt_path[ : x_y_elev_vel_txt_path.rfind(".")] + "_spring_hyp.txt";
	out_name_su = x_y_elev_vel_txt_path[ : x_y_elev_vel_txt_path.rfind(".")] + "_summer_hyp.txt";
	out_name_a  = x_y_elev_vel_txt_path[ : x_y_elev_vel_txt_path.rfind(".")] + "_autumn_hyp.txt";

	outfile    = open(out_name, "w");
	outfile_w  = open(out_name_w, "w");
	outfile_sp = open(out_name_sp, "w");
	outfile_su = open(out_name_su, "w");
	outfile_a  = open(out_name_a, "w");

	for bin_elev in vels:

		sorted_vels = sorted(vels[bin_elev]);
		median_vel  = sorted_vels[len(sorted_vels) / 2];
		mean_vel    = sum(sorted_vels) / len(sorted_vels);
		vel_unc     = (sum(uncs[bin_elev])**0.5 / counts[bin_elev]);
		outfile.write(str(float(bin_elev) * BIN_SIZE) + " " + str(median_vel) + " " + str(mean_vel) + " " + str(vel_unc) + " " + str(counts[bin_elev]) + " " + str(times[bin_elev]) + "\n");

		if bin_elev in vels_w and len(vels_w[bin_elev]) > 0:
			sorted_vels = sorted(vels_w[bin_elev]);
			median_vel  = sorted_vels[len(sorted_vels) / 2];
			mean_vel    = sum(sorted_vels) / len(sorted_vels);
			vel_unc     = (sum(uncs_w[bin_elev])**0.5 / counts_w[bin_elev]);
			outfile_w.write(str(float(bin_elev) * BIN_SIZE) + " " + str(median_vel) + " " + str(mean_vel) + " " + str(vel_unc) + " " + str(counts_w[bin_elev]) + " " + str(times_w[bin_elev]) + "\n");

		if bin_elev in vels_sp and len(vels_sp[bin_elev]) > 0:
			sorted_vels = sorted(vels_sp[bin_elev]);
			median_vel  = sorted_vels[len(sorted_vels) / 2];
			mean_vel    = sum(sorted_vels) / len(sorted_vels);
			vel_unc     = (sum(uncs_sp[bin_elev])**0.5 / counts_sp[bin_elev]);
			outfile_sp.write(str(float(bin_elev) * BIN_SIZE) + " " + str(median_vel) + " " + str(mean_vel) + " " + str(vel_unc) + " " + str(counts_sp[bin_elev]) + " " + str(times_sp[bin_elev]) + "\n");

		if bin_elev in vels_su and len(vels_su[bin_elev]) > 0:
			sorted_vels = sorted(vels_su[bin_elev]);
			median_vel  = sorted_vels[len(sorted_vels) / 2];
			mean_vel    = sum(sorted_vels) / len(sorted_vels);
			vel_unc     = (sum(uncs_su[bin_elev])**0.5 / counts_su[bin_elev]);
			outfile_su.write(str(float(bin_elev) * BIN_SIZE) + " " + str(median_vel) + " " + str(mean_vel) + " " + str(vel_unc) + " " + str(counts_su[bin_elev]) + " " + str(times_su[bin_elev]) + "\n");

		if bin_elev in vels_a and len(vels_a[bin_elev]) > 0:
			sorted_vels = sorted(vels_a[bin_elev]);
			median_vel  = sorted_vels[len(sorted_vels) / 2];
			mean_vel    = sum(sorted_vels) / len(sorted_vels);
			vel_unc     = (sum(uncs_a[bin_elev])**0.5 / counts_a[bin_elev]);
			outfile_a.write(str(float(bin_elev) * BIN_SIZE) + " " + str(median_vel) + " " + str(mean_vel) + " " + str(vel_unc) + " " + str(counts_a[bin_elev]) + " " + str(times_a[bin_elev]) + "\n");

	outfile.close();
	outfile_w.close();
	outfile_sp.close();
	outfile_su.close();
	outfile_a.close();

	return;


if __name__ == "__main__":

	import os;
	import sys;

	assert len(sys.argv) > 1, "\n***** ERROR: velHyp.py requires 1 argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: \"" + sys.argv[1] + "\" not found, exiting...\n";

	velHyp(sys.argv[1]);

	exit();

