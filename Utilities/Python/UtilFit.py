# Class: TimeSeriesDEM(np.ndarray)
# used for dhdt
# by Whyjay Zheng, Jul 27 2016
# last edit: Aug 17 2016

import numpy as np
from datetime import datetime

class TimeSeriesDEM(np.ndarray):

	"""
	This class can include many DEMs (in UtilRaster.SingleRaster object) and then create a 3-D matrix.
	each DEM is aligned along z-axis so that TimeSeriesDEM[m, n, :] would be the time series at pixel (m, n).
	"""

	def __new__(cls, dem=None, array=None, date=None, uncertainty=None):

		""" 
		You need to provide a UtilRaster.SingleRaster object, or provide array, date, and uncertainty separately.
		TimeSeriesDEM is a n-m-k ndarray matrix, which n-m is the dem dimension, k is the count of dems.
		You need to make sure all input dems have the same size (pixel number).
		TimeSeriesDEM.date: a list of datetime object, which the length is k.
		TimeSeriesDEM.uncertainty: a list of uncertainty for each DEM. The length is also k.

		example:
		tsdem = TimeSeriesDEM(dem=foo)  ---> Add single DEM.  the method "AddDEM" also does the trick after tsdem is created.
		tsdem = TimeSeriesDEM(array=bar, date=bar2, uncertainty=bar3)   ---> Add single DEMs or multiple DEMs.
		        Note that bar.shape[2] == len(bar2) == len(bar3)

		Refered to
		http://docs.scipy.org/doc/numpy/user/basics.subclassing.html 
		http://stackoverflow.com/questions/27910013/how-can-a-class-that-inherits-from-a-numpy-array-change-its-own-values
		"""

		if dem is not None:
			# retrieve band 1 array, and then replace NoDataValue by np.nan
			dem_array = dem.ReadAsArray()
			dem_array[dem_array == dem.GetNoDataValue()] = np.nan
			obj = np.asarray(dem_array).view(cls)
			obj.date = [dem.date]
			obj.uncertainty = [dem.uncertainty]
		elif all([arg is not None for arg in [array, date, uncertainty]]):
			obj = np.asarray(array).view(cls)
			obj.date = date if type(date) is list else [date]
			obj.uncertainty = uncertainty if type(uncertainty) is list else [uncertainty]
		else:
			raise ValueError('You need to either set "dem" or set "array, date and uncertainty".') 
		obj.daydelta = None
		obj.weight = None
		return obj

	def __array_finalize__(self, obj):

		""" See TimeSeriesDEM.__new__ for comments """

		if obj is None: return
		self.date = getattr(obj, 'date', None)
		self.uncertainty = getattr(obj, 'uncertainty', None)
		self.daydelta = getattr(obj, 'daydelta', None)
		self.weight = getattr(obj, 'weight', None)


	def AddDEM(self, dem):

		"""
		Add a new DEM to the DEM time series.
		dem is a UtilRaster.SingleRaster object.
		"""

		self.date.append(dem.date)
		self.uncertainty.append(dem.uncertainty)
		# Add the first band, and then replace NoDataValue by np.nan
		dem_array = dem.ReadAsArray()
		dem_array[dem_array == dem.GetNoDataValue()] = np.nan
		return TimeSeriesDEM(array=np.dstack([self, dem_array]), date=self.date, uncertainty=self.uncertainty)

	def Date2DayDelta(self):

		"""
		Make self.daydelta from [self.date - min(self.date)]
		"""

		t = np.array(self.date) - min(self.date)
		self.daydelta = np.array([i.days for i in t])

	def SetWeight(self):

		"""
		Weight is set to 1/sigma^2
		"""

		self.weight = 1.0 / np.array(self.uncertainty) ** 2

	def Polyfit(self, min_count=5, min_time_span=365, min_year=2000, max_year=2016):

		"""
		Note that x and w are all 1-d array like, with the same length of the third dimension of the reg_array.
		w is the weight, which is often set to the inverse of data covariance matrix, C_d^-1
		Here w must have the same length of x.
		"""

		reg_size = list(self.shape)
		pixel_count = reg_size[0] * reg_size[1]

		y = self.reshape(pixel_count, reg_size[2]).T
		slope         = np.zeros(pixel_count)
		slope_err     = np.zeros(pixel_count)
		intercept     = np.zeros(pixel_count)
		intercept_err = np.zeros(pixel_count)
		for i in range(y.shape[1]):
			if i % 10000 == 0:
				print("processing " + str(i) + " pixels out of " + str(y.shape[1]) + " pixels")
			px_y = y[:, i]
			valid_idx = ~np.isnan(px_y)
			# judge if a pixel is able to do regression using the given arguments
			minlim_idx = np.array(self.date) > datetime(min_year, 1, 1)
			maxlim_idx = np.array(self.date) < datetime(max_year, 1, 1)
			valid_idx = valid_idx & minlim_idx & maxlim_idx
			if sum(valid_idx) < min_count:
				slope[i] = slope_err[i] = intercept[i] = intercept_err[i] = np.nan
			elif max(self.daydelta[valid_idx]) - min(self.daydelta[valid_idx]) < min_time_span:
				slope[i] = slope_err[i] = intercept[i] = intercept_err[i] = np.nan
			# begin the polyfits
			else:
				px_y = px_y[valid_idx]
				px_x = self.daydelta[valid_idx]
				px_w = self.weight[valid_idx]
				# This method minimizes sum(w * (y_i - y^hat_i) ^ 2)
				#    Here we set w=np.sqrt(px_w) becuase np.polyfit minimizes sum( (w * (y_i - y^hat_i)) ^ 2) by default.
				# Covariance is estimated from multivariate t-distribution.
				# Comparing to the v0.1 version, this new method is slightly more conservative
				#    because it considers the case of small d.o.f.
				p, c = np.polyfit(px_x, px_y, 1, w=np.sqrt(px_w), cov=True)
				slope[i]         = p[0]
				slope_err[i]     = np.sqrt(c[0, 0])
				intercept[i]     = p[1]
				intercept_err[i] = np.sqrt(c[1, 1])

		return slope.reshape(reg_size[:-1]), intercept.reshape(reg_size[:-1]), slope_err.reshape(reg_size[:-1]), intercept_err.reshape(reg_size[:-1])
