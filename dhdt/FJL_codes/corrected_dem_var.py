#/usr/bin/env python
# Determine the variance of each ICESat-corrected WV DEM (part 2)
# by WhyJ, Feb 18 2016

import numpy as np

mad = lambda x : 1.482 * np.median(abs(x - np.median(x)))

available_wv_file = '/data/whyj/Projects/Franz_Josef_Land/dHdt/Regression/Hooker/availableWV.txt'

grdtrack_output_file = '/data/whyj/Projects/Franz_Josef_Land/dHdt/Regression/Hooker/grdtrack_output.txt'
grdtrack_output = np.loadtxt(grdtrack_output_file)

wv_diff = []

with open(available_wv_file, 'r') as wv_str_fid:
	for i in range(5):
		wv_str = wv_str_fid.readline().split('\n')
		single_dat = grdtrack_output[:, i+3] - grdtrack_output[:, 2]
		single_dat = single_dat[~np.isnan(single_dat)]
		median_val = np.median(single_dat)
		mad_val = mad(single_dat)
		lbound = median_val - 3. * mad_val
		ubound = median_val + 3. * mad_val
		idx = np.logical_and(single_dat > lbound, single_dat < ubound)
		single_dat = single_dat[idx]
		wv_diff.append(single_dat)
		print 'Name of the WorldView File: ' + wv_str[0]
		print 'Trimming -> Lbound: %f Ubound: %f' % (lbound, ubound)
		print 'N        -> Before: %d After:  %d' % (len(idx), len(single_dat))
		print 'Mean     -> %f' % (wv_diff[i].mean())
		print 'StdDev   -> %f\n' % (wv_diff[i].std(ddof=1))

