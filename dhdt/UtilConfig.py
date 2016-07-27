# Class: ConfParams
# used for dhdt
# by Whyjay Zheng, Jul 27 2016

import ConfigParser
import csv
from UtilDEM import SingleDEM

class ConfParams:

	def __init__(self, fpath=None):
		self.fpath = fpath
		self.gdalwarp = {}
		self.demlist = {}
		self.regression = {}
		self.output = {}

	def ReadParam(self):
		if self.fpath is not None:
			config = ConfigParser.RawConfigParser()
			config.read(self.fpath)
			demlist_options = config.items("DEM List")
			for item in demlist_options:
				self.demlist[item[0]] = item[1]
			gdalwarp_options = config.items("Gdalwarp Options")
			for item in gdalwarp_options:
				self.gdalwarp[item[0]] = item[1]
			regression_options = config.items("Regression Options")
			for item in regression_options:
				self.regression[item[0]] = int(item[1])
			output_options = config.items("Output Options")
			for item in output_options:
				self.output[item[0]] = item[1]
		else:
			print('Warning: No ini file is given. Nothing will run.')

	def GetDEM(self):

		"""
		From the settings of "csvfile" get DEMs. Saved and returned as a list of SingleDEM objects.
		"""

		dems = []
		if 'csvfile' in self.demlist:
			with open(self.demlist['csvfile'], 'r') as csvfile:
				csvcontent = csv.reader(csvfile, skipinitialspace=True)
				next(csvcontent, None)    # Skip the header
				for row in csvcontent:
					dems.append(SingleDEM(*row))
		else:
			print('Waring: No DEM-list file is given. Nothing will run.')
		return dems