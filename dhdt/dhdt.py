#!/usr/bin/env python
#
# Main dh/dt script
# by Whyjay Zheng, Jul 27 2016
# last edit: Aug 17 2016
#
# usage: python dhdt.py config_file
#
# try: 
#    python dhdt.py defaults.ini 
# for testing session.
#
# complete readme is at CARST/Doc/dhdt/README.rst


import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('../Utilities/v0_2'))        # for all modules
from UtilDEM import SingleDEM
from UtilConfig import ConfParams
from UtilFit import TimeSeriesDEM

if len(sys.argv) < 2:
	print('Error: Usage: dhdt.py config_file')
	sys.exit(1)

# ==== Read ini file and get DEM object list ====

inipath = sys.argv[1]
ini = ConfParams(inipath)
ini.ReadParam()
demlist = ini.GetDEM()

# ==== warp all DEMs using gdalwarp ====

for dem in demlist:
	dem.Unify(ini.gdalwarp)

# ==== Complie DEM time series (including data, time, and variance) ====

dem_timeseries = TimeSeriesDEM(demlist[0])
for i in range(1, len(demlist)):
	print('Add DEM: ' + demlist[i].fpath)
	dem_timeseries = dem_timeseries.AddDEM(demlist[i])

# ==== Weighted regression ====

dem_timeseries.Date2DayDelta()
dem_timeseries.SetWeight()
print("Start Polyfit; pixel number = " + str(dem_timeseries.shape[0] * dem_timeseries.shape[1]))
slope, intercept, slope_err, intercept_err = dem_timeseries.Polyfit(**ini.regression)

# ==== Write to file ====

dhdt_dem     = SingleDEM('/'.join([ini.result['output_dir'], ini.result['gtiff_slope']]))
dhdt_dem.Array2Raster(slope, demlist[0])
dhdt_err_dem = SingleDEM('/'.join([ini.result['output_dir'], ini.result['gtiff_slope_err']]))
dhdt_err_dem.Array2Raster(slope_err, demlist[0])