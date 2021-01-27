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
from scipy.stats import gaussian_kde
import pickle
import matplotlib.pyplot as plt

class DuoZArray:

	def __init__(self, z1=None, z2=None, ini=None):



		self.z1 = z1
		self.z2 = z2
		self.ini = ini
		self.signal_idx = None

	def OutlierDetection2D(self, thres_sigma=3.0, plot=True):
		x = self.z1
		y = self.z2
		xy = np.vstack([x, y])
		z = gaussian_kde(xy)(xy)

		thres_multiplier = np.e ** (thres_sigma ** 2 / 2)   # normal dist., +- sigma number 
		thres = max(z) / thres_multiplier
		idx = z >= thres
		self.signal_idx = idx

		if plot:
			pt_style = {'s': 5, 'edgecolor': None}
			ax_center = [x[idx].mean(), y[idx].mean()]
			ax_halfwidth = max([max(x) - x[idx].mean(), 
				                x[idx].mean() - min(x),
				                max(y) - y[idx].mean(),
				                y[idx].mean() - min(y)]) + 1
			plt.subplot(121)
			plt.scatter(x, y, c=z, **pt_style)
			plt.scatter(x[~idx], y[~idx], c='xkcd:red', **pt_style)
			plt.axis('scaled')
			plt.xlim([ax_center[0] - ax_halfwidth, ax_center[0] + ax_halfwidth])
			plt.ylim([ax_center[1] - ax_halfwidth, ax_center[1] + ax_halfwidth])
			plt.ylabel('Offset-Y (pixels)')
			plt.xlabel('Offset-X (pixels)')
			plt.subplot(122)
			plt.scatter(x, y, c=z, **pt_style)
			plt.scatter(x[~idx], y[~idx], c='xkcd:red', **pt_style)
			plt.axis('scaled')
			plt.xlim([min(x[idx]) - 1, max(x[idx]) + 1])
			plt.ylim([min(y[idx]) - 1, max(y[idx]) + 1])
			plt.savefig(self.ini.velocorrection['label_bedrock_histogram'] + '_vx-vs-vy.png', format='png', dpi=200)
			plt.clf()

	def HistWithOutliers(self, which=None):
		if which == 'x':
			x = self.z1
			pnglabel = '_vx.png'
		elif which == 'y':
			x = self.z2
			pnglabel = '_vy.png'
		else:
			raise ValueError('Please indicate "x" or "y" for your histogram.')

		r_uniq, r_uniq_n = np.unique(x, return_counts=True)
		b_uniq, b_uniq_n = np.unique(x[self.signal_idx], return_counts=True)

		bar_w = min(np.diff(r_uniq))
		lbound = min(x[self.signal_idx]) - np.std(x)
		rbound = max(x[self.signal_idx]) + np.std(x)
		N_outside_lbound_red = int(sum(x < lbound))
		N_outside_rbound_red = int(sum(x > rbound))

		plt.bar(r_uniq, r_uniq_n, width=bar_w, color='xkcd:red')
		plt.bar(b_uniq, b_uniq_n, width=bar_w, color='xkcd:blue')
		plt.xlim([lbound, rbound])
		title_str = 'Red points outside (L|R): {}|{}'.format(N_outside_lbound_red, N_outside_rbound_red)
		plt.title(title_str)
		plt.ylabel('N')
		plt.xlabel('offset (pixels)')
		plt.savefig(self.ini.velocorrection['label_bedrock_histogram'] + pnglabel, format='png', dpi=200)
		plt.clf()	

	def VeloCorrectionInfo(self):

		a = SingleRaster(self.ini.imagepair['image1'], date=self.ini.imagepair['image1_date'])
		b = SingleRaster(self.ini.imagepair['image2'], date=self.ini.imagepair['image2_date'])
		datedelta = b.date - a.date
		geot = a.GetGeoTransform()
		xres = geot[1]
		yres = geot[5]

		x_culled = self.z1[self.signal_idx]
		y_culled = self.z2[self.signal_idx]

		self.z1.MAD_median = np.median(x_culled)
		self.z1.MAD_std    =    np.std(x_culled, ddof=1)
		self.z1.MAD_mean   =   np.mean(x_culled)
		self.z2.MAD_median = np.median(y_culled)
		self.z2.MAD_std    =    np.std(y_culled, ddof=1)
		self.z2.MAD_mean   =   np.mean(y_culled)

		vx_zarray_velo            = self.z1[:]         * abs(xres) / datedelta.days
		vx_zarray_velo.MAD_median = self.z1.MAD_median * abs(xres) / datedelta.days
		vx_zarray_velo.MAD_std    = self.z1.MAD_std    * abs(xres) / datedelta.days
		vx_zarray_velo.MAD_mean   = self.z1.MAD_mean   * abs(xres) / datedelta.days
		vy_zarray_velo            = self.z2[:]         * abs(yres) / datedelta.days
		vy_zarray_velo.MAD_median = self.z2.MAD_median * abs(yres) / datedelta.days
		vy_zarray_velo.MAD_std    = self.z2.MAD_std    * abs(yres) / datedelta.days
		vy_zarray_velo.MAD_mean   = self.z2.MAD_mean   * abs(yres) / datedelta.days

		with open(self.ini.velocorrection['label_logfile'], 'w') as f:
			f.write( 'Total points over bedrock =   {:6n}\n'.format(self.z1.size) )
			f.write( '-------- Unit: Pixels --------\n')
			f.write( 'median_x_px    = {:6.3f}\n'.format(float(self.z1.MAD_median)) )
			f.write( 'median_y_px    = {:6.3f}\n'.format(float(self.z2.MAD_median)) )
			f.write( 'std_x_px       = {:6.3f}\n'.format(float(self.z1.MAD_std)) )
			f.write( 'std_y_px       = {:6.3f}\n'.format(float(self.z2.MAD_std)) )
			f.write( 'mean_x_px      = {:6.3f}\n'.format(float(self.z1.MAD_mean)) )
			f.write( 'mean_y_px      = {:6.3f}\n'.format(float(self.z2.MAD_mean)) )
			f.write( '-------- Unit: Velocity (L/T; most likely m/day) --------\n')
			f.write( 'median_x       = {:6.3f}\n'.format(float(vx_zarray_velo.MAD_median)) )
			f.write( 'median_y       = {:6.3f}\n'.format(float(vy_zarray_velo.MAD_median)) )
			f.write( 'std_x          = {:6.3f}\n'.format(float(vx_zarray_velo.MAD_std)) )
			f.write( 'std_y          = {:6.3f}\n'.format(float(vy_zarray_velo.MAD_std)) )
			f.write( 'mean_x         = {:6.3f}\n'.format(float(vx_zarray_velo.MAD_mean)) )
			f.write( 'mean_y         = {:6.3f}\n'.format(float(vy_zarray_velo.MAD_mean)) )

		return vx_zarray_velo, vy_zarray_velo


