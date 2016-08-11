# get uncertainty of a single DEM, using the referenced ICESAT returns over bedrock.
# used for dhdt
# by Whyjay Zheng, Jul 28 2016
#
# Modified from
#     v0.1: getPointsAtIcesat.py
#     later version: corrected_dem_var.bash corrected_dem_var.py
#
# usage: getUncertaintyDEM.py PointFile DEMfile outputcsv
#                                          ^ Single GTiff file
#        getUncertaintyDEM.py PointFile -b DEMfiles outputcsv
#                                             ^ a text file with path to a GTiff file at each row
#
# DEMfile: GeoTiff format
# PointFile: GMT .xyz format

import sys
from UtilDEM import SingleDEM
from UtilXYZ import XYZFile
from UtilConfig import CsvTable

def getUncertaintyDEM(demfpath, pointfilepath):
	dem = SingleDEM(demfpath)
	xyzfile_output = dem.GetPointsFromXYZ(pointfilepath)
	xyz = XYZFile(xyzfile_output, pointfilepath, demfpath)
	xyz.Read()
	return xyz.StatisticOutput()

if len(sys.argv) < 4:
	print('Error: Usage: getUncertaintyDEM.py PointFile DEMfile outputcsv')
	sys.exit(1)
elif sys.argv[2] != '-b':
	csv = CsvTable(sys.argv[3])
	csv.SaveData(getUncertaintyDEM(sys.argv[2], sys.argv[1]))
elif len(sys.argv) >= 5:
	demlist = [line.rstrip('\n') for line in open(sys.argv[3])]
	csv = CsvTable(sys.argv[4])
	for demfpath in demlist:
		csv.SaveData(getUncertaintyDEM(demfpath, sys.argv[1]))
else:
	print('Error: Usage: getUncertaintyDEM.py PointFile -b DEMfiles outputcsv')
	sys.exit(1)

csv.Write2File()