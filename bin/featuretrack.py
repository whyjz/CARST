#!/usr/bin/env python
#
# Main pixel-tracking (feature-tracking) script
# by Whyjay Zheng, Jul 6 2018
# laste modified: May 15, 2020

# The code uses the ampcor module, which was developed as part of 
# ROI_PAC and was inherited by ISCE.
# To use this script, ISCE must be installed first.
#
# usage: python pixeltrack.py config_file [-s STAGE]
#
# availabe STAGE name: 
#    ampcor        ---> perform ampcor (amplitude correlator) using NCC
#    rawvelo       ---> read the raw ampcor output data (in python's pickle format) and convert them into geotiffs
#    correctvelo   ---> read the data at user-defined regions where velocity is assumed to be zero, and calculate corrected velocities and uncertainties
#    rmnoise       ---> mask pixels with unreliable data
# when -s option is omitted, the script will run all the steps 
#
# try: 
#    python pixeltrack.py defaults.ini 
# for testing session.
#
# complete readme is at CARST/Doc/pixeltrack/README.rst

from argparse import ArgumentParser
import sys
import os
from carst import SingleRaster, RasterVelos, ConfParams
from carst.libft import ampcor_task, writeout_ampcor_task
from carst.libxyz import ZArray, DuoZArray, AmpcoroffFile, points_in_polygon
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
	if ini.pxsettings['gaussian_hp']:
		a.GaussianHighPass(sigma=ini.pxsettings['gaussian_hp_sigma'])
		b.GaussianHighPass(sigma=ini.pxsettings['gaussian_hp_sigma'])
	a.AmpcorPrep()
	b.AmpcorPrep()

	# ==== Run main processes ====

	task = ampcor_task([a, b], ini)
	writeout_ampcor_task(task, ini)

if args.step == 'rawvelo' or args.step is None:

	ampoff = AmpcoroffFile(ini.rawoutput['label_ampcor'] + '.p')
	ampoff.Load()
	ampoff.SetIni(ini)
	ampoff.FillwithNAN()   # fill holes with nan
	ampoff.Ampcoroff2Velo()
	ampoff.Velo2XYV(generate_xyztext=ini.rawoutput['if_generate_xyztext'])
	ampoff.XYV2Raster()

if args.step == 'correctvelo' or args.step is None:

	# We don't do elevation-depended correction for this version.
	# Maybe it will be included in the future release.

	ampoff = AmpcoroffFile(ini.rawoutput['label_ampcor'] + '.p')
	ampoff.Load()
	ampoff.SetIni(ini)
	ampoff.FillwithNAN()
	ampoff.Ampcoroff2Velo(velo_or_pixel='pixel')

	shp = ini.velocorrection['bedrock']
	prefix = ini.rawoutput['label_geotiff']
	velo = RasterVelos(vx=SingleRaster(prefix + '_vx.tif'),
		               vy=SingleRaster(prefix + '_vy.tif'),
		               snr=SingleRaster(prefix + '_snr.tif'),
		               mag=SingleRaster(prefix + '_mag.tif'),
		               errx=SingleRaster(prefix + '_errx.tif'),
		               erry=SingleRaster(prefix + '_erry.tif'))

	idx = points_in_polygon(ampoff.data[:, [0,2]], shp)

	# SNR constraint
	snr_threshold = ampoff.snr[:, 2] >= ini.noiseremoval['snr']
	idx = np.logical_and(idx, snr_threshold)


	vxraw_bdval = ZArray(ampoff.velo_x[idx, 2])
	vyraw_bdval = ZArray(ampoff.velo_y[idx, 2])
	vxyraw_bdval = DuoZArray(z1=vxraw_bdval, z2=vyraw_bdval, ini=ini)
	vxyraw_bdval.OutlierDetection2D(thres_sigma=ini.velocorrection['refvelo_outlier_sigma'])
	vxyraw_bdval.HistWithOutliers(which='x')
	vxyraw_bdval.HistWithOutliers(which='y')
	vxraw_bdval_velo, vyraw_bdval_velo = vxyraw_bdval.VeloCorrectionInfo()
	velo.VeloCorrection(vxraw_bdval_velo, vyraw_bdval_velo, ini.velocorrection['label_geotiff'])

if args.step == 'rmnoise' or args.step is None:

	try: 
		velo
	except NameError:
		prefix = ini.velocorrection['label_geotiff']
		velo = RasterVelos(vx=SingleRaster(prefix + '_vx.tif'),
		                   vy=SingleRaster(prefix + '_vy.tif'),
		                   snr=SingleRaster(ini.rawoutput['label_geotiff'] + '_snr.tif'),
		                   mag=SingleRaster(prefix + '_mag.tif'),
		                   errx=SingleRaster(prefix + '_errx.tif'),
		                   erry=SingleRaster(prefix + '_erry.tif'),
		                   errmag=SingleRaster(prefix + '_errmag.tif'))

	velo.SNR_CutNoise(snr_threshold=ini.noiseremoval['snr'])
	velo.Gaussian_CutNoise(sigma=ini.noiseremoval['gaussian_lp_mask_sigma'])
	velo.SmallObjects_CutNoise(min_size=ini.noiseremoval['min_clump_size'])
	# velo.MorphoOpen_CutNoise()
	# velo.Fahnestock_CutNoise()
	velo.MaskAllRasters()







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
