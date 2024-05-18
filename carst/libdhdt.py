# Class: PixelTimeSeries, DemPile
# Func: timeit, resample_array, EVMD group, wlr_corefun, onclick_ipynb
# by Whyjay Zheng, Jul 27 2016
# last edit: Apr 23 2023

import numpy as np
from numpy.linalg import inv
import os
# import sys
try:
    from osgeo import gdal
except ImportError:
    import gdal    # this was used until GDAL 3.1
from datetime import datetime, date, timedelta
from shapely.geometry import Polygon
from carst import ConfParams
from carst.libraster import SingleRaster
import pickle
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.cluster import DBSCAN
from rasterio.errors import RasterioIOError
from pathlib import Path

from scipy.optimize import curve_fit
from scipy.signal import argrelextrema
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel
from sklearn.gaussian_process.kernels import RationalQuadratic

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

def resample_array(source, reference, method='bilinear', destination=None):
    """
    latest version. 
    resample the source raster using the extent and spacing provided by the reference raster. Two rasters must be in the same CRS.
    
    source: class UtilRaster.SingleRaster object
    reference: class UtilRaster.SingleRaster object
    destination: str, filename for the output to be written. If None, a temporary file (/vismem/) will be used.
    
    returns: an numpy array, which you can use the methods in UtilRaster to trasform it into a raster.

    For better COG processing efficiency, we rasterio to check the if the source and the reference intersect each other.
    For fasting resampling, we use GDAL and its C library.
    """
    
    s_ulx, s_uly, s_lrx, s_lry = source.get_extent()
    source_extent = Polygon([(s_ulx, s_uly), (s_lrx, s_uly), (s_lrx, s_lry), (s_ulx, s_lry)])
    ulx, uly, lrx, lry = reference.get_extent()
    reference_extent = Polygon([(ulx, uly), (lrx, uly), (lrx, lry), (ulx, lry)])
    if source_extent.intersects(reference_extent):
        ds = gdal.Open(source.fpath)
        opts = gdal.WarpOptions(outputBounds=(ulx, lry, lrx, uly), xRes=reference.get_x_res(), yRes=reference.get_y_res(), resampleAlg=method)
        if not destination:
            out_ds = gdal.Warp('/vsimem/resampled.tif', ds, options=opts)
        else:
            out_ds = gdal.Warp(destination, ds, options=opts)
        return out_ds.GetRasterBand(1).ReadAsArray()
    else:
        return np.full((reference.get_y_size(), reference.get_x_size()), reference.get_nodata())


    
def EVMD_DBSCAN(x, y, eps=6, min_samples=4):
    """
    See EVMD & EVMD_idx.
    Recommended to use this inreplace of EVMD and EVMD_idx.
    verified_y_labels:
        -1: outliers
        0: 1st cluster
        1: 2nd cluster
        ...
    """
    # x, assuming the temporal axis (unit=days), is scaled by 365 for proper eps consideration.
    x2d = np.column_stack((x / 365, y))
    if x2d.shape[0] >= min_samples:
        db = DBSCAN(eps=eps, min_samples=min_samples).fit(x2d)
        # verified_y_labels = db.labels_ >= 0
        verified_y_labels = db.labels_
        # verified_y_labels_idx = np.where(verified_y_labels)
        if any(verified_y_labels >= 0):
            exitstate = 1
        else:
            exitstate = -1
    else:
        exitstate = -1
        # verified_y_labels = np.full_like(y, False)
        verified_y_labels = np.full_like(y, -1)
    return exitstate, verified_y_labels
    
    
def EVMD(y, x=None, threshold=6, method='legacy'):
    """
    Elevation Verification from Multiple DEMs.
    method: 'DBSCAN' or 'legacy'
    """
    if method == 'DBSCAN':
        # x, assuming the temporal axis (unit=days), is scaled by 100 for proper eps consideration.
        x2d = np.coulmn_stack((x / 100, y))
        # min samples is fixed at 4 (i.e., four DEMs together can be considered as a cluster!)
        min_samples = 3
        db = DBSCAN(eps=threshold, min_samples=min_samples).fit(x2d)
        verified_y_labels = db.labels_ >= 0
        verified_y_labels_idx = np.where(verified_y_labels)
        if any(verified_y_labels):
            exitstate = -10
            validated_value = y[verified_y_labels_idx[0]]
            validated_value_idx = verified_y_labels_idx[0]
        else:
            exitstate = 1
            validated_value = None
            validated_value_idx = None
    elif method == 'legacy':
        validated_value = None
        validated_value_idx = None
        if y.size <= 1:
            exitstate = y.size
        else:
            exitstate = 1
            for i in range(y.size - 1):
                comparison = y[i+1:] - y[i]
                if any(abs(comparison) < threshold):
                    validated_value_idx = i
                    validated_value = y[i]
                    exitstate = -10
                    break
                else:
                    exitstate += 1
    else:
        raise ValueError('method must be "DBSCAN" or "legacy".')
    return exitstate, validated_value, validated_value_idx

def EVMD_idx(y, validated_value, threshold=6):
    validated_range = [validated_value - threshold, validated_value + threshold]
    idx = np.zeros_like(y, dtype=bool)
    for i in range(y.size):
        if validated_range[0] <= y[i] <= validated_range[1]:
            idx[i] = True
            tmp = np.append(validated_range, [y[i] - threshold, y[i] + threshold])
            validated_range = [min(tmp), max(tmp)]
    return idx

def wlr_corefun(x, y, ye, evmd_labels=None, evmd_threshold=6, detailed=False, min_samples=4, min_time_span=365):
    """
    # wlr = weighted linear regression.
    # exitstate, validated_value, validated_value_idx = EVMD(y, threshold=evmd_threshold)
    # WARNING issue: count does not represent the same meaning in the following if-else statement!!!

    weighted linear regression ver 1. Kept for backward compatibility.
    """
    if evmd_labels is None:
        exitstate, evmd_labels = EVMD_DBSCAN(x, y, eps=evmd_threshold, min_samples=min_samples)
    else:
        exitstate = 1 if any(evmd_labels >= 0) else -1
        
    idx = evmd_labels >= 0
    # if exitstate >= 0 or (max(x) - min(x)) < 1:
    if exitstate < 0:
        slope, slope_err, resid, count = -9999.0, -9999.0, -9999.0, x.size
        if detailed:
            return slope, slope_err, resid, count, np.array([]), np.array([]), np.array([])
        else:
            return slope, slope_err, resid, count
    else:
        # if x.size == 3:
        # print(x, y, ye)
        # idx = EVMD_idx(y, validated_value, threshold=evmd_threshold)
        if sum(idx) >= 3 and (max(x[idx]) - min(x[idx])) > min_time_span:
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
            #   print(x,y,ye,cookd,goodpoint)
            if detailed:
                return slope, slope_err, resid, count, x, y, y_est
            else:
                return slope, slope_err, resid, count
        else:
            slope, slope_err, resid, count = -9999.0, -9999.0, -9999.0, x.size
            if detailed:
                x = x[idx]
                y = y[idx]
                return slope, slope_err, resid, count, x, y, y
            else:
                return slope, slope_err, resid, count


