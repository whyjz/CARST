#!/usr/bin/env python
#
# Main dh/dt script
# by Whyjay Zheng, Jul 27 2016
# last edit: Aug 17 2016
# Major rehaul: May 4, 2018
# modified from the workflow of the FJL paper (Zheng et al, 2018)
#
# usage: python dhdt.py config_file
#
# try: 
#    python dhdt.py defaults.ini 
# for testing session.
#
# complete readme is at CARST/Doc/dhdt/README.rst

from argparse import ArgumentParser
import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(sys.argv[0])) + '/../Utilities/Python')        # for all modules
from UtilRaster import SingleRaster
from UtilConfig import ConfParams
from UtilFit import TimeSeriesDEM
from UtilFit import Resample_Array
from datetime import datetime
import pickle

parser = ArgumentParser()
parser.add_argument('config_file', help='Configuration file')
parser.add_argument('-s', '--step', help='Do a single stpe', dest='step')
args = parser.parse_args()

# ==== Read ini file ====

inipath = args.config_file
ini = ConfParams(inipath)
ini.ReadParam()
ini.VerifyParam()

def TSpickle(ini):
	# ==== Get DEM object list ====
	demlist = ini.GetDEM()

	time_a = datetime.now()
	print('Program Start: {}'.format(time_a.strftime('%Y-%m-%d %H:%M:%S')))

	# ==== sort DEMs by date (ascending order) ====

	dem_dates = [i.date for i in demlist]
	dateidx = np.argsort(dem_dates)
	demlist = [demlist[i] for i in dateidx]

	# ==== Prepare the reference geometry ====

	refgeo = SingleRaster(ini.refgeometry['gtiff'])
	refgeo_array = refgeo.ReadAsArray().astype(bool)
	refgeo_Ysize = refgeo.GetRasterYSize()
	refgeo_Xsize = refgeo.GetRasterXSize()
	refgeo_TS = [[{'date': [], 'uncertainty': [], 'value': []} for i in range(refgeo_Xsize)] for j in range(refgeo_Ysize)]

	pix_num = np.sum(refgeo_array)
	print('total number of pixels to be processed: {}'.format(pix_num))

	# ==== Start to read every DEM and save it to our final array ====

	for i in range(len(demlist)):
		print('{}) {}'.format(i + 1, os.path.basename(demlist[i].fpath) ))
		datedelta = demlist[i].date - datetime.strptime(ini.settings['refdate'], '%Y-%m-%d')
		znew = Resample_Array(demlist[i], refgeo)
		znew_mask = np.logical_and(znew > 0, refgeo_array)

		fill_idx = np.where(znew_mask)
		for m,n in zip(fill_idx[0], fill_idx[1]):
			refgeo_TS[m][n]['date'] += [datedelta.days]
			refgeo_TS[m][n]['uncertainty'] += [demlist[i].uncertainty]
			refgeo_TS[m][n]['value'] += [znew[m, n]]

	# pickle_file = os.path.join(ini.result['picklefile_dir'], os.path.basename(ini.refgeometry['gtiff']).replace('.tif', '_TSpickle.p'))
	pickle.dump(refgeo_TS, open(ini.result['picklefile'], "wb"))

	time_b = datetime.now()
	print('Program End: {}'.format(time_b.strftime('%Y-%m-%d %H:%M:%S')))
	print('Time taken: ' + str(time_b - time_a))
	return refgeo_TS

