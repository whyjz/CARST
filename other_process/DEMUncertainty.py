#!/usr/bin/env python
#
# get uncertainty of a single DEM, using the provided reference points (e.g. ICESAT).
# last modified: Whyjay Zheng, June 6, 2019
#
#
# usage: DEMUncertainty.py [-h] [-z Z_FIELD] Refpts_file DEM_file
#        positional arguments:
#                Refpts_file           Path to the reference points 
#                                      (can be an ESRI shapefile or a 3-column textfile in XYZ format)
#                DEM_file              DEM file name (Must be a Geotiff, CRS must agree with the reference points)
#
#        optional arguments:
#               -z Z_FIELD, --zfield Z_FIELD   Field name for accessing reference values
#                                              (MANDATORY if using a shapefile for reference points)
#
#
# example: 1) DEMUncertainty.py data/ICESAT_subset.shp ../dhdt/Demo_DEMs/HookerFJL_11AUG16WV01DEM1_EPSG32640.tif -z H_ell
#          2) DEMUncertainty.py data/ICESAT_subset2.xyz ../dhdt/Demo_DEMs/HookerFJL_11AUG16WV01DEM1_EPSG32640.tif 
#
#
# output: There are 2 output files. All have the same file name from DEM file, but the file extensions are different.
#         1) A png file showing the histogram of the offset between the DEM and the reference points.
#         2) A text (.param) file showing statistics of the offset; the std of which is used to estimate DEM uncertainty.
#         The output file is properly formatted so it fits the param file the main dh/dt script (dhdt.py) needs.
#
# version history: This script is modified from
#     v0.1: getPointsAtIcesat.py
#     v0.2: corrected_dem_var.bash, corrected_dem_var.py
#     v1.0: getUncertaintyDEM.py (This one runs slowly on a large DEM or a large reference dataset)


from argparse import ArgumentParser
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(sys.argv[0])) + '/../Utilities/Python')        # for all modules
from UtilRaster import SingleRaster, timeit
from UtilXYZ import ZArray
import numpy as np

parser = ArgumentParser()
parser.add_argument('Refpts_file', help='Path to the reference points')
parser.add_argument('DEM_file',    help='DEM file name')
parser.add_argument('-z', '--zfield',   help='(MANDATORY if using a shapefile for reference points) Field name for accessing reference values', dest='z_field')
args = parser.parse_args()

@timeit
def DEMUncertainty(pointfilepath, demfpath, zfield=None):

	if pointfilepath.split('.')[-1] == 'shp':
		import geopandas as gpd
		shp = gpd.read_file(pointfilepath)
		x = np.array([i.x for i in shp['geometry']])
		y = np.array([i.y for i in shp['geometry']])
		z = np.array([i for i in shp[zfield]])
	else:
		xyz = np.loadtxt(pointfilepath)
		x = xyz[:, 0]
		y = xyz[:, 1]
		z = xyz[:, 2]	

	dem = SingleRaster(demfpath)
	demz = dem.ReadGeolocPoints(x, y)

	offset = demz - z
	nonan_idx = ~np.isnan(offset)
	offset = ZArray(offset[nonan_idx])
	output_png = demfpath.replace('.tif', '.png')
	# output_png = output_png.split('/')[-1]
	offset.MADStats()
	offset.MADHist(output_png)
	return offset

offset = DEMUncertainty(args.Refpts_file, args.DEM_file, args.z_field)
paramfile = args.DEM_file.replace('.tif', '.param')
# paramfile = paramfile.split('/')[-1]
with open(paramfile, 'w') as f:
	f.write('n      = {}\n'.format(offset.size))
	f.write('mean   = {}\n'.format(offset.MAD_mean))
	f.write('median = {}\n'.format(offset.MAD_median))
	f.write('std    = {}\n'.format(offset.MAD_std))
	f.write('refpts = {}\n'.format(os.path.abspath(args.Refpts_file)))





# ==== Other possible input for testing purpose ====
# pointfile = '/data/whyj/Projects/Franz_Josef_Land/Source/Shapefile_ICESAT_classification/ICESAT_forFJL_correction/ICESAT_FJL_UTM40_BR_SP_SS_RemovedOutlier.shp'
# demfile = '/13t1/whyj/Projects/Franz_Josef_Land/DEM_Aligned/WV_3m_Rankfiltered/RankFilterSquare4Thres50_11AUG16_WV01_FJL_1020010015941D00_1020010015D7CD00_DEM1-3m_ICESAT-Aligned.tif'
# demfile = '/13t1/whyj/Projects/Franz_Josef_Land/DEM_Aligned/WV_3m_Rankfiltered/RankFilterSquare4Thres50_12MAR22_WV01_FJL_102001001A7FC400_102001001AB83F00_DEM1-3m_ICESAT-Aligned.tif' # a huge one