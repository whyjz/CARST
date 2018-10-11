#!/usr/bin/env python
#
# Main pixel-tracking (feature-tracking) script
# by Whyjay Zheng, Jul 6 2018
# laste modified: Sep 13, 2018

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
from UtilRaster import SingleRaster, RasterVelos
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
	if ini.pxsettings['gaussian_hp']:
		a.GaussianHighPass(sigma=3)
		b.GaussianHighPass(sigma=3)
	a.AmpcorPrep()
	b.AmpcorPrep()

	# ==== Run main processes ====

	task = ampcor_task([a, b], ini)
	writeout_ampcor_task(task, ini)

if args.step == 'rawvelo' or args.step is None:

	ampoff = AmpcoroffFile(ini.rawoutput['label_ampcor'] + '.p')
	ampoff.Load()
	ampoff.SetIni(ini)
	ampoff.Ampcoroff2Velo()
	ampoff.Velo2XYV(generate_xyztext=ini.rawoutput['if_generate_xyztext'])
	ampoff.XYV2Raster()

if args.step == 'correctvelo' or args.step is None:

	# We don't do elevation-depended correction for this version.
	# Maybe it will be included in the future release.

	shp = ini.velocorrection['bedrock']
	prefix = ini.rawoutput['label_geotiff']
	velo = RasterVelos(vx=SingleRaster(prefix + '_vx.tif'),
		               vy=SingleRaster(prefix + '_vy.tif'),
		               snr=SingleRaster(prefix + '_snr.tif'),
		               mag=SingleRaster(prefix + '_mag.tif'),
		               errx=SingleRaster(prefix + '_errx.tif'),
		               erry=SingleRaster(prefix + '_erry.tif'))

	# SNR constraint
	snr_bdval = ZArray(velo.snr.ClippedByPolygon(shp))
	selected_bd_pos = snr_bdval >= ini.noiseremoval['snr']

	vxraw_bdval = ZArray(velo.vx.ClippedByPolygon(shp))
	vxraw_bdval = vxraw_bdval[selected_bd_pos]
	vxraw_bdval.StatisticOutput(pngname=ini.velocorrection['label_bedrock_histogram'] + '_vx.png')

	vyraw_bdval = ZArray(velo.vy.ClippedByPolygon(shp))
	vyraw_bdval = vyraw_bdval[selected_bd_pos]
	vyraw_bdval.StatisticOutput(pngname=ini.velocorrection['label_bedrock_histogram'] + '_vy.png')

	velo.VeloCorrectionInfo(vxraw_bdval, vyraw_bdval, ini.velocorrection['label_logfile'], pngname=ini.velocorrection['label_bedrock_histogram'] + '_vx-vs-vy.png' )
	velo.VeloCorrection(vxraw_bdval, vyraw_bdval, ini.velocorrection['label_geotiff'])

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
	velo.Gaussian_CutNoise()
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