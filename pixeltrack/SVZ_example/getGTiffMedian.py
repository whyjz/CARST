#!/usr/bin/env python
# return the Median value of a Geotiff image (only containing 1 band)

import sys
import numpy as np
from osgeo import gdal

filename = sys.argv[1]
gtif = gdal.Open(filename)
image = gtif.GetRasterBand(1)
value_arr = image.ReadAsArray()
print np.median(value_arr[~np.isnan(value_arr)])