def wl_reg(xx, yy, ye=None, min_datapoints=4, min_time_span=365):
    """
    weighted linear regression ver 2.
    """
    x_pred_pos = np.linspace(xx.min(), xx.max(), 200)
    duration = (xx.max() - xx.min()) / 365.25
    if xx.size >= min_datapoints and duration > min_time_span / 365.25:
        w     = [1 / k for k in ye]
        G     = np.vstack([xx, np.ones(xx.size)]).T   # defines the model (y = a + bx)
        W     = np.diag(w)
        Gw    = W @ G
        yw    = W @ yy.T                         # assuming y is a 1-by-N array
        cov_m =     inv(Gw.T @ Gw)               # covariance matrix
        p     =     inv(Gw.T @ Gw) @ Gw.T @ yw   # model coefficients
        H     = G @ inv(Gw.T @ Gw) @ Gw.T @ W    # projection matrix
        h     = np.diag(H)                       # leverage
        y_est = np.polyval(p, xx)                # the estimate of y
        ri2   = (yy - y_est) ** 2
        resid = np.sum(ri2)                      # sum of squared error
        error = np.sqrt(cov_m[0, 0])
        p_num = 2                                # how many coefficients we want (in this case, 2 comes from y = a + bx)
        mse   = resid / (xx.size - p_num)         # mean squared error
        slope = p[0] * 365.25
        slope_stderr = np.sqrt(cov_m[0, 0]) * 365.25
        y_prediction = np.polyval(p, x_pred_pos)
        # count = x.size
        # if resid > 100000:
        #   print(x,y,ye,cookd,goodpoint)
        # if detailed:
        #     return slope, slope_err, resid, count, x, y, y_est
        # else:
        #     return slope, slope_err, resid, count
        exitstate = 1
        return x_pred_pos, y_prediction, slope, slope_stderr, duration, exitstate
    else:
        exitstate = -1
        y_prediction = np.full_like(x_pred_pos, np.nan)
        return x_pred_pos, y_prediction, slope, slope_stderr, duration, exitstate
    

def sigmoid_reg(xx, yy, ye=None, k_bounds=None, x0_bounds=None, downward_first=True):
    xx_rescaled = (xx - np.mean(xx)) / np.std(xx)
    yy_rescaled = (yy - np.mean(yy)) / np.std(yy)
    if ye is not None:
        ye_rescaled = ye / np.std(yy)
        absolute_sigma=True
    else:
        ye_rescaled = None
        absolute_sigma=False
    def sigmoid(x, L, k, x0, a1, a0):
        return L / (1 + np.exp(-k * (x - x0))) + a1 * x + a0
    def linear(x, a1, a0):
        return a1 * x + a0

    x_pred_pos_rescaled = np.linspace(xx_rescaled.min(), xx_rescaled.max(), 200)
    x_pred_pos = x_pred_pos_rescaled * np.std(xx) + np.mean(xx)

    if k_bounds is None:
        k_bounds = [1, 150]
    if x0_bounds is None:
        x0_bounds = [xx_rescaled.min(), xx_rescaled.max()]
    downward_sigmoid_bounds = ((-np.inf, k_bounds[0], x0_bounds[0], -np.inf, -np.inf), 
                               (0,       k_bounds[1], x0_bounds[1],  np.inf,  np.inf))
    upward_sigmoid_bounds   = ((0,       k_bounds[0], x0_bounds[0], -np.inf, -np.inf), 
                               (np.inf,  k_bounds[1], x0_bounds[1],  np.inf,  np.inf))
    # downward_sigmoid_p0 = [-1, np.mean(k_bounds), np.mean(x0_bounds), 0, 0]
    # upward_sigmoid_p0   = [ 1, np.mean(k_bounds), np.mean(x0_bounds), 0, 0]
    downward_sigmoid_p0 = [-1, 10, 0, 0, 0]
    upward_sigmoid_p0   = [ 1, 10, 0, 0, 0]
    
    try:
        if downward_first:
            popt, pcov = curve_fit(sigmoid, xx_rescaled, yy_rescaled, sigma=ye_rescaled, p0=downward_sigmoid_p0, 
                                   absolute_sigma=absolute_sigma, bounds=downward_sigmoid_bounds, maxfev=5000)
        else:
            popt, pcov = curve_fit(sigmoid, xx_rescaled, yy_rescaled, sigma=ye_rescaled, p0=upward_sigmoid_p0, 
                                   absolute_sigma=absolute_sigma, bounds=upward_sigmoid_bounds, maxfev=5000)
        # sigmoid_height = popt[0] * np.std(yy)
        sigmoid_height = (popt[0] + (popt[3] * 2 * np.log(99) / popt[1])) * np.std(yy)    # height change between sigmoid component = {0.01L, 0.99L}
        # sigmoid_height_stderr = np.sqrt(pcov[0, 0]) * np.std(yy)
        # error propagation assuming k (sharpness of the sigmoid) is fixed 
        sigmoid_height_stderr = np.sqrt(pcov[0, 0] + pcov[3, 3] * (2 * np.log(99) / popt[1]) ** 2 + 2 * (2 * np.log(99) / popt[1]) * pcov[0, 3]) * np.std(yy)    
        sigmoid_timing = popt[2] * np.std(xx) + np.mean(xx)
        y_prediction_rescaled = sigmoid(x_pred_pos_rescaled, *popt)
        y_prediction = y_prediction_rescaled * np.std(yy) + np.mean(yy)
        exitstate = 1
        # print(popt)
        return x_pred_pos, y_prediction, sigmoid_height, sigmoid_height_stderr, sigmoid_timing, exitstate
    except ValueError:     # "ValueError('array must not contain infs or NaNs')" which seemed to be a bug of curve_fit
        y_prediction_rescaled = np.full_like(x_pred_pos_rescaled, np.nan)
        y_prediction = y_prediction_rescaled
        sigmoid_height = np.nan
        sigmoid_height_stderr = np.nan
        sigmoid_timing = np.nan
        exitstate = -1
        return x_pred_pos, y_prediction, sigmoid_height, sigmoid_height_stderr, sigmoid_timing, exitstate
    except RuntimeError:
        pass

    try:
        if downward_first:
            popt, pcov = curve_fit(sigmoid, xx_rescaled, yy_rescaled, sigma=ye_rescaled, p0=upward_sigmoid_p0, 
                                   absolute_sigma=absolute_sigma, bounds=upward_sigmoid_bounds, maxfev=5000)
        else:
            popt, pcov = curve_fit(sigmoid, xx_rescaled, yy_rescaled, sigma=ye_rescaled, p0=downward_sigmoid_p0, 
                                   absolute_sigma=absolute_sigma, bounds=downward_sigmoid_bounds, maxfev=5000)
        # sigmoid_height = popt[0] * np.std(yy)
        sigmoid_height = (popt[0] + (popt[3] * 2 * np.log(99) / popt[1])) * np.std(yy)    # height change between sigmoid component = {0.01L, 0.99L}
        # sigmoid_height_stderr = np.sqrt(pcov[0, 0]) * np.std(yy)
        # error propagation assuming k (sharpness of the sigmoid) is fixed 
        sigmoid_height_stderr = np.sqrt(pcov[0, 0] + pcov[3, 3] * (2 * np.log(99) / popt[1]) ** 2 + 2 * (2 * np.log(99) / popt[1]) * pcov[0, 3]) * np.std(yy)    
        sigmoid_timing = popt[2] * np.std(xx) + np.mean(xx)
        y_prediction_rescaled = sigmoid(x_pred_pos_rescaled, *popt)
        y_prediction = y_prediction_rescaled * np.std(yy) + np.mean(yy)
        exitstate = 2
        return x_pred_pos, y_prediction, sigmoid_height, sigmoid_height_stderr, sigmoid_timing, exitstate
    except RuntimeError:
        pass

    try:
        popt, pcov = curve_fit(linear, xx_rescaled, yy_rescaled, sigma=ye_rescaled, absolute_sigma=absolute_sigma)
        sigmoid_height = np.nan
        sigmoid_height_stderr = np.nan
        sigmoid_timing = np.nan
        y_prediction_rescaled = linear(x_pred_pos_rescaled, *popt)
        y_prediction = y_prediction_rescaled * np.std(yy) + np.mean(yy)
        exitstate = 3
        return x_pred_pos, y_prediction, sigmoid_height, sigmoid_height_stderr, sigmoid_timing, exitstate
    except RuntimeError:
        y_prediction_rescaled = np.full_like(x_pred_pos_rescaled, np.nan)
        y_prediction = y_prediction_rescaled
        sigmoid_height = np.nan
        sigmoid_height_stderr = np.nan
        sigmoid_timing = np.nan
        exitstate = -1
        return x_pred_pos, y_prediction, sigmoid_height, sigmoid_height_stderr, sigmoid_timing, exitstate


