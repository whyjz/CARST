#!/usr/bin/env python
#
# Main dh/dt script
# by Whyjay Zheng, Jul 27 2016
# last edit: Aug 17 2016
# Major rehaul: May 7, 2018
# modified from the workflow of the FJL paper (Zheng et al, 2018)
#
# usage: python dhdt.py config_file
#
# try: 
#    python dhdt.py defaults.ini 
# for testing session.
#
# complete readme is at CARST/Doc/dhdt/README.rst

from argparse import ArgumentParser
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(sys.argv[0])) + '/../Utilities/Python')        # for all modules
from UtilConfig import ConfParams
from UtilFit import DemPile

parser = ArgumentParser()
parser.add_argument('config_file', help='Configuration file')
parser.add_argument('-s', '--step', help='Do a single stpe', dest='step')
args = parser.parse_args()

# ==== Read ini file ====

inipath = args.config_file
ini = ConfParams(inipath)
ini.ReadParam()
ini.VerifyParam()

# ==== Create a DemPile object and load the config file into the object ====

a = DemPile()
a.ReadConfig(ini)

# ==== Run main processes ====

if args.step is None:
	a.InitTS()
	a.PileUp()
	a.DumpPickle()
	a.Polyfit()
	a.Fitdata2File()
elif args.step == 'stack':
	a.InitTS()
	a.PileUp()
	a.DumpPickle()
elif args.step == 'dhdt':
	a.LoadPickle()
	a.Polyfit()
	a.Fitdata2File()
else:
	print('Wrong Way!')


# ==== Codes for test ====

# import sys
# sys.path.insert(0, '/data/whyj/Projects/Github/CARST/Utilities/Python/')
# from UtilRaster import SingleRaster
# from UtilConfig import ConfParams
# from UtilFit import DemPile
# inipath = 'defaults.ini'
# ini = ConfParams(inipath)
# ini.ReadParam()
# ini.VerifyParam()
# demlist = ini.GetDEM()
# a = DemPile()
# a.ReadConfig(ini)