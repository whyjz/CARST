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
from carst import ConfParams
from carst.libdhdt import DemPile, onclick_wrapper
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

parser = ArgumentParser()
parser.add_argument('config_file', help='Configuration file')
parser.add_argument('-s', '--step', help='Do a single step', dest='step')
args = parser.parse_args()

# ==== Read ini file ====

inipath = args.config_file

ini_file = Path(inipath)
if ini_file.exists() == False:
    print('File not exists.')
    exit(1)

# ==== Create a DemPile object and load the config file into the object ====

a = DemPile()
a.read_config(inipath)

# ==== Run main processes ====

if args.step is None:
    a.init_ts()
    a.pileup()
    a.dump_pickle()
    a.polyfit()
    a.fitdata2file()
elif args.step == 'stack':
    a.init_ts()
    a.pileup()
    a.dump_pickle()
elif args.step == 'dhdt':
    a.load_pickle()
    a.polyfit()
    a.fitdata2file()
elif args.step == 'viewts':
    a.load_pickle()
    a.viz()
    plt.show()
#     data = a.ts
#     dhdt_raster, _, _, _ = a.ShowDhdtTifs()
#     img = dhdt_raster.ReadAsArray()

#     fig, ax = plt.subplots()
#     img[img < -9000] = np.nan
#     ax.imshow(img, cmap='RdBu', vmin=-6, vmax=6)
#     onclick = onclick_wrapper(data, fig, ax)

#     cid = fig.canvas.mpl_connect('button_press_event', onclick)

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
