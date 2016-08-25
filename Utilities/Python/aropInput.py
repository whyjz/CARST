#!/usr/bin/python


# Created by Adam Stewart, 2014

import os


# Helper functions for assert statements of functions in class AropInput

def valid_file_type(file_type):
    '''Returns: True if file_type is a string of either GEOTIFF or BINARY; False otherwise.'''

    return isinstance(file_type, str) and (file_type == 'GEOTIFF' or file_type == 'BINARY')

def valid_number(num):
    '''Returns: True if num is a string of an number >= -1; False otherwise.'''

    return isinstance(num, str) and float(num) >= -1

def valid_pos_number(num):
    '''Returns: True if num is a string of a number > 0.'''

    return isinstance(num, str) and float(num) > 0

def valid_coord(coord):
    '''Returns: True if coord is a string containing two numbers in the format:
    "num1, num2" where num1 and num2 are numbers >= 1; False otherwise.'''

    truth = isinstance(coord, str)
    coord = coord.split(', ')
    for num in coord:
        truth = truth and valid_number(num)
    return truth

def valid_utm_zone(utm_zone):
    '''Returns: True if utm_zone is a string of a positive or negative int in the range 1..60; False otherwise.'''

    return isinstance(utm_zone, str) and abs(int(utm_zone)) in range(1,61)

def valid_satellite(sat):
    '''Returns: True if sat is a valid satellite; False otherwise.'''

    satellites = ['Landsat1', 'Landsat2', 'Landsat3', 'Landsat4', 'Landsat5', 'Landsat7', 'Landsat8', 'TERRA', 'CBERS1', 'CBERS2', 'AWIFS']
    return sat in satellites

def valid_latitude(lat):
    '''Returns: True if lat is a string of a float between -90.0 and 90.0; False otherwise.'''

    return isinstance(lat, str) and -90.0 <= float(lat) and float(lat) <= 90.0

def valid_longitude(lon):
    '''Returns: True if lon is a string of a float between -180.0 and 180.0; False otherwise.'''

    return isinstance(lon, str) and -180.0 <= float(lon) and float(lon) <= 180.0

def valid_coord_degrees(coord):
    '''Returns: True if coord is a string containing two numbers in the format:
    "num1, num2" where num1 and num2 are floats representing latitude and longitude; False otherwise.'''

    truth = isinstance(coord, str)
    coord = coord.split(', ')
    truth = truth and valid_latitude(coord[0])
    truth = truth and valid_longitude(coord[1])
    return truth

def valid_images(images):
    '''Returns: True if images is a string listing valid warp images, separated by commas.'''

    truth = True
    images = images.split(', ')
    for item in images:
        truth = truth and os.path.exists(item)
    return truth

def valid_unit(unit):
    '''Returns: True if unit is a string of an int in the range 0..5.'''

    return isinstance(unit, str) and int(unit) in range(6)


