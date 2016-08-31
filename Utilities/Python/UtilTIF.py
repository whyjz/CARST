# Class: singleTIF
# used for dhdt
# by Whyjay Zheng, Jul 20 2016 (was UtilDEM.py)
# last edit: Aug 26 2016

import sys
import os
import subprocess
from subprocess import PIPE
import numpy as np
from datetime import datetime
try:
	import gdal
except:
	from osgeo import gdal        # sometimes gdal is part of osgeo modules
from osgeo import osr
# we assume the fpath is the file with .tif or .TIF suffix.

class SingleTIF:

	"""
	DEM object. Provide operations like "Unify" (gdalwarp) and "GetPointsFromXYZ" (grdtrack).
	Future improvement: detect I/O error, like this:

	if not os.path.exists(image1_path):
	print("\n***** WARNING: \"" + image1_path + "\" not found, make sure full path is provided, skipping corresponding pair...\n");
	continue;
	"""

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

	def GetNoDataValue(self, band=1):
		ds = gdal.Open(self.fpath)
		dsband = ds.GetRasterBand(band)
		return dsband.GetNoDataValue()

	def GetProj4(self):

		"""
		return Proj.4 string.
		"""

		ds = gdal.Open(self.fpath)
		wkt_text = ds.GetProjection()
		srs = osr.SpatialReference()
		srs.ImportFromWkt(wkt_text)
		return srs.ExportToProj4()

	def GetRasterXSize(self):
		""" This is 'samples' of a image """
		ds = gdal.Open(self.fpath)
		return ds.RasterXSize

	def GetRasterYSize(self):
		""" This is 'lines' of a image """
		ds = gdal.Open(self.fpath)
		return ds.RasterYSize

	def GetExtent(self):

		"""
		return extent: ul_x, ul_y, lr_x, lr_y. ul = upper left; lr = lower right.
		"""

		ds = gdal.Open(self.fpath)
		ulx, xres, xskew, uly, yskew, yres  = ds.GetGeoTransform()
		lrx = ulx + (ds.RasterXSize * xres)
		lry = uly + (ds.RasterYSize * yres)
		return ulx, uly, lrx, lry

	def Unify(self, params):

		""" Use gdalwarp to clip, reproject, and resample a DEM using a given set of params (which can 'unify' all DEMs). """

		print('Calling Gdalwarp...')
		fpath_warped = self.fpath[:-4] + '_warped' + self.fpath[-4:]
		if 'output_dir' in params:
			newpath = '/'.join([params['output_dir'], fpath_warped.split('/')[-1]])
		else:
			# for pixel tracking (temporarily)
			newfolder = 'test_folder'
			if not os.path.exists(newfolder):
				os.makedirs(newfolder)
			newpath = '/'.join([newfolder, fpath_warped.split('/')[-1]])
			newpath = newpath.replace(newpath.split('.')[-1], 'img')
		gdalwarp_cmd = 'gdalwarp -t_srs ' + params['t_srs'] + ' -tr ' + params['tr'] + ' -te ' + params['te']
		if 'of' in params:
			gdalwarp_cmd += ' -of ' + params['of']
		if 'ot' in params:
			gdalwarp_cmd += ' -ot ' + params['ot']
		gdalwarp_cmd += ' -overwrite ' + self.fpath + ' ' + newpath
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
		# Of course, set nan to NoDataValue
		array[np.isnan(array)] = refdem.GetNoDataValue()
		out_raster.GetRasterBand(1).SetNoDataValue( refdem.GetNoDataValue() )
		out_raster.GetRasterBand(1).WriteArray(array)
		# Save to file
		out_raster.FlushCache()

	def GetPointsFromXYZ(self, xyzfilename):

		"""
		Get points from a xyzfile, using grdtrack. Return the output .xyz file. 
		Currently the output .xyz file is fixed as 'log_getUncertaintyDEM_grdtrack_output.xyz'
		and will be overwritten by later commands.
		"""

		print('Calling Grdtrack...')
		newpath = 'log_getUncertaintyDEM_grdtrack_output.xyz'
		grdtrack_cmd = 'grdtrack ' + xyzfilename +\
					   ' -G' + self.fpath +\
					   ' > ' + newpath
		print(grdtrack_cmd)
		retcode = subprocess.call(grdtrack_cmd, shell=True)
		if retcode != 0:
			print('Grdtrack failed. Please check if all the input parameters are properly set.')
			sys.exit(retcode)
		return newpath
		


