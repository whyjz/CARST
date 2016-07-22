# Class: 
# used for dhdt
# by Whyjay Zheng, Jul 21 2016

import numpy as np

class TimeSeriesDEM(np.ndarray):

	def __new__(cls, dem=None, array=None, date=None, uncertainty=None):

		""" 
		You need to provide a UtilDEM.SingleDEM object, or provide array, date, and uncertainty separately.
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
			obj = np.asarray(dem.ReadAsArray()).view(cls)
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

	'''
	def __array_wrap__(self, out_arr, context=None):

		""" See TimeSeriesDEM.__new__ for comments """
		return np.ndarray.__array_wrap__(self, out_arr, context)
	'''

	def AddDEM(self, dem):

		"""
		Add a new DEM to the DEM time series.
		dem is a UtilDEM.SingleDEM object.
		"""

		self.date.append(dem.date)
		self.uncertainty.append(dem.uncertainty)
		# Add the first band
		return TimeSeriesDEM(array=np.dstack([self, dem.ReadAsArray()]), date=self.date, uncertainty=self.uncertainty)

	def Date2DayDelta(self):
		t = np.array(self.date) - self.date[0]
		self.daydelta = np.array([i.days for i in t])

	def SetWeight(self):
		self.weight = 1.0 / np.array(self.uncertainty) ** 2

	#def Polyfit(self, x, w):
	def Polyfit(self):

		"""
		Note that x and w are all 1-d array like, with the same length of the third dimension of the reg_array.
		w is the weight, which is often set to the inverse of data covariance matrix, C_d^-1
		Here w must have the same length of x.
		"""

		reg_size = list(self.shape)
		pixel_count = reg_size[0] * reg_size[1]

		y = self.reshape(pixel_count, reg_size[2]).T
		p, c = np.polyfit(self.daydelta, y, 1, w=np.sqrt(self.weight), cov=True)
		#                                   The number 1 here means the first order, i.e. y = a0 + a1 * x
		#                                   And the setting of w = np.sqrt(w) would minimize sigma(w * (y - y_hat) ^ 2)
		# p would be pixel_count-by-2 matrix, and c would be 2-by-2-by-pixel_count matrix.
		# p[0, :] is the slope
		# p[1, :] is the intercept
		# c[0, 0, k] is the slope variance for the k-th pixel
		# c[1, 1, k] is the intercept variance for the k-th pixel

		slope         = p[0, :].reshape(reg_size[:-1])
		intercept     = p[1, :].reshape(reg_size[:-1])
		slope_err     = np.sqrt(c[0, 0, :].reshape(reg_size[:-1]))
		intercept_err = np.sqrt(c[1, 1, :].reshape(reg_size[:-1]))
		return slope, intercept, slope_err, intercept_err