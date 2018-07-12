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
		self.xoffset = None
		self.yoffset = None
		self.xyv_x   = None
		self.xyv_y   = None
		self.xyv_mag = None
		self.ini     = None

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

		self.xoffset = self.data[:,[0,2,1]]
		self.yoffset = self.data[:,[0,2,3]]

	def Velo2XYV(self, xyvfileprefix=None, spatialres=None):

		"""
		spatialres: the spatial resolution of the XYV file.
		xyvfileprefix: the prefix for output xyv file.
		"""

		if xyvfileprefix is None:
			xyvfileprefix = self.ini.result['geotiff_prefix']
		if spatialres is None:
			y_list = np.unique(self.xoffset[:, 1])
			spatialres = np.sqrt((self.xoffset[1, 0] - self.xoffset[0, 0]) * (y_list[-1] - y_list[-2]))

		x = np.arange(self.xoffset[0, 0], self.xoffset[-1, 0], spatialres)
		y = np.arange(self.xoffset[0, 1], self.xoffset[-1, 1], -spatialres)
		xx, yy = np.meshgrid(x, y)

		vx = griddata(self.xoffset[:, [0,1]], self.xoffset[:, 2], (xx, yy), method='linear')
		vy = griddata(self.yoffset[:, [0,1]], self.yoffset[:, 2], (xx, yy), method='linear')
		mag = np.sqrt(vx ** 2 + vy ** 2)

		self.xyv_x   = np.stack([xx.flatten(), yy.flatten(), vx.flatten()]).T
		self.xyv_y   = np.stack([xx.flatten(), yy.flatten(), vy.flatten()]).T
		self.xyv_mag = np.stack([xx.flatten(), yy.flatten(), mag.flatten()]).T

		np.savetxt(xyvfileprefix + '_vx.xyz', self.xyv_x, delimiter=" ", fmt='%10.2f %10.2f %10.6f')
		np.savetxt(xyvfileprefix + '_vy.xyz', self.xyv_y, delimiter=" ", fmt='%10.2f %10.2f %10.6f')
		np.savetxt(xyvfileprefix + '_mag.xyz', self.xyv_mag, delimiter=" ", fmt='%10.2f %10.2f %10.6f')

	def XYV2Raster(self, xyvfileprefix=None, ref_raster=None):

		"""
		xyvfileprefix: the prefix for output xyv file.
		"""

		if xyvfileprefix is None:
			xyvfileprefix = self.ini.result['geotiff_prefix']
		if ref_raster is None:
			ref_raster = SingleRaster(self.ini.imagepair['image1'], date=self.ini.imagepair['image1_date'])

		vx_xyz = xyvfileprefix + '_vx.xyz'
		vy_xyz = xyvfileprefix + '_vy.xyz'
		mag_xyz = xyvfileprefix + '_mag.xyz'

		vx_gtiff = vx_xyz.replace('xyz', 'tif')
		vy_gtiff = vy_xyz.replace('xyz', 'tif')
		mag_gtiff = mag_xyz.replace('xyz', 'tif')

		xraster = SingleRaster(vx_gtiff)
		yraster = SingleRaster(vy_gtiff)
		magraster = SingleRaster(mag_gtiff)

		proj = ref_raster.GetProjection()

		xraster.XYZ2Raster(vx_xyz, projection=proj)
		yraster.XYZ2Raster(vy_xyz, projection=proj)
		magraster.XYZ2Raster(mag_xyz, projection=proj)


