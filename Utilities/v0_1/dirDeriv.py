#!/usr/bin/python

def dirDeriv(val_mat, direction_mat, inc):

	import scipy;
	import scipy.linalg;
	import math;

	cell_angles  = scipy.array([[3 * math.pi / 4, math.pi / 2, math.pi / 4], [math.pi, scipy.nan, 0], [-3 * math.pi / 4, -1 * math.pi / 2, -1 * math.pi / 4]]);
	cell_incs    = scipy.array([[(inc**2 + inc**2)**0.5, inc, (inc**2 + inc**2)**0.5], [inc, scipy.nan, inc], [(inc**2 + inc**2)**0.5, inc, (inc**2 + inc**2)**0.5]]);
	angle        = direction_mat[1,1];
	cell_cosines = scipy.cos(angle - cell_angles);
	cell_sines   = scipy.sin(angle - cell_angles);
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
#	print(temp);
	ux_x_f = sum(temp[~scipy.isnan(temp)]);
	temp   = vals_x * cell_cosines_b;
#	print(temp);
	ux_x_b = sum(temp[~scipy.isnan(temp)]);
	temp   = vals_x * cell_sines_f;
#	print(temp);
	ux_y_f = sum(temp[~scipy.isnan(temp)]);
	temp   = vals_x * cell_sines_b;
#	print(temp);
	ux_y_b = sum(temp[~scipy.isnan(temp)]);
	temp   = vals_y * cell_cosines_f;
#	print(temp);
	uy_x_f = sum(temp[~scipy.isnan(temp)]);
	temp   = vals_y * cell_cosines_b;
#	print(temp);
	uy_x_b = sum(temp[~scipy.isnan(temp)]);
	temp   = vals_y * cell_sines_f;
#	print(temp);
	uy_y_f = sum(temp[~scipy.isnan(temp)]);
	temp   = vals_y * cell_sines_b;
#	print(temp);
	uy_y_b = sum(temp[~scipy.isnan(temp)]);

#	print(speeds);

	ux_x = scipy.array([ux_x_b, val_mat[1,1], ux_x_f]);
	ux_y = scipy.array([ux_y_b, val_mat[1,1], ux_y_f]);
	uy_x = scipy.array([uy_x_b, 0, uy_x_f]);
	uy_y = scipy.array([uy_y_b, 0, uy_y_f]);

	xs = scipy.array([-1 * int(inc), 0, int(inc)]);
	A  = scipy.vstack([xs, scipy.ones(len(xs))]).T;

	dux_dx, intercept = scipy.linalg.lstsq(A, ux_x)[0];
	dux_dy, intercept = scipy.linalg.lstsq(A, ux_y)[0];
	duy_dx, intercept = scipy.linalg.lstsq(A, uy_x)[0];
	duy_dy, intercept = scipy.linalg.lstsq(A, uy_y)[0];

#	print(dux_dx, dux_dy, duy_dx, duy_dy);

	return dux_dx, dux_dy, duy_dx, duy_dy;


if __name__ == "__main__":
	
	import math;
	import scipy;

	speeds = scipy.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]);
#	angles = scipy.array([[math.pi / 4, math.pi / 4, math.pi / 4], [math.pi / 4, math.pi / 4, 0], [math.pi / 4, -1 * math.pi / 2, math.pi / 4]]);
#	angles = scipy.array([[math.pi / 4, math.pi / 4, math.pi / 4], [math.pi / 4, math.pi / 4, math.pi / 4], [math.pi / 4, math.pi / 4, math.pi / 4]]);
	angles = scipy.array([[math.pi / 2, math.pi / 2, math.pi / 2], [math.pi / 2, math.pi / 4, math.pi / 2], [math.pi / 2, math.pi / 2, math.pi / 2]]);

	dirDeriv(speeds, angles, 120);	

	exit();


