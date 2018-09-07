# Class: XYZFile
# used for getUncertaintyDEM
# by Whyjay Zheng, Jul 28 2016
#
# Class: AmpcoroffFile
# manipulating the ampcor outpuf (and translating it into a geotiff)
# by Whyjay Zheng, Jul 10 2018

import numpy as np
from UtilRaster import SingleRaster
from scipy.interpolate import griddata

class ZArray(np.ndarray):

	def __new__(cls, input_array):
		# For now input_array should be a 1-d array
		# Input array is an already formed ndarray instance
		# We need first to cast to be our class type
		obj = np.asarray(input_array).view(cls)
		return obj

	def __array_finalize__(self, obj):
		if obj is None: return
		# self.info = getattr(obj, 'info', None)

	# =============================================================================================
	# ==== The following functions are designed firstly for the functions in the class XYZFile ====
	# ==== and later is has modified to a QGIS processing scripts called MAD_outlier_filter.py ====
	# ==== now we have copied them back. ==========================================================
	# =============================================================================================
	def StatisticOutput(self, plot=True, mad_multiplier=3.0, pngname=None):
		mad = lambda x : 1.482 * np.median(abs(x - np.median(x)))
		if self.size == 0:
			print('WARNING: there is no Z records.')
			return [], np.nan, np.nan, np.nan
		else:
			offset_median = np.median(self)
			offset_mad = mad(self)
			lbound = offset_median - mad_multiplier * offset_mad
			ubound = offset_median + mad_multiplier * offset_mad
			idx2 = np.logical_and(self > lbound, self < ubound)
			if plot == True and pngname is not None:
				self.HistWithOutliers(idx2, pngname)
			trimmed_numlist = self[idx2]
			return idx2, trimmed_numlist.mean(), np.median(trimmed_numlist), trimmed_numlist.std(ddof=1)

	def HistWithOutliers(self, idx2, pngname, histogram_bound=10):

		import matplotlib.pyplot as plt
		nbins = len(self) // 4 + 1
		nbins = 201 if nbins > 201 else nbins
		lbound = min(self) if min(self) >= -histogram_bound else -histogram_bound
		rbound = max(self) if max(self) <= histogram_bound else histogram_bound
		if lbound >= rbound:
			lbound = min(self)
			rbound = max(self)
		bins = np.linspace(lbound, rbound, nbins)
		trimmed_numlist = self[idx2]
		N_outside_lbound_red = int(sum(self < lbound))
		N_outside_rbound_red = int(sum(self > rbound))
		N_outside_lbound_blue = int(sum(trimmed_numlist < lbound))
		N_outside_rbound_blue = int(sum(trimmed_numlist > rbound))
		title_str = '[Red|Blue] L outside: [{}|{}] R outside: [{}|{}]'.format(N_outside_lbound_red, N_outside_lbound_blue, N_outside_rbound_red, N_outside_rbound_blue)
		# plot histograms
		plt.hist(self, bins=bins, color=[0.95, 0.25, 0.1])
		plt.hist(trimmed_numlist, bins=bins, color=[0.1, 0.25, 0.95])
		plt.ylabel('N')
		plt.xlabel('offset (pixel value unit)')
		plt.title(title_str)
		plt.savefig(pngname, format='png', dpi=200)
		plt.cla()
	# =============================================================================================
	# ==== The functions above are designed firstly for the functions in the class XYZFile ========
	# ==== and later is has modified to a QGIS processing scripts called MAD_outlier_filter.py ====
	# ==== now we have copied them back. ==========================================================
	# =============================================================================================



