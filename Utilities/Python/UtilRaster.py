# Class: SingleRaster
# used for dhdt
# by Whyjay Zheng, Jul 20 2016 (was UtilDEM.py)
# last edit: Aug 26 2016
# last edit: Dec 7 2016 (fixed a bug of SingleRaster.Array2Raster -> nodatavalue)
# last edit: Doc 12 2016 (Change the self.uncertainty in __init__ and add ReadGeolocPoint method) 
# last edit: Sep 11 2018 (added a new class: RasterVelos)

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

def timeit(func):
    def time_wrapper(*args, **kwargs):
        time_a = datetime.now()
        print('Program Start: {}'.format(time_a.strftime('%Y-%m-%d %H:%M:%S')))
        dec_func = func(*args, **kwargs)
        time_b = datetime.now()
        print('Program End: {}'.format(time_b.strftime('%Y-%m-%d %H:%M:%S')))
        print('Time taken: ' + str(time_b - time_a))
        return dec_func
    return time_wrapper

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

	def SetPath(self, fpath):
		self.fpath = fpath

	def GetProjection(self):
		ds = gdal.Open(self.fpath)
		return ds.GetProjection()

	def GetGeoTransform(self):
		""" returns [ulx, xres, xskew, uly, yskew, yres] """
		ds = gdal.Open(self.fpath)
		return ds.GetGeoTransform()

	def GetXRes(self):
		ds = gdal.Open(self.fpath)
		geot = ds.GetGeoTransform()
		return geot[1]

	def GetYRes(self):
		ds = gdal.Open(self.fpath)
		geot = ds.GetGeoTransform()
		return geot[-1]

	def GetNoDataValue(self, band=1):
		ds = gdal.Open(self.fpath)
		dsband = ds.GetRasterBand(band)
		return dsband.GetNoDataValue()

	def SetNoDataValue(self, nodata_val, band=1):
		ds = gdal.Open(self.fpath, gdal.GA_Update)
		dsband = ds.GetRasterBand(band)
		dsband.SetNoDataValue(nodata_val)
		dsband.FlushCache()
		ds = dsband = None

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
		This is to write an xyzfile-like array to raster. Be cautious overwritting the old one! 
		projection is in wkt string. it can be given by the GetProjection() from a SingleRaster or a gdal.Dataset object.
		This method will use the geotransform values from the xyzfile-like array itself; i.e. 
		ul coordinate is (min(x), max(y)) and the spacing is unique(diff(unique(x))) and unique(diff(unique(y))).
		The nodata value is not set.
		"""

		driver = gdal.GetDriverByName('GTiff')
		# Saved in gdal 32-bit float geotiff format
		xaxis = np.unique(array[:,0])
		yaxis = np.unique(array[:,1])
		out_raster = driver.Create(self.fpath, len(xaxis),  len(yaxis), 1, gdal.GDT_Float32)
		# here I rounded the number to the 6th decimal to get the spacing, since a small error (around 1e-10)
		# would generate when reading the ampcor-off file.
		xspacing = np.unique(np.diff(xaxis).round(decimals=7))
		yspacing = np.unique(np.diff(yaxis).round(decimals=7))
		# print(xspacing)
		# print(yspacing)
		if len(xspacing) == 1 and len(yspacing) == 1:
			# assuming no rotation in the Affine transform
			new_geotransform = (min(xaxis), xspacing[0], 0, max(yaxis), 0, -yspacing[0])
		else:
			raise TypeError('There is someting wrong in XYZ array format. Check the consistency of the x- or y-spacing.')
		out_raster.SetGeoTransform( new_geotransform )
		out_raster.SetProjection(projection)
		# out_raster.GetRasterBand(1).SetNoDataValue(nodatavalue)
		out_raster.GetRasterBand(1).WriteArray(np.reshape(array[:, 2], (len(yaxis), len(xaxis))))
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

		# ==== need a vrt file
		# >= Python 3.4 
		from pathlib import Path
		vrtpath = Path(self.fpath + '.vrt')
		if not vrtpath.is_file():
			print('Calling gdalbuildvrt...')
			gdalbuildvrt_cmd = 'gdalbuildvrt ' + self.fpath + '.vrt ' + self.fpath
			print(gdalbuildvrt_cmd)
			retcode = subprocess.call(gdalbuildvrt_cmd, shell=True)
			if retcode != 0:
				print('gdalbuildvrt failed. Please check if all the input parameters are properly set.')
				sys.exit(retcode)
		# ====================

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
		# geometry = geoms[0] # shapely geometry
		# geoms = [mapping(geoms[0])] # transform to GeJSON format
		geoms = [mapping(geoms[i]) for i in range(len(geoms))]
		with rasterio.open(self.fpath) as src:
			out_image, out_transform = mask(src, geoms, crop=True, nodata=-9999.0)
			# The out_image result is a Numpy masked array
			# no_data = src.nodata
			# if no_data is None:
			# 	no_data = 0.0
			nodata = -9999.0
		# print(out_image)
		# print(out_image.data.shape)
		# print(out_image.data)
		try:
			clipped_data = out_image.data[0]
		except NotImplementedError:
			clipped_data = out_image[0]
		# PROBABLY HAVE TO CHANGE TO out_image[0] HERE
		# extract the valid values
		# and return them as a numpy 1-D array
		return np.extract(clipped_data != nodata, clipped_data)

	def GaussianHighPass(self, sigma=3, truncate=1.0):

		"""
		Gaussian High Pass filter. Default sigma = 3.
		"""

		from scipy.ndimage import gaussian_filter
		data = self.ReadAsArray()
		data = data.astype(float)
		if self.GetNoDataValue() is not None:
			data[data == self.GetNoDataValue()] = np.nan
		else:
			data[data == 0] = np.nan    # LS-8 case
		lowpass = gaussian_filter(data, sigma, truncate=truncate)
		highpass = data - lowpass
		hp_raster_path = self.fpath.rsplit('.', 1)[0] + '_GHP-' + str(sigma) + 'sig.tif'
		hp_raster = SingleRaster(hp_raster_path)
		hp_raster.Array2Raster(highpass, self)
		self.SetPath(hp_raster_path)

	def GaussianLowPass(self, sigma=1):

		"""
		Gaussian Low Pass filter. Default sigma = 1.
		deal with nodata values.
		https://stackoverflow.com/questions/18697532/gaussian-filtering-a-image-with-nan-in-python
		"""

		from scipy.ndimage import gaussian_filter
		data = self.ReadAsArray()
		# data[data == self.GetNoDataValue()] = np.nan
		# lowpass = gaussian_filter(data.astype(float), sigma, truncate=truncate)
		nodata_pos = data == self.GetNoDataValue()
		data[nodata_pos] = 0
		w = np.ones_like(data)
		w[nodata_pos] = 0
		vv = gaussian_filter(data.astype(float), sigma)
		ww = gaussian_filter(w.astype(float), sigma)
		ww[ww == 0] = np.finfo(float).eps
		lowpass = vv / ww
		lowpass[nodata_pos] = self.GetNoDataValue()
		lp_raster_path = self.fpath.rsplit('.', 1)[0] + '_GLP-' + str(sigma) + 'sig.tif'
		lp_raster = SingleRaster(lp_raster_path)
		lp_raster.Array2Raster(lowpass, self)
		self.SetPath(lp_raster_path)


class RasterVelos():

	def __init__(self, vx=None, vy=None, mag=None, snr=None, errx=None, erry=None, errmag=None):

		'''
		All 6 attributes are supposed to be a SingleRaster object.
		'''

		self.vx = None
		# self.vx_val = None
		self.vy = None
		# self.vy_val = None
		self.mag = None
		self.mag_val = None
		self.snr = None
		self.errx = None
		self.erry = None
		self.errmag = None
		if type(vx) is SingleRaster:
			self.vx = vx
		if type(vy) is SingleRaster:
			self.vy = vy
		if type(mag) is SingleRaster:
			self.mag = mag
		if type(snr) is SingleRaster:
			self.snr = snr
		if type(errx) is SingleRaster:
			self.errx = errx
		if type(erry) is SingleRaster:
			self.erry = erry
		if type(errmag) is SingleRaster:
			self.errmag = errmag

	def SetVx(self, vx):
		self.vx = vx

	def SetVy(self, vy):
		self.vy = vy

	def SetMag(self, mag):
		self.mag = mag

	def SetSnr(self, snr):
		self.snr = snr

	def SetErrx(self, errx):
		self.errx = errx

	def SetErry(self, erry):
		self.erry = erry

	def SetErrmag(self, errmag):
		self.errmag = errmag

	def CalMag(self):
		if self.vx is None or self.vy is None:
			raise TypeError("You Need BOTH Vx and Vy to calculate the magnitude of velocity.")
		else:
			self.mag_val = np.sqrt(self.vx.ReadAsArray() ** 2 + self.vy.ReadAsArray() ** 2)

	def VeloCorrectionInfo(self, vx_zarray, vy_zarray, ini, pngname=None):

		a = SingleRaster(ini.imagepair['image1'], date=ini.imagepair['image1_date'])
		b = SingleRaster(ini.imagepair['image2'], date=ini.imagepair['image2_date'])
		datedelta = b.date - a.date
		geot = a.GetGeoTransform()
		xres = geot[1]
		yres = geot[5]

		vx_zarray_velo = vx_zarray[:]
		vx_zarray_velo            = vx_zarray_velo            * abs(xres) / datedelta.days
		vx_zarray_velo.MAD_median = vx_zarray_velo.MAD_median * abs(xres) / datedelta.days
		vx_zarray_velo.MAD_std    = vx_zarray_velo.MAD_std    * abs(xres) / datedelta.days
		vx_zarray_velo.MAD_mean   = vx_zarray_velo.MAD_mean   * abs(xres) / datedelta.days
		vy_zarray_velo = vy_zarray[:]
		vy_zarray_velo            = vy_zarray_velo            * abs(yres) / datedelta.days
		vy_zarray_velo.MAD_median = vy_zarray_velo.MAD_median * abs(yres) / datedelta.days
		vy_zarray_velo.MAD_std    = vy_zarray_velo.MAD_std    * abs(yres) / datedelta.days
		vy_zarray_velo.MAD_mean   = vy_zarray_velo.MAD_mean   * abs(yres) / datedelta.days

		with open(ini.velocorrection['label_logfile'], 'w') as f:
			f.write( 'Total points over bedrock =   {:6n}\n'.format(len(vx_zarray)) )
			f.write( '-------- Unit: Pixels --------\n')
			f.write( 'MAD_median_x_px    = {:6.3f}\n'.format(float(vx_zarray.MAD_median)) )
			f.write( 'MAD_median_y_px    = {:6.3f}\n'.format(float(vy_zarray.MAD_median)) )
			f.write( 'MAD_std_x_px       = {:6.3f}\n'.format(float(vx_zarray.MAD_std)) )
			f.write( 'MAD_std_y_px       = {:6.3f}\n'.format(float(vy_zarray.MAD_std)) )
			f.write( 'MAD_mean_x_px      = {:6.3f}\n'.format(float(vx_zarray.MAD_mean)) )
			f.write( 'MAD_mean_y_px      = {:6.3f}\n'.format(float(vy_zarray.MAD_mean)) )
			f.write( '-------- Unit: Velocity (L/T; most likely m/day) --------\n')
			f.write( 'MAD_median_x       = {:6.3f}\n'.format(float(vx_zarray_velo.MAD_median)) )
			f.write( 'MAD_median_y       = {:6.3f}\n'.format(float(vy_zarray_velo.MAD_median)) )
			f.write( 'MAD_std_x          = {:6.3f}\n'.format(float(vx_zarray_velo.MAD_std)) )
			f.write( 'MAD_std_y          = {:6.3f}\n'.format(float(vy_zarray_velo.MAD_std)) )
			f.write( 'MAD_mean_x         = {:6.3f}\n'.format(float(vx_zarray_velo.MAD_mean)) )
			f.write( 'MAD_mean_y         = {:6.3f}\n'.format(float(vy_zarray_velo.MAD_mean)) )

		if pngname is not None:
			import matplotlib.pyplot as plt
			# import matplotlib
			from scipy.stats import gaussian_kde
			# font = {'family' : 'sans-serif',
			#         'weight' : 'normal',
			#         'size'   : 26}
			# matplotlib.rc('font', **font)

			xy = np.vstack([vx_zarray, vy_zarray])
			z = gaussian_kde(xy)(xy)
			plt.scatter(vx_zarray, vy_zarray, c=z, s=8, edgecolor='')
			# cbar = plt.colorbar()
			# cbar.set_label('Kernel density estimation')
			# plt.scatter(np.reshape(c_data, -1), np.reshape(w_data, -1), c=cc)
			# plt.plot(np.reshape(c_data, -1), np.reshape(w_data, -1), '.')
			# plt.plot(np.arange(-25, 26), np.arange(-25, 26), 'k--', linewidth=2)

			plt.axis('scaled')
			lim = max([max(abs(vx_zarray)), max(abs(vx_zarray))])
			plt.xlim([-lim, lim])
			plt.ylim([-lim, lim])
			# plt.tight_layout()
			# plt.gca().set_aspect('equal')

			# plt.xlabel('CryoSat dH/dt (m/yr)')
			# plt.ylabel('WorldView dH/dt (m/yr)')
			plt.ylabel('Offset-X (pixels)')
			plt.xlabel('Offset-Y (pixels)')
			plt.savefig(pngname, format='png', dpi=200)
			plt.cla()

		return vx_zarray_velo, vy_zarray_velo

	def VeloCorrection(self, vx_zarray, vy_zarray, output_raster_prefix):

		'''
		vx_zarray and vy_zarray are ZArray objects.
		'''

		nodata_val = self.mag.GetNoDataValue()
		nodata_pos = self.mag.ReadAsArray() == nodata_val

		vx_val_corrected = self.vx.ReadAsArray() - vx_zarray.MAD_median
		vy_val_corrected = self.vy.ReadAsArray() - vy_zarray.MAD_median
		mag_val_corrected = np.sqrt(vx_val_corrected ** 2 + vy_val_corrected ** 2)

		vx_val_corrected[nodata_pos] = nodata_val
		vy_val_corrected[nodata_pos] = nodata_val
		mag_val_corrected[nodata_pos] = nodata_val

		raster_vx_corrected = SingleRaster(output_raster_prefix + '_vx.tif')
		raster_vx_corrected.Array2Raster(vx_val_corrected, self.vx)
		raster_vy_corrected = SingleRaster(output_raster_prefix + '_vy.tif')
		raster_vy_corrected.Array2Raster(vy_val_corrected, self.vy)
		raster_mag_corrected = SingleRaster(output_raster_prefix + '_mag.tif')
		raster_mag_corrected.Array2Raster(mag_val_corrected, self.vx)

		self.SetVx(raster_vx_corrected)
		self.SetVy(raster_vy_corrected)
		self.SetMag(raster_mag_corrected)

		# ==== Calculate the corrected error ====
		# Note that we changed the way to calculate it from the previous version; Now the
		# offset is not considered as an independent variable.
		# Therefore, instead of using 
		#
		# sigma_vx' = sqrt(sigma_vx ^ 2 + corrected_std ^ 2)     (ref. realistic_speed_error.bash)
		#
		# we use
		#
		# sigma_vx' = sigma_vx + corrected_std 
		#
		# for a more realistic and conserved error estimate.

		if self.errx is not None:
			errx_val_corrected = self.errx.ReadAsArray() + vx_zarray.MAD_std
			errx_val_corrected[nodata_pos] = nodata_val
			raster_errx_corrected = SingleRaster(output_raster_prefix + '_errx.tif')
			raster_errx_corrected.Array2Raster(errx_val_corrected, self.errx)
			self.SetErrx(raster_errx_corrected)


		if self.erry is not None:
			erry_val_corrected = self.erry.ReadAsArray() + vy_zarray.MAD_std
			erry_val_corrected[nodata_pos] = nodata_val
			raster_erry_corrected = SingleRaster(output_raster_prefix + '_erry.tif')
			raster_erry_corrected.Array2Raster(erry_val_corrected, self.erry)
			self.SetErry(raster_erry_corrected)

		if self.errx is not None and self.erry is not None:
			errmag_val_corrected = np.sqrt(
				                   (vx_val_corrected ** 2 * errx_val_corrected ** 2 + vy_val_corrected ** 2 * erry_val_corrected ** 2)
				                   / (vx_val_corrected ** 2 + vy_val_corrected ** 2)
				                   )
			errmag_val_corrected[nodata_pos] = nodata_val
			raster_errmag_corrected = SingleRaster(output_raster_prefix + '_errmag.tif')
			raster_errmag_corrected.Array2Raster(errmag_val_corrected, self.errx)
			self.SetErrmag(raster_errmag_corrected)

	def SNR_CutNoise(self, snr_threshold=5):
		bad_pts = self.snr.ReadAsArray() <= snr_threshold
		mag_val = self.mag.ReadAsArray()
		mag_val[bad_pts] = self.mag.GetNoDataValue()
		raster_mag_cutnoise = SingleRaster(self.mag.fpath.rsplit('.', 1)[0]  + '_SNT.tif')
		raster_mag_cutnoise.Array2Raster(mag_val, self.mag)
		self.SetMag(raster_mag_cutnoise)

	def Gaussian_CutNoise(self, sigma=1):
		mag_val = self.mag.ReadAsArray()
		mag_val_ok = Gussian_noise_remover(mag_val, sigma=sigma, nodata_val=self.mag.GetNoDataValue())
		raster_mag_cutnoise = SingleRaster(self.mag.fpath.rsplit('.', 1)[0]  + '-GAU.tif')
		raster_mag_cutnoise.Array2Raster(mag_val_ok, self.mag)
		self.SetMag(raster_mag_cutnoise)

	def MorphoOpen_CutNoise(self, iterations=1):
		mag_val = self.mag.ReadAsArray()
		mag_val_ok = MorphoOpen_noise_remover(mag_val, nodata_val=self.mag.GetNoDataValue(), iterations=1)
		raster_mag_cutnoise = SingleRaster(self.mag.fpath.rsplit('.', 1)[0]  + '-MOR.tif')
		raster_mag_cutnoise.Array2Raster(mag_val_ok, self.mag)
		self.SetMag(raster_mag_cutnoise)

	def SmallObjects_CutNoise(self, min_size=17):
		from skimage.morphology import remove_small_objects
		mag_val = self.mag.ReadAsArray()
		mag_val_ok = SmallObjects_noise_remover(mag_val, nodata_val=self.mag.GetNoDataValue(), min_size=min_size)
		raster_mag_cutnoise = SingleRaster(self.mag.fpath.rsplit('.', 1)[0]  + '-RSO.tif')
		raster_mag_cutnoise.Array2Raster(mag_val_ok, self.mag)
		self.SetMag(raster_mag_cutnoise)

	def Fahnestock_CutNoise(self):
		mag_val = self.mag.ReadAsArray()
		magerr_val = self.errmag.ReadAsArray()
		mag_val_ok = Fahnestock_noise_remover(mag_val, magerr_val, nodata_val=-9999.0)
		raster_mag_cutnoise = SingleRaster(self.mag.fpath.rsplit('.', 1)[0]  + '-FAH.tif')
		raster_mag_cutnoise.Array2Raster(mag_val_ok, self.mag)
		self.SetMag(raster_mag_cutnoise)

	def MaskAllRasters(self):
		mag_val = self.mag.ReadAsArray()
		nodata = mag_val == self.mag.GetNoDataValue()
		vx_val = self.vx.ReadAsArray()
		vx_val[nodata] = self.vx.GetNoDataValue()
		raster_vx_cutnoise = SingleRaster(self.mag.fpath.replace('mag', 'vx'))
		raster_vx_cutnoise.Array2Raster(vx_val, self.vx)
		self.SetVx(raster_vx_cutnoise)
		vy_val = self.vy.ReadAsArray()
		vy_val[nodata] = self.vy.GetNoDataValue()
		raster_vy_cutnoise = SingleRaster(self.mag.fpath.replace('mag', 'vy'))
		raster_vy_cutnoise.Array2Raster(vy_val, self.vy)
		self.SetVy(raster_vy_cutnoise)
		errx_val = self.errx.ReadAsArray()
		errx_val[nodata] = self.errx.GetNoDataValue()
		raster_errx_cutnoise = SingleRaster(self.mag.fpath.replace('mag', 'errx'))
		raster_errx_cutnoise.Array2Raster(errx_val, self.errx)
		self.SetErrx(raster_errx_cutnoise)
		erry_val = self.erry.ReadAsArray()
		erry_val[nodata] = self.erry.GetNoDataValue()
		raster_erry_cutnoise = SingleRaster(self.mag.fpath.replace('mag', 'erry'))
		raster_erry_cutnoise.Array2Raster(erry_val, self.erry)
		self.SetErry(raster_erry_cutnoise)
		errmag_val = self.errmag.ReadAsArray()
		errmag_val[nodata] = self.errmag.GetNoDataValue()
		raster_errmag_cutnoise = SingleRaster(self.mag.fpath.replace('mag', 'errmag'))
		raster_errmag_cutnoise.Array2Raster(errmag_val, self.errmag)
		self.SetErrmag(raster_errmag_cutnoise)


@timeit
def Gussian_noise_remover(array, sigma=1, nodata_val=-9999.0):

	"""
	Gaussian Low Pass filter. Default sigma = 1.
	deal with nodata values.
	https://stackoverflow.com/questions/18697532/gaussian-filtering-a-image-with-nan-in-python
	"""

	from scipy.ndimage import gaussian_filter
	nodata_pos = array == nodata_val
	array[nodata_pos] = 0
	w = np.ones_like(array)
	w[nodata_pos] = 0
	vv = gaussian_filter(array.astype(float), sigma)
	ww = gaussian_filter(w.astype(float), sigma)
	ww[ww == 0] = np.finfo(float).eps
	lowpass = vv / ww
	lowpass[nodata_pos] = nodata_val
	diff = np.abs(array - lowpass)
	mask = diff >= 1
	array[mask] = nodata_val
	return array

@timeit
def SmallObjects_noise_remover(array, nodata_val=-9999.0, min_size=17):

	from skimage.morphology import remove_small_objects
	nodata_pos = array == nodata_val
	bin_array = np.ones_like(array)
	bin_array[nodata_pos] = 0
	new_bin_array = remove_small_objects(bin_array.astype(bool), min_size=min_size)
	array[~new_bin_array] = nodata_val
	return array

@timeit
def MorphoOpen_noise_remover(array, nodata_val=-9999.0, iterations=1):

	from scipy.ndimage import binary_opening
	nodata_pos = array == nodata_val
	bin_array = np.ones_like(array)
	bin_array[nodata_pos] = 0
	new_bin_array = binary_opening(bin_array, iterations=iterations, structure=np.ones((3,3)))
	array[~new_bin_array] = nodata_val
	return array

from skimage.morphology import remove_small_objects

@timeit
def Fahnestock_noise_remover(array, error_array, nodata_val=-9999.0):

	# based on the algorithm of Fahnestock et al. (2015): Landsat 8 image processing
	# from the matlab file: smooth_step2.m
	# that one was lastly modified by Whyjay Zheng, 2016 Mar 31
	# we simplified the processes a little bit!

	idxm = []
	idxn = []

	for m in range(1, array.shape[0] - 1):
		for n in range(1, array.shape[1] - 1):
			if m % 10 == 0 and n == 2:
				print(m)
			masked = False
			data_point = array[m, n]
			if data_point != nodata_val:
				# masked = True
				# else:
				judge_array = array[m-1:m+2, n-1:n+2]
				judge_array = judge_array.flatten()
				# neighbors = np.delete(judge_array, 4)
				judge_array = judge_array[judge_array != nodata_val]
				# judge_array = np.delete(judge_array.flatten(), 4)
				# judge_array = judge_array[judge_array != nodata_val]
				if judge_array.size <= 2:
					masked = True
				# elif judge_array.size == 1:
				# 	if abs(data_point - judge_array[0]) >= 1:
				# 		masked = True
				else:
					if abs(data_point - judge_array.mean()) > 3 * judge_array.std():
						masked = True
					# elif np.std(judge_array) >= 1:
					# 	masked = True
					# elif np.std(judge_array) >= 3 * error_array[m, n]:
					# 	masked = True
					elif max(judge_array) - min(judge_array) > 3 * error_array[m, n]:
						masked = True
					# elif max(judge_array) - min(judge_array) >= 1:
					# 	masked = True
					# we cancelled this criterion
					# elif judge_array.std() <= 0.001:
					# 	masked = True
			if masked:
				idxm.append(m)
				idxn.append(n)

	for k in range(len(idxm)):
		array[idxm[k], idxn[k]] = nodata_val

	idxm2 = []
	idxn2 = []

	for m in range(1, array.shape[0] - 1):
		for n in range(1, array.shape[1] - 1):
			if m % 10 == 0 and n == 2:
				print(m)
			if array[m, n] != nodata_val:
				judge_array = array[m-1:m+2, n-1:n+2]
				# judge_array = np.delete(judge_array.flatten(), 4)
				judge_array = judge_array.flatten()
				judge_array = judge_array[judge_array != nodata_val]
				if judge_array.size <= 3:
					idxm2.append(m)
					idxn2.append(n)

	for k in range(len(idxm2)):
		array[idxm2[k], idxn2[k]] = nodata_val

	return array

