#!/usr/bin/python


# removeQuadOff.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def residuals(p, y, xs):

	err = y;

#	for i in range(0, len(xs)):
#		err = err - p[i] * xs[i];
	for i in range(0, len(xs)):
		err = err - p[i] * xs;

	return err;


def peval(xs, p):

	value = p[0] * xs[0];

#	for i in range(1, len(xs)):
#		value = value + p[i] * xs[i];
	for i in range(1, len(xs)):
		value = value + p[i] * xs;

	return value;


def removeQuadOff(input_unw_path, width, length):

	ramp_removed_unw_path = "ramp_removed_" + input_unw_path[input_unw_path.rfind("/") + 1 : input_unw_path.rfind(".")] + ".unw";

	assert not os.path.exists(ramp_removed_unw_path), "\n***** ERROR: " + ramp_removed_unw_path + " already exists, exiting...\n";

	import subprocess;

	mag = input_unw_path[input_unw_path.rfind("/") + 1 : input_unw_path.rfind(".")] + ".mag";
	phs = input_unw_path[input_unw_path.rfind("/") + 1 : input_unw_path.rfind(".")] + ".phs";
	
	cmd  = "\nrmg2mag_phs " + input_unw_path + " " + mag + " " + phs + " " + width + "\n";
	cmd += "\nrm " + mag + "\n";
	subprocess.call(cmd,shell=True);

	infile = open(phs, "rb");

	import pylab;

	indat = pylab.fromfile(infile,pylab.float32,-1).reshape(int(length), int(width));
	#indat = pylab.fromfile(infile,pylab.float32,-1).reshape(int(width) * int(length), -1);

	infile.close();

	import scipy;

	x = scipy.arange(0, int(length));
	y = scipy.arange(0, int(width));

	import numpy;

	x_grid, y_grid = numpy.meshgrid(x, y);

	indices = numpy.arange(0, int(width) * int(length));

	mx = scipy.asarray(x_grid).reshape(-1);
	my = scipy.asarray(y_grid).reshape(-1);
	d  = scipy.asarray(indat).reshape(-1); 

	nonan_ids = indices[scipy.logical_not(numpy.isnan(d))];

	mx = mx[nonan_ids];
	my = my[nonan_ids];
	d  = d[nonan_ids];

	init_mx      = scipy.asarray(x_grid).reshape(-1)[nonan_ids];
	init_my      = scipy.asarray(y_grid).reshape(-1)[nonan_ids];
	#ramp_removed = scipy.asarray(indat).reshape(-1)[nonan_ids];
	ramp_removed = scipy.zeros(int(length) * int(width))[nonan_ids];
	init_m_ones  = scipy.ones(int(length) * int(width))[nonan_ids];

#	init_xs = [init_m_ones, init_mx, init_my, scipy.multiply(init_mx,init_my), scipy.power(init_mx,2), scipy.power(init_my,2)];
	init_xs = [init_mx];

	print(len(init_xs));

	p0 = scipy.zeros(len(init_xs));
	p  = scipy.zeros(len(init_xs));

	import scipy.optimize;

	for i in scipy.arange(0,10):

		m_ones = scipy.ones(scipy.size(mx));

#		xs     = [m_ones, mx, my, scipy.multiply(mx,my), scipy.power(mx,2), scipy.power(my,2)];
		xs     = [mx];

		G      = scipy.vstack(xs).T;
		print(mx);
		plsq   = scipy.optimize.leastsq(residuals, p0, args = (d, xs));

		res    = d - peval(xs, plsq[0]);
		mod    = plsq[0];

		p = p + mod;
		print(plsq[0]);

#		synth  = G * scipy.matrix(mod).T;
#		cutoff = res.std(axis=0,ddof=1);
		#print(cutoff);

#		indices  = numpy.arange(0, numpy.size(mx));
#		good_ids = indices[abs(res) <= cutoff];

#		plt.figure(i + 2);
#		plt.plot(mx,d,'b.',label='alloff');
#		plt.plot(mx[good_ids],synth[good_ids],'.',label='fit',color='lightgreen');
#		plt.plot(mx[bad_ids],d[bad_ids],'r.',label='cull #' + str(i + 1));
#		plt.legend();
 
#		mx = mx[good_ids];
#		my = my[good_ids];
#		d  = res[good_ids];

		d  = res;
		print(sum(res));

#		ramp_removed = scipy.asarray(ramp_removed - peval(init_xs, plsq[0]));
		ramp_removed = scipy.asarray(ramp_removed + peval(init_xs, plsq[0]));

	d = scipy.asarray(indat).reshape(-1);

	for i in range(0, scipy.size(nonan_ids)):
	
		d[nonan_ids[i]] = ramp_removed[i];

	ramp_removed = d.reshape(int(length), int(width));

#	import matplotlib;
#	matplotlib.pyplot.imshow(scipy.array(indat),interpolation='nearest',origin='lower');
#	matplotlib.pyplot.show();

	outfile = open(ramp_removed_unw_path, "wb");

	outoff = scipy.matrix(scipy.hstack((ramp_removed, ramp_removed)), scipy.float32);

	outoff.tofile(outfile);

	outfile.close();




if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: removeQuadOff.py requires 3 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	removeQuadOff(sys.argv[1], sys.argv[2], sys.argv[3]);

	exit();


