#!/usr/bin/python


# velStrain.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def dirDeriv(val_mat, direction_mat, inc):

	import scipy;
	import scipy.linalg;
	import math;

	cell_angles  = scipy.flipud(scipy.array([[3 * math.pi / 4, math.pi / 2, math.pi / 4], [math.pi, scipy.nan, 0], [-3 * math.pi / 4, -1 * math.pi / 2, -1 * math.pi / 4]]));
	cell_incs    = scipy.array([[(inc**2 + inc**2)**0.5, inc, (inc**2 + inc**2)**0.5], [inc, scipy.nan, inc], [(inc**2 + inc**2)**0.5, inc, (inc**2 + inc**2)**0.5]]);
	angle        = direction_mat[1,1];
	vals_x       = scipy.cos(angle - direction_mat) * val_mat;
	vals_y       = scipy.sin(angle - direction_mat) * val_mat;

	cell_cosines_f = scipy.cos(angle - cell_angles);
	cell_cosines_b = scipy.cos(angle - cell_angles);
	cell_sines_f   = scipy.sin(angle - cell_angles);
	cell_sines_b   = scipy.sin(angle - cell_angles);

	cell_cosines_f[cell_cosines_f < 0.00001] = scipy.nan;
	cell_cosines_f = cell_cosines_f**2;
	cell_cosines_f = cell_cosines_f / sum(cell_cosines_f[~scipy.isnan(cell_cosines_f)]);
	cell_cosines_b[cell_cosines_b > -0.00001] = scipy.nan;
	cell_cosines_b = cell_cosines_b**2;
	cell_cosines_b = cell_cosines_b / sum(cell_cosines_b[~scipy.isnan(cell_cosines_b)]);
	cell_sines_f[cell_sines_f < 0.00001] = scipy.nan;
	cell_sines_f   = cell_sines_f**2;
	cell_sines_f   = cell_sines_f / sum(cell_sines_f[~scipy.isnan(cell_sines_f)]);
	cell_sines_b[cell_sines_b > -0.00001] = scipy.nan;
	cell_sines_b   = cell_sines_b**2;
	cell_sines_b   = cell_sines_b / sum(cell_sines_b[~scipy.isnan(cell_sines_b)]);

	temp   = vals_x * cell_cosines_f;
	ux_x_f = sum(temp[~scipy.isnan(temp)]);

	temp   = vals_x * cell_cosines_b;
	ux_x_b = sum(temp[~scipy.isnan(temp)]);

	temp   = vals_x * cell_sines_f;
	ux_y_f = sum(temp[~scipy.isnan(temp)]);

	temp   = vals_x * cell_sines_b;
	ux_y_b = sum(temp[~scipy.isnan(temp)]);

	temp   = vals_y * cell_cosines_f;
	uy_x_f = sum(temp[~scipy.isnan(temp)]);

	temp   = vals_y * cell_cosines_b;
	uy_x_b = sum(temp[~scipy.isnan(temp)]);

	temp   = vals_y * cell_sines_f;
	uy_y_f = sum(temp[~scipy.isnan(temp)]);

	temp   = vals_y * cell_sines_b;
	uy_y_b = sum(temp[~scipy.isnan(temp)]);

	ux_x = scipy.array([ux_x_b, val_mat[1,1], ux_x_f]);
	ux_y = scipy.array([ux_y_b, val_mat[1,1], ux_y_f]);
	uy_x = scipy.array([uy_x_b, 0, uy_x_f]);
	uy_y = scipy.array([uy_y_b, 0, uy_y_f]);

	xs = scipy.array([-1 * int(inc), 0, int(inc)]);
	A  = scipy.vstack([xs, scipy.ones(len(xs))]).T;

	if sum(scipy.isnan(ux_x)) > 0 or sum(scipy.isnan(ux_y)) > 0 or sum(scipy.isnan(uy_x)) > 0 or sum(scipy.isnan(uy_y)) > 0:
		return scipy.nan, scipy.nan, scipy.nan, scipy.nan;

	dux_dx, intercept = scipy.linalg.lstsq(A, ux_x)[0];
	dux_dy, intercept = scipy.linalg.lstsq(A, ux_y)[0];
	duy_dx, intercept = scipy.linalg.lstsq(A, uy_x)[0];
	duy_dy, intercept = scipy.linalg.lstsq(A, uy_y)[0];

	return dux_dx, dux_dy, duy_dx, duy_dy;



def velStrain(east_grd_path):

	import math;
	import matplotlib;
	import matplotlib.pyplot;
	import os;
	import scipy;
	from scipy.io import netcdf;
	from scipy.sparse import lil_matrix;
	import subprocess;

	assert os.path.exists(east_grd_path), "\n***** ERROR: " + east_grd_path + " does not exist\n";

	north_grd_path  = east_grd_path.replace("east", "north");
	angles_grd_path = east_grd_path.replace("eastxyz", "angles");
	mag_grd_path    = east_grd_path.replace("eastxyz", "mag");

	if not os.path.exists(angles_grd_path):
		cmd = "\ngrdmath " + north_grd_path + " " + east_grd_path + " ATAN2 --IO_NC4_CHUNK_SIZE=c = " + angles_grd_path + "\n";
		subprocess.call(cmd, shell=True);

	f      = netcdf.netcdf_file(mag_grd_path,"r",False);
	x      = f.variables["x"].data;
	y      = f.variables["y"].data;
	speeds = f.variables["z"].data[:];
	f.close();

	f      = netcdf.netcdf_file(north_grd_path,"r",False);
	x      = f.variables["x"].data;
	y      = f.variables["y"].data;
	ns_vel = f.variables["z"].data[:];
	f.close();

	f      = netcdf.netcdf_file(mag_grd_path,"r",False);
	x      = f.variables["x"].data;
	y      = f.variables["y"].data;
	ew_vel = f.variables["z"].data[:];
	f.close();

	f      = netcdf.netcdf_file(angles_grd_path,"r",False);
	x      = f.variables["x"].data;
	y      = f.variables["y"].data;
	angles = f.variables["z"].data[:];
	f.close();

	width  = f.dimensions["x"];
	length = f.dimensions["y"];

	min_x  = min(x);
	max_x  = max(x);
	min_y  = min(y);
	max_y  = max(y);

	inc = int((max(x) - min(x)) / (width - 1));

#	Read in ice-only pixels

#	f        = netcdf.netcdf_file("ice_only.grd","r",False);
	f        = netcdf.netcdf_file(east_grd_path,"r",False);
        x        = f.variables["x"].data;
        y        = f.variables["y"].data;
        ice_vals = f.variables["z"].data[:];
        f.close();

#	Iteratively calculate strain rates

	print("#Longitude     Latitude     EW_vel     NS_vel     dux_dx     dux_dy     duy_dx     duy_dy");

	for i in range(1, length - 1):

		for j in range(1, width - 1):

			angle        = angles[i,j];

			sub_speeds   = speeds[i-1:i+2,j-1:j+2];
			sub_angles   = angles[i-1:i+2,j-1:j+2];

			dux_dx, dux_dy, duy_dx, duy_dy = dirDeriv(sub_speeds / (60. * 60. * 24.), sub_angles, inc);

			out_str = str(x[j]) + " " + \
				  str(y[i]) + " " + \
				  str(ew_vel[i,j]) + " " + \
				  str(ns_vel[i,j]) + " " + \
				  str(dux_dx) + " " + str(dux_dy) + " " + str(duy_dx) + " " + str(duy_dy);

			print(out_str);

	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: velStrain.py requires one argument, " + str(len(sys.argv)) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	velStrain(sys.argv[1]);

	exit();

