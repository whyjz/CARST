#! /usr/bin/env python
# find the image coregistration offset between 2 Geotiff images
# Designed for SEVZ, bedrock near the surging glacier
# By Whyjay, 2016/03/18

# The 2 Geotiff images must be the same size.
#
# usage:
#
# python image_coregistar.py first_image second_image
#
#

import sys
from osgeo import gdal
import numpy as np
from scipy.signal import correlate2d
import matplotlib.pyplot as plt
gdal.UseExceptions()

def read_image(filename):
	ds = gdal.Open(filename)
	band = ds.GetRasterBand(1)
	imagery = band.ReadAsArray()
	return imagery

file1 = sys.argv[1]
file2 = sys.argv[2]

ar1 = read_image(file1)
ar2 = read_image(file2)

if not ar1.shape[0] % 2:
	ar1 = ar1[:-1, :]
	ar2 = ar2[:-1, :]

if not ar1.shape[1] % 2:
	ar1 = ar1[:, :-1]
	ar2 = ar2[:, :-1]

ar1ar2 = correlate2d(ar1, ar2, mode='same', boundary='wrap')
peak = np.unravel_index(ar1ar2.argmax(), ar1ar2.shape)
center = np.array(ar1.shape) / 2
print peak
print center
offset = np.array(center) - np.array(peak)
print 'The center of the later one is (the center of the first one + (%d, %d) [lines(y), samples(x)]' % tuple(offset)
plt.imshow(ar1, cmap='gist_earth')
plt.show()
