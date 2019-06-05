#!/usr/bin/env python
# This is currently only for Landsat 8 images in Severnaya Zemlya (EPSG:32646, 32647, or 32645)
# return the EPSG number of a Geotiff image

import sys
from osgeo import gdal

filename = sys.argv[1]
gtif = gdal.Open(filename)
projstr = gtif.GetProjection()
projstr = projstr.split('],')
cent_meri = ''
for param in projstr:
    if param.find('central_meridian') >= 0:
        cent_meri = param.split(',')[1]
if cent_meri == '99':
    print 'EPSG:32647'
elif cent_meri == '93':
    print 'EPSG:32646'
elif cent_meri == '87':
    print 'EPSG:32645'
else:
    print 'Unknown'