class ZArray(np.ndarray):

	# A subclass from ndarray, with some new attributes and fancier methods for our purposes
	# please see
	# https://docs.scipy.org/doc/numpy-1.13.0/user/basics.subclassing.html
	# for more details.

	#WARNING: NO NANs SHOULD BE FOUND IN ZArray !!! IT CAN GIVE YOU A BAD RESULT !!!

	def __new__(cls, input_array):
		# For now input_array should be a 1-d array
		# Input array is an already formed ndarray instance
		# We need first to cast to be our class type
		obj = np.asarray(input_array).view(cls)
		obj.MAD_idx = None
		obj.MAD_mean = None
		obj.MAD_median = None
		obj.MAD_std = None
		# obj.signal_val = None
		# obj.signal_n = None
		obj.signal_array = None
		return obj

	def __array_finalize__(self, obj):
		if obj is None: return
		self.MAD_idx    = getattr(obj, 'MAD_idx', None)
		self.MAD_mean   = getattr(obj, 'MAD_mean', None)
		self.MAD_median = getattr(obj, 'MAD_median', None)
		self.MAD_std    = getattr(obj, 'MAD_std', None)
		# self.signal_val = getattr(obj, 'signal_val', None)
		# self.signal_n   = getattr(obj, 'signal_n', None)
		self.signal_array = getattr(obj, 'signal_array', None)

	# =============================================================================================
	# ==== The following functions represent new functions developed from =========================
	# ==== StatisticOutput and HistWithOutliers. ==================================================
	# =============================================================================================

	def MADStats(self):
		mad = lambda x : 1.482 * np.median(abs(x - np.median(x)))
		if self.size <= 3:
			print('WARNING: there are too few Z records (<= 3). Aborting the calculation.')
			return [], np.nan, np.nan, np.nan
		else:
			val_median = np.median(self)
			val_mad = mad(self)
			lbound = val_median - 3. * val_mad
			ubound = val_median + 3. * val_mad
			idx = np.logical_and(self >= lbound, self <= ubound)

			self.MAD_idx = idx
			self.MAD_mean = np.mean(self[idx])
			self.MAD_median = np.median(self[idx])
			self.MAD_std = np.std(self[idx], ddof=1)

	def MADHist(self, pngname):

		nbins = len(self) // 4 + 1
		nbins = 201 if nbins > 201 else nbins

		bins = np.linspace(min(self), max(self), nbins)
		plt.hist(self, bins=bins, color='xkcd:red')
		plt.hist(self[self.MAD_idx], bins=bins, color='xkcd:blue')
		plt.ylabel('N')
		plt.xlabel('Value (pixel value unit)')
		plt.savefig(pngname, format='png')
		plt.cla()

	# =============================================================================================
	# ==== The functions above represent new functions developed from =============================
	# ==== StatisticOutput and HistWithOutliers. ==================================================
	# =============================================================================================




	# =============================================================================================
	# ==== The following functions are designed firstly for the functions in the class XYZFile ====
	# ==== and later is has modified to a QGIS processing scripts called MAD_outlier_filter.py ====
	# ==== now we have copied them back. ==========================================================
	# =============================================================================================

	# Major Rehaul on Oct 25, 2018, added the background correction 
	# the default of mad_multiplier was 3.0
	# background correction redesigned on Nov 9, 2018 using more information from the PX

	def StatisticOutput(self, plot=True, pngname=None, ini=None):
		mad = lambda x : 1.482 * np.median(abs(x - np.median(x)))
		if self.size == 0:
			print('WARNING: there is no Z records.')
			return [], np.nan, np.nan, np.nan
		else:
			# if ini is not None:
			# 	ref_raster = SingleRaster(ini.imagepair['image1'])
			# 	-> to be continued

			mad_multiplier = ini.noiseremoval['peak_detection']

			uniq, uniq_n = np.unique(self, return_counts=True)
			uniq, uniq_n = fill_with_zero(uniq, uniq_n, ini.pxsettings['oversampling'])
			uniq_n_est, _, _ = backcor(uniq, uniq_n, order=ini.noiseremoval['backcor_order'])
			background_mad = mad(uniq_n - uniq_n_est)    # this is actually the noise level
			if background_mad == 0:
				background_mad = np.median(abs(uniq_n - uniq_n_est))
				print("Use the median of abs(uniq_n - uniq_n_est) as one SNR level since mad = 0")
			background_threshold = uniq_n_est + mad_multiplier * background_mad
			signal_idx = np.argwhere(uniq_n >= background_threshold)
			signal_idx = np.ndarray.flatten(signal_idx)
			signal_val = uniq[signal_idx]
			# self.signal_val = uniq[signal_idx]
			signal_n = uniq_n[signal_idx]
			# self.signal_n = uniq_n[signal_idx]
			self.signal_array = np.repeat(signal_val, signal_n.astype(int))
			


			self.MAD_mean = self.signal_array.mean()
			self.MAD_median = np.median(self.signal_array)
			self.MAD_std = self.signal_array.std(ddof=1)

			# offset_median = np.median(self.signal_array)
			# offset_mad = mad(self.signal_array)
			# if offset_mad == 0:
			# 	# the case when over half of the numbers are at the median number,
			# 	# we use the Median absolute deviation around the mean instead of around the median.
			# 	offset_mad = 1.482 * np.median(abs(self.signal_array - np.mean(self.signal_array)))
			# lbound = offset_median - mad_multiplier * offset_mad
			# ubound = offset_median + mad_multiplier * offset_mad
			# self.MAD_idx = np.logical_and(self.signal_array > lbound, self.signal_array < ubound)
			# trimmed_numlist = self.signal_array[self.MAD_idx]
			# self.MAD_mean = trimmed_numlist.mean()
			# self.MAD_median = np.median(trimmed_numlist)
			# self.MAD_std = trimmed_numlist.std(ddof=1)
			if plot == True and pngname is not None:
				self.VerifyBackcor(pngname, uniq, uniq_n, uniq_n_est, background_threshold)
				self.HistWithOutliers(pngname)
				pickle.dump(self, open(pngname.replace('.png', '.p'), 'wb'))
			# return idx2, trimmed_numlist.mean(), np.median(trimmed_numlist), trimmed_numlist.std(ddof=1)

	def VerifyBackcor(self, pngname, uniq, uniq_n, uniq_n_est, background_threshold):

		import matplotlib.pyplot as plt

		pngname = pngname.replace('.png', '-backcor.png')
		plt.plot(uniq, uniq_n, label='Histogram', color='xkcd:plum')
		plt.plot(uniq, uniq_n_est, label='Background', color='xkcd:lightgreen')
		plt.plot(uniq, background_threshold, label='Detection Threshold', color='xkcd:coral')
		# plt.xlim([min(uniq), max(uniq)])
		plt.ylabel('N')
		plt.xlabel('offset (pixels)')
		plt.legend(loc='best')
		plt.savefig(pngname, format='png', dpi=200)
		plt.cla()


	def HistWithOutliers(self, pngname, histogram_bound=10):

		import matplotlib.pyplot as plt

		nbins = len(self) // 4 + 1
		nbins = 201 if nbins > 201 else nbins

		lbound = min(self) if (min(self) >= -histogram_bound) or (np.mean(self) < -histogram_bound) else -histogram_bound
		rbound = max(self) if (max(self) <= histogram_bound)  or (np.mean(self) > histogram_bound)  else histogram_bound

		if lbound >= rbound:
			lbound = min(self)
			rbound = max(self)
		bins = np.linspace(lbound, rbound, nbins)
		# trimmed_numlist = self.signal_array[self.MAD_idx]
		trimmed_numlist = self.signal_array
		N_outside_lbound_red = int(sum(self < lbound))
		N_outside_rbound_red = int(sum(self > rbound))
		N_outside_lbound_blue = int(sum(trimmed_numlist < lbound))
		N_outside_rbound_blue = int(sum(trimmed_numlist > rbound))
		title_str = '[Red|Blue] L outside: [{}|{}] R outside: [{}|{}]'.format(N_outside_lbound_red, N_outside_lbound_blue, N_outside_rbound_red, N_outside_rbound_blue)
		# plot histograms
		plt.hist(self, bins=bins, color=[0.95, 0.25, 0.1])
		plt.hist(trimmed_numlist, bins=bins, color=[0.1, 0.25, 0.95])
		plt.ylabel('N')
		plt.xlabel('offset (pixels)')
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

		import pickle
		self.data = pickle.load(open(self.fpath, 'rb'))
		# self.data = np.loadtxt(self.fpath)
		self.CheckData()

	def CheckData(self):
		"""
		Check if there's any strange value in the ampoff.
		"""

		# 1000 is an arbitrary value
		idx = np.argwhere(abs(self.data[:, [1, 3]]) > 1000)
		idx = np.unique(idx[:, 0])
		self.data = np.delete(self.data, idx, 0)

	def SetIni(self, ini):

		self.ini = ini

	def FillwithNAN(self):
		"""
		Fill hole with nan value.
		"""
		x_linenum = np.arange(min(self.data[:, 0]), max(self.data[:, 0]) + self.ini.pxsettings['skip_across'], self.ini.pxsettings['skip_across'])
		y_linenum = np.unique(self.data[:, 2])
		xx_linenum, yy_linenum = np.meshgrid(x_linenum, y_linenum)
		complete_xymap = np.vstack((xx_linenum.flatten(), yy_linenum.flatten())).T
		raw_xymap = self.data[:, [0, 2]]

		# ---- collapse x & y linenumber to a 1-d array. 
		#### NOTE THIS WILL GO WRONG IF YOU HAVE A SUPER HUGE ARRAY!

		cxy = complete_xymap[:, 0] * 1000000 + complete_xymap[:, 1]
		rxy = raw_xymap[:, 0] * 1000000 + raw_xymap[:, 1]
		# ----

		idx = np.where(np.isin(cxy, rxy))
		idx = idx[0]
		newdata = np.empty((complete_xymap.shape[0],8))
		newdata[:] = np.nan
		newdata[:,[0,2]] = complete_xymap
		newdata[idx,1] = self.data[:, 1]
		newdata[idx,3] = self.data[:, 3]
		newdata[idx,4] = self.data[:, 4]
		newdata[idx,5] = self.data[:, 5]
		newdata[idx,6] = self.data[:, 6]
		newdata[idx,7] = self.data[:, 7]

		self.data = newdata

	def Ampcoroff2Velo(self, ref_raster=None, datedelta=None, velo_or_pixel='velo'):

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

		if velo_or_pixel == 'velo':
			self.data[:, 0] = ulx + (self.data[:, 0] - 1) * xres
			self.data[:, 1] = self.data[:, 1] * abs(xres) / datedelta.days
			self.data[:, 2] = uly + (self.data[:, 2] - 1) * yres
			self.data[:, 3] = self.data[:, 3] * abs(yres) / datedelta.days
			self.data[:, 5] = np.sqrt(self.data[:, 5]) / datedelta.days
			self.data[:, 6] = np.sqrt(self.data[:, 6]) / datedelta.days
			self.velo_x = self.data[:,[0,2,1]]
			self.velo_y = self.data[:,[0,2,3]]
			self.velo_y[:, -1] = -self.velo_y[:, -1]  # UL-LR system to Cartesian
			self.snr    = self.data[:,[0,2,4]]
			self.err_x  = self.data[:,[0,2,5]]
			self.err_y  = self.data[:,[0,2,6]]
		elif velo_or_pixel == 'pixel':
			self.data[:, 0] = ulx + (self.data[:, 0] - 1) * xres
			self.data[:, 2] = uly + (self.data[:, 2] - 1) * yres
			self.velo_x = self.data[:,[0,2,1]]
			self.velo_y = self.data[:,[0,2,3]]   
			self.velo_y[:, -1] = -self.velo_y[:, -1]  # UL-LR system to Cartesian
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
			xyvfileprefix = self.ini.rawoutput['label_geotiff']
		if spatialres is None:
			y_list = np.unique(self.velo_x[:, 1])
			spatialres = np.sqrt((self.velo_x[1, 0] - self.velo_x[0, 0]) * (y_list[-1] - y_list[-2]))

		x = np.arange(min(self.velo_x[:, 0]), max(self.velo_x[:, 0]), spatialres)
		y = np.arange(max(self.velo_x[:, 1]), min(self.velo_x[:, 1]), -spatialres)
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
			xyvfileprefix = self.ini.rawoutput['label_geotiff']
		if ref_raster is None:
			ref_raster = SingleRaster(self.ini.imagepair['image1'], date=self.ini.imagepair['image1_date'])

		# vx_xyz = xyvfileprefix + '_vx.xyz'
		# vy_xyz = xyvfileprefix + '_vy.xyz'
		# mag_xyz = xyvfileprefix + '_mag.xyz'

		# vx_gtiff = vx_xyz.replace('xyz', 'tif')
		# vy_gtiff = vy_xyz.replace('xyz', 'tif')
		# mag_gtiff = mag_xyz.replace('xyz', 'tif')

		nodata_val = -9999.0

		self.xyv_velo_x[np.isnan(self.xyv_velo_x)]  = nodata_val
		self.xyv_velo_y[np.isnan(self.xyv_velo_y)]  = nodata_val
		self.xyv_mag[np.isnan(self.xyv_mag)]  = nodata_val
		self.xyv_snr[np.isnan(self.xyv_snr)]  = nodata_val
		self.xyv_err_x[np.isnan(self.xyv_err_x)]  = nodata_val
		self.xyv_err_y[np.isnan(self.xyv_err_y)]  = nodata_val

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

		proj = ref_raster.GetProjection()
		# print(self.xyv_velo_x)
		# print(proj)

		# xraster.XYZ2Raster(vx_xyz, projection=proj)
		# yraster.XYZ2Raster(vy_xyz, projection=proj)
		# magraster.XYZ2Raster(mag_xyz, projection=proj)

		xraster.XYZArray2Raster(self.xyv_velo_x, projection=proj)
		yraster.XYZArray2Raster(self.xyv_velo_y, projection=proj)
		magraster.XYZArray2Raster(self.xyv_mag, projection=proj)
		snrraster.XYZArray2Raster(self.xyv_snr, projection=proj)
		errxraster.XYZArray2Raster(self.xyv_err_x, projection=proj)
		erryraster.XYZArray2Raster(self.xyv_err_y, projection=proj)

		xraster.SetNoDataValue(nodata_val)
		yraster.SetNoDataValue(nodata_val)
		magraster.SetNoDataValue(nodata_val)
		snrraster.SetNoDataValue(nodata_val)
		errxraster.SetNoDataValue(nodata_val)
		errxraster.SetNoDataValue(nodata_val)


