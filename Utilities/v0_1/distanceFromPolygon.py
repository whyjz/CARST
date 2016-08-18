#!/usr/bin/python


# distanceFromPolygon.py
# Author: Andrew Kenneth Melkonian
# All rights reserved



def distanceFromPolygon(input_grd_path, polygon_txt_path):

	import math;
	import matplotlib;
	import matplotlib.pyplot;
	import os;
	import scipy;
	from scipy.io import netcdf;
	from scipy.sparse import lil_matrix;
	import subprocess;

	assert os.path.exists(input_grd_path), "\n***** ERROR: " + input_grd_path + " does not exist\n";
	assert os.path.exists(polygon_txt_path), "\n***** ERROR: " + polygon_txt_path + " does not exist\n";

	f      = netcdf.netcdf_file(input_grd_path,"r",False);
	x      = f.variables["x"].data;
	y      = f.variables["y"].data;
	values = f.variables["z"].data[:];
	f.close();

	width  = f.dimensions["x"];
	length = f.dimensions["y"];

	min_x  = min(x);
	max_x  = max(x);
	min_y  = min(y);
	max_y  = max(y);

	inc = int((max(x) - min(x)) / (width - 1));

	polygon_xs = scipy.zeros((length,width));
	polygon_ys = scipy.zeros((length,width));
	polygon_xs[polygon_xs < 1] = scipy.nan;
	polygon_ys[polygon_ys < 1] = scipy.nan;

#	Read in points, initialize fluxes

	points = {};

	infile = open(polygon_txt_path, "r");

	for line in infile:

		if line.find(">") > -1 or line.find("#") > -1:
			continue;

		elements = line.strip().split();
		utm_x    = elements[0];
		utm_y    = elements[1];

		j = int(round((float(utm_x) - float(min_x)) / int(inc)));
		i = int(round((float(utm_y) - float(min_y)) / int(inc)));

		if not (i >= 0 and i < length and j >= 0 and j < width):
			continue;

		polygon_xs[i,j] = j;
		polygon_ys[i,j] = i;


	infile.close();	

	for i in range(0, length):

		for j in range(0, width):

			if scipy.isnan(values[i,j]):
				continue;

			min_k = i - 20;
			max_k = i + 20;
			min_m = j - 20;
			max_m = j + 20;

			if min_k < 0:
				min_k = 0;

			if max_k >= length:
				max_k = length - 1;

			if min_m < 0:
				min_m = 0;

			if max_m >= width:
				max_m = width - 1;

			nearby_points = polygon_xs[min_k:max_k, min_m:max_m];
			nearby_xs     = nearby_points[~scipy.isnan(nearby_points)];

			nearby_points = polygon_ys[min_k:max_k, min_m:max_m];
			nearby_ys     = nearby_points[~scipy.isnan(nearby_points)];

			distances = (((nearby_xs - j)*inc)**2 + ((nearby_ys - i)*inc)**2)**0.5;

			min_dist  = str(((20*inc)**2 + (20*inc)**2)**0.5);

			if len(distances) > 0:
				min_dist = str(min(distances));

			print(str(x[j]) + " " + str(y[i]) + " " + min_dist);

	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: distanceFromPolygon.py requires two arguments, " + str(len(sys.argv)) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	
	distanceFromPolygon(sys.argv[1], sys.argv[2]);

	exit();

