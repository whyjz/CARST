=========================================================
Surface Elevation Change (dh/dt) package in CARST: Readme
=========================================================

Here we briefly introduce the dh/dt package **[v1.0]** in CARST. It consists of a main python script
``/dhdt/dhdt.py`` and three modules for various utilities. **dhdt.py** reads a configuration 
file which provides details for I/O and fitting options, and then piles all the input geotiff files
together to form a time series for each pixel, Next, it performs linear regression pixel-by-pixel, using 
the uncertainty of each geotiff as weight. The output is in GeoTiff format as well, representing 
the dh/dt value (slope of regression line) on a daily basis; i.e. (z unit)/day, and its uncertainty.

One of the great improvements from **[v1.0]** is that the program now uses pickle module to store the intermediate
data (the piled DEM time series) instead of text file. It gives users a full flexibility on different map
spacing and extents, as long as all the DEMs are projected into the same coordinate reference system (CRS).
In addition. by properly setting up the reference geometry, ones can process many high-resolution DEMs at the same time
without consuming too much computer memory. If you are doing dh/dt over a region with a fine spatial 
resolution, you can split the reference geometry into multiple files, and preform this program many times using each
file.

Usage
-----------------------------------------------------
Firstly, check if ./Utilities/Python is on the python path. All the necessary modules are in this folder.

Usage: 
  ``dhdt.py [-h] [-s STEP] config_file``

The ``config_file`` should have the same layout as  ``./dhdt/defaults.ini``.

optional arguments:
  -h, --help            Show help message and exit
  -s STEP, --step STEP  Do a single step

There are only 2 steps available right now: ``stack`` and ``dhdt``. If there is no ``-s`` flag, the program
will do both steps (``stack`` and then ``dhdt``). in the end of the step ``stack``, the program
dumps all the processing information into a pickle file. If the ``-s dhdt`` is prompted,
the program will read this information form the pickle file.

Configuration Parameters
-----------------------------------------------------
[demlist]: DEM list

- *csvfile*: CSV file for DEMs paths, dates, and uncertainties.

[refgeometry]: Reference Geometry

- *gtiff*: A Geotiff file representing the reference geometry. This is used for specifying the pixel spacing
  and the map extent of output geotiff files. You can freely tweak the spacing and/or map extent freely using, 
  gdal or other similar tools, but the CRS must agree with all the input geotiff files.  
  This file will be read as binary data, and anywhere with a pixel value = 0 will not be further processed. Note that
  the NoData value in a geotiff is usually set to -9999, not 0, which means the NoData pixels in this files will
  still be processed!

[settings]: various settings

- *refdate*: Specifying the reference date for all input geotiffs, in the format of YYYY-MM-DD. For example,
  if the refdate is 2015-01-01 and one of your geotiff files is from 2015-01-06, the time tick of this geotiff
  will be set to t = 5 when piling up all geotiffs.

[result]: output options

- *picklefile*: Path to the intermediate pickle file.
- *dhdt_prefix*: The prefix to all the final output geotiffs.

CSV File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
It should have at least 3 columns:

1. DEM path
2. DEM date, in yyyy-mm-dd (e.g. 2016-08-17)
3. DEM uncertainty

An example is **deminput.csv** at ``dhdt``. A csv with more than 3 columns is acceptable,
although this script only reads the first 3 columns. For finding DEM uncertainty and making 
a csv file in this format, please see **getUncertaintyDEM.py** at ``other_process``.

Each DEM must be a geotiff file, and must have the same CRS with each other. However, the DEM spacing
and the map extent can be various. 

DEMO
-----------------------------------------------------
Please try ``python dhdt.py defaults.ini``.

Imported Modules
-----------------------------------------------------
- *UtilConfig.py*: for r/w configuration files 
    - class **ConfParams**
- *UtilRaster.py*: for r/w/resampling DEMs
    - class **SingleRaster**
- *UtilFit.py*: for DEM stacking and fitting using weighted regression
    - class **DemPile****
    - function **ResampleArray**
    - The class TimeSeriesDEM is deprecated.

Readme History
-----------------------------------------------------
Readme **[v1.0]** by Whyjay Zheng, May 7, 2018.

Readme **[v0.2]** was finalized by Whyjay Zheng in Aug 17, 2016.

Documentation for **[v0.1]** was written by Andrew Kenneth Melkonian, in May 26, 2015; 
but now it is deprecated (at ``Utilities/unused``).


Future Improvement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Add a dh/dt rate control threshold to filter out noises, like
   upper_threshold and lower_threshold parameters in v0.1.
2. Output improvement (including intercept output)