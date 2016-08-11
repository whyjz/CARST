# Class: XYZFile
# used for getUncertaintyDEM
# by Whyjay Zheng, Jul 28 2016

import numpy as np

class XYZFile:

	def __init__(self, fpath=None, refpts_path=None, dem_path=None):
		self.fpath = fpath
		self.refpts_path = refpts_path
		self.dem_path = dem_path
		self.data = None

	def Read(self):

		"""
		self.data will be usually a 3- or 4-column np.array
		column 1: easting
		column 2: northing
		column 3: height of the 1st group (usually reference points)
		column 4: height of the 2nd group (usually DEM points made from grdtrack)
		"""

		self.data = np.loadtxt(self.fpath)

	def StatisticOutput(self):
		mad = lambda x : 1.482 * np.median(abs(x - np.median(x)))
		if self.data.size == 0:
			print('NOTE: ' + self.dem_path + ' does not cover any ref points.')
			return [self.dem_path, '', '', '', '', '', '', self.refpts_path]
		elif self.data.shape[1] == 4:
			idx = ~np.isnan(self.data[:, 3])
			diffval = self.data[idx, 3] - self.data[idx, 2]
			offset_median = np.median(diffval)
			offset_mad = mad(diffval)
			lbound = offset_median - 3. * offset_mad
			ubound = offset_median + 3. * offset_mad
			idx2 = np.logical_and(diffval > lbound, diffval < ubound)
			diffval_trimmed = diffval[idx2]
			# The return value is ready for CsvTable.SaveData method.
			# ['filename', 'date', 'uncertainty', 'mean_offset_wrt_refpts', \
			#  'trimmed_N', 'trimming_lb', 'trimming_up', 'refpts_file']
			# 'date' is an empty string since we don't specify any date string in .xyz file.
			return [self.dem_path, '', diffval_trimmed.std(ddof=1), diffval_trimmed.mean(), \
			          len(diffval_trimmed), lbound, ubound, self.refpts_path]
		elif self.data.shape[1] == 3:
			print("Not yet designed.")
			return []
		else:
			print("This program currently doesn't support the xyz file whose column number is not 3 or 4.")
			return []
