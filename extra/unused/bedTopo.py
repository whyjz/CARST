#!/usr/bin/python

def dirDeriv(val_mat, direction_mat, inc):

	import scipy;
	import scipy.linalg;
	import math;

	cell_angles  = scipy.array([[3 * math.pi / 4, math.pi / 2, math.pi / 4], [math.pi, scipy.nan, 0], [-3 * math.pi / 4, -1 * math.pi / 2, -1 * math.pi / 4]]);
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

	dux_dx, intercept = scipy.linalg.lstsq(A, ux_x)[0];
	dux_dy, intercept = scipy.linalg.lstsq(A, ux_y)[0];
	duy_dx, intercept = scipy.linalg.lstsq(A, uy_x)[0];
	duy_dy, intercept = scipy.linalg.lstsq(A, uy_y)[0];

	return dux_dx, dux_dy, duy_dx, duy_dy;


def getThicknesses(val_mat, direction_mat, out_flux, inc):

	import scipy;
        import math;

        cell_angles  = scipy.array([[3 * math.pi / 4, math.pi / 2, math.pi / 4], [math.pi, scipy.nan, 0], [-3 * math.pi / 4, -1 * math.pi / 2, -1 * math.pi / 4]]);
        cell_incs    = scipy.array([[(inc**2 + inc**2)**0.5, inc, (inc**2 + inc**2)**0.5], [inc, scipy.nan, inc], [(inc**2 + inc**2)**0.5, inc, (inc**2 + inc**2)**0.5]]);

        vels_in      = scipy.cos((cell_angles - math.pi) - direction_mat);
	vels_in[1,1] = scipy.nan;
        vels_in[vels_in < 0.00001] = scipy.nan;
        vels_in      = vels_in * val_mat;
        in_fluxes    = (vels_in ** 2 / sum(vels_in[~scipy.isnan(vels_in)]**2) * out_flux);

        cosines      = scipy.cos((cell_angles - math.pi) - direction_mat);
	cosines[1,1] = scipy.nan;
        cosines[cosines < 0.00001] = scipy.nan;
        thicknesses  = in_fluxes / (cosines * val_mat);

        return thicknesses;


#	import scipy;

#	cell_angles  = scipy.array([[3 * math.pi / 4, math.pi / 2, math.pi / 4], [math.pi, scipy.nan, 0], [-3 * math.pi / 4, -1 * math.pi / 2, -1 * math.pi / 4]]);
#	cell_incs    = scipy.array([[(inc**2 + inc**2)**0.5, inc, (inc**2 + inc**2)**0.5], [inc, scipy.nan, inc], [(inc**2 + inc**2)**0.5, inc, (inc**2 + inc**2)**0.5]]);
#	angle        = direction_mat[0,0];
#	cell_cosines = scipy.cos(angle - cell_angles);
#	cell_sines   = scipy.sin(angle - cell_angles);
#	vals_x       = scipy.cos(angle - direction_mat);
#	vals_y       = scipy.sin(angle - direction_mat);

#	vals_x_f = vals_x;
#	vals_x_f[vals_x < 0.00001] = scipy.nan;
#	vals_x_f = vals_x_f * val_mat;
#	vals_x_b = vals_x;
#	vals_x_b[vals_x > -0.00001] = scipy.nan;
#	vals_x_b = vals_x_b * val_mat;
#	vals_y_f = vals_y;
#	vals_y_f[vals_y < 0.00001] = scipy.nan;
#	vals_y_f = vals_y_f * val_mat;
#	vals_y_b = vals_y;
#	vals_y_b[vals_y > -0.00001] = scipy.nan;
#	vals_y_b = vals_y_b * val_mat;

#	cell_cosines_f = cell_cosines;
#	cell_cosines_f[cell_cosines < 0.00001] = scipy.nan;
#	cell_cosines_f = cell_cosines_f**2;
#	cell_cosines_f = cell_cosines_f / sum(cell_cosines_f[~scipy.isnan(cell_cosines_f)]);
#	cell_cosines_b = cell_cosines;
#	cell_cosines_b[cell_cosines > -0.00001] = scipy.nan;
#	cell_cosines_b = cell_cosines_b**2;
#	cell_cosines_b = cell_cosines_b / sum(cell_cosines_b[~scipy.isnan(cell_cosines_b)]);
#	cell_sines_f   = cell_sines;
#	cell_sines_f[cell_sines < 0.00001] = scipy.nan;
#	cell_sines_f   = cell_sines_f**2;
#	cell_sines_f   = cell_sines_f / sum(cell_sines_f[~scipy.isnan(cell_sines_f)]);
#	cell_sines_b   = cell_sines;
#	cell_sines_b[cell_sines > -0.00001] = scipy.nan;
#	cell_sines_b   = cell_sines_b**2;
#	cell_sines_b   = cell_sines_b / sum(cell_sines_b[~scipy.isnan(cell_sines_b)]);