class AropInput(object):
    '''Instance contains all of the data needed for an AROP input file.

    An AROP input file can be created by running self.write_arop(path)

    All input parameters must be strings.

    Instance Attributes:
        # base image attributes
        _base_file_type:                define input file type, use GEOTIFF or BINARY
        _base_nsample:                  number of samples (columns) or use value from GEOTIFF file (-1)
        _base_nline:                    number of lines (rows) or use value from GEOTIFF file (-1)
        _base_pixel_size:               pixel size in meters
        _base_upper_left_corner:        upper left coordinate in meters or use value from GEOTIFF file (-1)
        _base_landsat:                  base image for "r" and "b" options (one band)
        _utm_zone:                      UTM projection of base image, base image must be in UTM projection for this version
                                            use positive UTM for North and negative for South 
        _base_satellite:                Landsat 1-5, 7-8, TERRA, CBERS1, CBERS2, AWIFS

        # warp image attributes
        _warp_file_type:                define input file type, use GEOTIFF or BINARY
        _warp_nsample:                  number of samples (columns) or use value from GEOTIFF file (-1)
        _warp_nline:                    number of lines (rows) or use value from GEOTIFF file (-1)
        _warp_pixel_size:               pixel size in meters
        _warp_upper_left_corner:        upper left coordinate in meters or use value from GEOTIFF file (-1)
        _warp_upper_left_corner_degree: upper left coordinate in degrees or use value from GEOTIFF file (-1)
                                            only need one of the above (meters or degrees)
        _warp_satellite:                Landsat 1-5, 7-8, TERRA, CBERS1, CBERS2, AWIFS
        _warp_satellite_pointingangle:  sensor pointing angle in degrees (for ASTER)
        _warp_orientation_angle:        map orientation angle in degrees for warp image
        _warp_nbands:                   number of input bands
        _warp_landsat_band:             list each band filename separated by comma
        _warp_band_data_type:           define data type for each band in: 1=8-bit; 2=16-bit
        _warp_base_match_band:          define matching warp band to base_landsat
        _warp_projection_code:          define projection for warp image if different from base image
                                            don't need these information if warp image projection is same as base
                                            define projection in GCTPC format (see GCTPC documents for details)
                                            0=GEO; 1=UTM (default: UTM) 
        _warp_utm_zone:                 UTM projection of warp image; use positive UTM for North and negative for South
        _warp_projection_param:         15 GCTPC projection parameters (default: 0.0; not required for UTM)
        _warp_unit:                     0=radians; 1=US feet; 2=meters; 3=seconds of arc; 
                                        4=degree of arc; 5=international feet (default: meters)
        _warp_datum:                    0=Clarke 1866; 8=GRS 1980; 12=WGS 84 (default: WGS 84)

        # output image attributes
        _out_pixel_size:                pixel size in meters
        _resample method:               define resampling approach (NN, BI, CC, AGG)
                                            NN for nearest neighbor,
                                            BI for bilinear interpolation
                                            CC for cubic convolution
                                            AGG for pixel aggregation 
        _out_extent:                    define image extent for the output (BASE, WARP, DEF)
                                            BASE uses base map extent
                                            WARP uses warp map extent
                                            DEF takes user defined map extent 
        _out_upper_left_corner:         if DEF is defined, needs to be defined (in meters)
        _out_lower_right_corner:        if DEF is defined, needs to be defined (in meters)
        _out_landsat_band:              define corresponding output files for each band separated by comma
        _out_base_match_band:           define one corresponding output matching band for geolocation verification
                                            define matching out band to base_landsat
        _out_base_poly_order:           the maximum degree of polynomial transformation (0, 1, 2)
                                            note that 2nd degree is not recommended unless have to
        _input_dem_file:                ancillary inputs for orthorectification process
                                            define terrain elevation file (must be in GeoTIFF format)
                                            the SRTM DEM data in GeoTIFF format can be downloaded from the UMD GLCF 
        _dem_projection_code:           define projection for DEM data if it is different from base image
                                            projection information is not needed if projection for DEM data is same as base image
                                            define projection in GCTPC format (see GCTPC documents for details) (default: UTM)
        _dem_utm_zone:                  UTM projection of output image; use positive UTM for North and negative for South
        _dem_projection_param:          15 GCTPC projection parameters (default: 0.0; not required for UTM)
        _dem_unit:                      0=radians; 1=US feet; 2=meters; 3=seconds of arc; 
                                        4=degree of arc; 5=international feet (default: meters)
        _dem_datum:                     0=Clarke 1866; 8=GRS 1980; 12=WGS 84 (default: WGS 84)
        _cp_parameters_file:            tie point searching control parameters file (defined separately)
    '''

    # Base image setters

    def setBaseFileType(self, file_type):
        '''Setter for _base_file_type.
        Preconditions: file_type must be a string of either GEOTIFF or BINARY.'''
        assert valid_file_type(file_type)

        self._base_file_type = file_type

    def setBaseNSample(self, nsample):
        '''Setter for _base_nsample.

        Preconditions: nsample is a string of an int >= -1.'''
        assert valid_number(nsample)

        self._base_nsample = nsample

    def setBaseNLine(self, nline):
        '''Setter for _base_nline.

        Preconditions: nline is a string of an int >= -1.'''
        assert valid_number(nline)

        self._base_nline = nline

    def setBasePixelSize(self, pixel_size):
        '''Setter for _base_pixel_size.
            
        Preconditions: pixel_size is a string of a positive number.'''
        assert valid_pos_number(pixel_size)

        self._base_pixel_size = pixel_size

    def setBaseUpperLeftCorner(self, upper_left_corner):
        '''Setter for _base_upper_left_corner.

        Preconditions: upper_left_corner is a string containing two numbers in the format:
        "num1, num2" where num1 and num2 are ints >= 1'''
        assert valid_coord(upper_left_corner)

        self._base_upper_left_corner = upper_left_corner

    def setBaseLandsat(self, image):
        '''Setter for _base_landsat.

        Preconditions: image is a valid file path.'''
        #assert os.path.exists(image)

        self._base_landsat = image

    def setUTMZone(self, zone):
        '''Setter for _utm_zone.

        Preconditions: zone is a string of a positive or negative int in the range 1..60.'''
        assert valid_utm_zone(zone)

        self._utm_zone = zone

    def setBaseSatellite(self, satellite):
        '''Setter for _base_satellite.

        Preconditions: satellite is a valid satellite name.'''
        assert valid_satellite(satellite)

        self._base_satellite = satellite

    # Warp image setters

    def setWarpFileType(self, file_type):
        '''Setter for _warp_file_type.
        Preconditions: file_type must be a string of either GEOTIFF or BINARY.'''
        assert valid_file_type(file_type)

        self._warp_file_type = file_type

    def setWarpNSample(self, nsample):
        '''Setter for _warp_nsample.

        Preconditions: nsample is a string of an int >= -1.'''
        assert valid_number(nsample)

        self._warp_nsample = nsample

    def setWarpNLine(self, nline):
        '''Setter for _warp_nline.

        Preconditions: nline is a string of an int >= -1.'''
        assert valid_number(nline)

        self._warp_nline = nline

    def setWarpPixelSize(self, pixel_size):
        '''Setter for _warp_pixel_size.
            
        Preconditions: pixel_size is a string of a positive number.'''
        assert valid_pos_number(pixel_size)

        self._warp_pixel_size = pixel_size

    def setWarpUpperLeftCorner(self, upper_left_corner):
        '''Setter for _warp_upper_left_corner.

        Preconditions: upper_left_corner is a string containing two numbers in the format:
        "num1, num2" where num1 and num2 are ints >= 1'''
        assert valid_coord(upper_left_corner)

        self._warp_upper_left_corner = upper_left_corner
        self._warp_upper_left_corner_degree = ''

    def setWarpUpperLeftCornerDegree(self, upper_left_corner_degree):
        '''Setter for _warp_upper_left_corner_degree.

        Preconditions: upper_left_corner_degree is a string containing two numbers in the format:
        "num1, num2" where num1 and num2 are floats representing latitude and longitude.'''
        assert valid_coord_degrees(upper_left_corner_degree)

        self._warp_upper_left_corner_degree = upper_left_corner_degree
        self._warp_upper_left_corner = ''

    def setWarpSatellite(self, satellite):
        '''Setter for _warp_satellite.

        Preconditions: satellite is a valid satellite name.'''
        assert valid_satellite(satellite)

        self._warp_satellite = satellite

    def setWarpSatellitePointingAngle(self, pointing_angle):
        '''Setter for _warp_satellite_pointingangle.

        Preconditions: pointing_angle is a string of a float between -90.0 and 90.0.'''
        assert valid_latitude(pointing_angle)

        self._warp_satellite_pointingangle = pointing_angle

    def setWarpOrientationAngle(self, orientation_angle):
        '''Setter for _warp_orientation_angle.

        Preconditions: orientation_angle is a string of a float between -180.0 and 180.0.'''
        assert valid_longitude(orientation_angle)

        self._warp_orientation_angle = orientation_angle

    def setWarpNBands(self, nbands):
        '''Setter for _warp_nbands.

        Preconditions: nbands is a string of an int > 0.'''
        assert valid_pos_number(nbands)

        self._warp_nbands = nbands

    def setWarpLandsatBand(self, images):
        '''Setter for _warp_landsat_band.

        Preconditions: images is a string listing valid warp images, separated by commas.'''

        self._warp_landsat_band = images

    def setWarpBandDataType(self, data_type):
        '''Setter for _warp_band_data_type.

        Preconditions: data_type is either "1" or "2".'''
        assert data_type == '1' or data_type == '2'

        self._warp_band_data_type = data_type + ' '

    def setWarpBaseMatchBand(self, image):
        '''Setter for _warp_base_match_band.

        Preconditions: image is a valid image file.'''

        self._warp_base_match_band = image

    def setWarpProjectionCode(self, code):
        '''Setter for _warp_projection_code.

        Preconditions: code is either "0" or "1".'''
        assert code == '0' or code == '1'

        self._warp_projection_code = code

    def setWarpUTMZone(self, zone):
        '''Setter for _warp_utm_zone.

        Preconditions: zone is a string of a positive or negative int in the range 1..60.'''
        assert valid_utm_zone(zone)

        self._warp_utm_zone = zone

    def setWarpProjectionParam(self, param):
        '''Setter for _warp_projection_param.'''

        self._warp_projection_param = param

    def setWarpUnit(self, unit):
        '''Setter for _warp_unit.

        Preconditions: unit is a string of an int in the range 0..5.'''
        assert valid_unit(unit)

        self._warp_unit = unit

    def setWarpDatum(self, datum):
        '''Setter for self._warp_datum.

        Preconditions: datum is either "0", "8", or "12".'''
        assert datum == '0' or datum == '8' or datum == '12'

        self._warp_datum = datum

    # Output image setters

    def setOutPixelSize(self, pixel_size):
        '''Setter for _out_pixel_size.
            
        Preconditions: pixel_size is a string of a positive number.'''
        assert valid_pos_number(pixel_size)

        self._out_pixel_size = pixel_size

    def setResampleMethod(self, method):
        '''Setter for _resample_method.

        Preconditions: method is a valid resampling method, either "NN", "BI", "CC", or "AGG".'''
        assert method == "NN" or method == "BI" or method == "CC" or method == "AGG"

        self._resample_method = method

    def setOutExtent(self, extent):
        '''Setter for _out_extent.

        Preconditions: extent is either "BASE", "WARP", or "DEF".'''
        assert extent == 'BASE' or extent == 'WARP' or extent == 'DEF'

        self._out_extent = extent

    def setOutUpperLeftCorner(self, upper_left_corner):
        '''Setter for _out_upper_left_corner.

        Preconditions: upper_left_corner is a string containing two numbers in the format:
        "num1, num2" where num1 and num2 are ints >= 1'''
        assert valid_coord(upper_left_corner)

        self._out_upper_left_corner = upper_left_corner

    def setOutLowerRightCorner(self, lower_right_corner):
        '''Setter for _out_lower_right_corner.

        Preconditions: lower_right_corner is a string containing two numbers in the format:
        "num1, num2" where num1 and num2 are ints >= 1'''
        assert valid_coord(lower_right_corner)

        self._out_lower_right_corner = lower_right_corner

    def setOutLandsatBand(self, images):
        '''Setter for _out_landsat_band.

        Preconditions: images is a string listing valid warp images, separated by commas.'''
        assert isinstance(images, str)

        self._out_landsat_band = images

    def setOutBaseMatchBand(self, image):
        '''Setter for _out_base_match_band.

        Preconditions: image is a string listing a valid image file.'''
        assert isinstance(image, str)

        self._out_base_match_band = image

    def setOutBasePolyOrder(self, num):
        '''Setter for _out_base_poly_order.

        Preconditions: num is a string of an int in the range 0..2.'''
        assert isinstance(num, str) and int(num) in range(3)

        self._out_base_poly_order = num

    def setInputDEMFile(self, dem):
        '''Setter for _input_dem_file.

        Preconditions: dem is a valid dem file path.'''
        assert os.path.exists(dem)

        self._input_dem_file = dem

    def setDEMProjectionCode(self, code):
        '''Setter for _dem_projection_code.

        Preconditions: code is either "0" or "1".'''
        assert code == '0' or code == '1'

        self._dem_projection_code = code

    def setDEMUTMZone(self, zone):
        '''Setter for _dem_utm_zone.

        Preconditions: zone is a string of a positive or negative int in the range 1..60.'''
        assert valid_utm_zone(zone)

        self._dem_utm_zone = zone

    def setDEMProjectionParam(self, param):
        '''Setter for _dem_projection_param.'''

        self._dem_projection_param = param

    def setDEMUnit(self, unit):
        '''Setter for _dem_unit.

        Preconditions: unit is a string of an int in the range 0..5.'''
        assert valid_unit(unit)

        self._dem_unit = unit

    def setDEMDatum(self, datum):
        '''Setter for self._dem_datum.

        Preconditions: datum is either "0", "8", or "12".'''
        assert datum == '0' or datum == '8' or datum == '12'

        self._dem_datum = datum

    def setCPParametersFile(self, param_file):
        '''Setter for _cp_parameters_file.

        Preconditions: param_file is a valid file path.'''
        assert os.path.exists(param_file)

        self._cp_parameters_file = param_file

    # Initializer

    def __init__(self):
        '''Initializer: Creates an instance of class AropInput.

        Preconditions: path is a file path to where the AROP input file should be saved, '.' by default.'''
        # Initialize base image attributes
        self.setBaseFileType('GEOTIFF')
        self.setBaseNSample('-1')
        self.setBaseNLine('-1')
        self._base_pixel_size = ''
        self.setBaseUpperLeftCorner('-1, -1')
        self._base_landsat = ''
        self._utm_zone = ''
        self._base_satellite = ''

        # Initialize warp image attributes
        self.setWarpFileType('GEOTIFF')
        self.setWarpNSample('-1')
        self.setWarpNLine('-1')
        self._warp_pixel_size = ''
        self.setWarpUpperLeftCorner('-1, -1')
        self._warp_satellite = ''
        self._warp_satellite_pointingangle = ''
        self._warp_orientation_angle = ''
        self.setWarpNBands('1')
        self._warp_landsat_band = ''
        self.setWarpBandDataType('1')
        self._warp_base_match_band = ''
        self.setWarpProjectionCode('1')
        self._warp_utm_zone = ''
        self._warp_projection_param = '0.0'
        self.setWarpUnit('2')
        self.setWarpDatum('12')

        # Initialize output image attributes
        self._out_pixel_size = ''
        self.setResampleMethod('CC')
        self.setOutExtent('WARP')
        self.setOutUpperLeftCorner = ''
        self.setOutLowerRightCorner = ''
        self._out_landsat_band = ''
        self._out_base_match_band = ''
        self._out_base_poly_order = ''
        self._input_dem_file = ''
        self.setDEMProjectionCode('1')
        self._dem_utm_zone = ''
        self._dem_projection_param = '0.0'
        self.setDEMUnit('2')
        self.setDEMDatum('12')
        self.setCPParametersFile('/home/akm26/Public/public_AROP_v2.2.4/tests/aster_ortho.cps_par.ini')

    def write_arop(self, path):
        '''Writes AROP input file to destination path.

        Preconditions: path is a string.'''
        assert isinstance(path, str)

        outfile = open(path, 'w')
        outfile.write('PARAMETER_FILE\n')
        outfile.write('###################\n')
        outfile.write('# define base image\n')
        outfile.write('###################\n')
        outfile.write('BASE_FILE_TYPE = ' + self._base_file_type + '\n')
        outfile.write('BASE_NSAMPLE = ' + self._base_nsample + '\n')
        outfile.write('BASE_NLINE = ' + self._base_nline + '\n')
        outfile.write('BASE_PIXEL_SIZE = ' + self._base_pixel_size + '\n')
        outfile.write('BASE_UPPER_LEFT_CORNER = ' + self._base_upper_left_corner + '\n')
        outfile.write('BASE_LANDSAT = ' + self._base_landsat + '\n')
        outfile.write('UTM_ZONE = ' + self._utm_zone + '\n')
        outfile.write('BASE_SATELLITE = ' + self._base_satellite + '\n')
        outfile.write('####################\n')
        outfile.write('# define warp images\n')
        outfile.write('####################\n')
        outfile.write('WARP_FILE_TYPE = ' + self._warp_file_type + '\n')
        outfile.write('WARP_NSAMPLE = ' + self._warp_nsample + '\n')
        outfile.write('WARP_NLINE = ' + self._warp_nline + '\n')
        outfile.write('WARP_PIXEL_SIZE = ' + self._warp_pixel_size + '\n')
        if self._warp_upper_left_corner != '':
            outfile.write('WARP_UPPER_LEFT_CORNER = ' + self._warp_upper_left_corner + '\n')
        else:
            outfile.write('WARP_UPPER_LEFT_CORNER_DEGREE = ' + self._warp_upper_left_corner_degree + '\n')
        outfile.write('WARP_SATELLITE = ' + self._warp_satellite + '\n')
        if self._warp_satellite == 'TERRA':
            outfile.write('WARP_SATELLITE_POINTINGANGLE = ' + self._warp_satellite_pointingangle + '\n')
            outfile.write('WARP_ORIENTATION_ANGLE = ' + self._warp_orientation_angle + '\n')
        outfile.write('WARP_NBANDS = ' + self._warp_nbands + '\n')
        outfile.write('WARP_LANDSAT_BAND = ' + self._warp_landsat_band + '\n')
        outfile.write('WARP_BAND_DATA_TYPE = ' + (self._warp_band_data_type*int(self._warp_nbands))[:-1] + '\n')
        outfile.write('WARP_BASE_MATCH_BAND = ' + self._warp_base_match_band + '\n')
        if self._warp_projection_code != '1':
            outfile.write('WARP_PROJECTION_CODE = ' + self._warp_projection_code + '\n')
        outfile.write('WARP_UTM_ZONE = ' + self._warp_utm_zone + '\n')
        if self._warp_projection_param != '0.0':
            outfile.write('WARP_PROJECTION_PARAM = ' + self._warp_projection_param + '\n')
        if self._warp_unit != '2':
            outfile.write('WARP_UNIT = ' + self._warp_unit + '\n')
        if self._warp_datum != '12':
            outfile.write('WARP_DATUM = ' + self._warp_datum + '\n')
        outfile.write('######################\n')
        outfile.write('# define output images\n')
        outfile.write('######################\n')
        outfile.write('OUT_PIXEL_SIZE = ' + self._out_pixel_size + '\n')
        outfile.write('RESAMPLE_METHOD = ' + self._resample_method + '\n')
        outfile.write('OUT_EXTENT = ' + self._out_extent + '\n')
        if self._out_extent == 'DEF':
            outfile.write('OUT_UPPER_LEFT_CORNER = ' + self._out_upper_left_corner + '\n')
            outfile.write('OUT_LOWER_RIGHT_CORNER = ' + self._out_lower_right_corner + '\n')
        outfile.write('OUT_LANDSAT_BAND = ' + self._out_landsat_band + '\n')
        outfile.write('OUT_BASE_MATCH_BAND = ' + self._out_base_match_band + '\n')
        if self._out_base_poly_order != '':
            outfile.write('OUT_BASE_POLY_ORDER = ' + self._out_base_poly_order + '\n')
        if self._base_satellite == 'TERRA' and self._warp_satellite == 'TERRA':
            outfile.write('INPUT_DEM_FILE = ' + self._input_dem_file + '\n')
            if self._dem_projection_code != '1':
                outfile.write('DEM_PROJECTION_CODE = ' + self._dem_projection_code + '\n')
            outfile.write('DEM_UTM_ZONE = ' + self._dem_utm_zone + '\n')
            if self._dem_projection_param != '0.0':
                outfile.write('DEM_PROJECTION_PARAM = ' + self._dem_projection_param + '\n')
            if self._dem_unit != '2':
                outfile.write('DEM_UNIT = ' + self._dem_unit + '\n')
            if self._dem_datum != '12':
                outfile.write('DEM_DATUM = ' + self._dem_datum + '\n')
        outfile.write('CP_PARAMETERS_FILE = ' + self._cp_parameters_file + '\n')
        outfile.write('END\n')
        outfile.close()
