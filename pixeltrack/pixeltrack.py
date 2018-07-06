#!/usr/bin/env python
#
# Main pixel-tracking (feature-tracking) script
# by Whyjay Zheng, Jul 6 2018

# All concepts are from the old pixel-tracking code
# but this code is using ampcor packing in ISCE instead of ROI_PAC
# Hence, everything is rewritten to fit the CARST convention
#
# usage: python pixeltrack.py config_file
#
# try: 
#    python pixeltrack.py defaults.ini 
# for testing session.
#
# complete readme is at CARST/Doc/pixeltrack/README.rst

from argparse import ArgumentParser
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(sys.argv[0])) + '/../Utilities/Python')        # for all modules
from UtilRaster import SingleRaster
from UtilConfig import ConfParams
from UtilPX import ampcor_task, writeout_ampcor_task
# from UtilFit import DemPile
import numpy as np
from scipy.interpolate import griddata

parser = ArgumentParser()
parser.add_argument('config_file', help='Configuration file')
parser.add_argument('-s', '--step', help='Do a single step', dest='step')
args = parser.parse_args()

# ==== Read ini file ====

inipath = args.config_file
ini = ConfParams(inipath)
ini.ReadParam()
ini.VerifyParam()

# # ==== Create two SingleRaster object and make them ready for pixel tracking ====

if args.step == 'ampcor':

	a = SingleRaster(ini.imagepair['image1'], date=ini.imagepair['image1_date'])
	b = SingleRaster(ini.imagepair['image2'], date=ini.imagepair['image2_date'])
	a.AmpcorPrep()
	b.AmpcorPrep()

	# # ==== Run main processes ====

	task = ampcor_task([a, b], ini)
	writeout_ampcor_task(task, ini)

elif args.step == 'cont':

	a = SingleRaster(ini.imagepair['image1'], date=ini.imagepair['image1_date'])
	b = SingleRaster(ini.imagepair['image2'], date=ini.imagepair['image2_date'])
	ampoff = np.loadtxt(ini.result['ampcor_results'])
	# extent = a.GetExtent()
	geot = a.GetGeoTransform()
	ulx = geot[0]
	uly = geot[3]
	xres = geot[1]
	yres = geot[5]
	datedelta = b.date - a.date
	ampoff[:, 0] = ulx + (ampoff[:, 0] - 1) * xres
	ampoff[:, 1] = ampoff[:, 1] * abs(xres) / datedelta.days
	ampoff[:, 2] = uly + (ampoff[:, 2] - 1) * yres
	ampoff[:, 3] = ampoff[:, 3] * abs(yres) / datedelta.days

	xoffset = ampoff[:,[0,2,1]]
	yoffset = ampoff[:,[0,2,3]]


	np.savetxt('Demo_Tifs/xoff.txt', xoffset, delimiter=" ", fmt='%10.2f %10.2f %10.6f')

	outres = np.sqrt((xoffset[1, 0] - xoffset[0, 0]) * (xoffset[0, 1] - xoffset[37, 1]))
	x = np.arange(xoffset[0, 0], xoffset[-1, 0], outres)
	y = np.arange(xoffset[0, 1], xoffset[-1, 1], -outres)
	xx, yy = np.meshgrid(x, y)

	zz = griddata(xoffset[:, [0,1]], xoffset[:, 2], (xx, yy), method='linear')

	xoffset_xyz = np.stack([xx.flatten(), yy.flatten(), zz.flatten()]).T
	np.savetxt('Demo_Tifs/xoff.xyz', xoffset_xyz, delimiter=" ", fmt='%10.2f %10.2f %10.6f')

	xout = SingleRaster('Demo_Tifs/xoff.tif')
	xout.XYZ2Raster('Demo_Tifs/xoff.xyz', projection=a.GetProjection())






# if args.step is None:
# 	a.InitTS()
# 	a.PileUp()
# 	a.DumpPickle()
# 	a.Polyfit()
# 	a.Fitdata2File()
# elif args.step == 'stack':
# 	a.InitTS()
# 	a.PileUp()
# 	a.DumpPickle()
# elif args.step == 'dhdt':
# 	a.LoadPickle()
# 	a.Polyfit()
# 	a.Fitdata2File()
# else:
# 	print('Wrong Way!')


# ==== Codes for test ====

import sys
sys.path.insert(0, '/data/whyj/Projects/Github/CARST/Utilities/Python/')
from UtilRaster import SingleRaster
from UtilConfig import ConfParams
import numpy as np
inipath = 'defaults.ini'
ini = ConfParams(inipath)
ini.ReadParam()
ini.VerifyParam()