def points_in_polygon(points_geometry, shp_filename):
	# points_geometry: N-by-2 np array defining the geometry of points
	# shp_filename: shapefile name 
	# Both datasets should have the SAME CRS!

	# return: np mask array showing where the targeted points are.

	import logging
	logging.basicConfig(level=logging.WARNING)
	import geopandas as gpd
	from shapely.geometry import Point
	# from shapely.geometry import mapping


	shapefile = gpd.read_file(shp_filename)
	poly_geometries = [shapefile.loc[i]['geometry'] for i in range(len(shapefile))]
	pt_geometries = [Point(xy) for xy in zip(points_geometry[:, 0], points_geometry[:, 1])]
	pt_gs = gpd.GeoSeries(pt_geometries)

	idx = None
	for single_poly in poly_geometries:
		if idx is None:
			idx = pt_gs.within(single_poly)
		else:
			tmp = pt_gs.within(single_poly)
			idx = np.logical_or(idx, tmp)

	return idx


def fill_with_zero(uniq, uniq_n, ini_oversampling):
	"""
	Fill the gaps between min and max with zero (counts)
	for the uniq and uniq_n.
	"""
	# ---- Verification of the sub-pixel sampling rate
	def_sampling_rate = ini_oversampling * 2   # sampling rate defined in the ini file
	real_sampling_rate = 1 / min(np.diff(uniq))
	if int(def_sampling_rate) != int(real_sampling_rate):
		raise ValueError('Over-sampling rate of the data mismatches the one defined in the ini file!')
	# ----

	complete_uniq = np.arange(min(uniq), max(uniq) + min(np.diff(uniq)), min(np.diff(uniq)))
	complete_uniq_n = np.zeros_like(complete_uniq)

	idx = np.where(np.isin(complete_uniq, uniq))
	complete_uniq_n[idx] = uniq_n

	return ZArray(complete_uniq), ZArray(complete_uniq_n)