def gp_reg(xx, yy, ye=None, kernel=None, return_ystd=False):
    """
    GP regression ver 2.
    """
    xx_rescaled = (xx - np.mean(xx)) / np.std(xx)
    xx_rescaled = xx_rescaled.reshape(-1, 1)    # to form a vertical vector
    yy_rescaled = (yy - np.mean(yy)) / np.std(yy)
    if ye is not None:
        ye_rescaled = ye / np.std(yy)
        alpha = ye_rescaled ** 2
    else:
        ye_rescaled = None
        alpha = 1e-10    # default value, probably not so good
    if kernel is None:
        kernel = ConstantKernel(constant_value=160, constant_value_bounds='fixed') * RationalQuadratic(
                                length_scale=1.2, alpha=0.1, alpha_bounds='fixed', length_scale_bounds='fixed')

    gaussian_process = GaussianProcessRegressor(kernel=kernel, alpha=alpha, n_restarts_optimizer=5)
    gaussian_process.fit(xx_rescaled, yy_rescaled)


    x_pred_pos_rescaled = np.linspace(xx_rescaled.min(), xx_rescaled.max(), 200).reshape(-1, 1)
    x_pred_pos = x_pred_pos_rescaled * np.std(xx) + np.mean(xx)
    x_pred_pos = x_pred_pos.flatten()
    y_prediction_rescaled, y_prediction_std_rescaled = gaussian_process.predict(x_pred_pos_rescaled, return_std=True)
    y_prediction = y_prediction_rescaled * np.std(yy) + np.mean(yy)
    y_prediction_std = y_prediction_std_rescaled * np.std(yy)

    #########################################
    #### Finding transient height change ####
    #########################################

    localmax_pos = argrelextrema(y_prediction, np.greater)
    localmax_pos = localmax_pos[0]
    
    localmin_pos = argrelextrema(y_prediction, np.less)
    localmin_pos = localmin_pos[0]

    # Add head and tail to the local_pos
    if localmin_pos.any() and localmax_pos.any():
        if localmin_pos[0] < localmax_pos[0]:
            localmax_pos = np.insert(localmax_pos, 0, 0)
        else:
            localmin_pos = np.insert(localmin_pos, 0, 0)
        if localmin_pos[-1] < localmax_pos[-1]:
            localmin_pos = np.append(localmin_pos, y_prediction.size - 1)
        else:
            localmax_pos = np.append(localmax_pos, y_prediction.size - 1)
    elif localmin_pos.any() or localmax_pos.any():
        if localmin_pos:
            localmax_pos = np.insert(localmax_pos, 0, 0)
            localmax_pos = np.append(localmax_pos, y_prediction.size - 1)
        else:
            localmin_pos = np.insert(localmin_pos, 0, 0)
            localmin_pos = np.append(localmin_pos, y_prediction.size - 1)

    # Set up transient event duration
    index_spacing = np.round(730 / (x_pred_pos[1] - x_pred_pos[0]))    # transient duration < 730 days (2 years)
    index_spacing = index_spacing.astype(int)

    # Search all transient events
    maxmin_pairs = []
    for maxpeak_pos in localmax_pos:
        proximity = np.abs(maxpeak_pos - localmin_pos) <=  index_spacing
        if np.any(proximity):
            for minpeak_pos in localmin_pos[proximity]:
                if maxpeak_pos > minpeak_pos:
                    maxmin_pairs.append([minpeak_pos, maxpeak_pos])
                else:
                    maxmin_pairs.append([maxpeak_pos, minpeak_pos])

    # Find the most significant transient events
    if maxmin_pairs:
        dh_list = []
        dh_std_list = [] 
        for pair in maxmin_pairs:
            elev = y_prediction[pair]
            elev_std = y_prediction_std[pair]
            elev_change = elev[1] - elev[0]
            elev_change_std = elev_std[1] + elev_std[0]    # assuming full dependence
            dh_list.append(elev_change)
            dh_std_list.append(elev_change_std)

        max_transient_pos = np.argmin(dh_list)
        max_transient_dh = dh_list[max_transient_pos]
        max_transient_dh_stderr = dh_std_list[max_transient_pos]
        max_transient_timing = x_pred_pos[maxmin_pairs[max_transient_pos][0]]
        exitstate = 1
    else:
        max_transient_dh = np.nan
        max_transient_dh_stderr = np.nan
        max_transient_timing = np.nan
        exitstate = -1

    if return_ystd:
        return x_pred_pos, y_prediction, y_prediction_std, max_transient_dh, max_transient_dh_stderr, max_transient_timing, exitstate, gaussian_process.kernel_
    else:
        return x_pred_pos, y_prediction, max_transient_dh, max_transient_dh_stderr, max_transient_timing, exitstate


