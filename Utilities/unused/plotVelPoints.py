#!/usr/bin/python


# plotVelPoints.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def plotVelPoints(dvdt_path, vel_values_path):

	import math;
	import matplotlib;
	import matplotlib.pyplot as plt;
	import numpy;
	import os;
	import pylab;
	import scipy;

	assert os.path.exists(dvdt_path), "\n***** ERROR: " + dvdt_path + " does not exist\n";
	assert os.path.exists(vel_values_path), "\n***** ERROR: " + vel_values_path + " does not exist\n";

	dvdts = {};

	xmin = 1000000000.0;
	xmax = -1000000000.0;
	ymin = 1000000000.0;
	ymax = -1000000000.0;


	infile = open(dvdt_path, "r");

	infile.readline();

	for line in infile:

		elements = line.split();

		x = elements[0];
		y = elements[1];

		if float(x) < xmin:
			xmin = float(x);

		elif float(x) > xmax:
			xmax = float(x);

		if float(y) < ymin:
			ymin = float(y);

		elif float(y) > ymax:
			ymax = float(y);

		dvdts[x + " " + y] = line.strip();	

	infile.close();	

	width  = int((xmax - xmin) / 120.) + 1;
	length = int((ymax - ymin) / 120.) + 1;

	print(width, length);
	print(xmin, xmax, ymin, ymax);

	xs = scipy.ones((length,width)) * scipy.arange(xmin,xmax + 120,120.);
	ys = (scipy.ones((width,length)) * scipy.arange(ymax,ymin - 120,-120.)).transpose();

	dvdt_array      = scipy.zeros((length,width)) * scipy.nan;
	intercept_array = scipy.zeros((length,width)) * scipy.nan;
	interval_array  = scipy.zeros((length,width)) * scipy.nan;
	firstdate_array = scipy.zeros((length,width)) * scipy.nan;

	for coord in dvdts:

		elements  = dvdts[coord].split();
		x         = float(elements[0]);
		y         = float(elements[1]);
		dvdt      = float(elements[2]);
		intercept = float(elements[4]);
		firstdate = float(elements[7]);
		interval  = float(elements[19]);

		x_ind = int((x - xmin) / 120.);
		y_ind = int((ymax - y) / 120.);

		dvdt_array[y_ind, x_ind]      = dvdt;
		intercept_array[y_ind, x_ind] = intercept;
		interval_array[y_ind, x_ind]  = interval;
		firstdate_array[y_ind, x_ind] = firstdate;

	vels  = {};

	infile = open(vel_values_path,"r");

	for line in infile:

		if line.find(">") > -1:
			continue;

		x, y, vel, date, unc = line.split();

		if x + " " + y not in vels:
			vels[x + " " + y] = scipy.asarray([float(vel), float(date), float(unc)]);
		else:
			vels[x + " " + y] = scipy.vstack((vels[x + " " + y],[float(vel), float(date), float(unc)]));

	infile.close();

	polygons_xs    = [];
	polygons_ys    = [];
	i              = 0;
	polygons_xs.append([]);
	polygons_ys.append([]);

	infile = open("/data/akm/Elias/Boundaries/StEliasMtn_ice_utm7v.gmt","r");

	infile.readline();

	for line in infile:

		if line.find("#") > -1:
			continue;

		elif line.find(">") > -1:
			i += 1;
			polygons_xs.append([]);
			polygons_ys.append([]);

		else:
			elements = line.split();
			polygons_xs[i].append(float(elements[0]));
			polygons_ys[i].append(float(elements[1]));

	infile.close();


#	Finished reading in data, display figures

	fig1    = plt.figure(1);
	imgplot = plt.pcolor(xs, ys, dvdt_array, cmap="jet", vmin=-1.0, vmax=1.0);
	plt.colorbar();

	for i in range(0, len(polygons_xs)):
		plt.plot(polygons_xs[i], polygons_ys[i], "b-");

	plots = [];
	plots.append(imgplot);

	def onclick(event):

		x = xmin + 120 * math.floor((event.xdata - xmin) / 120);
		y = ymax - 120 * math.floor((ymax - event.ydata) / 120);
		x_ind = int((x - xmin) / 120.);
		y_ind = int((ymax - y) / 120.);

		if str(x) + " " + str(y) not in vels:
			return;

		dsdt      = dvdt_array[y_ind, x_ind];
		intercept = intercept_array[y_ind, x_ind];
		interval  = interval_array[y_ind, x_ind];
		firstdate = firstdate_array[y_ind, x_ind];
		dsdt_str  = str(dsdt);
		cur_vels  = vels[str(x) + " " + str(y)];

#		print("Mouse_X, X, X_Index, Xs[Y_Index, X_index], Mouse_Y, Y, Y_Index, Ys[Y_Index, X_index], DVDT[Y_Index, X_Index");
#		print(event.xdata, x, x_ind, xs[y_ind, x_ind], event.ydata, y, y_ind, ys[y_ind, x_ind], dvdt_array[y_ind, x_ind]);
		print(intercept, interval, firstdate, dvdt_array[y_ind, x_ind]);

		plt.figure(1);
		plots.append(plt.plot(x, y, "ro"));

		if len(plots) > 2:
			cur_point = plots[1][0];
			cur_point.remove();
			plots.remove([cur_point]);

		fig2 = plt.figure(2); 
		fig2.clf();
		speed_plt = plt.errorbar(cur_vels[:,1], cur_vels[:,0], yerr=cur_vels[:,2], fmt='bo');
		plt.plot([firstdate, interval + firstdate], [intercept, intercept + dvdt_array[y_ind, x_ind] * interval]);
		plt.xlabel("Year");
		plt.ylabel("Speed");
		plt.title("Acceleration from weighted regression");
		plt.text(firstdate + interval / 2, intercept, "x: " + str(x) + "\ny: " + str(y) + "\nds/dt: " + dsdt_str[ : dsdt_str.rfind(".") + 3]);

		plt.show();

	cid = fig1.canvas.mpl_connect('button_press_event', onclick);

	plt.show();

	return;


if __name__ == "__main__":

	import os;
	import sys;

	assert len(sys.argv) > 2, "\n***** ERROR: elevProfile.py requires 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";

	plotVelPoints(sys.argv[1], sys.argv[2]);

	exit();


