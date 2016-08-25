#!/usr/bin/python


# removeQuadOff_ENVI.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def residuals(p, y, xs):

	err = y;

	for i in range(0, len(xs)):
		err = err - p[i] * xs[i];

#	for i in range(0, len(xs)):
#		err = err - p[i] * xs;

	return err;


def peval(xs, p):

	value = p[0] * xs[0];

	for i in range(1, len(xs)):
		value = value + p[i] * xs[i];

#	for i in range(1, len(xs)):
#		value = value + p[i] * xs;

	return value;


def removeQuadOff_ENVI(input_image_path):

	import numpy;
	import pylab;
	import re;
	import scipy;
	import scipy.optimize;
	import subprocess;

	ramp_removed_image_path = "ramp_removed_" + input_image_path[input_image_path.rfind("/") + 1 : input_image_path.rfind(".")] + ".img";

	assert not os.path.exists(ramp_removed_image_path), "\n***** " + ramp_removed_image_path + " already exists, exiting...\n";

	cmd  = "\ngdalinfo " + input_image_path + "\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read();
	pipe.close();

	size = info[re.search("Size is \d+, \d+", info).start(0) + 8 : re.search("Size is \d+, \d+", info).end(0)];

	width, length = size.split(",");

	width  = width.strip();
	length = length.strip();

	if info.find("ENVI") < 0:
		out_path = input_image_path[ input_image_path.rfind("/") + 1 : input_image_path.rfind(".")] + ".img";
		cmd  = "\ngdalwarp -of ENVI -srcnodata \"nan\" -dstnodata \"nan\" " + input_image_path + " " + out_path + "\n";
		subprocess.call(cmd, shell=True);
		input_image_path = out_path;

	infile = open(input_image_path, "rb");

	indat = pylab.fromfile(infile,pylab.float32,-1).reshape(int(length), int(width));
	#indat = pylab.fromfile(infile,pylab.float32,-1).reshape(int(width) * int(length), -1);

	infile.close();

	x = scipy.arange(0, int(length));
	y = scipy.arange(0, int(width));

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
	init_xs = [init_m_ones, init_mx, init_my];

	p0 = scipy.zeros(len(init_xs));
	p  = scipy.zeros(len(init_xs));

	for i in scipy.arange(0, 1):

		m_ones = scipy.ones(scipy.size(mx));

#		xs     = [m_ones, mx, my, scipy.multiply(mx,my), scipy.power(mx,2), scipy.power(my,2)];
		xs     = [m_ones, mx, my];

		G      = scipy.vstack(xs).T;
#		print(mx);

#		print(scipy.size(d), scipy.size(xs));

		plsq   = scipy.optimize.leastsq(residuals, p0, args = (d, xs));

		res    = d - peval(xs, plsq[0]);
		mod    = plsq[0];

		p = p + mod;
#		print(plsq[0]);

		synth  = G * scipy.matrix(mod).T;
		cutoff = res.std(axis=0,ddof=1);
		#print(cutoff);

		indices  = numpy.arange(0, numpy.size(mx));
		good_ids = indices[abs(res) <= cutoff];

#		plt.figure(i + 2);
#		plt.plot(mx,d,'b.',label='alloff');
#		plt.plot(mx[good_ids],synth[good_ids],'.',label='fit',color='lightgreen');
#		plt.plot(mx[bad_ids],d[bad_ids],'r.',label='cull #' + str(i + 1));
#		plt.legend();
 
		mx = mx[good_ids];
		my = my[good_ids];
		d  = res[good_ids];

#		ramp_removed = scipy.asarray(ramp_removed - peval(init_xs, plsq[0]));
		ramp_removed = scipy.asarray(ramp_removed + peval(init_xs, plsq[0]));

	d = scipy.asarray(indat).reshape(-1);

	for i in range(0, scipy.size(nonan_ids)):
	
		d[nonan_ids[i]] = ramp_removed[i];

	ramp_removed = d.reshape(int(length), int(width));

#	import matplotlib;
#	matplotlib.pyplot.imshow(scipy.array(indat),interpolation='nearest',origin='lower');
#	matplotlib.pyplot.show();

	outfile = open(ramp_removed_image_path, "wb");

	outoff = scipy.matrix(ramp_removed, scipy.float32);

	outoff.tofile(outfile);

	outfile.close();




if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: removeQuadOff_ENVI.py requires one argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	removeQuadOff_ENVI(sys.argv[1]);

	exit();