def gaussian_process_reg(xx, yy, kernel, alpha=4**2):
    """
    GP regression ver 1. Kept for backward compatibility.
    """
    yy_mean = yy.mean()
    gaussian_process = GaussianProcessRegressor(kernel=kernel, alpha=alpha, n_restarts_optimizer=5)
    gaussian_process.fit(xx, yy - yy_mean)
    x_pred_pos = np.linspace(xx.min(), xx.max(), 200).reshape(-1, 1)
    mean_prediction, std_prediction = gaussian_process.predict(x_pred_pos, return_std=True)
    mean_prediction += yy_mean
    return x_pred_pos, mean_prediction, std_prediction, gaussian_process.kernel_
            
            
class PixelTimeSeries(object):
    """
    Store all measurements of a single pixel in the reference DEM.
    Always an n-by-3 array:
    Column 1: date
    Column 2: value
    Column 3: uncertainty
    Column 4: # of DEM that links to the value (indexed by the input DEM list)
    EVMD labels are also stored in this object.
    Bitmask labels (if any, only for the ArcticDEM data set) are stored in this object.
    """
    def __init__(self, data=[]):
        data = np.ndarray([0, 4]) if not data else data                      # [] --> np.ndarray([0, 4])
        data = np.array(data) if type(data) is not np.ndarray else data      # [1, 2, 3, 4] --> np.array([1, 2, 3, 4])
        self.verify_record(data)
        self._data = data
        self.evmd_labels = None
        self.bitmask_labels = None

    def __repr__(self):
        return 'PixelTimeSeries({})'.format(self._data)
    
    def get_date(self):
        return self._data[:, 0]
    
    def get_value(self):
        return self._data[:, 1]
    
    def get_uncertainty(self):
        return self._data[:, 2]
    
    def get_demno(self):
        return self._data[:, 3]
    
    @staticmethod
    def verify_record(record):
        """
        Verify if the input record meets the format requirements.
        """
        if record.ndim == 1 and record.size == 4:
            pass
        elif record.ndim == 2 and record.shape[1] == 4:
            pass
        else:
            raise ValueError("Inconsistent input record. Must be an n-by-3 array.")
           
    def add_record(self, record):
        """
        Add one or more records to the time series.
        """
        record = np.array(record) if type(record) is not np.ndarray else record
        self.verify_record(record)
        self._data = np.vstack((self._data, record))
        
    def verify_evmd_labels(self, labels):
        """
        Verify if the input EVMD labels meet the format requirements.
        """
        if labels.size == self._data.shape[0]:
            pass
        else:
            raise ValueError("Inconsistent EVMD label input. Must be n labels where n = data points in the data.")
        
    def add_evmd_labels(self, labels):
        labels = np.array(labels) if type(labels) is not np.ndarray else labels
        self.verify_evmd_labels(labels)
        self.evmd_labels = labels
        
    def verify_bitmask_labels(self, labels):
        """
        Verify if the input bitmask labels meet the format requirements.
        """
        if labels.size == self._data.shape[0]:
            pass
        else:
            raise ValueError("Inconsistent bitmask label input. Must be n labels where n = data points in the data.")
            
    def add_bitmask_labels(self, labels):
        labels = np.array(labels) if type(labels) is not np.ndarray else labels
        self.verify_bitmask_labels(labels)
        self.bitmask_labels = labels
        
    def do_evmd(self, eps=6, min_samples=4):
        date = self.get_date()
        value = self.get_value()
        exitstate, labels = EVMD_DBSCAN(date, value, eps=eps, min_samples=min_samples)
        return exitstate, labels
    
    def do_wlr(self, evmd_threshold=6, min_samples=4, min_time_span=365):
        date = self.get_date()
        value = self.get_value()
        uncertainty = self.get_uncertainty()
        evmd_labels = self.evmd_labels
        
        single_results = wlr_corefun(date, value, uncertainty, evmd_labels=evmd_labels, evmd_threshold=evmd_threshold, min_samples=min_samples, min_time_span=min_time_span)
        # single_results is (slope, slope_err, residual, count)
        return single_results


