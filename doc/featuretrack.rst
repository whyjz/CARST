==================================================================
Pixel Tracking (PX, aka Feature Tracking) package in CARST: Readme
==================================================================

Introduce the pixle-tracking (PX) package **[v1.0]** in CARST. It consists of a main python script
``pixeltrack.py`` and four modules for various utilities. **pixeltrack.py** reads a configuration 
file which provides details for I/O and fitting options, and then track features from an Geotiff pair
using amplitude correlation module ``ampcor`` from ISCE. Each pixel will have its own offset and 
the offset will be transformed into speed since the date of both images is provided. The offset
is calibrated by area where a user assumes no movement (e.g. bedrock, compared to glacier movement)
and the PX uncertainty is determined by the "bedrock movement". The output files are also in Geotiff
format. There are many output files, corresponding to different level of processing (error filtering)
and the phisical quantities (Vx, Vy, Magnitude, Error, etc.). 

The PX **[v1.0]** is a major rehaul of the previous version **[v0.2]**. We now use the ampcor in ISCE 
instead of that in ROI_PAC so that everything can be run in a single python script, which makes the whole 
tool executable using only python. In addition, we have updated approaches to pre-process and post-process
the ``ampcor`` product to make the whole work flow more user-friendly and phisically make sense. Like the ``dhdt``
module, the main output from ampcor is now stored as a pickle file instead of a text file to save disk space
and computing resource. 


Usage
-----------------------------------------------------
Firstly, check if ./Utilities/Python is on the python path. All the necessary modules are in this folder.

Usage: 
  ``pixeltrack.py [-h] [-s STEP] config_file``

The ``config_file`` should have the same layout as  ``./pixeltrack/defaults.ini``.

optional arguments:
  -h, --help            Show help message and exit
  -s STEP, --step STEP  Do a single step

There are 4 steps available right now: ``ampcor``, ``rawvelo``, ``correctvelo``, and ``rmnoise``.
If there is no ``-s`` flag, the program will do all the steps in order.

- ``ampcor`` : Call ``ampcor`` module in ISCE and run amplitude correlator
- ``rawvelo``: Resample the ``ampcor`` output and translate it into Geotiff files
- ``correctvelo``: Perform bedrock-movement correction
- ``rmnoise``: Noise filtering step-by-step

Configuration Parameters
-----------------------------------------------------
[imagepair]: List of the image pair

- *image1*: First image path
- *image2*: Second image path
- *image1_date*: First image date (yyyy-mm-dd)
- *image2_date*: Second image date (yyyy-mm-dd)

[pxsettings]: Pixel tracking settings

- *refwindow_x*: Reference window size, x-direction (in pixels)
- *refwindow_y*: Reference window size, y-direction (in pixels)
- *searchwindow_x*: Search window size, x-direction (in pixels)
- *searchwindow_y*: Search window size, y-direction (in pixels)
- *skip_across*: Skip in x-direction. Also determines the output pixel spacing in x-direction ("every n pixels")
- *skip_down*:   Skip in y-direction. Also determines the output pixel spacing in y-direction ("every n pixels")
- *oversampling*: Oversampling rate (n per pixel)
- *threads*: How many CPU threads to be used
- *gaussian_hp*: 0 to turn off; 1 to turn on the gaussian high-pass (GHP) filter before doing PX
- *gaussian_hp_sigma*: the strength of the GHP filter. default is 3 sigma

[outputcontrol]: Output filename control

- *datepair_prefix*: 0 to add nothing; 1 to add date mark on the output files (e.g. yyyyymmdd-yyyymmdd)
- *output_folder*: output folder

[rawoutput]: Controls what is stored after the running ampcor module

- *if_generate_ampofftxt*: Whether does the program generate the ampoff txt file. (0 or 1)
- *if_generate_xyztext*: Whether does the program generate the xyz-format txt file. (0 or 1)
- *label_ampcor*: ampcor file label
- *label_geotiff*: geotiff file label

[velocorrection]: Controls the filename after bedrock correction

- *bedrock*: Bedrock file (path to a shapefile; mush has the same CRS with the image pair)
- *label_bedrock_histogram*: bedrock histogram file label
- *label_geotiff*: geotiff file label
- *label_logfile*: log file label
- *refvelo_outlier_sigma*: the sigma threshold for determining what pixels would be classified as outliers when calculating bedrock histograms and uncertainty

[noiseremoval]: Parameters for noise removal

- *snr*: Signal-to-Noise ratio
- *gaussian_lp_mask_sigma*: the strength of the Gaussian low-pass filter, which is used as a mask to filter out bad data (default is 5)
- *min_clump_size*: minimum clump size to be recgonized as trul signal

DEMO
-----------------------------------------------------
Please try ``python pixeltrack.py defaults.ini``.

Imported Modules
-----------------------------------------------------
- *UtilConfig.py*: for r/w configuration files 
    - class **ConfParams**
- *UtilRaster.py*: for r/w/resampling DEMs
    - class **SingleRaster**, **RasterVelos**
- *UtilPX.py*: for Pixel Tracking
    - class **ampcor_task**, **writeout_ampcor_task**
- *UtilXYZ*: for manipulating text data
    - class **ZArray**, **DuoZArray**, **AmpcoroffFile**
    - function **points_in_polygon**

Readme History
-----------------------------------------------------
Readme **[v1.0]** by Whyjay Zheng, June 4, 2019.

There is no Readme **[v0.2]**.

Documentation for **[v0.1]** was written by Andrew Kenneth Melkonian, in Aug 28, 2014; 
but now it is deprecated (at ``Utilities/unused/SARPixelTracking``).


Future Improvement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. SAR pixel tracking seems to work. Add more note.
2. Better constraint on bedrock correction using cluster analysis
