#print(dem.fpath)# Class: singleDEM
# used for dhdt
# by Whyjay Zheng, Jul 21 2016

import ConfigParser
# for Python 3, this should be changed to "configparser"
import numpy as np
from UtilDEM import SingleDEM
from UtilConfig import ConfParams
from UtilFit import TimeSeriesDEM
#import matplotlib.pyplot as plt

inipath = 'defaults.ini'
outpath = 'out_dhdt.tif'

# ==== Read ini file and get DEM object list ====

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
slope, intercept, slope_err, intercept_err = dem_timeseries.Polyfit()

# ==== Write to file ====

outdem = SingleDEM(outpath)
outdem.Array2Raster(slope, demlist[0])

'''

arrayshape = list(demlist[0].ReadAsArray().shape)
arrayshape.append(len(demlist))
reg_array = np.empty(arrayshape)
t = list(np.empty(len(demlist)))    # transformed to list becuase np.array cannot allow objects and numbers together in the same array
w = np.empty(len(demlist))

for i in range(len(demlist)):
	reg_array[:, :, i] = demlist[i].ReadAsArray()
	t[i] = demlist[i].date
	w[i] = 1.0 / demlist[i].uncertainty ** 2

# from datetime object to timedelta (offset from the first date), in days
t = np.array(t) - t[0]
t = np.array([i.days for i in t])

# ==== Weighted regression ====

dem_timeseries = TimeSeriesDEM(reg_array)
slope, intercept, slope_err, intercept_err = dem_timeseries.Polyfit(t, w)

# ==== Write to file ====

outdem = SingleDEM(outpath)
outdem.Array2Raster(slope, demlist[0])

'''



#plt.imshow(slope)
#plt.show()