#	temp   = vals_x * cell_cosines_f;
#	ux_x_f = sum(temp[~scipy.isnan(temp)]);
#	temp   = vals_x * cell_cosines_b;
#	ux_x_b = sum(temp[~scipy.isnan(temp)]);
#	temp   = vals_x * cell_sines_f;
#	ux_y_f = sum(temp[~scipy.isnan(temp)]);
#	temp   = vals_x * cell_sines_b;
#	ux_y_b = sum(temp[~scipy.isnan(temp)]);
#	temp   = vals_y * cell_cosines_f;
#	uy_x_f = sum(temp[~scipy.isnan(temp)]);
#	temp   = vals_y * cell_cosines_b;
#	uy_x_b = sum(temp[~scipy.isnan(temp)]);
#	temp   = vals_y * cell_sines_f;
#	uy_y_f = sum(temp[~scipy.isnan(temp)]);
#	temp   = vals_y * cell_sines_b;
#	uy_y_b = sum(temp[~scipy.isnan(temp)]);

#	ux_x = scipy.array([ux_x_b, val_mat[1,1], ux_x_f]);
#	ux_y = scipy.array([ux_y_b, val_mat[1,1], ux_y_f]);
#	uy_x = scipy.array([uy_x_b, 0, uy_x_f]);
#	uy_y = scipy.array([uy_y_b, 0, uy_y_f]);

#	xs = scipy.array([-1 * int(inc), 0, int(inc)]);
#	A  = scipy.vstack([xs, scipy.ones(len(xs))]).T;

#	dux_dx, intercept = scipy.linalg.lstsq(A, ux_x)[0];
#	dux_dy, intercept = scipy.linalg.lstsq(A, ux_y)[0];
#	duy_dx, intercept = scipy.linalg.lstsq(A, uy_x)[0];
#	duy_dy, intercept = scipy.linalg.lstsq(A, uy_y)[0];

#	return dux_dx, dux_dy, duy_dx, duy_dy;