class XYZFile:

	def __init__(self, fpath=None, refpts_path=None, dem_path=None):
		self.fpath = fpath
		self.refpts_path = refpts_path
		self.dem_path = dem_path
		self.data = None
		self.diffval = None
		self.diffval_trimmed = None

	def Read(self):

		"""
		self.data will be usually a 3- or 4-column np.array
		column 1: easting
		column 2: northing
		column 3: height of the 1st group (usually reference points)
		column 4: height of the 2nd group (usually DEM points made from grdtrack)
		"""

		self.data = np.loadtxt(self.fpath)

	def StatisticOutput(self, pngname):

		# for getUncertaintyDEM

		mad = lambda x : 1.482 * np.median(abs(x - np.median(x)))
		if self.data.size == 0:
			print('NOTE: ' + self.dem_path + ' does not cover any ref points.')
			return [self.dem_path, '', '', '', '', '', '', self.refpts_path]
		elif self.data.shape[1] == 4:
			idx = ~np.isnan(self.data[:, 3])
			self.diffval = self.data[idx, 3] - self.data[idx, 2]
			offset_median = np.median(self.diffval)
			offset_mad = mad(self.diffval)
			lbound = offset_median - 3. * offset_mad
			ubound = offset_median + 3. * offset_mad
			idx2 = np.logical_and(self.diffval > lbound, self.diffval < ubound)
			self.diffval_trimmed = self.diffval[idx2]
			# The return value is ready for CsvTable.SaveData method.
			# ['filename', 'date', 'uncertainty', 'mean_offset_wrt_refpts', \
			#  'trimmed_N', 'trimming_lb', 'trimming_up', 'refpts_file']
			# 'date' is an empty string since we don't specify any date string in .xyz file.
			self.HistWithOutliers(pngname)
			return [self.dem_path, '', self.diffval_trimmed.std(ddof=1), self.diffval_trimmed.mean(), \
			          len(self.diffval_trimmed), lbound, ubound, self.refpts_path]
		elif self.data.shape[1] == 3:
			print("Not yet designed.")
			return []
		else:
			print("This program currently doesn't support the xyz file whose column number is not 3 or 4.")
			return []

	def HistWithOutliers(self, pngname):

		# for getUncertaintyDEM

		import matplotlib.pyplot as plt
		
		nbins = len(self.diffval) // 5
		nbins = 200 if nbins > 200 else nbins
		bins = np.linspace(min(self.diffval), max(self.diffval), nbins)
		plt.hist(self.diffval, bins=bins, color=[0.95, 0.25, 0.1])
		plt.hist(self.diffval_trimmed, bins=bins, color=[0.1, 0.25, 0.95])
		plt.ylabel('N')
		plt.xlabel('offset (pixel value unit)')
		plt.savefig(pngname, format='png')
		plt.cla()

