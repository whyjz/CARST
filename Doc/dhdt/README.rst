=========================================================
Surface Elevation Change (dh/dt) package in CARST: Readme
=========================================================

Here we introduce how to use the dh/dt script **dhdt.py**. You will find the core 
script at ``CARST/dhdt`` folder. The required python modules are put at ``CARST/Utilities/v0_2``.
**dhdt.py** reads a configuration file which provides details about input DEMs and fitting options. 
It (optionally) warps all input DEM files (in GeoTiff format) to the same extent and the same 
pixel size, and then performs weighted regression using given threshold values over each pixel. 
The output is also in GeoTiff format, representing the dh/dt value (slope of regression line) and its
uncertainty, in m/day.

Usage
-----------------------------------------------------
To run the script, type

``python dhdt.py config_file``

config_file should have the same layout as **defaults.ini** at ``CARST/dhdt``.


Configuration Parameters
-----------------------------------------------------
[DEM List]

- *csvfile*: CSV file for a list of DEMs.

[Gdalwarp Options]

- *t_srs*: Projection in Proj.4 format. All the input DEMs will be re-projected to this CRS.
- *tr*: Pixel size in x and y direction. All the input DEMs will be resampled to this resolution.
- *te*: Extent under the specified projection. All the input DEMs will be clipped to this extent.
- *output_dir*: Path to save processed DEMs

[Regression Options]

- *min_count*: Minimum valid DEM count at a pixel. **dhdt.py** picks out NaN values for each DEM, 
  so there may be only few DEM count at some pixels, if the DEM count is lower than this value, we will not 
  do regression and the output pixel value is thus set to NaN. Do not set it under 5 or the 
  fitting error would significantly increase.
- *min_time_span*: Minimum DEM time span at a pixel, in days. Too short time span will also increase the fitting error,
  and if DEM time span at pixel is shorter than the values given here, the output pixel value will be set to NaN.
  Recommended value is *365* (a year).
- *min_year*: A DEM which was taken before this year will not be included for regression. 
- *max_year*: A DEM which was taken after this year will not be included for regression. 

[DHDT Result Options]

- *output_dir*: Path to save the results of weighted regression
- *gtiff_slope*: Output file name for dh/dt value (m/day), in GeoTiff (.tif) format
- *gtiff_slope_err*: Output file name for dh/dt error, in GeoTiff (.tif) format

CSV File for a DEM list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
It should have at least 3 columns:

1. DEM path
2. DEM date, in yyyy-mm-dd (e.g. 2016-08-17)
3. DEM uncertainty

An example is **deminput.csv** at ``CARST/dhdt``. A csv with more than 3 columns is acceptable,
although this script only reads the first 3 columns. For finding DEM uncertainty and making 
a csv file in this format, please see **getUncertaintyDEM.py** at ``CARST/other_process``.

DEMO
-----------------------------------------------------
Please try 

``python dhdt.py defaults.ini``

**dhdt.py** and **defaults.ini** are at the same path.


Imported Modules
-----------------------------------------------------
- *UtilConfig.py*: for r/w configuration files 
- *UtilDEM.py*: for r/w/resampling DEMs
- *UtilFit.py*: for fitting using weighted regression

Readme History
-----------------------------------------------------
This readme is for v0.2, by Whyjay Zheng in Aug 17, 2016.

Documentation for v0.1 is at ``./v0_1`` with DEMO files, by Andrew Kenneth Melkonian, in May 26, 2015.

v0.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``./v0_1/DEMO/*.txt``: files used at ./v0_1/README.pdf
- ``./v0_1/DEMO/case_FJL/yymmmdd.txt``: The cases in Franz Josef Land
- ``./v0_1/DEMO/case_FJL/input_for_dhdt.txt``: the output of aggregate.py
- ``./v0_1/DEMO/case_FJL/FJL_p10m10*``: the output of weightedRegression.py

Future Improvement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Add a dh/dt rate control threshold to filter out noises, like
   upper_threshold and lower_threshold parameters in v0.1.
2. Output improvement (including intercept output)