def backcor(n, y, order=4, s=0.01, fct='sh'):
	# from backcor.m, https://www.mathworks.com/matlabcentral/fileexchange/27429-background-correction
	# Impletion using Python by Whyjay, Oct 25, 2018

	# Note: 'ah', 'stq', and 'atq' are not finalized yet, so it will generate an error.

	# Credits (from backcor.m):
	# For more informations, see:
	# - V. Mazet, C. Carteret, D. Brie, J. Idier, B. Humbert. Chemom. Intell. Lab. Syst. 76 (2), 2005.
	# - V. Mazet, D. Brie, J. Idier. Proceedings of EUSIPCO, pp. 305-308, 2004.
	# - V. Mazet. PhD Thesis, University Henri Poincaré Nancy 1, 2005.
	# 
	# 22-June-2004, Revised 19-June-2006, Revised 30-April-2010,
	# Revised 12-November-2012 (thanks E.H.M. Ferreira!)
	# Comments and questions to: vincent.mazet@unistra.fr.
	#
	# Usage (fram backcor.m):
	# BACKCOR   Background estimation by minimizing a non-quadratic cost function.

	# [EST,COEFS,IT] = BACKCOR(N,Y,ORDER,THRESHOLD,FUNCTION) computes and estimation EST
	# of the background (aka. baseline) in a spectroscopic signal Y with wavelength N.
	# The background is estimated by a polynomial with order ORDER using a cost-function
	# FUNCTION with parameter THRESHOLD. FUNCTION can have the four following values:
	#     'sh'  - symmetric Huber function :  f(x) = { x^2  if abs(x) < THRESHOLD,
	#                                                { 2*THRESHOLD*abs(x)-THRESHOLD^2  otherwise.
	#     'ah'  - asymmetric Huber function :  f(x) = { x^2  if x < THRESHOLD,
	#                                                 { 2*THRESHOLD*x-THRESHOLD^2  otherwise.
	#     'stq' - symmetric truncated quadratic :  f(x) = { x^2  if abs(x) < THRESHOLD,
	#                                                     { THRESHOLD^2  otherwise.
	#     'atq' - asymmetric truncated quadratic :  f(x) = { x^2  if x < THRESHOLD,
	#                                                      { THRESHOLD^2  otherwise.
	# COEFS returns the ORDER+1 vector of the estimated polynomial coefficients
	# (computed with n sorted and bounded in [-1,1] and y bounded in [0,1]).
	# IT returns the number of iterations.

	# Check arguments
	# if nargin < 2, error('backcor:NotEnoughInputArguments','Not enough input arguments'); end;
	# if nargin < 5, [z,a,it,order,s,fct] = backcorgui(n,y); return; end; % delete this line if you do not need GUI
	if fct not in ['sh', 'ah', 'stq', 'atq']:
		raise ValueError('Unknown function.')

	# Rescaling
	N = len(n)
	i = np.argsort(n)
	n = n[i]
	y = y[i]
	maxy = max(y)
	dely = (maxy - min(y)) / 2
	n = 2 * (n[:] - n[-1]) / (n[-1] - n[0]) + 1;
	y = (y[:] - maxy) / dely + 1;

	# Vandermonde matrix
	p = np.linspace(0, order, order+1)
	temp1 = np.tile(n, (order + 1, 1)).T
	temp2 = np.tile(p, (N, 1))
	T = np.tile(n, (order + 1, 1)).T ** np.tile(p, (N, 1))
	Tinv = np.matmul(np.linalg.pinv(np.matmul(T.T, T)), T.T)

	# Initialisation (least-squares estimation)
	a = np.matmul(Tinv, y)
	z = np.matmul(T, a)

	# Other variables
	alpha = 0.99 * 1/2      # Scale parameter alpha
	it = 0                  # Iteration number
	zp = np.ones((1, N))    # Previous estimation

	# LEGEND
	while np.sum((z - zp) ** 2) / np.sum(zp ** 2) > 1e-9:

		it += 1             # Iteration number
		zp = z[:]           # Previous estimation
		res = y - z         # Residual

		# Estimate d
		if fct == 'sh':
			d = (res * (2 * alpha - 1)) * (abs(res) < s) + (-alpha * 2 * s - res) * (res <= -s) + (alpha * 2 * s - res) * (res >= s)
		elif fct == 'ah':
			raise ValueError('This has not implemented yet.')
			# d = (res*(2*alpha-1)) .* (res<s) + (alpha*2*s-res) .* (res>=s)
		elif fct == 'stq':
			raise ValueError('This has not implemented yet.')
			# d = (res*(2*alpha-1)) .* (abs(res)<s) - res .* (abs(res)>=s)
		elif fct == 'atq':
			raise ValueError('This has not implemented yet.')
			# d = (res*(2*alpha-1)) .* (res<s) - res .* (res>=s)

		# Estimate z
		a = np.matmul(Tinv, y + d)   # Polynomial coefficients a
		z = np.matmul(T, a)          # Polynomial

	# Rescaling
	j = np.argsort(i)
	z = (z[j] - 1) * dely + maxy

	a[0] -= 1
	a *= dely

	return z, a, it