def bedTopo(east_grd_path, slope_grd_path, thickness_txt_path):

	import math;
	import matplotlib;
	import matplotlib.pyplot;
	import os;
	import scipy;
	from scipy.io import netcdf;
	from scipy.sparse import lil_matrix;
	import subprocess;

	assert os.path.exists(east_grd_path), "\n***** ERROR: " + east_grd_path + " does not exist\n";
	assert os.path.exists(slope_grd_path), "\n***** ERROR: " + slope_grd_path + " does not exist\n";
	assert os.path.exists(thickness_txt_path), "\n***** ERROR: " + thickness_txt_path + " does not exist\n";

	north_grd_path    = east_grd_path.replace("east", "north");
	angles_grd_path   = east_grd_path.replace("eastxyz", "angles");
	mag_grd_path      = east_grd_path.replace("eastxyz", "mag");

	if not os.path.exists(angles_grd_path):
		cmd = "\ngrdmath " + north_grd_path + " " + east_grd_path + " ATAN2 --IO_NC4_CHUNK_SIZE=c = " + angles_grd_path + "\n";
		subprocess.call(cmd, shell=True);

	cmd  = "\ngrdclip " + angles_grd_path + " -Sa0.7853981633974483/NaN -Sb0/NaN -Gone.grd\n";
	cmd += "\ngrdclip " + angles_grd_path + " -Sa1.5707963267948966/NaN -Sb0.7853981633974483/NaN -Gtwo.grd\n";
	cmd += "\ngrdclip " + angles_grd_path + " -Sa2.356194490192345/NaN -Sb1.5707963267948966/NaN -Gthree.grd\n";
	cmd += "\ngrdclip " + angles_grd_path + " -Sa3.141592653589793/NaN -Sb2.356194490192345/NaN -Gfour.grd\n";
	cmd += "\ngrdclip " + angles_grd_path + " -Sa-2.356194490192345/NaN -Gfive.grd\n";
	cmd += "\ngrdclip " + angles_grd_path + " -Sa-1.5707963267948966/NaN -Sb-2.356194490192345/NaN -Gsix.grd\n";
	cmd += "\ngrdclip " + angles_grd_path + " -Sa-0.7853981633974483/NaN -Sb-1.5707963267948966/NaN -Gseven.grd\n";
	cmd += "\ngrdclip " + angles_grd_path + " -Sa0/NaN -Sb-0.7853981633974483/NaN -Geight.grd\n";

	cmd += "\ngrdmath one.grd two.grd AND = u.grd\n";
	cmd += "\ngrdmath three.grd u.grd AND = u.grd\n";
	cmd += "\ngrdmath four.grd u.grd AND = u.grd\n";

	cmd += "\ngrdmath five.grd six.grd AND = d.grd\n";
	cmd += "\ngrdmath seven.grd d.grd AND = d.grd\n";
	cmd += "\ngrdmath eight.grd d.grd AND = d.grd\n";

	cmd += "\ngrdmath three.grd four.grd AND = l.grd\n";
	cmd += "\ngrdmath five.grd l.grd AND = l.grd\n";
	cmd += "\ngrdmath six.grd l.grd AND = l.grd\n";

	cmd += "\ngrdmath one.grd two.grd AND = r.grd\n";
	cmd += "\ngrdmath eight.grd r.grd AND = r.grd\n";
	cmd += "\ngrdmath seven.grd r.grd AND = r.grd\n";

	cmd += "\ngrdmath two.grd three.grd AND = ul.grd\n";
	cmd += "\ngrdmath four.grd ul.grd AND = ul.grd\n";
	cmd += "\ngrdmath five.grd ul.grd AND = ul.grd\n";

	cmd += "\ngrdmath one.grd two.grd AND = ur.grd\n";
	cmd += "\ngrdmath three.grd ur.grd AND = ur.grd\n";
	cmd += "\ngrdmath eight.grd ur.grd AND = ur.grd\n";

	cmd += "\ngrdmath four.grd five.grd AND = dl.grd\n";
	cmd += "\ngrdmath six.grd dl.grd AND = dl.grd\n";
	cmd += "\ngrdmath seven.grd dl.grd AND = dl.grd\n";

	cmd += "\ngrdmath one.grd six.grd AND = dr.grd\n";
	cmd += "\ngrdmath seven.grd dr.grd AND = dr.grd\n";
	cmd += "\ngrdmath eight.grd dr.grd AND = dr.grd\n";

	cmd += "\ngrdmath 1.5707963267948966 u.grd SUB = u.grd\n";
	cmd += "\ngrdmath u.grd ABS = u.grd\n";
	cmd += "\ngrdmath u.grd COS = u.grd\n";
	cmd += "\ngrdmath u.grd " + mag_grd_path + " MUL --IO_NC4_CHUNK_SIZE=c = u.grd";

	cmd += "\ngrdmath -1.5707963267948966 d.grd SUB = d.grd\n";
	cmd += "\ngrdmath d.grd ABS = d.grd\n";
	cmd += "\ngrdmath d.grd COS = d.grd\n";
	cmd += "\ngrdmath d.grd " + mag_grd_path + " MUL --IO_NC4_CHUNK_SIZE=c = d.grd";

	cmd += "\ngrdmath 3.141592653589793 l.grd SUB = l.grd\n";
	cmd += "\ngrdmath l.grd ABS = l.grd\n";
	cmd += "\ngrdmath l.grd COS = l.grd\n";
	cmd += "\ngrdmath l.grd " + mag_grd_path + " MUL --IO_NC4_CHUNK_SIZE=c = l.grd";

	cmd += "\ngrdmath 0 r.grd SUB = r.grd\n";
	cmd += "\ngrdmath r.grd ABS = r.grd\n";
	cmd += "\ngrdmath r.grd COS = r.grd\n";
	cmd += "\ngrdmath r.grd " + mag_grd_path + " MUL --IO_NC4_CHUNK_SIZE=c = r.grd";

	cmd += "\ngrdmath 2.356194490192345 ul.grd SUB = ul.grd\n";
	cmd += "\ngrdmath ul.grd ABS = ul.grd\n";
	cmd += "\ngrdmath ul.grd COS = ul.grd\n";
	cmd += "\ngrdmath ul.grd " + mag_grd_path + " MUL --IO_NC4_CHUNK_SIZE=c = ul.grd";

	cmd += "\ngrdmath 0.7853981633974483 ur.grd SUB = ur.grd\n";
	cmd += "\ngrdmath ur.grd ABS = ur.grd\n";
	cmd += "\ngrdmath ur.grd COS = ur.grd\n";
	cmd += "\ngrdmath ur.grd " + mag_grd_path + " MUL --IO_NC4_CHUNK_SIZE=c = ur.grd";

	cmd += "\ngrdmath -2.356194490192345 dl.grd SUB = dl.grd\n";
	cmd += "\ngrdmath dl.grd ABS = dl.grd\n";
	cmd += "\ngrdmath dl.grd COS = dl.grd\n";
	cmd += "\ngrdmath dl.grd " + mag_grd_path + " MUL --IO_NC4_CHUNK_SIZE=c = dl.grd";

	cmd += "\ngrdmath -0.7853981633974483 dr.grd SUB = dr.grd\n";
	cmd += "\ngrdmath dr.grd ABS = dr.grd\n";
	cmd += "\ngrdmath dr.grd COS = dr.grd\n";
	cmd += "\ngrdmath dr.grd " + mag_grd_path + " MUL --IO_NC4_CHUNK_SIZE=c = dr.grd";

	subprocess.call(cmd, shell=True);


	f = netcdf.netcdf_file("u.grd","r",False);
	x = f.variables["x"].data;
	y = f.variables["y"].data;
	u = f.variables["z"].data[:];
	f.close();

	f = netcdf.netcdf_file("d.grd","r",False);
	x = f.variables["x"].data;
	y = f.variables["y"].data;
	d = f.variables["z"].data[:];
	f.close();

	f = netcdf.netcdf_file("l.grd","r",False);
	x = f.variables["x"].data;
	y = f.variables["y"].data;
	l = f.variables["z"].data[:];
	f.close();

	f = netcdf.netcdf_file("r.grd","r",False);
	x = f.variables["x"].data;
	y = f.variables["y"].data;
	r = f.variables["z"].data[:];
	f.close();

	f  = netcdf.netcdf_file("ul.grd","r",False);
	x  = f.variables["x"].data;
	y  = f.variables["y"].data;
	ul = f.variables["z"].data[:];
	f.close();

	f  = netcdf.netcdf_file("ur.grd","r",False);
	x  = f.variables["x"].data;
	y  = f.variables["y"].data;
	ur = f.variables["z"].data[:];
	f.close();

	f  = netcdf.netcdf_file("dl.grd","r",False);
	x  = f.variables["x"].data;
	y  = f.variables["y"].data;
	dl = f.variables["z"].data[:];
	f.close();

	f  = netcdf.netcdf_file("dr.grd","r",False);
	x  = f.variables["x"].data;
	y  = f.variables["y"].data;
	dr = f.variables["z"].data[:];
	f.close();

	f      = netcdf.netcdf_file(mag_grd_path,"r",False);
	x      = f.variables["x"].data;
	y      = f.variables["y"].data;
	speeds = f.variables["z"].data[:];
	f.close();

	f      = netcdf.netcdf_file(slope_grd_path,"r",False);
	x      = f.variables["x"].data;
	y      = f.variables["y"].data;
	slopes = f.variables["z"].data[:];
	f.close();

	f      = netcdf.netcdf_file(angles_grd_path,"r",False);
	x      = f.variables["x"].data;
	y      = f.variables["y"].data;
	angles = f.variables["z"].data[:];
	f.close();

	width  = f.dimensions["x"];
	length = f.dimensions["y"];

	min_x = min(x);
	max_x = max(x);
	min_y = min(y);
	max_y = max(y);

	inc = int((max(x) - min(x)) / (width - 1));


