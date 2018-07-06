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

parser = ArgumentParser()
parser.add_argument('config_file', help='Configuration file')
# parser.add_argument('-s', '--step', help='Do a single step', dest='step')
args = parser.parse_args()

# ==== Read ini file ====

inipath = args.config_file
ini = ConfParams(inipath)
ini.ReadParam()
ini.VerifyParam()

# # ==== Create two SingleRaster object and make them ready for pixel tracking ====

a = SingleRaster(ini.imagepair['image1'], date=ini.imagepair['image1_date'])
b = SingleRaster(ini.imagepair['image2'], date=ini.imagepair['image2_date'])
a.AmpcorPrep()
b.AmpcorPrep()

# # ==== Run main processes ====

task = ampcor_task([a, b], ini)
writeout_ampcor_task(task, ini)

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

# import sys
# sys.path.insert(0, '/data/whyj/Projects/Github/CARST/Utilities/Python/')
# from UtilRaster import SingleRaster
# from UtilConfig import ConfParams
# inipath = 'defaults.ini'
# ini = ConfParams(inipath)
# ini.ReadParam()
# ini.VerifyParam()