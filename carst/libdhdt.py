# Class: TimeSeriesDEM(np.ndarray)
# Func: Resample_Array(UtilRaster.SingleRaster, UtilRaster.SingleRaster)
# used for dhdt
# by Whyjay Zheng, Jul 27 2016
# last edit: Jun 22 2017

import numpy as np
from numpy.linalg import inv
import os
import sys
try:
	import gdal
except:
	from osgeo import gdal        # sometimes gdal is part of osgeo modules
from datetime import datetime
from shapely.geometry import Polygon
from scipy.interpolate import interp2d
from scipy.interpolate import NearestNDInterpolator
from scipy.interpolate import griddata
import gc
from carst.libraster import SingleRaster
import pickle
import matplotlib.pyplot as plt

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

def Resample_Array2(orig_dem, resamp_ref_dem, resampleAlg='bilinear'):

	"""
	resample orig_dem using the extent and spacing provided by resamp_ref_dem
	orig_dem: class UtilRaster.SingleRaster object
	resamp_ref_dem: class UtilRaster.SingleRaster object
	returns: an numpy array, which you can use the methods in UtilRaster to trasform it into a raster

	This one uses gdal.Warp API.
	"""

	ds = gdal.Open(orig_dem.fpath)
	ulx, uly, lrx, lry = resamp_ref_dem.GetExtent()
	opts = gdal.WarpOptions(outputBounds=(ulx, lry, lrx, uly), xRes=resamp_ref_dem.GetXRes(), yRes=resamp_ref_dem.GetYRes(), resampleAlg=resampleAlg)
	out_ds = gdal.Warp('tmp.tif', ds, options=opts)
	return out_ds.GetRasterBand(1).ReadAsArray()


def Resample_Array(orig_dem, resamp_ref_dem, resamp_method='linear'):

	"""
	resample orig_dem using the extent and spacing provided by resamp_ref_dem
	orig_dem: class UtilRaster.SingleRaster object
	resamp_ref_dem: class UtilRaster.SingleRaster object
	returns: an numpy array, which you can use the methods in UtilRaster to trasform it into a raster

	Uses linear interpolation because it best represent flat ice surface.
	-9999.0 (default nan in a Geotiff) is used to fill area outside the extent of orig_dem.

	resamp_method: 'linear', 'cubic', 'quintic', 'nearest'

	"""
	o_ulx, o_uly, o_lrx, o_lry = orig_dem.GetExtent()
	o_ulx, o_xres, o_xskew, o_uly, o_yskew, o_yres = orig_dem.GetGeoTransform()
	orig_dem_extent = Polygon([(o_ulx, o_uly), (o_lrx, o_uly), (o_lrx, o_lry), (o_ulx, o_lry)])
	ulx, uly, lrx, lry = resamp_ref_dem.GetExtent()
	ulx, xres, xskew, uly, yskew, yres = resamp_ref_dem.GetGeoTransform()
	resamp_ref_dem_extent = Polygon([(ulx, uly), (lrx, uly), (lrx, lry), (ulx, lry)])
	if orig_dem_extent.intersects(resamp_ref_dem_extent):
		x = np.linspace(o_ulx, o_lrx - o_xres, orig_dem.GetRasterXSize())
		y = np.linspace(o_uly, o_lry - o_yres, orig_dem.GetRasterYSize())
		z = orig_dem.ReadAsArray()
		# z[z == orig_dem.GetNoDataValue()] = np.nan    # this line probably needs improvement
		if resamp_method == 'nearest':
			print('resampling method = nearest')
			xx, yy = np.meshgrid(x, y)
			points = np.stack((np.reshape(xx, xx.size), np.reshape(yy, yy.size)), axis=-1)
			values = np.reshape(z, z.size)
			fun = NearestNDInterpolator(points, values)
			xnew = np.linspace(ulx, lrx - xres, resamp_ref_dem.GetRasterXSize())
			ynew = np.linspace(uly, lry - yres, resamp_ref_dem.GetRasterYSize())
			xxnew, yynew = np.meshgrid(xnew, ynew)
			znew = fun(xxnew, yynew)    # if the image is big, this may take a long time (much longer than linear approach)
		elif resamp_method == 'linear':
			nan_value = orig_dem.GetNoDataValue()
			print('resampling method = interp2d - ' + resamp_method)
			fun = interp2d(x, y, z, kind=resamp_method, bounds_error=False, copy=False, fill_value=nan_value)
			xnew = np.linspace(ulx, lrx - xres, resamp_ref_dem.GetRasterXSize())
			ynew = np.linspace(uly, lry - yres, resamp_ref_dem.GetRasterYSize())
			znew = np.flipud(fun(xnew, ynew))    # I don't know why, but it seems f(xnew, ynew) is upside down.
			fun2 = interp2d(x, y, z != nan_value, kind=resamp_method, bounds_error=False, copy=False, fill_value=0)
			zmask = np.flipud(fun2(xnew, ynew))
			znew[zmask <= 0.999] = nan_value
		else:
			# This is deprecated...
			print('resampling method = griddata - ' + resamp_method)
			xx, yy = np.meshgrid(x, y)
			xx = xx.ravel()
			yy = yy.ravel()
			zz = z.ravel()
			realdata_pos = zz != orig_dem.GetNoDataValue()
			xx = xx[realdata_pos]
			yy = yy[realdata_pos]
			zz = zz[realdata_pos]
			xnew = np.linspace(ulx, lrx - xres, resamp_ref_dem.GetRasterXSize())
			ynew = np.linspace(uly, lry - yres, resamp_ref_dem.GetRasterYSize())
			znew = griddata((xx, yy), zz, (xnew[None,:], ynew[:,None]), method='linear')
		del z
		gc.collect()
		return znew
	else:
		return np.ones_like(resamp_ref_dem.ReadAsArray()) * -9999.0