#	Read in ice-only pixels

#	f        = netcdf.netcdf_file("ice_only.grd","r",False);
	f        = netcdf.netcdf_file(east_grd_path,"r",False);
        x        = f.variables["x"].data;
        y        = f.variables["y"].data;
        ice_vals = f.variables["z"].data[:];
        f.close();


#	Read in thicknesses, initialize fluxes

	thicknesses = {};
	f_lons      = {};
	f_lats      = {};
	dr_stresses = {};
	basal_drags = {};
	
	
	fluxes      = scipy.zeros((length, width));
	locked      = scipy.zeros((length, width));

	infile = open(thickness_txt_path, "r");

	for line in infile:

		utm_x, utm_y, thickness = line.strip().split();

#		j = str(int(math.floor((float(utm_x) - float(min_x)) / int(inc))));
#		i = str(int(math.floor((float(utm_y) - float(min_y)) / int(inc))));

		j = str(int(round((float(utm_x) - float(min_x)) / int(inc))));
		i = str(int(round((float(utm_y) - float(min_y)) / int(inc))));

		thicknesses[i + " " + j] = float(thickness);
		fluxes[int(i), int(j)]   = speeds[int(i), int(j)] * float(thickness);
		locked[int(i), int(j)]   = 1;

#		print(str(int(j) * int(inc) + float(min_x)) + " " + str(int(i) * int(inc) + float(min_y)) + " " + thickness);
		
	infile.close();	