def dhdt(ini, ref_dem_TS=None):
	# ==== Read pickle file ====

	print('Program Start: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

	# TS_pickle_file = sys.argv[1]
	if ref_dem_TS is None:
		ref_dem_TS = pickle.load( open(ini.result['picklefile'], "rb") )
	print('TimeSeries has been read!')

	# ==== Prepare the reference geometry ====

	refgeo = SingleRaster(ini.refgeometry['gtiff'])

	# ==== Create final array ====
	slope_arr = np.ones_like(ref_dem_TS, dtype=float) * -9999
	slope_error_arr = np.ones_like(ref_dem_TS, dtype=float) * -9999
	residual_arr = np.ones_like(ref_dem_TS, dtype=float) * -9999
	count_arr = np.zeros_like(ref_dem_TS, dtype=float)

	#### 15-m case
	# gridnum = basename(TS_pickle_file)[14:-2]    # 000x_000x

	# pin_dem = SingleRaster('/22t1/whyj/Projects/Franz_Josef_Land/ArcticDEM_dhdt/point_TS_tile/pin_dem/oldest_v2_' + gridnum + '.tif')
	# pin_dem_array = pin_dem.ReadAsArray()
	# pin_dem_date = SingleRaster('/22t1/whyj/Projects/Franz_Josef_Land/ArcticDEM_dhdt/point_TS_tile/pin_dem/oldest_v2_date_' + gridnum + '.tif')
	# pin_dem_date_array = pin_dem_date.ReadAsArray()

	print('m total: ', len(ref_dem_TS))

	# ==== Weighted regression ====

	for m in range(len(ref_dem_TS)):
		if m % 100 == 0:
			print(m)
		for n in range(len(ref_dem_TS[0])):
			if len(ref_dem_TS[m][n]['date']) >= 3:
				date = np.array(ref_dem_TS[m][n]['date'])
				uncertainty = np.array(ref_dem_TS[m][n]['uncertainty'])
				value = np.array(ref_dem_TS[m][n]['value'])
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
				count_arr[m, n] = len(date)
				if (len(np.unique(date)) >= 3) and (date[-1] - date[0] > 200):
					w = [1 / k for k in uncertainty]
					case = 0
					if len(date) == 4:
						case = 1
						# This is to avoid dividing by zero when N = 4 and to give us a better error estimate
						date = np.append(date, date[-1])
						value = np.append(value, value[-1])
						uncertainty = np.append(uncertainty, uncertainty[-1])
						w = np.append(w, sys.float_info.epsilon)
					elif len(date) == 3:
						case = 2
						# This is to avoid negative Cd^2 when N = 3 and to give us a better error estimate
						date = np.append(date, [date[-1], date[-1]])
						value = np.append(value, [value[-1], value[-1]])
						uncertainty = np.append(uncertainty, [uncertainty[-1], uncertainty[-1]])
						w = np.append(w, [sys.float_info.epsilon, sys.float_info.epsilon])
					p, c = np.polyfit(date, value, 1, w=w, cov=True)
					_, res, _, _, _ = np.polyfit(date, value, 1, w=w, full=True)
					# where c is the covariance matrix of p -> c[0, 0] is the variance estimate of the slope.
					# what we want is ({G_w}^T G_w)^{-1}, which is equal to c * (N - m - 2) / res
					cov_m = c * (len(w) - 4) / res
					slope_arr[m, n] = p[0] * 365.25
					slope_error_arr[m, n] = np.sqrt(cov_m[0, 0]) * 365.25
					# slope_error_arr[m, n] = np.sqrt(c[0, 0]) * 365.25
					# ./point_TS_ver2-2_linreg.py:^^^^^^^^: RuntimeWarning: invalid value encountered in sqrt
					# /data/whyj/Software/anaconda3/lib/python3.5/site-packages/numpy/lib/polynomial.py:606: RuntimeWarning: divide by zero encountered in true_divide
					# fac = resids / (len(x) - order - 2.0)
					if case == 0:
						residual_arr[m, n] = np.sum((np.polyval(p, date) - value) ** 2)
					elif case == 1:
						residual_arr[m, n] = np.sum((np.polyval(p, date[:-1]) - value[:-1]) ** 2)
					elif case == 2:
						residual_arr[m, n] = np.sum((np.polyval(p, date[:-2]) - value[:-2]) ** 2)
						# residual_arr[m, n] = res[0]
			else:
				count_arr[m, n] = len(ref_dem_TS[m][n]['date'])
				# elif (date[-1] - date[0] > 0):
				# 	slope_arr[m, n] = (value[1] - value[0]) / float(date[1] - date[0]) * 365.25

	# ==== Write to file ====

	prefix = ini.result['dhdt_prefix']
	dhdt_dem = SingleRaster(prefix + '_dhdt.tif')
	dhdt_error = SingleRaster(prefix + '_dhdt_error.tif')
	dhdt_res = SingleRaster(prefix + '_dhdt_residual.tif')
	dhdt_count = SingleRaster(prefix + '_dhdt_count.tif')
	dhdt_dem.Array2Raster(slope_arr, refgeo)
	dhdt_error.Array2Raster(slope_error_arr, refgeo)
	dhdt_res.Array2Raster(residual_arr, refgeo)
	dhdt_count.Array2Raster(count_arr, refgeo)

	print('Program End: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))



if args.step is None:
	refgeo = TSpickle(ini)
	dhdt(ini, refgeo)
elif args.step == 'stack':
	TSpickle(ini)
elif args.step == 'dhdt':
	dhdt(ini)
else:
	print('Wrong Way!')