def EVMD(y, threshold=6):
	validated_value = None
	if y.size <= 1:
		exitstate = y.size
	else:
		exitstate = 1
		for i in range(y.size - 1):
			comparison = y[i+1:] - y[i]
			if any(abs(comparison) < threshold):
				validated_value = y[i]
				exitstate = -10
				break
			else:
				exitstate += 1
	return exitstate, validated_value

def EVMD_idx(y, validated_value, threshold=6):
	validated_range = [validated_value - threshold, validated_value + threshold]
	idx = np.zeros_like(y, dtype=bool)
	for i in range(y.size):
		if validated_range[0] <= y[i] <= validated_range[1]:
			idx[i] = True
			tmp = np.append(validated_range, [y[i] - threshold, y[i] + threshold])
			validated_range = [min(tmp), max(tmp)]
	return idx

def wlr_corefun(x, y, ye, evmd_threshold=6, detailed=False):
	# wlr = weighted linear regression.
	exitstate, validated_value = EVMD(y, threshold=evmd_threshold)
	if exitstate >= 0 or (max(x) - min(x)) < 1:
		slope, slope_err, resid, count = -9999.0, -9999.0, -9999.0, x.size
		return slope, slope_err, resid, count
	else:
		# if x.size == 3:
		# print(x, y, ye)
		idx = EVMD_idx(y, validated_value, threshold=evmd_threshold)
		if sum(idx) >= 3:
			x = x[idx]
			y = y[idx]
			ye = ye[idx]
			w     = [1 / k for k in ye]
			G     = np.vstack([x, np.ones(x.size)]).T   # defines the model (y = a + bx)
			W     = np.diag(w)
			Gw    = W @ G
			yw    = W @ y.T                          # assuming y is a 1-by-N array
			cov_m =     inv(Gw.T @ Gw)               # covariance matrix
			p     =     inv(Gw.T @ Gw) @ Gw.T @ yw   # model coefficients
			H     = G @ inv(Gw.T @ Gw) @ Gw.T @ W    # projection matrix
			h     = np.diag(H)                       # leverage
			y_est = np.polyval(p, x)                 # the estimate of y
			ri2   = (y - y_est) ** 2
			resid = np.sum(ri2)                      # sum of squared error
			error =  np.sqrt(cov_m[0, 0])
			p_num = 2                                # how many coefficients we want (in this case, 2 comes from y = a + bx)
			mse   = resid / (x.size - p_num)         # mean squared error
			slope = p[0] * 365.25
			slope_err = np.sqrt(cov_m[0, 0]) * 365.25
			count = x.size
			# if resid > 100000:
			# 	print(x,y,ye,cookd,goodpoint)
			if detailed:
				return slope, slope_err, resid, count, x, y, y_est
			else:
				return slope, slope_err, resid, count
		else:
			slope, slope_err, resid, count = -9999.0, -9999.0, -9999.0, x.size
			if detailed:
				return slope, slope_err, resid, count, x, y, y
			else:
				return slope, slope_err, resid, count


		# ============ Using Cook's Distance ============
		# cookd     = ri2 / (p_num * mse) * (h / (1 - h) ** 2)    # Cook's Distance
		# goodpoint = cookd < 4 / x.size                          # Bollen, Kenneth A.; Jackman, Robert W. (1990) (see wikipedia)
		# # xnew = x[goodpoint]
		# # ynew = y[goodpoint]
		# # yenew = ye[goodpoint]
		# # wnew = [1 / k for k in yenew]
		# if np.all(goodpoint):
		# 	slope = p[0] * 365.25
		# 	slope_err = np.sqrt(cov_m[0, 0]) * 365.25
		# 	count = x.size
		# 	if resid > 100000:
		# 		print(x,y,ye,cookd,goodpoint)
		# 	return slope, slope_err, resid, count
		# else:
		# 	xnew = x[goodpoint]
		# 	ynew = y[goodpoint]
		# 	yenew = ye[goodpoint]
		# 	return wlr_corefun(xnew, ynew, yenew)

	# =========== Old function ===========
	# if xnew.size > 4:
	# 	p, c            = np.polyfit(xnew, ynew, 1, w=wnew, cov=True)
	# 	_, res, _, _, _ = np.polyfit(xnew, ynew, 1, w=wnew, full=True)
	# 	residual = np.sum((np.polyval(p, xnew) - ynew) ** 2)
	# 	cov_m = c * (len(w) - 4) / res
	# 	error =  np.sqrt(cov_m[0, 0])
	# 	slope = p[0] * 365.25
	# 	slope_err = np.sqrt(cov_m[0, 0]) * 365.25
	# else:
	# 	error = -9999.0
	# 	slope = -9999.0
	# 	slope_err = -9999.0

	# case = 0
	# w = [1 / k for k in ye]
	# if len(x) == 4:
	# 	case = 1
	# 	# This is to avoid dividing by zero when N = 4 and to give us a better error estimate
	# 	x  = np.append(x,   x[-1])
	# 	y  = np.append(y,   y[-1])
	# 	ye = np.append(ye, ye[-1])
	# 	w  = np.append(w, sys.float_info.epsilon)
	# elif len(x) == 3:
	# 	case = 2
	# 	# This is to avoid negative Cd^2 when N = 3 and to give us a better error estimate
	# 	x  = np.append(x,  [x[-1],  x[-1]])
	# 	y  = np.append(y,  [y[-1],  y[-1]])
	# 	ye = np.append(ye, [ye[-1], ye[-1]])
	# 	w  = np.append(w,  [sys.float_info.epsilon, sys.float_info.epsilon])
	# p, c            = np.polyfit(x, y, 1, w=w, cov=True)
	# _, res, _, _, _ = np.polyfit(x, y, 1, w=w, full=True)
	# # where c is the covariance matrix of p -> c[0, 0] is the variance estimate of the slope.
	# # what we want is ({G_w}^T G_w)^{-1}, which is equal to c * (N - m - 2) / res
	# cov_m = c * (len(w) - 4) / res
	# slope = p[0] * 365.25
	# slope_err = np.sqrt(cov_m[0, 0]) * 365.25
	# # slope_error_arr[m, n] = np.sqrt(c[0, 0]) * 365.25
	# # ./point_TS_ver2-2_linreg.py:^^^^^^^^: RuntimeWarning: invalid value encountered in sqrt
	# # /data/whyj/Software/anaconda3/lib/python3.5/site-packages/numpy/lib/polynomial.py:606: RuntimeWarning: divide by zero encountered in true_divide
	# # fac = resids / (len(x) - order - 2.0)
	# if case == 0:
	# 	residual = np.sum((np.polyval(p, x) - y) ** 2)
	# elif case == 1:
	# 	residual = np.sum((np.polyval(p, x[:-1]) - y[:-1]) ** 2)
	# elif case == 2:
	# 	residual = np.sum((np.polyval(p, x[:-2]) - y[:-2]) ** 2)
	# return slope, slope_err, residual

