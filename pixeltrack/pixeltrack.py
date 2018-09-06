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
from UtilXYZ import ZArray, AmpcoroffFile
# from UtilFit import DemPile
import numpy as np

parser = ArgumentParser()
parser.add_argument('config_file', help='Configuration file')
parser.add_argument('-s', '--step', help='Do a single step', dest='step')
args = parser.parse_args()

# ==== Read ini file ====

inipath = args.config_file
ini = ConfParams(inipath)
ini.ReadParam()
ini.VerifyParam()

# ==== Create two SingleRaster object and make them ready for pixel tracking ====

if args.step == 'ampcor' or args.step is None:

	a = SingleRaster(ini.imagepair['image1'], date=ini.imagepair['image1_date'])
	b = SingleRaster(ini.imagepair['image2'], date=ini.imagepair['image2_date'])
	a.AmpcorPrep()
	b.AmpcorPrep()

	# ==== Run main processes ====

	task = ampcor_task([a, b], ini)
	writeout_ampcor_task(task, ini)

if args.step == 'rawvelo' or args.step is None:

	ampoff = AmpcoroffFile(ini.result['ampcor_results'])
	ampoff.Load()
	ampoff.SetIni(ini)
	ampoff.Ampcoroff2Velo()
	ampoff.Velo2XYV()
	ampoff.XYV2Raster()

if args.step == 'correctvelo' or args.step is None:

	ras = ini.result['geotiff_prefix'] + '_vx.tif'
	shp = ini.velocorrection['bedrock']
	vx = SingleRaster(ras)
	bdval_list = ZArray(vx.ClippedByPolygon(shp))
	# print(bdval_list)
	idx2, mean, median_x, std = bdval_list.StatisticOutput(pngname=ini.velocorrection['histogram_x'])
	ras = ini.result['geotiff_prefix'] + '_vy.tif'
	shp = ini.velocorrection['bedrock']
	vy = SingleRaster(ras)
	bdval_list = ZArray(vy.ClippedByPolygon(shp))
	# print(bdval_list)
	idx2, mean, median_y, std = bdval_list.StatisticOutput(pngname=ini.velocorrection['histogram_y'])

	vxa = vx.ReadAsArray()
	vya = vy.ReadAsArray()
	vxa = vxa - median_x
	vya = vya - median_y
	maga = np.sqrt(vxa ** 2 + vya ** 2)

	ras_xa = SingleRaster(ini.velocorrection['geotiff_prefix'] + '_vx.tif')
	ras_ya = SingleRaster(ini.velocorrection['geotiff_prefix'] + '_vy.tif')
	ras_maga = SingleRaster(ini.velocorrection['geotiff_prefix'] + '_mag.tif')
	ras_xa.Array2Raster(vxa, vx)
	ras_ya.Array2Raster(vya, vx)
	ras_maga.Array2Raster(maga, vx)

# needs statistics

if args.step == 'hp':

	from scipy import ndimage
	a = SingleRaster(ini.imagepair['image2'], date=ini.imagepair['image2_date'])
	data = a.ReadAsArray()
	lowpass = ndimage.gaussian_filter(data.astype(float), 3)
	gauss_highpass = data - lowpass
	ag = SingleRaster(ini.imagepair['image2'].replace('.TIF', 'GHP_3sig.TIF'))
	ag.Array2Raster(gauss_highpass, a)
	# ag = SingleRaster(ini.imagepair['image1'].replace('.TIF', 'GLP_3sig.TIF'))
	# ag.Array2Raster(lowpass, a)



# ==== Codes for test ====

# import sys
# sys.path.insert(0, '/data/whyj/Projects/Github/CARST/Utilities/Python/')
# from UtilRaster import SingleRaster
# from UtilConfig import ConfParams
# import numpy as np
# inipath = 'defaults.ini'
# ini = ConfParams(inipath)
# ini.ReadParam()
# ini.VerifyParam()