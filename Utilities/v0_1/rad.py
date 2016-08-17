#!/usr/bin/python

import numpy;
import scipy;
import subprocess;

radarld="radar_ODR_5rlks";
width="1122";
wavelength=100.0*0.0565646;

cmd="\nrmg2mag_phs "+radarld+".unw "+radarld+".mag "+radarld+".phs "+width+"\n";
subprocess.call(cmd,shell=True);

file=open(radarld+".phs","rb");
phs=scipy.matrix(numpy.fromfile(file,numpy.float32,-1)).reshape(int(width),-1);
phs=phs*wavelength/4/numpy.pi;
file.close();

phs=scipy.matrix(phs,scipy.float32);
phs.tofile("adj_"+radarld+".phs");

exit();