class AmpcoroffFile:

	def __init__(self, fpath=None):
		self.fpath = fpath
		self.data = None
		self.velo_x  = None
		self.velo_y  = None
		self.snr     = None
		self.err_x   = None
		self.err_y   = None
		self.ini     = None
		self.xyv_velo_x   = None
		self.xyv_velo_y   = None
		self.xyv_mag      = None
		self.xyv_snr      = None
		self.xyv_err_x    = None
		self.xyv_err_y    = None


	def Load(self):

		"""
		self.data will be usually a 3- or 4-column np.array
		column 1: x cell # (from ul to the East)
		column 2: offset along across (x) direction, in pixels
		column 3: y cell # (from ul to the South) 
		column 4: offset along down (y) direction, in pixels
		column 5: SNR ratio
		column 6: Conv 1 (x)
		column 7: Conv 2 (y)
		column 8: Conv 3
		"""

		self.data = np.loadtxt(self.fpath)

	def SetIni(self, ini):

		self.ini = ini

	def Ampcoroff2Velo(self, ref_raster=None, datedelta=None):

		"""
		ref_raster: a SingleRaster object that is used for this pixel tracking
		datedelta: a timedelta object that is the time span between two input images
		these values will override the settings from self.ini, if self.ini also exists.

		the final output is
		1. self.velo_x  ->  the x comp of velocity (m/days) at where Ampcor has processed
		2. self.velo_y  ->  the y comp of velocity (m/days) ...
		3. self.snr     ->  the Signal-to-Noise Ratio ...
		4. self.err_x   ->  the x comp of the error of the velocity (m/days) ....
		5. self.err_y   ->  the y comp of the error of the velocity (m/days) ....
		All of these are in N-by-3 array, and the columns are 
		1) projected x coor, 2) projected y coor, 3) the desired quantity, respectively.
		"""

		if ref_raster is None:
			ref_raster = SingleRaster(self.ini.imagepair['image1'], date=self.ini.imagepair['image1_date'])
		if datedelta is None:
			a = SingleRaster(self.ini.imagepair['image1'], date=self.ini.imagepair['image1_date'])
			b = SingleRaster(self.ini.imagepair['image2'], date=self.ini.imagepair['image2_date'])
			datedelta = b.date - a.date

		geot = ref_raster.GetGeoTransform()
		ulx = geot[0]
		uly = geot[3]
		xres = geot[1]
		yres = geot[5]
		self.data[:, 0] = ulx + (self.data[:, 0] - 1) * xres
		self.data[:, 1] = self.data[:, 1] * abs(xres) / datedelta.days
		self.data[:, 2] = uly + (self.data[:, 2] - 1) * yres
		self.data[:, 3] = self.data[:, 3] * abs(yres) / datedelta.days
		self.data[:, 5] = np.sqrt(self.data[:, 5]) / datedelta.days
		self.data[:, 6] = np.sqrt(self.data[:, 6]) / datedelta.days

		self.velo_x = self.data[:,[0,2,1]]
		self.velo_y = self.data[:,[0,2,3]]
		self.snr    = self.data[:,[0,2,4]]
		self.err_x  = self.data[:,[0,2,5]]
		self.err_y  = self.data[:,[0,2,6]]


	def Velo2XYV(self, xyvfileprefix=None, spatialres=None, generate_xyztext=False):

		"""
		spatialres: the spatial resolution of the XYV file.
		xyvfileprefix: the prefix for output xyv file.

		the final output is
		self.xyv_...  -> after griddata, the data have been warped into a grid with a fixed spatial resolution.
		"""

		if xyvfileprefix is None:
			xyvfileprefix = self.ini.result['geotiff_prefix']
		if spatialres is None:
			y_list = np.unique(self.velo_x[:, 1])
			spatialres = np.sqrt((self.velo_x[1, 0] - self.velo_x[0, 0]) * (y_list[-1] - y_list[-2]))

		x = np.arange(self.velo_x[0, 0], self.velo_x[-1, 0], spatialres)
		y = np.arange(self.velo_x[0, 1], self.velo_x[-1, 1], -spatialres)
		xx, yy = np.meshgrid(x, y)

		vx = griddata(self.velo_x[:, [0,1]], self.velo_x[:, 2], (xx, yy), method='linear')
		vy = griddata(self.velo_y[:, [0,1]], self.velo_y[:, 2], (xx, yy), method='linear')
		mag = np.sqrt(vx ** 2 + vy ** 2)
		snr  = griddata(self.snr[:, [0,1]],   self.snr[:, 2],   (xx, yy), method='linear')
		errx = griddata(self.err_x[:, [0,1]], self.err_x[:, 2], (xx, yy), method='linear')
		erry = griddata(self.err_y[:, [0,1]], self.err_y[:, 2], (xx, yy), method='linear')

		self.xyv_velo_x   = np.stack([xx.flatten(), yy.flatten(), vx.flatten()]).T
		self.xyv_velo_y   = np.stack([xx.flatten(), yy.flatten(), vy.flatten()]).T
		self.xyv_mag = np.stack([xx.flatten(), yy.flatten(), mag.flatten()]).T
		self.xyv_snr = np.stack([xx.flatten(), yy.flatten(), snr.flatten()]).T
		self.xyv_err_x = np.stack([xx.flatten(), yy.flatten(), errx.flatten()]).T
		self.xyv_err_y = np.stack([xx.flatten(), yy.flatten(), erry.flatten()]).T

		if generate_xyztext:
			np.savetxt(xyvfileprefix + '_vx.xyz', self.xyv_velo_x, delimiter=" ", fmt='%10.2f %10.2f %10.6f')
			np.savetxt(xyvfileprefix + '_vy.xyz', self.xyv_velo_y, delimiter=" ", fmt='%10.2f %10.2f %10.6f')
			np.savetxt(xyvfileprefix + '_mag.xyz', self.xyv_mag, delimiter=" ", fmt='%10.2f %10.2f %10.6f')
			np.savetxt(xyvfileprefix + '_snr.xyz', self.xyv_snr, delimiter=" ", fmt='%10.2f %10.2f %10.6f')
			np.savetxt(xyvfileprefix + '_errx.xyz', self.xyv_err_x, delimiter=" ", fmt='%10.2f %10.2f %10.6f')
			np.savetxt(xyvfileprefix + '_erry.xyz', self.xyv_err_y, delimiter=" ", fmt='%10.2f %10.2f %10.6f')


	def XYV2Raster(self, xyvfileprefix=None, ref_raster=None):

		"""
		xyvfileprefix: the prefix for output xyv file.
		"""

		if xyvfileprefix is None:
			xyvfileprefix = self.ini.result['geotiff_prefix']
		if ref_raster is None:
			ref_raster = SingleRaster(self.ini.imagepair['image1'], date=self.ini.imagepair['image1_date'])

		# vx_xyz = xyvfileprefix + '_vx.xyz'
		# vy_xyz = xyvfileprefix + '_vy.xyz'
		# mag_xyz = xyvfileprefix + '_mag.xyz'

		# vx_gtiff = vx_xyz.replace('xyz', 'tif')
		# vy_gtiff = vy_xyz.replace('xyz', 'tif')
		# mag_gtiff = mag_xyz.replace('xyz', 'tif')

		vx_gtiff = xyvfileprefix + '_vx.tif'
		vy_gtiff = xyvfileprefix + '_vy.tif'
		mag_gtiff = xyvfileprefix + '_mag.tif'
		snr_gtiff = xyvfileprefix + '_snr.tif'
		errx_gtiff = xyvfileprefix + '_errx.tif'
		erry_gtiff = xyvfileprefix + '_erry.tif'

		xraster = SingleRaster(vx_gtiff)
		yraster = SingleRaster(vy_gtiff)
		magraster = SingleRaster(mag_gtiff)
		snrraster = SingleRaster(snr_gtiff)
		errxraster = SingleRaster(errx_gtiff)
		erryraster = SingleRaster(erry_gtiff)

		# proj = ref_raster.GetProjection()

		# xraster.XYZ2Raster(vx_xyz, projection=proj)
		# yraster.XYZ2Raster(vy_xyz, projection=proj)
		# magraster.XYZ2Raster(mag_xyz, projection=proj)

		xraster.Array2Raster(self.xyv_velo_x, ref_raster)