#	Iteratively calculate fluxes, thicknesses

	max_iterations = 50;
	cur_iteration  = 0;
	cs1            = 0.0;
	cs2            = 0.0;

	todo   = thicknesses.keys();


	while cur_iteration < max_iterations:

		tolock  = {};
		inputs  = {};
		outputs = {};

		for coord in todo:

			str_i, str_j = coord.split();
			y_i = int(str_i);
			x_i = int(str_j);

			cs1 += fluxes[y_i,x_i];

			in_total  = 0.0;
			out_total = 0.0
			cs3       = 0.0;
			factor    = 4;


#			Calculate input fluxes

			if locked[y_i-1,x_i] < 1 and not scipy.isnan(ice_vals[y_i-1,x_i]) and not scipy.isnan(u[y_i-1,x_i]):
				in_total  += u[y_i-1,x_i]**factor;

			if locked[y_i+1,x_i] < 1 and not scipy.isnan(ice_vals[y_i+1,x_i]) and not scipy.isnan(d[y_i+1,x_i]):
				in_total += d[y_i+1,x_i]**factor;

			if locked[y_i,x_i+1] < 1 and not scipy.isnan(ice_vals[y_i,x_i+1]) and not scipy.isnan(l[y_i,x_i+1]):
				in_total += l[y_i,x_i+1]**factor;

			if locked[y_i,x_i-1] < 1 and not scipy.isnan(ice_vals[y_i,x_i-1]) and not scipy.isnan(r[y_i,x_i-1]):
				in_total += r[y_i,x_i-1]**factor;

			if locked[y_i-1,x_i+1] < 1 and not scipy.isnan(ice_vals[y_i-1,x_i+1]) and not scipy.isnan(ul[y_i-1,x_i+1]):
				in_total += ul[y_i-1,x_i+1]**factor;

			if locked[y_i-1,x_i-1] < 1 and not scipy.isnan(ice_vals[y_i-1,x_i-1]) and not scipy.isnan(ur[y_i-1,x_i-1]):
				in_total += ur[y_i-1,x_i-1]**factor;

			if locked[y_i+1,x_i+1] < 1 and not scipy.isnan(ice_vals[y_i+1,x_i+1]) and not scipy.isnan(dl[y_i+1,x_i+1]):
				in_total += dl[y_i+1,x_i+1]**factor;

			if locked[y_i+1,x_i-1] < 1 and not scipy.isnan(ice_vals[y_i+1,x_i-1]) and not scipy.isnan(dr[y_i+1,x_i-1]):
				in_total += dr[y_i+1,x_i-1]**factor;

			if locked[y_i-1,x_i] < 1 and not scipy.isnan(ice_vals[y_i-1,x_i]) and not scipy.isnan(u[y_i-1,x_i]):
				fluxes[y_i-1,x_i] += fluxes[y_i,x_i] * (u[y_i-1,x_i]**factor / in_total);
				tolock[str(y_i-1) + " " + str(x_i)] = True;
				inputs[str(y_i-1) + " " + str(x_i)] = True;
				cs3 += (u[y_i-1,x_i]**factor / in_total);

			if locked[y_i+1,x_i] < 1 and not scipy.isnan(ice_vals[y_i+1,x_i]) and not scipy.isnan(d[y_i+1,x_i]):
				fluxes[y_i+1,x_i] += fluxes[y_i,x_i] * (d[y_i+1,x_i]**factor / in_total);
				tolock[str(y_i+1) + " " + str(x_i)] = True;
				inputs[str(y_i+1) + " " + str(x_i)] = True;
				cs3 += (d[y_i+1,x_i]**factor / in_total);

			if locked[y_i,x_i+1] < 1 and not scipy.isnan(ice_vals[y_i,x_i+1]) and not scipy.isnan(l[y_i,x_i+1]):
				fluxes[y_i,x_i+1] += fluxes[y_i,x_i] * (l[y_i,x_i+1]**factor / in_total);
				tolock[str(y_i) + " " + str(x_i+1)] = True;
				inputs[str(y_i) + " " + str(x_i+1)] = True;
				cs3 += (l[y_i,x_i+1]**factor / in_total);

			if locked[y_i,x_i-1] < 1 and not scipy.isnan(ice_vals[y_i,x_i-1]) and not scipy.isnan(r[y_i,x_i-1]):
				fluxes[y_i,x_i-1] += fluxes[y_i,x_i] * (r[y_i,x_i-1]**factor / in_total);
				tolock[str(y_i) + " " + str(x_i-1)] = True;
				inputs[str(y_i) + " " + str(x_i-1)] = True;
				cs3 += (r[y_i,x_i-1]**factor / in_total);

			if locked[y_i-1,x_i+1] < 1 and not scipy.isnan(ice_vals[y_i-1,x_i+1]) and not scipy.isnan(ul[y_i-1,x_i+1]):
				fluxes[y_i-1,x_i+1] += fluxes[y_i,x_i] * (ul[y_i-1,x_i+1]**factor / in_total);
				tolock[str(y_i-1) + " " + str(x_i+1)] = True;
				inputs[str(y_i-1) + " " + str(x_i+1)] = True;
				cs3 += (ul[y_i-1,x_i+1]**factor / in_total);

			if locked[y_i-1,x_i-1] < 1 and not scipy.isnan(ice_vals[y_i-1,x_i-1]) and not scipy.isnan(ur[y_i-1,x_i-1]):
				fluxes[y_i-1,x_i-1] += fluxes[y_i,x_i] * (ur[y_i-1,x_i-1]**factor / in_total);
				tolock[str(y_i-1) + " " + str(x_i-1)] = True;
				inputs[str(y_i-1) + " " + str(x_i-1)] = True;
				cs3 += (ur[y_i-1,x_i-1]**factor / in_total);

			if locked[y_i+1,x_i+1] < 1 and not scipy.isnan(ice_vals[y_i+1,x_i+1]) and not scipy.isnan(dl[y_i+1,x_i+1]):
				fluxes[y_i+1,x_i+1] += fluxes[y_i,x_i] * (dl[y_i+1,x_i+1]**factor / in_total);
				tolock[str(y_i+1) + " " + str(x_i+1)] = True;
				inputs[str(y_i+1) + " " + str(x_i+1)] = True;
				cs3 += (dl[y_i+1,x_i+1]**factor / in_total);

			if locked[y_i+1,x_i-1] < 1 and not scipy.isnan(ice_vals[y_i+1,x_i-1]) and not scipy.isnan(dr[y_i+1,x_i-1]):
				fluxes[y_i+1,x_i-1] += fluxes[y_i,x_i] * (dr[y_i+1,x_i-1]**factor / in_total);
				tolock[str(y_i+1) + " " + str(x_i-1)] = True;
				inputs[str(y_i+1) + " " + str(x_i-1)] = True;
				cs3 += (dr[y_i+1,x_i-1]**factor / in_total);


