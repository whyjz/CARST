#!/usr/bin/python



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

	dux_dx, intercept = scipy.linalg.lstsq(A, ux_x)[0];
	dux_dy, intercept = scipy.linalg.lstsq(A, ux_y)[0];
	duy_dx, intercept = scipy.linalg.lstsq(A, uy_x)[0];
	duy_dy, intercept = scipy.linalg.lstsq(A, uy_y)[0];

	return dux_dx, dux_dy, duy_dx, duy_dy;



def elevDeriv(val_mat, direction_mat, inc):

	import scipy;
	import scipy.linalg;
	import math;

	cell_angles  = scipy.flipud(scipy.array([[3 * math.pi / 4, math.pi / 2, math.pi / 4], [math.pi, scipy.nan, 0], [-3 * math.pi / 4, -1 * math.pi / 2, -1 * math.pi / 4]]));
	cell_incs    = scipy.array([[(inc**2 + inc**2)**0.5, inc, (inc**2 + inc**2)**0.5], [inc, scipy.nan, inc], [(inc**2 + inc**2)**0.5, inc, (inc**2 + inc**2)**0.5]]);
	angle        = direction_mat[1,1];

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

	temp  = val_mat * cell_cosines_f;
	h_x_f = sum(temp[~scipy.isnan(temp)]);

	temp  = val_mat * cell_cosines_b;
	h_x_b = sum(temp[~scipy.isnan(temp)]);

	temp  = val_mat * cell_sines_f;
	h_y_f = sum(temp[~scipy.isnan(temp)]);

	temp  = val_mat * cell_sines_b;
	h_y_b = sum(temp[~scipy.isnan(temp)]);

	h_x = scipy.array([h_x_b, val_mat[1,1], h_x_f]);
	h_y = scipy.array([h_y_b, val_mat[1,1], h_y_f]);

	xs = scipy.array([-1 * int(inc), 0, int(inc)]);
	A  = scipy.vstack([xs, scipy.ones(len(xs))]).T;

#	print("A: " + str(A));
#	print("h_x_b: " + str(h_x_b));
#	print("val_mat[1,1]: " + str(val_mat[1,1]));
#	print("h_x_f: " + str(h_x_f));

	dh_dx, intercept = scipy.linalg.lstsq(A, h_x)[0];
	dh_dy, intercept = scipy.linalg.lstsq(A, h_y)[0];

	return dh_dx, dh_dy;



def getFluxes(val_mat, direction_mat, out_flux, inc):

	import scipy;
	import math;

	speed_factor = 3;
	angle_factor = 1;
	inc_factor   = 1;

	cell_angles  = scipy.flipud(scipy.array([[-1 * math.pi / 4, -1 * math.pi / 2, -3 * math.pi / 4], [0, scipy.nan, math.pi], [math.pi / 4, math.pi / 2, 3 * math.pi / 4]]));

	cell_incs    = scipy.array([[(inc**2 + inc**2)**0.5, inc, (inc**2 + inc**2)**0.5], [inc, scipy.nan, inc], [(inc**2 + inc**2)**0.5, inc, (inc**2 + inc**2)**0.5]]);
	cell_incs    = (1 / cell_incs**inc_factor);
	cell_incs    = cell_incs / sum(cell_incs[~scipy.isnan(cell_incs)]);

	vels_in      = scipy.cos(cell_angles - direction_mat);
	vels_in[1,1] = scipy.nan;
	vels_in[vels_in < 0.00001] = scipy.nan;
	vels_in      = vels_in**angle_factor * val_mat**speed_factor * cell_incs;
	in_fluxes    = (vels_in / sum(vels_in[~scipy.isnan(vels_in)]) * out_flux);

        return in_fluxes;



def bedTopo(east_grd_path, dem_grd_path, thickness_txt_path):

	import math;
	import matplotlib;
	import matplotlib.pyplot;
	import os;
	import scipy;
	from scipy.io import netcdf;
	from scipy.sparse import lil_matrix;
	import subprocess;

	assert os.path.exists(east_grd_path), "\n***** ERROR: " + east_grd_path + " does not exist\n";
	assert os.path.exists(dem_grd_path), "\n***** ERROR: " + dem_grd_path + " does not exist\n";
	assert os.path.exists(thickness_txt_path), "\n***** ERROR: " + thickness_txt_path + " does not exist\n";

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

	f      = netcdf.netcdf_file(dem_grd_path,"r",False);
	x      = f.variables["x"].data;
	y      = f.variables["y"].data;
	elevs  = f.variables["z"].data[:];
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

