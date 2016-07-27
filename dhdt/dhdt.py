#print(dem.fpath)# Class: singleDEM
# used for dhdt
# by Whyjay Zheng, Jul 27 2016

import ConfigParser
# for Python 3, this should be changed to "configparser"
import numpy as np
from UtilDEM import SingleDEM
from UtilConfig import ConfParams
from UtilFit import TimeSeriesDEM
import sys

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
	dem_timeseries = dem_timeseries.AddDEM(demlist[i])

# ==== Weighted regression ====

dem_timeseries.Date2DayDelta()
dem_timeseries.SetWeight()
slope, intercept, slope_err, intercept_err = dem_timeseries.Polyfit(**ini.regression)

# ==== Write to file ====

outdem = SingleDEM(ini.output['gtiff_slope'])
outdem.Array2Raster(slope, demlist[0])
