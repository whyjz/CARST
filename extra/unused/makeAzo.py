#!/usr/bin/python

# makeAzo.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


import numpy;
import pylab;
import scipy;
import sys;


def makeAzo(azo_off_path, da_p, r_e, p_h, dr, angle, wsamp, rwin, awin, search_x, search_y, width, length): 

	index = azo_off_path.rfind("/");

	azo_dir = azo_off_path[ : index];

	if index < 0:
		azo_dir = ".";

	cmd = "sed -e '/\*/d' " + azo_off_path + " > temp\nmv " + azo_off_path + " " + azo_off_path + ".old\nmv temp " + azo_off_path +"\n";

	infile = open(azo_off_path, "r");

	# Read entire binary file into matrix "indat" which
	# is reshaped to have 8 columns
	#indat = pylab.fromfile(infile,pylab.float32,-1).reshape(-1,8);
	indat = numpy.genfromtxt(infile);

	infile.close();

	#da_p = ;#azimuth pixel size at orbit radius
	#r_e  = ; #earth radius
	#p_h  = ; #platform height
	r_p  = r_e + p_h;        #platform radius
	da_e = da_p * r_e / r_p * 100; #az pixel size at earth surface, cm    
	#dr   = ; #range pixel size
	la   =  angle * pylab.pi / 180;      #look angle
	dr_g = dr / pylab.sin(la) * 100;  #ground pixel size in range direction, cm

	x1ind  = scipy.matrix([indat[:,0]],pylab.int32).conj().transpose();
	dx     = scipy.matrix([indat[:,1]]).conj().transpose();
	y1ind  = scipy.matrix([indat[:,2]],pylab.int32).conj().transpose(); 
	dy     = scipy.matrix([indat[:,3]]).conj().transpose();
	snr = scipy.matrix([indat[:,4]]).conj().transpose();
	c11 = scipy.matrix([scipy.sqrt(indat[:,5])]).conj().transpose(); #1 sigma drng
	c22 = scipy.matrix([scipy.sqrt(indat[:,6])]).conj().transpose(); #1 sigma dazo
	c12 = scipy.matrix([indat[:,7]]).conj().transpose();

	#these may need to be hardwired for eventual geocoding        
	#width  = max(x1ind)+rwin
	#length = max(y1ind)+awin
	#must read in from azo.rsc file

	x1 = x1ind * dr_g; 
	dx = dx * dr_g;
	y1 = y1ind * da_e;
	dy = dy * da_e;
	c11 = c11 * dr_g; #1 sigma drng
	c22 = c22 * da_e; #1 sigma dazo
	x2 = x1+dx;
	y2 = y1+dy;

	rlooks = rwin / wsamp;
	alooks = awin / wsamp;

	width1  = scipy.floor(width / rlooks);
	length1 = scipy.floor(length / alooks);
	[xg,yg] = scipy.meshgrid(scipy.arange(1,width1+1,1),scipy.arange(1,length1+1,1));
	xg = xg * dr_g * rlooks / 1e5; #convert from pix to km
	yg = yg * da_e * alooks / 1e5; #convert from pix to km

	#load_azo

	sigy_thresh = 1e1000;  #cm
	sigx_thresh = 1e1000; #cm
	snr_thresh  = 0;   #(not log10)
	mag_threshx  = 1e1000; #cm
	mag_threshy  = 1e1000; #cm

	#initial mask
	c22good = scipy.matrix(pylab.find(c22<sigy_thresh)).conj().transpose();
	c11good = scipy.matrix(pylab.find(c11<sigx_thresh)).conj().transpose();
	snrgood = scipy.matrix(pylab.find(snr>snr_thresh)).conj().transpose();

	good = (scipy.matrix(scipy.unique(scipy.asarray(scipy.concatenate((snrgood, c11good, c22good),axis=0))))).conj().transpose();

	x1good    = x1[good].reshape(-1,1);
	x1goodind = x1ind[good].reshape(-1,1);
	y1good    = y1[good].reshape(-1,1);
	y1goodind = y1ind[good].reshape(-1,1);
	x2good    = x2[good].reshape(-1,1);
	y2good    = y2[good].reshape(-1,1);

	#get and remove affine fit
	good2 = scipy.matrix(pylab.find(good<300000)).conj().transpose();

	x1good    = x1[good2].reshape(-1,1);
	y1good    = y1[good2].reshape(-1,1);
	x2good    = x2[good2].reshape(-1,1);
	y2good    = y2[good2].reshape(-1,1);

	c0 = scipy.matrix(scipy.zeros((scipy.size(good2)))).reshape(-1,1);
	c1 = scipy.matrix(scipy.ones((scipy.size(good2)))).reshape(-1,1);
	n  = c1.shape[0];

	A = scipy.vstack((scipy.hstack((x1good, y1good, c0, c0, c1, c0)),
	                  scipy.hstack((c0, c0, x1good, y1good, c0, c1))));

	b = scipy.vstack((x2good,y2good));

	M = numpy.linalg.lstsq(A,b)[0];

	pred = A*M;
	res  = pred - b;

	# std() in python defaults to 0 degrees of freedom
	resdev=res.std(axis=0,ddof=1);
	q = pylab.find(abs(res)<1.5*resdev);
	A1 = A[q,];
	b1 = b[q];
	M = numpy.linalg.lstsq(A1,b1)[0];
	pred = A*M;


	x1good    = x1[good].reshape(-1,1);
	x1goodind = x1ind[good].reshape(-1,1);
	y1good    = y1[good].reshape(-1,1);
	y1goodind = y1ind[good].reshape(-1,1);
	x2good    = x2[good].reshape(-1,1);
	y2good    = y2[good].reshape(-1,1);

	c0 = scipy.matrix(scipy.zeros((scipy.size(good)))).reshape(-1,1);
	c1 = scipy.matrix(scipy.ones((scipy.size(good)))).reshape(-1,1);
	n  = c1.shape[0];

	A = scipy.vstack((scipy.hstack((x1good, y1good, c0, c0, c1, c0)),
	                  scipy.hstack((c0, c0, x1good, y1good, c0, c1))));

	b = scipy.vstack((x2good,y2good));

	pred = A*M;

	n  = c1.shape[0];

	res  = pred - b;
	resdx = res[0:n];
	resdy = res[(n):(2*n)];

	#remap into matrix
	newx = scipy.matrix(scipy.ceil(x1goodind/rlooks),pylab.int32);
	newy = scipy.matrix(scipy.floor(y1goodind/alooks),pylab.int32);

	vind = scipy.asarray((newy-1)*width1+newx,pylab.int32).reshape(-1);

	temp = scipy.matrix(0*(scipy.arange(1,length1*width1+1,1))).conj().transpose();
	temp[vind] = resdy;
	dyg = temp.reshape(length1,width1);

	temp = scipy.matrix(0*(scipy.arange(1,length1*width1+1,1))).conj().transpose();
	temp[vind] = resdx;
	dxg = temp.reshape(length1,width1);

	#setup mask indicies
	newx = scipy.matrix(scipy.ceil(x1ind  / rlooks),pylab.int32);
	newy = scipy.matrix(scipy.floor(y1ind / alooks),pylab.int32);
	vind = scipy.asarray((newy-1)*width1+newx,pylab.int32).reshape(-1);
	temp = scipy.NaN*scipy.matrix(scipy.arange(0,length1*width1,1)).conj().transpose();

	#sigma_y mask
	temp[vind] = c22;
	sigyg = temp.reshape(length1,width1);
	mask_sigy = scipy.zeros(dyg.shape);
	mask_sigy[(sigyg>sigy_thresh)] = scipy.NaN;

	#sigma_x mask
	temp = scipy.NaN*scipy.matrix(scipy.arange(0,length1*width1,1)).conj().transpose();
	temp[vind] = c11;
	sigxg = temp.reshape(length1,width1);
	mask_sigx = scipy.zeros(dxg.shape);
	mask_sigx[(sigxg>sigx_thresh)] = scipy.NaN;

	#SNR mask
	temp = scipy.NaN*scipy.matrix(scipy.arange(0,length1*width1,1)).conj().transpose();
	temp[vind] = snr;
	snrg = temp.reshape(length1,width1);
	mask_snr = scipy.zeros(dyg.shape);
	mask_snr[(snrg<snr_thresh)] = scipy.NaN;

	#mag mask y
	mask_magy = scipy.zeros(dyg.shape);
	mask_magy[abs(dyg)>mag_threshy] = scipy.NaN;

	#mag mask x
	mask_magx = scipy.zeros(dxg.shape);
	mask_magx[abs(dxg)>mag_threshx] = scipy.NaN;

	#final mask
	mask_total = mask_snr + mask_sigy + mask_magy;
	bad = scipy.isnan(mask_total);
	dyg[bad] = scipy.NaN;

	mask_total = mask_snr + mask_sigx + mask_magx;
	bad = scipy.isnan(mask_total);
	dxg[bad] = scipy.NaN;

	#dump output to binary file
	outg = scipy.hstack((abs(dyg),dyg));
	outr = scipy.hstack((dxg,dxg));
	outsnr = scipy.hstack((snrg,snrg));
	ind =scipy.isnan(outg);
	outg[ind==1]=0;
	outr[ind==1]=0;

	outfile = open(azo_dir + "/azimuth_r" + str(rwin) + "x" + str(awin) + "_s" + search_x + "x" + search_y + "_" + str(int(rwin)/int(wsamp)) + "rlks.unw", 'wb');
	outg = scipy.matrix(outg,scipy.float32);
	outg.tofile(outfile);
	outfile.close();

	outfile = open(azo_dir + "/range_r" + str(rwin) + "x" + str(awin) + "_s" + search_x + "x" + search_y + "_" + str(int(rwin)/int(wsamp)) + "rlks.unw", 'wb');
	outr = scipy.matrix(outr,scipy.float32);
	outr.tofile(outfile);
	outfile.close();

	outfile = open(azo_dir + "/snr_r" + str(rwin) + "x" + str(awin) + "_s" + search_x + "x" + search_y + "_" + str(int(rwin)/int(wsamp)) + "rlks.unw", 'wb');
	outsnr = scipy.matrix(outsnr,scipy.float32);
	outsnr.tofile(outfile);
	outfile.close();
	
	return;


def main():
	load_and_make_azo();
	exit;

	
if __name__ == "__main__":
	import sys;
	load_and_make_azo(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10], sys.argv[11], sys.argv[12], sys.arv[13]);