#	Read in thicknesses, initialize fluxes

	thicknesses   = {};
	current_cells = {};
	todo_cells    = {};
	in_cells      = {};
	counts        = {};
	tolock        = {};

	f_lons   = scipy.zeros((length, width));
	f_lats   = scipy.zeros((length, width));
	tau_ds   = scipy.zeros((length, width));
	tau_bs   = scipy.zeros((length, width));
	fluxes   = scipy.zeros((length, width));
	t_fluxes = scipy.zeros((length, width));
	locked   = scipy.ones((length, width)) * (ice_vals / ice_vals);

	f_lons[f_lons < 1] = scipy.nan;
	f_lats[f_lats < 1] = scipy.nan;
	tau_ds[tau_ds < 1] = scipy.nan;
	tau_bs[tau_bs < 1] = scipy.nan;

	infile = open(thickness_txt_path, "r");

	for line in infile:

		utm_x, utm_y, thickness = line.strip().split();

		j = str(int(round((float(utm_x) - float(min_x)) / int(inc))));
		i = str(int(round((float(utm_y) - float(min_y)) / int(inc))));

		thicknesses[i + " " + j]   = float(thickness);
		current_cells[i + " " + j] = True;
		fluxes[int(i), int(j)]     = speeds[int(i), int(j)] * float(thickness);
		t_fluxes[int(i), int(j)]     = speeds[int(i), int(j)] * float(thickness);
		locked[int(i), int(j)]     = scipy.nan;

	infile.close();	

#	Iteratively calculate fluxes, thicknesses

        cell_angles     = scipy.flipud(scipy.array([[-1 * math.pi / 4, -1 * math.pi / 2, -3 * math.pi / 4], \
						    [0, scipy.nan, math.pi], \
						    [math.pi / 4, math.pi / 2, 3 * math.pi / 4]]));
	max_iterations  = 60;
	cur_iteration   = 0;

	while cur_iteration < max_iterations:

		for coord in current_cells:

			str_i, str_j = coord.split();
			i = int(str_i);
			j = int(str_j);

			in_locked = locked[i-1:i+2,j-1:j+2] * scipy.ones((3,3));
			in_speeds = speeds[i-1:i+2,j-1:j+2] * scipy.ones((3,3));
			in_angles = angles[i-1:i+2,j-1:j+2] * scipy.ones((3,3));

			in_speeds[1,1] = scipy.nan;
			in_angles[1,1] = scipy.nan;
			in_locked[1,1] = scipy.nan;

			out_flux  = fluxes[i,j];

			in_fluxes = getFluxes(in_speeds, in_angles, out_flux, inc);

			for k in range(0, in_fluxes.shape[0]):

				for m in range(0, in_fluxes.shape[1]):

					if scipy.isnan(in_fluxes[k,m]) or ~scipy.isnan(in_locked[k,m]):
						continue;

					t_fluxes[i+(k-1),j+(m-1)] += in_fluxes[k,m];
					t_fluxes[i,j]             -= in_fluxes[k,m];

		for coord in current_cells:

			str_i, str_j = coord.split();
			i = int(str_i);
			j = int(str_j);

			in_locked = locked[i-1:i+2,j-1:j+2] * scipy.ones((3,3));
			in_speeds = speeds[i-1:i+2,j-1:j+2] * scipy.ones((3,3)) * in_locked;
			in_angles = angles[i-1:i+2,j-1:j+2] * scipy.ones((3,3)) * in_locked;

			in_speeds[1,1] = scipy.nan;
			in_angles[1,1] = scipy.nan;
			in_locked[1,1] = scipy.nan;

			out_flux  = t_fluxes[i,j];

			in_fluxes = getFluxes(in_speeds, in_angles, out_flux, inc);

			for k in range(0, in_fluxes.shape[0]):

				for m in range(0, in_fluxes.shape[1]):

					if scipy.isnan(in_fluxes[k,m]):
						continue;

					fluxes[i+(k-1),j+(m-1)] += in_fluxes[k,m];
					in_coord                 = str(i+(k-1)) + " " + str(j+(m-1));
					todo_cells[in_coord]     = True;
			
		current_cells = {};

		for coord in todo_cells:

			str_i, str_j = coord.split();
			i = int(str_i);
			j = int(str_j);

			if scipy.isnan(locked[i,j]):
				continue;	

			thicknesses[coord]   = fluxes[i,j] / speeds[i,j];
			locked[i,j]          = scipy.nan;
			current_cells[coord] = True;

		todo_cells     = {};
		t_fluxes       = fluxes * 1;
		cur_iteration += 1;

	for coord in thicknesses:

		str_i, str_j = coord.split();
		i            = int(str_i);
		j            = int(str_j);
		angle        = angles[i,j];
		sub_speeds   = speeds[i-1:i+2,j-1:j+2];
		sub_elevs    = elevs[i-1:i+2,j-1:j+2];
		sub_angles   = angles[i-1:i+2,j-1:j+2];

		dux_dx, dux_dy, duy_dx, duy_dy = dirDeriv(sub_speeds / (60. * 60. * 24.), sub_angles, inc);

		dh_dx = scipy.nan;
		dh_dy = scipy.nan;

		if not scipy.isnan(sub_elevs[1,1]):
			dh_dx, dh_dy = elevDeriv(sub_elevs, sub_angles, inc);

		B      = 316.44532035341405;
		eps_xx = dux_dx;
		eps_yy = duy_dy;
		eps_xy = 0.5 * (dux_dy + duy_dx);
		eps_zz = 0 - eps_xx - eps_yy;
		eps_e  = ((eps_xx**2 + eps_yy**2 + eps_zz**2) + 2 * eps_xy**2)**0.5;
		f_lons[i,j] = thicknesses[coord] * B * eps_e**(1./3. - 1) * (2 * eps_xx + eps_yy);
		f_lats[i,j] = thicknesses[coord] * B * eps_e**(1./3. - 1) * eps_xy;
		tau_ds[i,j] = -1 * thicknesses[coord] * 0.9 * 9.8 * dh_dx;
