# Class: CsvTable and ConfParams
# used for dhdt
# by Whyjay Zheng, Jul 28 2016

import ConfigParser
import csv
import os
import numpy as np
from UtilDEM import SingleDEM

class CsvTable:

	def __init__(self, fpath=None, data=[]):
		self.fpath = fpath
		self.data = data

	def GetDEM(self):

		"""
		From the settings of "csvfile" get DEMs. Saved and returned as a list of SingleDEM objects.
		"""

		dems = []
		with open(self.fpath, 'r') as csvfile:
			csvcontent = csv.reader(csvfile, skipinitialspace=True)
			next(csvcontent, None)    # Skip the header
			for row in csvcontent:
				dems.append(SingleDEM(*row[:3]))
		return dems

	def SaveData(self, data):

		"""
		Save given data to this object.
		"""

		if not self.data:
			self.data.append(data)
		elif len(self.data[0]) == len(data):
			self.data.append(data)
		else:
			print('Warning: The length of the input data is not same with the previous data. Do nothing.')

	def Write2File(self):

		"""
		Write self.data to self.fname. Be cautious! This may overwirte previous csvfile content.
		Header is pre-defined. That means each column has been specified.
		"""

		if self.data:
			header = ['filename', 'date', 'uncertainty', 'mean_offset_wrt_refpts', \
			          'trimmed_N', 'trimming_lb', 'trimming_up', 'refpts_file']
			with open(self.fpath, 'wb') as csvfile:
				csvwriter = csv.writer(csvfile, delimiter=',')
				csvwriter.writerow(header)
				for row in self.data:
					csvwriter.writerow(row)


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
			for item in config.items("DEM List"):
				self.demlist[item[0]] = item[1]
			for item in config.items("Gdalwarp Options"):
				self.gdalwarp[item[0]] = item[1]
			# create gdalwarp output folder
			if not os.path.exists(self.gdalwarp['output_dir']):
				os.makedirs(self.gdalwarp['output_dir'])
			for item in config.items("Regression Options"):
				self.regression[item[0]] = int(item[1])
			for item in config.items("Output Options"):
				self.output[item[0]] = item[1]
		else:
			print('Warning: No ini file is given. Nothing will run.')

	def GetDEM(self):

		"""
		From the settings of "csvfile" get DEMs. Saved and returned as a list of SingleDEM objects.
		"""

		if 'csvfile' in self.demlist:
			csv = CsvTable(self.demlist['csvfile'])
			return csv.GetDEM()
		else:
			print('Warning: No DEM-list file is given. Nothing will run.')
			return []
