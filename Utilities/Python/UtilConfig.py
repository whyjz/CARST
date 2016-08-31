# Class: CsvTable and ConfParams
# used for dhdt
# by Whyjay Zheng, Jul 28 2016
# last edit: Aug 17 2016

import sys
import csv
import os
import numpy as np
try:
	import ConfigParser                    # python 2
except:
	import configparser as ConfigParser    # python 3
from UtilTIF import SingleTIF

class CsvTable:

	"""
	Manipulating csv table which provides DEM information
	"""

	def __init__(self, fpath=None, data=[]):
		self.fpath = fpath
		self.data = data
		self.python_version = sys.version_info[0]      # detecting python 2 or 3, for csv module
		self.read_pythonver_dict = {2: 'rb', 3: 'r'}   # csv module in python 2/3 runs differently
		self.write_pythonver_dict = {2: 'wb', 3: 'w'}  # csv module in python 2/3 runs differently


	def GetDEM(self, delimiter=','):

		"""
		Get DEMs from the contents of this csv file. Return a list of SingleTIF objects.
		"""

		dems = []
		with open(self.fpath, self.read_pythonver_dict[self.python_version]) as csvfile:
			csvcontent = csv.reader(csvfile, skipinitialspace=True, delimiter=delimiter)
			next(csvcontent, None)    # Skip the header
			for row in csvcontent:
				dems.append(SingleTIF(*row[:3]))
		return dems

	def GetImgPair(self, delimiter=','):

		"""
		Get ImgPair from the contents of this csv file
		"""

		imgpairs = []
		with open(self.fpath, self.read_pythonver_dict[self.python_version]) as csvfile:
			csvcontent = csv.reader(csvfile, skipinitialspace=True, delimiter=delimiter)
			for row in csvcontent:
				row_obj = [SingleTIF(i) for i in row[:2]]
				imgpairs.append(row_obj)
		return imgpairs

	def SaveData(self, data):

		"""
		Save given data (a list of csv infor) to this object. Used to create a csv table (with Write2File).
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
			with open(self.fpath, self.write_pythonver_dict[self.python_version]) as csvfile:
				# python 3 should be open(fname, 'w', newline='') and we didn't add argument "newline" here. 
				# I don't know if it would cause some issues or not?
				csvwriter = csv.writer(csvfile, delimiter=',')
				csvwriter.writerow(header)
				for row in self.data:
					csvwriter.writerow(row)


class ConfParams:

	"""
	Read variables in a configuration file. The file should have the specified structure like CARST/dhdt/defaults.ini
	"""

	def __init__(self, fpath=None):
		self.fpath = fpath
		# self.gdalwarp = {}
		# self.demlist = {}
		# self.regression = {}
		# self.result = {}

	def ReadParam(self):

		"""
		Read parameters and save them as self.xxxx
		example: if there is a section called [gdalwarp]
		and there is an option named tr = 30 30
		then self.gdalwarp['tr'] = '30 30'
		"""

		if self.fpath is not None:
			config = ConfigParser.RawConfigParser()
			config.read(self.fpath)

			for section in config.sections():
				section_contents = {}
				for item in config.items(section):
					section_contents[item[0]] = item[1]
				setattr(self, section, section_contents)

		else:
			print('Warning: No ini file is given. Nothing will run.')

	def VerifyParam(self):

		"""
		Verify params and modify them to proper types.
		"""

		if hasattr(self, 'regression'):
			for key in self.regression:
				self.regression[key] = int(self.regression[key])
		if hasattr(self, 'gdalwarp'):
			if 'output_dir' in self.gdalwarp:
				if not os.path.exists(self.gdalwarp['output_dir']):
					os.makedirs(self.gdalwarp['output_dir'])    # create gdalwarp output folder
		if hasattr(self, 'splitampcor'):
			for key in self.splitampcor:
				self.splitampcor[key] = int(self.splitampcor[key])
		if hasattr(self, 'parallel'):
			if 'gnu_parallel' in self.parallel:
				s = self.parallel['gnu_parallel'].lower()
				self.parallel['gnu_parallel'] = s in ['true', 't', 'yes', 'y', '1']



	"""
	# ======== Check if PAIRS_DIR, METADATA_DIR, and PAIRS exist ========
	if not os.path.exists(PAIRS_DIR):
		print("\n***** ERROR: Pair directory specified (\"" + PAIRS_DIR + "\") not found, make sure full path is provided, exiting...\n");
		sys.exit(1)

	if not os.path.exists(METADATA_DIR):
		print("\n***** ERROR: Metadata directory specified (\"" + METADATA_DIR + "\") not found, make sure full path is provided, exiting...\n");
		sys.exit(1)

	if not os.path.exists(PAIRS):
		print("\n***** ERROR: Pair list \"" + PAIRS + "\" not found, make sure full path is provided, exiting...\n");
	# ===================================================================
	"""


	def GetDEM(self):

		"""
		Get DEMs from "csvfile" field. Return a list of SingleTIF objects.
		"""

		if 'csvfile' in self.demlist:
			csv = CsvTable(self.demlist['csvfile'])
			return csv.GetDEM()
		else:
			print('Warning: No DEM-list file is given. Nothing will run.')
			return []

	def GetImgPair(self, delimiter=','):

		"""
		Get ImgPair from the contents of this csv file
		"""

		if 'pairs_list' in self.io:
			csv = CsvTable(self.io['pairs_list'])
			return csv.GetImgPair(delimiter=delimiter)
		else:
			print('Warning: No Img-list file is given. Nothing will run.')
			return []