class DemPile(object):

    """
    New class in replace of TimeSeriesDEM. It doesn't use nparray for avoiding huge memory consumption.
    Instead, it uses a novel method for stacking all DEMs and saves them as a dict array (which is what 
    is stored in the intermediate pickle file. 
    """

    def __init__(self, picklepath=None, refgeo=None, refdate=None, dhdtprefix=None, evmd_threshold=6):
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
        self.mosaic = {'value': [], 'date': [], 'uncertainty': []}
        self.maskparam = {'max_uncertainty': 9999, 'min_time_span': 0}
        self.evmd_threshold = evmd_threshold

    def add_dem(self, dems):
        # ==== Add DEM object list ====
        if type(dems) is list:
            self.dems = self.dems + dems
        elif type(dems) is SingleRaster:
            self.dems.append(dems)
        else:
            raise ValueError("This DEM type is neither a SingleRaster object nor a list of SingleRaster objects.")

    def sort_by_date(self):
        # ==== sort DEMs by date (ascending order) ====
        dem_dates = [i.date for i in self.dems]
        dateidx = np.argsort(dem_dates)
        self.dems = [self.dems[i] for i in dateidx]

    def set_refgeo(self, refgeo):
        # ==== Prepare the reference geometry ====
        if type(refgeo) is str:
            self.refgeo = SingleRaster(refgeo)
        elif type(refgeo) is SingleRaster:
            self.refgeo = refgeo
        else:
            raise ValueError("This refgeo must be either a SingleRaster object or a path to a geotiff file.")
        self.refgeomask = self.refgeo.ReadAsArray().astype(bool)

    def set_refdate(self, datestr):
        self.refdate = datetime.strptime(datestr, '%Y-%m-%d')

    def set_mask_params(self, ini):
        if 'max_uncertainty' in ini.settings:
            self.maskparam['max_uncertainty'] = float(ini.settings['max_uncertainty'])
        if 'min_time_span' in ini.settings:
            self.maskparam['min_time_span'] = float(ini.settings['min_time_span'])

    def set_evmd_threshold(self, ini):
        if 'evmd_threshold' in ini.regression:
            self.evmd_threshold = float(ini.regression['evmd_threshold'])

    def init_ts(self):
        # ==== Prepare the reference geometry ====
        refgeo_Ysize = self.refgeo.get_y_size()
        refgeo_Xsize = self.refgeo.get_x_size()
        self.ts = np.empty([refgeo_Ysize, refgeo_Xsize], dtype=object)
        # for j in range(self.ts.shape[0]):
        #     for i in range(self.ts.shape[1]):
        #         self.ts[j, i] = PixelTimeSeries()
        # self.ts = [[{'date': [], 'uncertainty': [], 'value': []} for i in range(refgeo_Xsize)] for j in range(refgeo_Ysize)]
        # self.ts = [[ [] for i in range(refgeo_Xsize)] for j in range(refgeo_Ysize)]
        print('total number of pixels to be processed: {}'.format(np.sum(self.refgeomask)))
        
    def read_config(self, ini):
        if type(ini) is str:
            ini = ConfParams(ini)
            ini.ReadParam()
            ini.VerifyParam()
        self.picklepath = ini.result['picklefile']
        self.dhdtprefix = ini.result['dhdt_prefix']
        self.add_dem(ini.GetDEM())
        self.sort_by_date()
        self.set_refgeo(ini.refgeometry['gtiff'])
        self.set_refdate(ini.settings['refdate'])
        self.set_mask_params(ini)
        self.set_evmd_threshold(ini)

    @timeit
    def pileup(self, bitmask=False):
        # ==== Start to read every DEM and save it to our final array ====
        ts = [[ [] for n in range(self.ts.shape[1])] for m in range(self.ts.shape[0])]
        if bitmask:
            ts_bitmask = [[ [] for n in range(self.ts.shape[1])] for m in range(self.ts.shape[0])]
        
        for i in range(len(self.dems)):
            print('{}) {}'.format(i + 1, os.path.basename(self.dems[i].fpath) ))
            if self.dems[i].uncertainty <= self.maskparam['max_uncertainty']:
                datedelta = self.dems[i].date - self.refdate
                try:
                    znew = resample_array(self.dems[i], self.refgeo, method='bilinear')
                except RasterioIOError as inst:    # To show and skip the error of a bad url
                    print(inst)
                    continue
                if bitmask:
                    bitmask_fpath = self.dems[i].fpath.replace('dem.tif', 'bitmask.tif')
                    bitmask_dem = SingleRaster(bitmask_fpath)
                    bitmask_znew = resample_array(bitmask_dem, self.refgeo, method='nearest')
                
                ### Attempt to remove the znew > 0 constraint (failed for now; there is a lot of -9999 points) 
                # znew_mask = self.refgeomask
                znew_mask = np.logical_and(znew > 0, self.refgeomask)
                fill_idx = np.where(znew_mask)
                for m,n in zip(fill_idx[0], fill_idx[1]):
                    record = [datedelta.days, znew[m, n], self.dems[i].uncertainty, i]
                    ts[m][n] += [record]
                    if bitmask:
                        record_bitmask = bitmask_znew[m, n]
                        ts_bitmask[m][n] += [record_bitmask]

            else:
                print("This one won't be piled up because its uncertainty ({}) exceeds the maximum uncertainty allowed ({})."
                      .format(self.dems[i].uncertainty, self.maskparam['max_uncertainty']))
                
        # After the content of ts is all populated, we move the data to self.ts as an array of PixelTimeSeries.
        for m in range(self.ts.shape[0]):
            for n in range(self.ts.shape[1]):
                self.ts[m, n] = PixelTimeSeries(ts[m][n])
                if bitmask: 
                    self.ts[m, n].add_bitmask_labels(ts_bitmask[m][n])
                
    def dump_pickle(self):
        pickle.dump(self.ts, open(self.picklepath, "wb"))

    def load_pickle(self):
        self.ts = pickle.load( open(self.picklepath, "rb") )
        
    def init_fitdata(self):
        # ==== Create final array ====
        self.fitdata['slope']     = np.full_like(self.ts, self.refgeo.get_nodata(), dtype=float)
        self.fitdata['slope_err'] = np.full_like(self.ts, self.refgeo.get_nodata(), dtype=float)
        self.fitdata['residual']  = np.full_like(self.ts, self.refgeo.get_nodata(), dtype=float)
        self.fitdata['count']     = np.full_like(self.ts, self.refgeo.get_nodata(), dtype=float)
        
    def init_mosaic(self):
        self.mosaic['value']      = np.full_like(self.ts, self.refgeo.get_nodata(), dtype=float)
        self.mosaic['date']       = np.full_like(self.ts, self.refgeo.get_nodata(), dtype=float)
        self.mosaic['uncertainty']= np.full_like(self.ts, self.refgeo.get_nodata(), dtype=float)
        
    @timeit
    def polyfit(self, parallel=False, chunksize=(1000, 1000), min_samples=4):
        # ==== Create final array ====
        self.init_fitdata()
        # ==== Weighted regression ====
        if parallel:
            import dask
            from dask.diagnostics import ProgressBar
            def batch(seq, min_time_span, evmd_threshold, nodata, min_samples):
                sub_results = []
                for x in seq:
                    date = x.get_date()
                    if date.size >= 2 and date[-1] - date[0] > min_time_span:
                        single_results = x.do_wlr(evmd_threshold=evmd_threshold, min_samples=min_samples)
                        # single_results is (slope, slope_err, residual, count)
                    else:
                        single_results = (nodata, nodata, nodata, nodata)
                    sub_results.append(single_results)
                return sub_results
            
            if self.ts.shape[0] <= chunksize[0] and self.ts.shape[1] <= chunksize[1]:
                ### Single chunk
                batches = []
                for m in range(self.ts.shape[0]):
                    result_batch = dask.delayed(batch)(self.ts[m, :], self.maskparam['min_time_span'], self.evmd_threshold, self.refgeo.get_nodata(), min_samples)
                    batches.append(result_batch)

                with ProgressBar():
                    results = dask.compute(batches)

                for m in range(self.ts.shape[0]):
                    for n in range(self.ts.shape[1]):
                        self.fitdata['slope'][m, n] = results[0][m][n][0]
                        self.fitdata['slope_err'][m, n] = results[0][m][n][1]
                        self.fitdata['residual'][m, n] = results[0][m][n][2]
                        self.fitdata['count'][m, n] = results[0][m][n][3]
                        
            else:
                ### Multiple chunks
                msize = chunksize[0]
                nsize = chunksize[1]
                m_nodes = np.arange(0, self.ts.shape[0], msize)
                n_nodes = np.arange(0, self.ts.shape[1], nsize)
                super_results = []
                for super_m in range(m_nodes.size):
                    self.display_progress(m_nodes[super_m], self.ts.shape[0])
                    batches = []
                    ts_slice = self.ts[m_nodes[super_m]:m_nodes[super_m]+msize, :]
                    for m in range(ts_slice.shape[0]):
                        for n in range(n_nodes.size):
                            result_batch = dask.delayed(batch)(ts_slice[m, n_nodes[n]:n_nodes[n]+nsize ], self.maskparam['min_time_span'], self.evmd_threshold, self.refgeo.get_nodata(), min_samples)
                            batches.append(result_batch)
                            
                    with ProgressBar():
                        results = dask.compute(batches)
                    super_results.append(results[0])

                for m in range(self.ts.shape[0]):
                    for n in range(self.ts.shape[1]):
                        idx1 = m // msize
                        idx2 = n_nodes.size * (m % msize) + n // nsize
                        idx3 = n % nsize
                        self.fitdata['slope'][m, n] = super_results[idx1][idx2][idx3][0]
                        self.fitdata['slope_err'][m, n] = super_results[idx1][idx2][idx3][1]
                        self.fitdata['residual'][m, n] = super_results[idx1][idx2][idx3][2]
                        self.fitdata['count'][m, n] = super_results[idx1][idx2][idx3][3]
                

        else:
            for m in range(self.ts.shape[0]):
                self.display_progress(m, self.ts.shape[0])
                for n in range(self.ts.shape[1]):
                    date = self.ts[m, n].get_date()
                    # uncertainty = self.ts[m, n].get_uncertainty()
                    # value = self.ts[m, n].get_value()
                    # evmd_labels = self.ts[m, n].evmd_labels

                    if date.size >= 2 and date[-1] - date[0] > self.maskparam['min_time_span']:
                        slope, slope_err, residual, count = self.ts[m, n].do_wlr(evmd_threshold=self.evmd_threshold, min_samples=min_samples, min_time_span=self.maskparam['min_time_span'])
                        # if residual > 100:
                        #    print(date, value, uncertainty)
                        self.fitdata['slope'][m, n] = slope
                        self.fitdata['slope_err'][m, n] = slope_err
                        self.fitdata['residual'][m, n] = residual
                        self.fitdata['count'][m, n] = count

    def fitdata2file(self):
        # ==== Write to file ====
        dhdt_dem = SingleRaster(self.dhdtprefix + '_dhdt.tif')
        dhdt_error = SingleRaster(self.dhdtprefix + '_dhdt_error.tif')
        dhdt_res = SingleRaster(self.dhdtprefix + '_dhdt_residual.tif')
        dhdt_count = SingleRaster(self.dhdtprefix + '_dhdt_count.tif')
        dhdt_dem.Array2Raster(self.fitdata['slope'], self.refgeo)
        dhdt_error.Array2Raster(self.fitdata['slope_err'], self.refgeo)
        dhdt_res.Array2Raster(self.fitdata['residual'], self.refgeo)
        dhdt_count.Array2Raster(self.fitdata['count'], self.refgeo)

    def show_dhdt_tifs(self):
        dhdt_dem = SingleRaster(self.dhdtprefix + '_dhdt.tif')
        dhdt_error = SingleRaster(self.dhdtprefix + '_dhdt_error.tif')
        dhdt_res = SingleRaster(self.dhdtprefix + '_dhdt_residual.tif')
        dhdt_count = SingleRaster(self.dhdtprefix + '_dhdt_count.tif')
        return dhdt_dem, dhdt_error, dhdt_res, dhdt_count
    
    @timeit
    def form_mosaic(self, order='ascending', method='DBSCAN', parallel=False, min_samples=4):
        """
        order options:
            ascending: early elevations will be populated first
            descending: late elevations will be populated first
        method: 'DBSCAN' or 'legacy'
        """
        # ==== Create mosaicked array ====
        self.init_mosaic()
        if method == 'DBSCAN' and self.ts[0, 0].evmd_labels is None:
            print('No EVMD labels detected. Run do_evmd first.')
            self.do_evmd(parallel=parallel, min_samples=min_samples)
        for m in range(self.ts.shape[0]):
            self.display_progress(m, self.ts.shape[0])
            for n in range(self.ts.shape[1]):
                date = self.ts[m, n].get_date()
                uncertainty = self.ts[m, n].get_uncertainty()
                value = self.ts[m, n].get_value()
                if method == 'DBSCAN':
                    labels = self.ts[m, n].evmd_labels
                    if any(labels >= 0):
                        verified_y_labels_idx = np.where(labels >= 0)[0]
                        if order == 'descending':
                            idx = verified_y_labels_idx[-1]
                        elif order == 'ascending':
                            idx = verified_y_labels_idx[0]
                        else:
                            raise ValueError('order must be "ascending" or "descending".')
                        self.mosaic['value'][m, n] = value[idx]
                        self.mosaic['date'][m, n] = date[idx]
                        self.mosaic['uncertainty'][m, n] = uncertainty[idx]
                elif method == 'legacy':
                    if order == 'descending':
                        date = np.flip(date)
                        uncertainty = np.flip(uncertainty)
                        value = np.flip(value)
                    elif order != 'ascending':
                        raise ValueError('order must be "ascending" or "descending".')
                    exitstate, validated_value, validated_value_idx = EVMD(value, threshold=self.evmd_threshold)
                    if exitstate < 0:
                        self.mosaic['value'][m, n] = validated_value
                        self.mosaic['date'][m, n] = date[validated_value_idx]
                        self.mosaic['uncertainty'][m, n] = uncertainty[validated_value_idx]
                else:
                    raise ValueError('method must be "DBSCAN" or "legacy".')
        mosaic_value       = SingleRaster('{}_mosaic-{}_value.tif'.format(self.dhdtprefix, order))
        mosaic_date        = SingleRaster('{}_mosaic-{}_date.tif'.format(self.dhdtprefix, order))
        mosaic_uncertainty = SingleRaster('{}_mosaic-{}_uncertainty.tif'.format(self.dhdtprefix, order))
        mosaic_value.Array2Raster(self.mosaic['value'], self.refgeo)
        mosaic_date.Array2Raster(self.mosaic['date'], self.refgeo)
        mosaic_uncertainty.Array2Raster(self.mosaic['uncertainty'], self.refgeo)
        
    @timeit
    def do_evmd(self, parallel=False, chunksize=(1000, 1000), min_samples=4, use_bitmask=False):
        if parallel:
            import dask
            from dask.diagnostics import ProgressBar
            def batch(seq, evmd_threshold, min_samples):
                sub_results = []
                for x in seq:
                    exitstate, labels = x.do_evmd(eps=evmd_threshold, min_samples=min_samples)
                    sub_results.append(labels)
                return sub_results
            
            if self.ts.shape[0] <= chunksize[0] and self.ts.shape[1] <= chunksize[1]:
                ### Single chunk
                batches = []
                for m in range(self.ts.shape[0]):
                    result_batch = dask.delayed(batch)(self.ts[m, :], self.evmd_threshold, min_samples)
                    batches.append(result_batch)

                with ProgressBar():
                    results = dask.compute(batches)

                for m in range(self.ts.shape[0]):
                    for n in range(self.ts.shape[1]):
                        if use_bitmask:
                            bitmask_lbl = self.ts[m, n].bitmask_labels
                            new_evmd_lbl = [0 if i >=0 and j == 0 else -1 for i, j in zip(results[0][m][n], bitmask_lbl)]
                            self.ts[m, n].add_evmd_labels(new_evmd_lbl)
                        else:
                            self.ts[m, n].add_evmd_labels(results[0][m][n])

            else:
                ### Multile chunks
                msize = chunksize[0]
                nsize = chunksize[1]
                m_nodes = np.arange(0, self.ts.shape[0], msize)
                n_nodes = np.arange(0, self.ts.shape[1], nsize)
                super_results = []
                for super_m in range(m_nodes.size):
                    self.display_progress(m_nodes[super_m], self.ts.shape[0])
                    batches = []
                    ts_slice = self.ts[m_nodes[super_m]:m_nodes[super_m]+msize, :]
                    for m in range(ts_slice.shape[0]):
                        for n in range(n_nodes.size):
                            result_batch = dask.delayed(batch)(ts_slice[m, n_nodes[n]:n_nodes[n]+nsize ], self.evmd_threshold, min_samples)
                            batches.append(result_batch)
                            
                    with ProgressBar():
                        results = dask.compute(batches)
                    super_results.append(results[0])

                for m in range(self.ts.shape[0]):
                    for n in range(self.ts.shape[1]):
                        idx1 = m // msize
                        idx2 = n_nodes.size * (m % msize) + n // nsize
                        idx3 = n % nsize
                        evmd_lbl = super_results[idx1][idx2][idx3]
                        if use_bitmask:
                            bitmask_lbl = self.ts[m, n].bitmask_labels
                            new_evmd_lbl = [0 if i >=0 and j == 0 else -1 for i, j in zip(evmd_lbl, bitmask_lbl)]
                            self.ts[m, n].add_evmd_labels(new_evmd_lbl)
                        else:
                            self.ts[m, n].add_evmd_labels(evmd_lbl)
        else:
            for m in range(self.ts.shape[0]):
                self.display_progress(m, self.ts.shape[0])
                for n in range(self.ts.shape[1]):
                    exitstate, evmd_lbl = self.ts[m, n].do_evmd(eps=self.evmd_threshold, min_samples=min_samples)
                    if use_bitmask:
                        bitmask_lbl = self.ts[m, n].bitmask_labels
                        new_evmd_lbl = [0 if i >=0 and j == 0 else -1 for i, j in zip(evmd_lbl, bitmask_lbl)]
                        self.ts[m, n].add_evmd_labels(new_evmd_lbl)
                    else:
                        self.ts[m, n].add_evmd_labels(evmd_lbl)
                    
                
    @staticmethod                
    def display_progress(m, total):
        if m % 100 == 0:
            print(f'{m}/{total} lines processed')
    
    def viz(self, figsize=(8,8), clim=(-6, 6), evmd_threshold=8, min_samples=4, reg_method='linear', gp_kernel=None, k_bounds=[10, 150], downward_first=True,
            use_bitmask_only=False, use_evmd_only=True, use_matrix_alpha=False):
        dhdt_raster, _, _, _ = self.show_dhdt_tifs()
        dhdt_raster_path = Path(dhdt_raster.fpath)
        
        fig, axs = plt.subplots(2, 1, figsize=figsize)
        
        if dhdt_raster_path.is_file():
            print(f'Showing {dhdt_raster.fpath} as a basemap') 
            nodata = dhdt_raster.get_nodata()
            img = dhdt_raster.ReadAsArray()
            img[img == nodata] = np.nan
            first_img = axs[0].imshow(img, cmap='RdBu', vmin=clim[0], vmax=clim[1])
        else:
            print(f'{dhdt_raster.fpath} not found; using topography as a basemap.')
            quick_topography_path = Path(self.dhdtprefix + '_median_topo.tif')
            if quick_topography_path.is_file():
                quick_topography = SingleRaster(quick_topography_path.as_posix())
                nodata = quick_topography.get_nodata()
                img = quick_topography.ReadAsArray()
                img[img == nodata] = np.nan
                first_img = axs[0].imshow(img, cmap='gist_earth')
            else:
                get_median_elev = lambda n: np.median(n.get_value())
                vfunc = np.vectorize(get_median_elev)
                img = vfunc(self.ts)
                quick_topography = SingleRaster(quick_topography_path.as_posix())
                quick_topography.Array2Raster(img, self.refgeo)
                first_img = axs[0].imshow(img, cmap='gist_earth')
        if gp_kernel is None:
            onclick = onclick_wrapper(self.ts, axs, self.refdate, evmd_threshold=evmd_threshold, min_samples=min_samples, reg_method=reg_method, 
                                      k_bounds=k_bounds, downward_first=downward_first,
                                      use_bitmask_only=use_bitmask_only, use_evmd_only=use_evmd_only, use_matrix_alpha=use_matrix_alpha)
        else:
            onclick = onclick_wrapper(self.ts, axs, self.refdate, evmd_threshold=evmd_threshold, min_samples=min_samples, reg_method=reg_method, 
                                      gp_kernel=gp_kernel, use_bitmask_only=use_bitmask_only, use_evmd_only=use_evmd_only, use_matrix_alpha=use_matrix_alpha)
        # onclick = onclick_wrapper(self.ts, axs, self.evmd_threshold, min_samples=min_samples, reg_method=reg_method, use_bitmask_only=use_bitmask_only)
        cid = fig.canvas.mpl_connect('button_press_event', onclick)
    