def onclick_wrapper(data, fig, ax):
	def onclick(event):
	    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
	          ('double' if event.dblclick else 'single', event.button,
	           event.x, event.y, event.xdata, event.ydata))
	    col = int(event.xdata)
	    row = int(event.ydata)
	    xx = np.array(data[row][col]['date'])
	    yy = np.array(data[row][col]['value'])
	    ye = np.array(data[row][col]['uncertainty'])
	    slope, slope_err, residual, count, x_good, y_good, y_goodest = wlr_corefun(xx, yy, ye, evmd_threshold=80, detailed=True)
	    SSReg = np.sum((y_goodest - np.mean(y_good)) ** 2)
	    SSRes = np.sum((y_good - y_goodest) ** 2)
	    SST = np.sum((y_good - np.mean(y_good)) ** 2)
	    Rsquared = 1 - SSRes / SST
	    ax.plot(event.xdata, event.ydata, '.', markersize=10, markeredgewidth=1, markeredgecolor='k', color='xkcd:green')
	    fig.canvas.draw()
	    figi = plt.figure()
	    axi = plt.gca()
	    axi.errorbar(xx, yy, yerr=ye * 2, linewidth=2, fmt='ko')
	    np.set_printoptions(precision=3)
	    np.set_printoptions(suppress=True)
	    xye = np.vstack((xx,yy,ye)).T
	    print(xye[xye[:,1].argsort()])
	    # print(xx)
	    # print(yy)
	    # print(ye)
	    axi.plot(x_good, y_goodest, color='g', linewidth=2, zorder=20)
	    axi.plot(x_good, y_good, '.', color='r', markersize=8, zorder=30)
	    axi.text(0.1, 0.1, 'R^2 = {:.4f}'.format(Rsquared), transform=ax.transAxes)
	    axi.set_xlabel('days, from 2015-01-01')
	    axi.set_ylabel('height (m)')
	    # plt.plot(xx, yy)
	    figi.show()
	return onclick