#			Calculate output fluxes
			"""
			if locked[y_i-1,x_i] < 1 and not scipy.isnan(ice_vals[y_i-1,x_i]) and not scipy.isnan(d[y_i,x_i]) and (str(y_i-1) + " " + str(x_i)) not in inputs:
				out_total += d[y_i,x_i]**factor;

			if locked[y_i+1,x_i] < 1 and not scipy.isnan(ice_vals[y_i+1,x_i]) and not scipy.isnan(u[y_i,x_i]) and (str(y_i+1) + " " + str(x_i)) not in inputs:
				out_total += u[y_i,x_i]**factor;

			if locked[y_i,x_i+1] < 1 and not scipy.isnan(ice_vals[y_i,x_i+1]) and not scipy.isnan(r[y_i,x_i]) and (str(y_i) + " " + str(x_i+1)) not in inputs:
				out_total += r[y_i,x_i]**factor;

			if locked[y_i,x_i-1] < 1 and not scipy.isnan(ice_vals[y_i,x_i-1]) and not scipy.isnan(l[y_i,x_i]) and (str(y_i) + " " + str(x_i-1)) not in inputs:
				out_total += l[y_i,x_i]**factor;

			if locked[y_i-1,x_i+1] < 1 and not scipy.isnan(ice_vals[y_i-1,x_i+1]) and not scipy.isnan(dr[y_i,x_i]) and (str(y_i-1) + " " + str(x_i+1)) not in inputs:
				out_total += dr[y_i,x_i]**factor;

			if locked[y_i-1,x_i-1] < 1 and not scipy.isnan(ice_vals[y_i-1,x_i-1]) and not scipy.isnan(dl[y_i,x_i]) and (str(y_i-1) + " " + str(x_i-1)) not in inputs:
				out_total += dl[y_i,x_i]**factor;

			if locked[y_i+1,x_i+1] < 1 and not scipy.isnan(ice_vals[y_i+1,x_i+1]) and not scipy.isnan(ur[y_i,x_i]) and (str(y_i+1) + " " + str(x_i+1)) not in inputs:
				out_total += ur[y_i,x_i]**factor;

			if locked[y_i+1,x_i-1] < 1 and not scipy.isnan(ice_vals[y_i+1,x_i-1]) and not scipy.isnan(ul[y_i,x_i]) and (str(y_i+1) + " " + str(x_i-1)) not in inputs:
				out_total += ul[y_i,x_i]**factor;

			if locked[y_i-1,x_i] < 1 and not scipy.isnan(ice_vals[y_i-1,x_i]) and not scipy.isnan(d[y_i,x_i]) and (str(y_i-1) + " " + str(x_i)) not in inputs:
				fluxes[y_i-1,x_i] += fluxes[y_i,x_i] * (d[y_i,x_i]**factor / out_total);
				tolock[str(y_i-1) + " " + str(x_i)] = True;

			if locked[y_i+1,x_i] < 1 and not scipy.isnan(ice_vals[y_i+1,x_i]) and not scipy.isnan(u[y_i,x_i]) and (str(y_i+1) + " " + str(x_i)) not in inputs:
				fluxes[y_i+1,x_i] += fluxes[y_i,x_i] * (u[y_i,x_i]**factor / out_total);
				tolock[str(y_i+1) + " " + str(x_i)] = True;

			if locked[y_i,x_i+1] < 1 and not scipy.isnan(ice_vals[y_i,x_i+1]) and not scipy.isnan(r[y_i,x_i]) and (str(y_i) + " " + str(x_i+1)) not in inputs:
				fluxes[y_i,x_i+1] += fluxes[y_i,x_i] * (r[y_i,x_i]**factor / out_total);
				tolock[str(y_i) + " " + str(x_i+1)] = True;

			if locked[y_i,x_i-1] < 1 and not scipy.isnan(ice_vals[y_i,x_i-1]) and not scipy.isnan(l[y_i,x_i]) and (str(y_i) + " " + str(x_i-1)) not in inputs:
				fluxes[y_i,x_i-1] += fluxes[y_i,x_i] * (l[y_i,x_i]**factor / out_total);
				tolock[str(y_i) + " " + str(x_i-1)] = True;

			if locked[y_i-1,x_i+1] < 1 and not scipy.isnan(ice_vals[y_i-1,x_i+1]) and not scipy.isnan(dr[y_i,x_i]) and (str(y_i-1) + " " + str(x_i+1)) not in inputs:
				fluxes[y_i-1,x_i+1] += fluxes[y_i,x_i] * (dr[y_i,x_i]**factor / out_total);
				tolock[str(y_i-1) + " " + str(x_i+1)] = True;

			if locked[y_i-1,x_i-1] < 1 and not scipy.isnan(ice_vals[y_i-1,x_i-1]) and not scipy.isnan(dl[y_i,x_i]) and (str(y_i-1) + " " + str(x_i-1)) not in inputs:
				fluxes[y_i-1,x_i-1] += fluxes[y_i,x_i] * (dl[y_i,x_i]**factor / out_total);
				tolock[str(y_i-1) + " " + str(x_i-1)] = True;

			if locked[y_i+1,x_i+1] < 1 and not scipy.isnan(ice_vals[y_i+1,x_i+1]) and not scipy.isnan(ur[y_i,x_i]) and (str(y_i+1) + " " + str(x_i+1)) not in inputs:
				fluxes[y_i+1,x_i+1] += fluxes[y_i,x_i] * (ur[y_i,x_i]**factor / out_total);
				tolock[str(y_i+1) + " " + str(x_i+1)] = True;

			if locked[y_i+1,x_i-1] < 1 and not scipy.isnan(ice_vals[y_i+1,x_i-1]) and not scipy.isnan(ul[y_i,x_i]) and (str(y_i+1) + " " + str(x_i-1)) not in inputs:
				fluxes[y_i+1,x_i-1] += fluxes[y_i,x_i] * (ul[y_i,x_i]**factor / out_total);
				tolock[str(y_i+1) + " " + str(x_i-1)] = True;
			"""

