#!/usr/bin/python


def imageVel(east_grd_path):

	import matplotlib;
	import matplotlib.pyplot;
	import os;
	from scipy.io import netcdf;

	assert os.path.exists(east_grd_path), "\n***** ERROR: " + east_grd_path + " does not exist\n";

	north_grd_path = east_grd_path.replace("east", "north");
	mag_grd_path   = east_grd_path.replace("eastxyz", "mag");

	f = netcdf.netcdf_file(east_grd_path,"r",False);
	x = f.variables["x"].data;
	y = f.variables["y"].data;
	eastvel = f.variables["z"].data[:];
	f.close();

	f = netcdf.netcdf_file(north_grd_path,"r",False);
	x = f.variables["x"].data;
	y = f.variables["y"].data;
	northvel = f.variables["z"].data[:];
	f.close();

	f = netcdf.netcdf_file(mag_grd_path,"r",False);
	x = f.variables["x"].data;
	y = f.variables["y"].data;
	speed = f.variables["z"].data[:];
	f.close();

#	matplotlib.pyplot.imshow(speed[1380:1440, 760:820], interpolation='nearest', origin='lower');
	matplotlib.pyplot.streamplot(x[760:820], y[1380:1440], eastvel[1380:1440, 760:820], northvel[1380:1440, 760:820], color=speed[1380:1440, 760:820], linewidth=2);
	matplotlib.pyplot.colorbar();
	matplotlib.pyplot.show();

#	matplotlib.pyplot.imshow(speed, interpolation='nearest', origin='lower');
#	matplotlib.pyplot.show();

	return;

if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: imageVel.py requires one argument, " + str(len(sys.argv)) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	imageVel(sys.argv[1]);

	exit();