def onclick_wrapper(data, axs, refdate, evmd_threshold=8, min_samples=4, reg_method='linear', k_bounds=[10, 150], downward_first=True,
                    use_bitmask_only=False, use_evmd_only=True, use_matrix_alpha=False,
                    gp_kernel = ConstantKernel(constant_value=160, constant_value_bounds='fixed') * RationalQuadratic(
                       length_scale=1.2, alpha=0.1, alpha_bounds='fixed', length_scale_bounds='fixed')):
    def onclick_ipynb(event):
        """
        Callback function for mouse click
        """
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))     # only works for non-Notebook backend?
        if event.inaxes is axs[0]:
            col = int(event.xdata)
            row = int(event.ydata)
            xx = data[row, col].get_date()
            yy = data[row, col].get_value()
            ye = data[row, col].get_uncertainty()
            
            if use_bitmask_only:
                bitmask_lbl = data[row, col].bitmask_labels
                good_idx = bitmask_lbl == 0
            else:
                if data[row, col].evmd_labels is None:
                    exitstate, evmd_lbl = data[row, col].do_evmd(eps=evmd_threshold, min_samples=min_samples)
                else:
                    evmd_lbl = data[row, col].evmd_labels
                if use_evmd_only:
                    good_idx = evmd_lbl >= 0
                else:
                    bitmask_lbl = data[row, col].bitmask_labels
                    good_idx = np.logical_and(bitmask_lbl == 0, evmd_lbl >= 0)
            
            axs[0].plot(event.xdata, event.ydata, '.', markersize=10, markeredgewidth=1, markeredgecolor='k', color='xkcd:green')
            axs[1].cla()
            xx_date = np.array([refdate + timedelta(days=i) for i in xx])
            axs[1].errorbar(xx_date, yy, yerr=ye * 2, linewidth=2, fmt='k.')
            # axs[1].errorbar(xx, yy, yerr=ye * 2, linewidth=2, fmt='k.')
            np.set_printoptions(precision=3)
            np.set_printoptions(suppress=True)
            
            if reg_method == 'gp':

                xx_good = xx[good_idx]
                yy_good = yy[good_idx]
                ye_good = ye[good_idx]
                
                x_pred_pos, y_prediction, y_prediction_std, max_transient_dh, max_transient_dh_stderr, max_transient_timing, exitstate, actual_kernel = gp_reg(
                    xx_good, yy_good, ye=ye_good, kernel=gp_kernel, return_ystd=True)

                axs[1].set_title(str(actual_kernel))
                x_pred_pos_date = [refdate + timedelta(days=i) for i in x_pred_pos]
                axs[1].plot(x_pred_pos_date, y_prediction, color='g', linewidth=2, zorder=20)
                xx_good_date = [refdate + timedelta(days=i) for i in xx_good]
                axs[1].plot(xx_good_date, yy_good, 's', color='k', markersize=7, zorder=5)
                # x_pred_pos_date = [refdate + timedelta(days=i) for i in x_pred_pos.ravel()]
                axs[1].fill_between(
                    x_pred_pos_date,
                    y_prediction - 1.96 * y_prediction_std,
                    y_prediction + 1.96 * y_prediction_std,
                    alpha=0.5,
                    label=r"95% confidence interval",
                    zorder=2,
                    color='xkcd:seafoam'
                    )
            
                # xx_gp = xx[good_idx]
                # yy_gp = yy[good_idx]
                # ye_gp = ye[good_idx]
                # xx_gp_yr = xx_gp / 365
                # xx_gp_yr = xx_gp_yr.reshape(-1, 1)
                # if use_matrix_alpha:
                #     alpha = ye_gp ** 2
                # else:
                #     alpha = np.median(ye_gp) ** 2
                # x_pred_pos, mean_prediction, std_prediction, optimized_kernel = gaussian_process_reg(xx_gp_yr, yy_gp, kernel=gp_kernel, alpha=alpha)
                # x_pred_pos *= 365
                # axs[1].set_title(str(gp_kernel))
                # x_pred_pos_date = [refdate + timedelta(days=i) for i in x_pred_pos.flatten()]
                # axs[1].plot(x_pred_pos_date, mean_prediction, color='g', linewidth=2, zorder=20)
                # xx_gp_date = [refdate + timedelta(days=i) for i in xx_gp]
                # axs[1].plot(xx_gp_date, yy_gp, 's', color='k', markersize=7, zorder=5)
                # x_pred_pos_date = [refdate + timedelta(days=i) for i in x_pred_pos.ravel()]
                # axs[1].fill_between(
                #     x_pred_pos_date,
                #     mean_prediction - 1.96 * std_prediction,
                #     mean_prediction + 1.96 * std_prediction,
                #     alpha=0.5,
                #     label=r"95% confidence interval",
                #     zorder=2,
                #     color='xkcd:seafoam'
                #     )

                
            elif reg_method == 'sigmoid':
                
                xx_good = xx[good_idx]
                yy_good = yy[good_idx]
                ye_good = ye[good_idx]
                
                x_pred, y_pred, sigmoid_height, sigmoid_height_stderr, sigmoid_timing, exitstate = sigmoid_reg(
                    xx_good, yy_good, ye=ye_good, k_bounds=k_bounds, downward_first=downward_first)
                axs[1].set_title(f'Sigmoid height (2-sigma) = {sigmoid_height:.2f}±{2 * sigmoid_height_stderr:.2f}' )
                x_pred_date = [refdate + timedelta(days=i) for i in x_pred]
                axs[1].plot(x_pred_date, y_pred, color='g', linewidth=2, zorder=20)
                xx_good_date = [refdate + timedelta(days=i) for i in xx_good]
                axs[1].plot(xx_good_date, yy_good, 's', color='k', markersize=7, zorder=5)
                if not np.isnan(sigmoid_timing):
                    axs[1].axvline(refdate + timedelta(days=sigmoid_timing), linestyle='--', color='xkcd:teal')
                
            elif reg_method == 'linear':
                # bitmask labels --> not implemented yet
                # evmd labels --> ok

                xx_good = xx[good_idx]
                yy_good = yy[good_idx]
                ye_good = ye[good_idx]
                x_pred, y_pred, slope, slope_stderr, duration, exitstate = wl_reg(xx_good, yy_good, ye=ye_good)
                axs[1].set_title(f'dh/dt (2-sigma) = {slope:.2f}±{2 * slope_stderr:.2f} m/yr' )
                x_pred_date = [refdate + timedelta(days=i) for i in x_pred]
                axs[1].plot(x_pred_date, y_pred, color='g', linewidth=2, zorder=20)
                xx_good_date = [refdate + timedelta(days=i) for i in xx_good]
                axs[1].plot(xx_good_date, yy_good, 's', color='k', markersize=7, zorder=5)
                
                # slope, slope_err, residual, count, x_good, y_good, y_goodest = wlr_corefun(
                #     xx, yy, ye, evmd_labels=evmd_lbl, evmd_threshold=evmd_threshold, min_samples=min_samples, detailed=True)
                # SSReg = np.sum((y_goodest - np.mean(y_good)) ** 2)
                # SSRes = np.sum((y_good - y_goodest) ** 2)
                # SST = np.sum((y_good - np.mean(y_good)) ** 2)
                # Rsquared = 1 - SSRes / SST
                # x_good_date = [refdate + timedelta(days=i) for i in x_good]
                # axs[1].plot(x_good_date, y_goodest, color='g', linewidth=2, zorder=20)
                # axs[1].plot(x_good_date, y_good, 's', color='k', markersize=7, zorder=5)
                
            # xye = np.vstack((xx,yy,ye)).T
            # print(xye[xye[:,1].argsort()])

            # axs[1].text(0.1, 0.1, 'R^2 = {:.4f}'.format(Rsquared), transform=ax.transAxes)
            bitmask_index = data[row, col].bitmask_labels
            if bitmask_index is not None:
                bitmask_colorcodes = ['xkcd:lilac', 'xkcd:gray', 'xkcd:light blue',  'xkcd:blue', 
                                      'xkcd:light yellow',  'xkcd:yellow', 'xkcd:gold', 'xkcd:brown']
                bitmask_comments = ['Good', 'Edge', 'Water', 'Water+Edge',              
                                    'Cloud', 'Cloud+Edge', 'Cloud+Water', 'Cloud+Edge+Water']
                for selected_bit, colorcode in zip([0, 1, 2, 3, 4, 5, 6, 7], bitmask_colorcodes):
                    selected_group_index = bitmask_index == selected_bit
                    axs[1].plot(xx_date[selected_group_index], yy[selected_group_index], '.', color=colorcode, 
                                markersize=12, markeredgewidth=1, markeredgecolor='k', zorder=selected_bit + 10)
                    # axs[1].plot(xx[selected_group_index], yy[selected_group_index], '.', color=colorcode, 
                    #             markersize=12, markeredgewidth=1, markeredgecolor='k', zorder=selected_bit + 10)
            else:
                axs[1].plot(xx_date, yy, '.', color='xkcd:light grey', 
                            markersize=12, markeredgewidth=1, markeredgecolor='k', zorder=10)
                # axs[1].plot(xx, yy, '.', color='xkcd:light grey', 
                #             markersize=12, markeredgewidth=1, markeredgecolor='k', zorder=10)

            axs[1].xaxis.set_major_locator(mdates.YearLocator())
            axs[1].xaxis.set_minor_locator(mdates.MonthLocator())
            plt.setp(axs[1].get_xticklabels(), rotation=-30, ha='left')
            axs[1].grid(axis='x', linestyle='--', color='xkcd:light grey')
            axs[1].set_xlabel('data[{}, {}]'.format(row, col))
            axs[1].set_ylabel('height (m)')
    return onclick_ipynb




