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

	factor = 2;

        cell_angles  = scipy.flipud(scipy.array([[-1 * math.pi / 4, -1 * math.pi / 2, -3 * math.pi / 4], [0, scipy.nan, math.pi], [math.pi / 4, math.pi / 2, 3 * math.pi / 4]]));
        cell_incs    = scipy.array([[(inc**2 + inc**2)**0.5, inc, (inc**2 + inc**2)**0.5], [inc, scipy.nan, inc], [(inc**2 + inc**2)**0.5, inc, (inc**2 + inc**2)**0.5]]);

        vels_in      = scipy.cos(cell_angles - direction_mat);
	vels_in[1,1] = scipy.nan;
        vels_in[vels_in < 0.00001] = scipy.nan;
        vels_in      = vels_in * val_mat;
        in_fluxes    = (vels_in**factor / sum(vels_in[~scipy.isnan(vels_in)]**factor) * out_flux);

#	print(in_fluxes);

#	cosines      = scipy.cos((cell_angles - math.pi) - direction_mat);
#	cosines[1,1] = scipy.nan;
#	cosines[cosines < 0.00001] = scipy.nan;
#	thicknesses  = in_fluxes / (cosines * val_mat);

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

	thicknesses = {};

	f_lons      = scipy.zeros((length, width));
	f_lats      = scipy.zeros((length, width));
	tau_ds      = scipy.zeros((length, width));
	tau_bs      = scipy.zeros((length, width));
	fluxes      = scipy.zeros((length, width));
	locked      = scipy.ones((length, width));

	f_lons[f_lons < 1] = scipy.nan;
	f_lats[f_lats < 1] = scipy.nan;
	tau_ds[tau_ds < 1] = scipy.nan;
	tau_bs[tau_bs < 1] = scipy.nan;

	infile = open(thickness_txt_path, "r");

	for line in infile:

		utm_x, utm_y, thickness = line.strip().split();

		j = str(int(round((float(utm_x) - float(min_x)) / int(inc))));
		i = str(int(round((float(utm_y) - float(min_y)) / int(inc))));

		thicknesses[i + " " + j] = float(thickness);
		fluxes[int(i), int(j)]   = speeds[int(i), int(j)] * float(thickness);
		locked[int(i), int(j)]   = scipy.nan;

		

	infile.close();	

#	Iteratively calculate fluxes, thicknesses

	max_iterations = 10;
	cur_iteration  = 0;

	todo   = thicknesses.keys();

	while cur_iteration < max_iterations:

		tolock  = {};
		inputs  = {};
		outputs = {};

		for coord in todo:

			str_i, str_j = coord.split();
			y_i = int(str_i);
			x_i = int(str_j);

			out_flux = fluxes[y_i,x_i];

#			Calculate input fluxes

			in_speeds     = speeds[y_i-1:y_i+2,x_i-1:x_i+2] * scipy.ones((3,3));
			in_angles     = angles[y_i-1:y_i+2,x_i-1:x_i+2] * scipy.ones((3,3));
			in_locked     = locked[y_i-1:y_i+2,x_i-1:x_i+2];
			in_ice        = ice_vals[y_i-1:y_i+2,x_i-1:x_i+2];

#			if str(x[int(str_j)]) == "550562.515415" and str(y[int(str_i)]) == "6489983.19815":
#				print(scipy.flipud(in_speeds));

        		cell_angles = scipy.flipud(scipy.array([[-1 * math.pi / 4, -1 * math.pi / 2, -3 * math.pi / 4], [0, scipy.nan, math.pi], [math.pi / 4, math.pi / 2, 3 * math.pi / 4]]));
			locked_fluxes = fluxes[y_i-1:y_i+2,x_i-1:x_i+2] * scipy.isnan(in_locked) * scipy.cos(cell_angles - in_angles);
			locked_fluxes[locked_fluxes < 0.0001] = scipy.nan;

#			in_speeds = in_speeds * in_locked; # * in_ice; 
#			in_angles = in_angles * in_locked; # * in_ice; 

			in_speeds[1,1] = scipy.nan;
			in_angles[1,1] = scipy.nan;

#			if not (str(x[int(str_j)]) == "550562.515415" and str(y[int(str_i)]) == "6489983.19815"):
#				continue;
				
			in_fluxes = getFluxes(in_speeds, in_angles, out_flux, inc);

#			print(scipy.flipud(in_angles));
#			print(locked_fluxes);
#			print(out_flux);
#			print(inc);
#			print(in_fluxes);

			for i in range(0, in_fluxes.shape[0]):

				for j in range(0, in_fluxes.shape[1]):

					if scipy.isnan(in_fluxes[i,j]) or scipy.isnan(locked[y_i+(i-1),x_i+(j-1)]):
						continue;

					key = str(y_i+(i-1)) + " " + str(x_i+(j-1));

					fluxes[y_i+(i-1),x_i+(j-1)] += in_fluxes[i,j];
					tolock[key]  = True;

		for coord in tolock:

			str_i, str_j = coord.split();
                        i = int(str_i);
                        j = int(str_j);

			thicknesses[coord] = fluxes[i,j] / speeds[i,j];
			locked[i,j]        = scipy.nan;
			todo               = tolock.keys();

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

#		B      = 2.4 * 1e-24;
		B      = 316.44532035341405;
		eps_xx = dux_dx;
		eps_yy = duy_dy;
		eps_xy = 0.5 * (dux_dy + duy_dx);
		eps_zz = 0 - eps_xx - eps_yy;
		eps_e  = ((eps_xx**2 + eps_yy**2 + eps_zz**2) + 2 * eps_xy**2)**0.5;
		f_lons[i,j] = thicknesses[coord] * B * eps_e**(1./3. - 1) * (2 * eps_xx + eps_yy);
		f_lats[i,j] = thicknesses[coord] * B * eps_e**(1./3. - 1) * eps_xy;
		tau_ds[i,j] = -1 * thicknesses[coord] * 0.9 * 9.8 * dh_dx;
# MULTIPLY BY AREA;

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