#		print(x[x_i],y[y_i]);
#		print(x[x_i-1],y[y_i]);
#		print(x[x_i+1],y[y_i]);
#		print(x[x_i],y[y_i-1]);
#		print(x[x_i],y[y_i+1]);
#		print(x[x_i+1],y[y_i+1]);
#		print(x[x_i+1],y[y_i-1]);
#		print(x[x_i-1],y[y_i+1]);
#		print(x[x_i-1],y[y_i-1]);
#		return;

		for coord in tolock:

			str_i, str_j = coord.split();
                        i = int(str_i);
                        j = int(str_j);

			cs2 += fluxes[i,j];

			thicknesses[coord] = fluxes[i,j] / speeds[i,j];
			locked[i,j]        = 1;
			todo               = tolock.keys();

#		print(cs1, cs2, cs3);

		cur_iteration += 1;


	for coord in thicknesses:

		i, j       = coord.split();
		angle      = angles[i,j];
		sub_speeds = speeds[i-1:i+2,j-1:j+2];
		sub_angles = angles[i-1:i+2,j-1:j+2];

		indices_x  = [1, 2, 2, 2, 1, 0, 0, 0];
		indices_y  = [0, 2, 0, 1, 2, 0, 2, 1];

		if angle >= math.pi / 4 and angle < math.pi / 2:
			indices_x = [2, 2, 2, 1, 0, 0, 0, 1];
			indices_y = [1, 2, 0, 2, 1, 0, 2, 0];

		elif angle >= math.pi / 2 and angle < 3 * math.pi / 4:
			indices_x = [2, 1, 2, 0, 0, 1, 0, 2];
			indices_y = [1, 2, 2, 2, 1, 0, 0, 0];

		elif angle >= 3 * math.pi / 4 and angle <= math.pi:
			indices_x = [2, 0, 1, 0, 0, 2, 1, 2];
			indices_y = [2, 2, 2, 1, 0, 0, 0, 1];

		elif angle < 0 and angle >= -1 * math.pi / 4:
			indices_x = [1, 2, 0, 2, 1, 0, 2, 0];
			indices_y = [0, 0, 0, 1, 2, 2, 2, 1];	

		elif angle < -1 * math.pi / 4 and angle >= -1 * math.pi / 2:
			indices_x = [0, 2, 0, 1, 2, 0, 2, 1];
			indices_y = [0, 0, 1, 0, 2, 2, 1, 2];

		elif angle < -1 * math.pi / 2 and angle >= -3 * math.pi / 4:
			indices_x = [0, 1, 0, 0, 2, 1, 2, 2];
			indices_y = [1, 0, 2, 0, 1, 2, 0, 2];

		elif angle < -3 * math.pi / 4 and angle >= -1 * math.pi:
			indices_x = [0, 0, 1, 0, 2, 2, 1, 2];
			indices_y = [2, 0, 2, 1, 0, 1, 0, 2];

		dux_dx = dirDeriv(sub_speeds, sub_angles, indices_x, inc);
		dux_dy = dirDeriv(sub_speeds, sub_angles, indices_y, inc);
		duy_dx = dirDeriv(sub_speeds, sub_angles, indices_x, inc);
		duy_dy = dirDeriv(sub_speeds, sub_angles, indices_y, inc);

		out_str = str(x[int(j)]) + " " + str(y[int(i)]) + " " + str(thicknesses[coord]) + " " + str(fluxes[i,j]);

		if coord in inputs:
			out_str += " input";
		elif coord in outputs:
			out_str += " output";

		print(out_str);

	os.remove("one.grd");
	os.remove("two.grd");
	os.remove("three.grd");
	os.remove("four.grd");
	os.remove("five.grd");
	os.remove("six.grd");
	os.remove("seven.grd");
	os.remove("eight.grd");
	os.remove("u.grd");
	os.remove("d.grd");
	os.remove("l.grd");
	os.remove("r.grd");
	os.remove("ul.grd");
	os.remove("ur.grd");
	os.remove("dl.grd");
	os.remove("dr.grd");


	return;

if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 3, "\n***** ERROR: bedTopo.py requires three arguments, " + str(len(sys.argv)) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";
	
	bedTopo(sys.argv[1], sys.argv[2], sys.argv[3]);

	exit();

