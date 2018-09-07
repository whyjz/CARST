# Class: SingleRaster
# used for dhdt
# by Whyjay Zheng, Jul 20 2016 (was UtilDEM.py)
# last edit: Aug 26 2016
# last edit: Dec 7 2016 (fixed a bug of SingleRaster.Array2Raster -> nodatavalue)
# last edit: Doc 12 2016 (Change the self.uncertainty in __init__ and add ReadGeolocPoint method) 

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

class SingleRaster:

	"""
	DEM object. Provide operations like "Unify" (gdalwarp) and "GetPointsFromXYZ" (grdtrack).
	Future improvement: detect I/O error, like this:

	if not os.path.exists(image1_path):
	print("\n***** WARNING: \"" + image1_path + "\" not found, make sure full path is provided, skipping corresponding pair...\n");
	continue;
	"""

	def __init__(self, fpath, date=None, uncertainty=None):
		self.fpath = fpath
		self.uncertainty = float(uncertainty) if uncertainty is not None      else None
		if type(date) is str:
			if len(date) == 10:
				self.date = datetime.strptime(date, '%Y-%m-%d')
			elif len(date) == 8:
				self.date = datetime.strptime(date, '%Y%m%d')
			elif len(date) == 7:
				self.date = datetime.strptime(date, '%y%b%d')  # YYMMMDD
			else:
				raise ValueError("This format of date string is not currently supported." +\
				                 "Please use YYYY-MM-DD, YYYYMMDD, or YYMMMDD.")
		elif type(date) is datetime:
			self.date = date
		elif date is None:
			self.date = None
		else:
			raise TypeError('The date format is not currently supported.')
		self.iscepointer = None

	def GetProjection(self):
		ds = gdal.Open(self.fpath)
		return ds.GetProjection()

	def GetGeoTransform(self):
		""" returns [ulx, xres, xskew, uly, yskew, yres] """
		ds = gdal.Open(self.fpath)
		return ds.GetGeoTransform()

	def GetNoDataValue(self, band=1):
		ds = gdal.Open(self.fpath)
		dsband = ds.GetRasterBand(band)
		return dsband.GetNoDataValue()

	def GetProj4(self):

		"""
		return projection as Proj.4 string.
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

	def GetDataType(self, band=1):

		"""
		return DataType: http://www.gdal.org/gdal_8h.html#a22e22ce0a55036a96f652765793fb7a4
		"""

		ds = gdal.Open(self.fpath)
		dsband = ds.GetRasterBand(band)
		return dsband.DataType


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

	def ReadGeolocPoint(self, x, y, band=1):

		"""
		It's almost the same as gdallocationinfo -geoloc srcfile x y
		Read a point in the georeferencing system of the raster, and then return the pixel value at that point.
		Returns NaN if (x, y) is not within the extent of the raster.
		"""

		ulx, uly, lrx, lry = self.GetExtent()
		ulx, xres, xskew, uly, yskew, yres  = self.GetGeoTransform()
		# print('xbound:', ulx, lrx, 'ybound:', uly, lry)
		# if y > 220000:
		# 	print(x, y, 'xbound:', ulx, lrx, 'ybound:', uly, lry)
		if (ulx <= x < lrx) & (uly >= y > lry):
			ds = gdal.Open(self.fpath)
			px = int((x - ulx) / xres) # x pixel coor
			py = int((y - uly) / yres) # y pixel coor
			dsband = ds.GetRasterBand(band)
			pixel_val = dsband.ReadAsArray(px, py, 1, 1)   # it numpy.array with shape of (1, 1)
			return float(pixel_val[0])
		else:
			return np.nan

	def ReadAsArray(self, band=1):

		""" The default will return the first band. """

		ds = gdal.Open(self.fpath)
		dsband = ds.GetRasterBand(band)
		return dsband.ReadAsArray()

	def Array2Raster(self, array, refdem):

		""" 
		This is to write array to raster. Be cautious overwritting the old one! 
		refdem (reference DEM) can be either a SingleRaster object or a gdal.Dataset object.
		This method will use the projection and the geotransform values from the refdem for the new geotiff file.
		"""

		driver = gdal.GetDriverByName('GTiff')
		# Saved in gdal 32-bit float geotiff format
		out_raster = driver.Create(self.fpath, array.shape[1], array.shape[0], 1, gdal.GDT_Float32)
		out_raster.SetGeoTransform( refdem.GetGeoTransform() )
		out_raster.SetProjection(   refdem.GetProjection()   )
		# Write data to band 1 (becuase this is a brand new file)
		# Of course, set nan to NoDataValue
		nodatavalue = refdem.GetNoDataValue() if refdem.GetNoDataValue() is not None else -9999.0
		array[np.isnan(array)] = nodatavalue
		out_raster.GetRasterBand(1).SetNoDataValue( nodatavalue )
		out_raster.GetRasterBand(1).WriteArray(array)
		# Save to file
		out_raster.FlushCache()

	def XYZArray2Raster(self, array, projection=''):

		""" 
		Starting from HERE!!!!!!!!!!!
		"""

		driver = gdal.GetDriverByName('GTiff')


		src_ds = gdal.Open(xyzfilename)
		out_raster = driver.CreateCopy(self.fpath, src_ds, 0 )
		out_raster.SetProjection(projection)
		out_raster.SetGeoTransform(   src_ds.GetGeoTransform()   )
		# out_raster.GetRasterBand(1).SetNoDataValue(nodatavalue)
		out_raster.FlushCache()

	def XYZ2Raster(self, xyzfilename, projection=''):

		""" 
		This is to write an xyzfile (ascii, sorted) to raster. Be cautious overwritting the old one! 
		projection is in wkt string. it can be given by the GetProjection() from a SingleRaster or a gdal.Dataset object.
		This method will use the geotransform values from the xyzfile itself. (that is, the first data is at "ul" position.)
		The nodata value is not set.
		"""

		driver = gdal.GetDriverByName('GTiff')
		src_ds = gdal.Open(xyzfilename)
		out_raster = driver.CreateCopy(self.fpath, src_ds, 0 )
		out_raster.SetProjection(projection)
		out_raster.SetGeoTransform(   src_ds.GetGeoTransform()   )
		# out_raster.GetRasterBand(1).SetNoDataValue(nodatavalue)
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

	def AmpcorPrep(self):

		"""
		Prepare to be used in ampcor.
		Ampcor package in ISCE uses a special file pointer for accessing geotiff data.
		Therefore, we need ISCE module "Image" for this purpose.
		"""

		import isce
		from isceobj.Image.Image import Image
		# need a vrt file

		obj = Image()
		obj.setFilename(self.fpath)
		obj.setWidth(self.GetRasterXSize())      # gdalinfo, first number
		if self.GetDataType() <= 3:
			obj.setDataType('SHORT')
		elif 4 <= self.GetDataType() <= 5:
			obj.setDataType('LONG')
		elif self.GetDataType() == 6:
			obj.setDataType('FLOAT')     
		elif self.GetDataType() == 7:
			obj.setDataType('DOUBLE') # SHORT, LONG, FLOAT, DOUBLE, etc
		else:
			obj.setDataType('CFLOAT') # not totally right, may be wrong
		# obj.setBands(1)   # "self" requires a single band 
		# obj.setAccessMode('read')
		obj.setCaster('read', 'FLOAT')    # fixed as float
		obj.createImage()
		self.iscepointer = obj

	def ClippedByPolygon(self, polygon_shapefile):

		"""
		return all pixel values within a given polygon shapefile.
		according to
		https://gis.stackexchange.com/questions/260304/extract-raster-values-within-shapefile-with-pygeoprocessing-or-gdal
		"""
		from rasterio import logging
		log = logging.getLogger()
		log.setLevel(logging.ERROR)

		import rasterio
		from rasterio.mask import mask
		import geopandas as gpd
		from shapely.geometry import mapping

		shapefile = gpd.read_file(polygon_shapefile)
		geoms = shapefile.geometry.values
		geometry = geoms[0] # shapely geometry
		geoms = [mapping(geoms[0])] # transform to GeJSON format
		with rasterio.open(self.fpath) as src:
			out_image, out_transform = mask(src, geoms, crop=True)
			# The out_image result is a Numpy masked array
			no_data = src.nodata
			if no_data is None:
				no_data = 0.0
		clipped_data = out_image.data[0]
		# extract the valid values
		# and return them as a numpy 1-D array
		return np.extract(clipped_data != no_data, clipped_data)