class PixelTimeSeries(object):
    """
    Store all measurements of a single pixel in the reference DEM.
    Always an n-by-3 array:
    Column 1: date
    Column 2: value
    Column 3: uncertainty
    """
    def __init__(self, data=np.ndarray([0, 3])):
        data = np.array(data) if type(data) is not np.ndarray else data
        self.verify_record(data)
        self.data = data

    def __repr__(self):
        return 'PixelTimeSeries({})'.format(self.data)
    
    @staticmethod
    def verify_record(record):
        """
        Verify if the input record meets the format requirements.
        """
        if record.ndim == 1 and record.size == 3:
            pass
        elif record.ndim == 2 and record.shape[1] == 3:
            pass
        else:
            raise ValueError("Inconsistent input record. Must be an n-by-3 array.")
    
    def add_record(self, record):
        """
        Add one or more records to the time series.
        """
        record = np.array(record) if type(record) is not np.ndarray else record
        self.verify_record(record)
        self.data = np.vstack((self.data, record))
        
    def get_date(self):
        return self.data[:, 0]
    
    def get_value(self):
        return self.data[:, 1]
    
    def get_uncertainty(self):
        return self.data[:, 2]


class DemPile(object):

	"""
	New class in replace of TimeSeriesDEM. It doesn't use nparray for avoiding huge memory consumption.
	Instead, it uses a novel method for stacking all DEMs and saves them as a dict array (which is what 
	is stored in the intermediate pickle file. 
	"""

	def __init__(self, picklepath=None, refgeo=None, refdate=None, dhdtprefix=None):
		self.picklepath = picklepath
		self.dhdtprefix = dhdtprefix
		self.ts = None
		self.dems = []
		self.refdate = None
		if refdate is not None:
			self.refdate = datetime.strptime(refdate, '%Y-%m-%d')
		self.refgeo = refgeo
		self.refgeomask = None
		if refgeo is not None:
			self.refgeomask = refgeo.ReadAsArray().astype(bool)
		self.fitdata = {'slope': [], 'slope_err': [], 'residual': [], 'count': []}
		self.maskparam = {'max_uncertainty': 9999, 'min_time_span': 0}
		self.evmd_threshold = 6

	def AddDEM(self, dems):
		# ==== Add DEM object list ====
		if type(dems) is list:
			self.dems = self.dems + dems
		elif type(dems) is SingleRaster:
			self.dems.append(dems)
		else:
			raise ValueError("This DEM type is neither a SingleRaster object nor a list of SingleRaster objects.")

	def SortByDate(self):
		# ==== sort DEMs by date (ascending order) ====
		dem_dates = [i.date for i in self.dems]
		dateidx = np.argsort(dem_dates)
		self.dems = [self.dems[i] for i in dateidx]

	def SetRefGeo(self, refgeo):
		# ==== Prepare the reference geometry ====
		if type(refgeo) is str:
			self.refgeo = SingleRaster(refgeo)
		elif type(refgeo) is SingleRaster:
			self.refgeo = refgeo
		else:
			raise ValueError("This refgeo must be either a SingleRaster object or a path to a geotiff file.")
		self.refgeomask = self.refgeo.ReadAsArray().astype(bool)

	def SetRefDate(self, datestr):
		self.refdate = datetime.strptime(datestr, '%Y-%m-%d')

	def SetMaskParam(self, ini):
		if 'max_uncertainty' in ini.settings:
			self.maskparam['max_uncertainty'] = float(ini.settings['max_uncertainty'])
		if 'min_time_span' in ini.settings:
			self.maskparam['min_time_span'] = float(ini.settings['min_time_span'])

	def SetEVMDThreshold(self, ini):
		if 'evmd_threshold' in ini.regression:
			self.evmd_threshold = float(ini.regression['evmd_threshold'])

	def InitTS(self):
		# ==== Prepare the reference geometry ====
		refgeo_Ysize = self.refgeo.GetRasterYSize()
		refgeo_Xsize = self.refgeo.GetRasterXSize()
		self.ts = [[{'date': [], 'uncertainty': [], 'value': []} for i in range(refgeo_Xsize)] for j in range(refgeo_Ysize)]
		print('total number of pixels to be processed: {}'.format(np.sum(self.refgeomask)))

	def ReadConfig(self, ini):
		self.picklepath = ini.result['picklefile']
		self.dhdtprefix = ini.result['dhdt_prefix']
		self.AddDEM(ini.GetDEM())
		self.SortByDate()
		self.SetRefGeo(ini.refgeometry['gtiff'])
		self.SetRefDate(ini.settings['refdate'])
		self.SetMaskParam(ini)
		self.SetEVMDThreshold(ini)

	@timeit
	def PileUp(self):
		# ==== Start to read every DEM and save it to our final array ====
		for i in range(len(self.dems)):
			print('{}) {}'.format(i + 1, os.path.basename(self.dems[i].fpath) ))
			if self.dems[i].uncertainty <= self.maskparam['max_uncertainty']:
				datedelta = self.dems[i].date - self.refdate
				# znew = Resample_Array(self.dems[i], self.refgeo, resamp_method='linear')
				znew = Resample_Array2(self.dems[i], self.refgeo)
				znew_mask = np.logical_and(znew > 0, self.refgeomask)
				fill_idx = np.where(znew_mask)
				for m,n in zip(fill_idx[0], fill_idx[1]):
					self.ts[m][n]['date'] += [datedelta.days]
					self.ts[m][n]['uncertainty'] += [self.dems[i].uncertainty]
					self.ts[m][n]['value'] += [znew[m, n]]
			else:
				print("This one won't be piled up because its uncertainty ({}) exceeds the maximum uncertainty allowed ({}).".format(self.dems[i].uncertainty, self.maskparam['max_uncertainty']))

	def DumpPickle(self):
		pickle.dump(self.ts, open(self.picklepath, "wb"))

	def LoadPickle(self):
		self.ts = pickle.load( open(self.picklepath, "rb") )

	@timeit
	def Polyfit(self):
		# ==== Create final array ====
		self.fitdata['slope']     = np.ones_like(self.ts, dtype=float) * -9999
		self.fitdata['slope_err'] = np.ones_like(self.ts, dtype=float) * -9999
		self.fitdata['residual']  = np.ones_like(self.ts, dtype=float) * -9999
		self.fitdata['count']     = np.ones_like(self.ts, dtype=float) * -9999
		# ==== Weighted regression ====
		print('m total: ', len(self.ts))
		for m in range(len(self.ts)):
			# if m < 600:
			# 	continue
			if m % 100 == 0:
				print(m)
			for n in range(len(self.ts[0])):
				# self.fitdata['count'][m, n] = len(self.ts[m][n]['date'])
				# if len(self.ts[m][n]['date']) >= 3:
				date = np.array(self.ts[m][n]['date'])
				uncertainty = np.array(self.ts[m][n]['uncertainty'])
				value = np.array(self.ts[m][n]['value'])
				# pin_value = pin_dem_array[m ,n]
				# pin_date = pin_dem_date_array[m, n]
				# date, uncertainty, value = filter_by_slope(date, uncertainty, value, pin_date, pin_value)
				# date, uncertainty, value = filter_by_redundancy(date, uncertainty, value)

				# slope_ref = [(value[i] - pin_value) / float(date[i] - pin_date) * 365.25 for i in range(len(value))]
				# for i in reversed(range(len(slope_ref))):
				# 	if (slope_ref[i] > dhdt_limit_upper) or (slope_ref[i] < dhdt_limit_lower):
				# 		_ = date.pop(i)
				# 		_ = uncertainty.pop(i)
				# 		_ = value.pop(i)
				# self.fitdata['count'][m, n] = len(date)

				# Whyjay: May 10, 2018: cancelled the min date span (date[-1] - date[0] > 0), previously > 200
				# if (len(np.unique(date)) >= 3) and (date[-1] - date[0] > 0):
				if date.size >= 2 and date[-1] - date[0] > self.maskparam['min_time_span']:
					slope, slope_err, residual, count = wlr_corefun(date, value, uncertainty, self.evmd_threshold)
					# if residual > 100:
					# 	print(date, value, uncertainty)
					self.fitdata['slope'][m, n] = slope
					self.fitdata['slope_err'][m, n] = slope_err
					self.fitdata['residual'][m, n] = residual
					self.fitdata['count'][m, n] = count
				# else:
					# self.fitdata['count'] = len(ref_dem_TS[m][n]['date'])
					# elif (date[-1] - date[0] > 0):
					# 	slope_arr[m, n] = (value[1] - value[0]) / float(date[1] - date[0]) * 365.25
		# self.fitdata['count'][~self.refgeomask] = -9999

	def Fitdata2File(self):
		# ==== Write to file ====
		dhdt_dem = SingleRaster(self.dhdtprefix + '_dhdt.tif')
		dhdt_error = SingleRaster(self.dhdtprefix + '_dhdt_error.tif')
		dhdt_res = SingleRaster(self.dhdtprefix + '_dhdt_residual.tif')
		dhdt_count = SingleRaster(self.dhdtprefix + '_dhdt_count.tif')
		dhdt_dem.Array2Raster(self.fitdata['slope'], self.refgeo)
		dhdt_error.Array2Raster(self.fitdata['slope_err'], self.refgeo)
		dhdt_res.Array2Raster(self.fitdata['residual'], self.refgeo)
		dhdt_count.Array2Raster(self.fitdata['count'], self.refgeo)

	def ShowDhdtTifs(self):
		dhdt_dem = SingleRaster(self.dhdtprefix + '_dhdt.tif')
		dhdt_error = SingleRaster(self.dhdtprefix + '_dhdt_error.tif')
		dhdt_res = SingleRaster(self.dhdtprefix + '_dhdt_residual.tif')
		dhdt_count = SingleRaster(self.dhdtprefix + '_dhdt_count.tif')
		return dhdt_dem, dhdt_error, dhdt_res, dhdt_count



class TimeSeriesDEM(np.ndarray):

	"""
	DEPRECATED IN DHDT v1.0.

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

