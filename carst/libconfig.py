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
from carst.libraster import SingleRaster
from datetime import datetime
from pathlib import Path

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
		Get DEMs from the contents of this csv file. Return a list of SingleRaster objects.
		"""

		dems = []
		with open(self.fpath, self.read_pythonver_dict[self.python_version]) as csvfile:
			csvcontent = csv.reader(csvfile, skipinitialspace=True, delimiter=delimiter)
			next(csvcontent, None)    # Skip the header
			for row in csvcontent:
				dems.append(SingleRaster(*row[:3]))
		return dems

	def GetImgPair(self, delimiter=','):

		"""
		Get ImgPair from the contents of this csv file
		"""

		imgpairs = []
		with open(self.fpath, self.read_pythonver_dict[self.python_version]) as csvfile:
			csvcontent = csv.reader(csvfile, skipinitialspace=True, delimiter=delimiter)
			for row in csvcontent:
				row_obj = [SingleRaster(i) for i in row[:2]]
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

    def verify_path(self, pathstr):
        """
        Verify and replace a file path. (now accepting absolute and relative (to the ini file) paths)
        """
        pathobj = Path(pathstr)
        if pathobj.exists():
            return pathstr
        else:
            relative_pathobj = Path(self.fpath).parent / pathobj
            if relative_pathobj.exists():
                return str(relative_pathobj)
            else:
                raise AssertionError(f'{pathstr} or {relative_pathobj} does not exist.')

    def VerifyParam(self):

        """
        Verify params and modify them to proper types.
        """

        """
        Paths that need to be verified:
        demlist['csvfile']
        refgeometry['gtiff']
        xxxx -- result['picklefile']
        """
        path_categories = ['demlist', 'refgeometry'] # , 'result']
        path_arguments = ['csvfile', 'gtiff'] # , 'picklefile']
        for category, argument in zip(path_categories, path_arguments):
            if hasattr(self, category):
                category_dict = getattr(self, category)
                if argument in category_dict:
                    category_dict[argument] = self.verify_path(category_dict[argument])
                    setattr(self, category, category_dict)


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
        if hasattr(self, 'pxsettings'):
            for key in self.pxsettings:
                if not self.pxsettings[key]:
                    # empty string
                    self.pxsettings[key] = None
                else:
                    self.pxsettings[key] = int(self.pxsettings[key])
            if 'size_across' not in self.pxsettings:
                self.pxsettings['size_across'] = None
            if 'size_down' not in self.pxsettings:
                self.pxsettings['size_down'] = None
            if 'gaussian_hp' in self.pxsettings:
                self.pxsettings['gaussian_hp'] = bool(int(self.pxsettings['gaussian_hp']))
            else:
                self.pxsettings['gaussian_hp'] = True
            if 'gaussian_hp_sigma' in self.pxsettings:
                self.pxsettings['gaussian_hp_sigma'] = float(self.pxsettings['gaussian_hp_sigma'])
            else:
                self.pxsettings['gaussian_hp_sigma'] = 3.0

        if hasattr(self, 'outputcontrol'):
            if 'datepair_prefix' in self.outputcontrol:
                if self.outputcontrol['datepair_prefix'] in ['false', 'f', 'no', 'n', '0']:
                    self.outputcontrol['if_generate_xyztext'] = False
                else:
                    self.outputcontrol['datepair_prefix'] = bool(int(self.outputcontrol['datepair_prefix']))
                    atime = datetime.strptime(self.imagepair['image1_date'], '%Y-%m-%d')
                    btime = datetime.strptime(self.imagepair['image2_date'], '%Y-%m-%d')
                    self.outputcontrol['label_datepair'] = atime.strftime('%Y%m%d') + '-' + btime.strftime('%Y%m%d' + '_')
            if 'output_folder' not in self.outputcontrol:
                self.outputcontrol['output_folder'] = '.'
        if hasattr(self, 'rawoutput'):
            if 'if_generate_xyztext' in self.rawoutput:
                self.rawoutput['if_generate_xyztext'] = bool(int(self.rawoutput['if_generate_xyztext']))
            else:
                self.rawoutput['if_generate_xyztext'] = False
            if 'if_generate_ampofftxt' in self.rawoutput:
                self.rawoutput['if_generate_ampofftxt'] = bool(int(self.rawoutput['if_generate_ampofftxt']))
            else:
                self.rawoutput['if_generate_ampofftxt'] = False
            if 'label_ampcor' in self.rawoutput:
                if self.outputcontrol['datepair_prefix'] not in ['false', 'f', 'no', 'n', '0']:
                    self.rawoutput['label_ampcor'] = os.path.join(self.outputcontrol['output_folder'], self.outputcontrol['label_datepair'] + self.rawoutput['label_ampcor'])
                else:
                    self.rawoutput['label_ampcor'] = os.path.join(self.outputcontrol['output_folder'], self.rawoutput['label_ampcor'])
            if 'label_geotiff' in self.rawoutput:
                if self.outputcontrol['datepair_prefix'] not in ['false', 'f', 'no', 'n', '0']:
                    self.rawoutput['label_geotiff'] = os.path.join(self.outputcontrol['output_folder'], self.outputcontrol['label_datepair'] + self.rawoutput['label_geotiff'])
                else:
                    self.rawoutput['label_geotiff'] = os.path.join(self.outputcontrol['output_folder'], self.rawoutput['label_geotiff'])
        if hasattr(self, 'velocorrection'):
            if 'label_bedrock_histogram' in self.velocorrection:
                if self.outputcontrol['datepair_prefix'] not in ['false', 'f', 'no', 'n', '0']:
                    self.velocorrection['label_bedrock_histogram'] = os.path.join(self.outputcontrol['output_folder'], self.outputcontrol['label_datepair'] + self.velocorrection['label_bedrock_histogram'])
                else:
                    self.velocorrection['label_bedrock_histogram'] = os.path.join(self.outputcontrol['output_folder'], self.velocorrection['label_bedrock_histogram'])
            if 'label_geotiff' in self.velocorrection:
                if self.outputcontrol['datepair_prefix'] not in ['false', 'f', 'no', 'n', '0']:
                    self.velocorrection['label_geotiff'] = os.path.join(self.outputcontrol['output_folder'], self.outputcontrol['label_datepair'] + self.velocorrection['label_geotiff'])
                else:
                    self.velocorrection['label_geotiff'] = os.path.join(self.outputcontrol['output_folder'], self.velocorrection['label_geotiff'])
            if 'label_logfile' in self.velocorrection:
                if self.outputcontrol['datepair_prefix'] not in ['false', 'f', 'no', 'n', '0']:
                    self.velocorrection['label_logfile'] = os.path.join(self.outputcontrol['output_folder'], self.outputcontrol['label_datepair'] + self.velocorrection['label_logfile'])
                else:
                    self.velocorrection['label_logfile'] = os.path.join(self.outputcontrol['output_folder'], self.velocorrection['label_logfile'])
            if 'refvelo_outlier_sigma' in self.velocorrection:
                self.velocorrection['refvelo_outlier_sigma'] = float(self.velocorrection['refvelo_outlier_sigma'])
            else:
                self.velocorrection['refvelo_outlier_sigma'] = 3.0
        if hasattr(self, 'noiseremoval'):
            for key in self.noiseremoval:
                self.noiseremoval[key] = float(self.noiseremoval[key])


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
        Get DEMs from "csvfile" field. Return a list of SingleRaster objects.
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


class LS8MTL:

	def __init__(self, fpath=None):
		self.fpath = fpath

	def fit_LS8metadata_to_configparser(MTL_file):
		for line in MTL_file:
			# Skip last line ("END") and the "END_GROUP" line.
			if ('=' in line) and ('END_GROUP' not in line):
				# Modify "GROUP = BLABLA" into "[BLABLA]" (in order to make headers for configparser)
				if 'GROUP' in line:
					line = '[' + line.rstrip().split(' ')[-1] + ']\n'
				yield line

	def ReadParam(self):

		"""
		Read parameters and save them as self.xxxx
		example: if there is a section called "GROUP = PRODUCT_METADATA"
		and there is an option named "DATE_ACQUIRED = 2016-07-18"
		then self.PRODUCT_METADATA['date_acquired'] = '2016-07-18'
		"""

		if self.fpath is not None:
			config = ConfigParser.RawConfigParser()
			config.read_file(fit_LS8metadata_to_configparser(open(self.fpath)))

			for section in config.sections():
				section_contents = {}
				for item in config.items(section):
					section_contents[item[0]] = item[1]
				setattr(self, section, section_contents)

		else:
			print('Warning: No MTL file is given. Nothing will run.')

