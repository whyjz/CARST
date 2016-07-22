# Class: singleDEM
# used for dhdt
# by Whyjay Zheng, Jul 20 2016

import sys
import subprocess
import gdal
from datetime import datetime
# or: from osgeo import gdal

# we assume the fpath is the file with .tif or .TIF suffix.

class SingleDEM:

	def __init__(self, fpath, date=None, uncertainty=None):
		self.fpath = fpath
		self.date = datetime.strptime(date, '%Y-%m-%d') if date is not None   else None
		self.uncertainty = float(uncertainty) if uncertainty is not None      else None

	def GetProjection(self):
		ds = gdal.Open(self.fpath)
		return ds.GetProjection()

	def GetGeoTransform(self):
		ds = gdal.Open(self.fpath)
		return ds.GetGeoTransform()

	def Unify(self, params):
		print('Calling Gdalwarp...')
		newpath = self.fpath[:-4] + '_warped' + self.fpath[-4:]
		gdalwarp_cmd = 'gdalwarp' +\
		               ' -t_srs ' + params['t_srs'] +\
		               ' -tr ' + params['tr'] +\
		               ' -te ' + params['te'] +\
		               ' -overwrite ' +\
		               self.fpath + ' ' + newpath
		print(gdalwarp_cmd)
		retcode = subprocess.call(gdalwarp_cmd, shell=True)
		if retcode != 0:
			print('Gdalwarp failed. Please check if all the input parameters are properly set.')
			sys.exit(retcode)
		self.fpath = newpath

	def ReadAsArray(self, band=1):

		""" The default will return the first band. """

		ds = gdal.Open(self.fpath)
		dsband = ds.GetRasterBand(band)
		return dsband.ReadAsArray()

	def Array2Raster(self, array, refdem):

		""" 
		This is to write array to raster. Be cautious overwritting the old one! 
		refdem (reference DEM) can be either a SingleDEM object or a gdal.Dataset object.
		This method will use the projection and the geotransform values from the refdem for the new geotiff file.
		"""

		driver = gdal.GetDriverByName('GTiff')
		# Saved in gdal 32-bit float geotiff format
		out_raster = driver.Create(self.fpath, array.shape[1], array.shape[0], 1, gdal.GDT_Float32)
		out_raster.SetGeoTransform( refdem.GetGeoTransform() )
		out_raster.SetProjection(   refdem.GetProjection()   )
		# Write data to band 1 (becuase this is a brand new file)
		out_raster.GetRasterBand(1).WriteArray(array)
		# Save to file
		out_raster.FlushCache()