# 		MULTIPLY BY AREA

	for coord in thicknesses:

		str_i, str_j = coord.split();
		i            = int(str_i);
		j            = int(str_j);

		sub_f_lons = f_lons[i-1:i+2,j-1:j+2];
		sub_f_lats = f_lats[i-1:i+2,j-1:j+2];
		sub_speeds   = speeds[i-1:i+2,j-1:j+2];
		sub_elevs    = elevs[i-1:i+2,j-1:j+2];
		sub_angles = angles[i-1:i+2,j-1:j+2];

		dux_dx, dux_dy, duy_dx, duy_dy = dirDeriv(sub_speeds / (60. * 60. * 24.), sub_angles, inc);

		dh_dx = scipy.nan;
		dh_dy = scipy.nan;

		if not scipy.isnan(sub_elevs[1,1]):
			dh_dx, dh_dy = elevDeriv(sub_elevs, sub_angles, inc);

		d_f_lons_dx = scipy.nan;
		d_f_lons_dy = scipy.nan;
		d_f_lats_dx = scipy.nan;
		d_f_lats_dy = scipy.nan;

		if not scipy.isnan(sub_f_lons[1,1]):
			d_f_lons_dx, d_f_lons_dy = elevDeriv(sub_f_lons, sub_angles, inc);

		if not scipy.isnan(sub_f_lats[1,1]):
			d_f_lats_dx, d_f_lats_dy = elevDeriv(sub_f_lats, sub_angles, inc);

		tau_bs[i,j] = tau_ds[i,j] + d_f_lons_dx + d_f_lats_dy;

		out_str = str(x[j]) + " " + \
			  str(y[i]) + " " + \
			  str(thicknesses[coord]) + " " + \
			  str(fluxes[i,j]) + " " + \
			  str(locked[i,j]) + " " + \
			  str(tau_ds[i,j]) + " " + \
			  str(tau_bs[i,j]) + " " + \
		 	  str(d_f_lons_dx) + " " + \
			  str(d_f_lats_dy) + " " + \
			  str(dux_dx) + " " + str(dux_dy) + " " + str(duy_dx) + " " + str(duy_dy) + " " + \
			  str(dh_dx);

		print(out_str);

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

