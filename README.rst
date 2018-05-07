Cryosphere And Remote Sensing Toolkit (CARST)
=============================================

The toolkit provides useful python and bash scripts that
use satellite imagery, particularly SAR and
optical images, to monitor changes of glaciers
and ice caps through time. The toolkit has two main
approaches: ice elevation changes (also known as dh/dt) 
and pixel tracking.


Required Platform and Software
------------------------------

dh/dt **[v1.0]**:

- All scripts are pythonized, i.e. it should be run on any Python-supported platforms (e.g. Windows, Linux).
- python, with the following modules installed 
    - numpy 
    - scipy
    - matplotlib
    - shapely
    - gdal

pixel tracking **[v0.2]**:

- Mainly written in Bash, which means this part is still exclusively for Linux system.
- ROI_PAC
- python
- matlab
- perl
- gdal
- GMT

Folder Structure
----------------
- Doc: Documentation
- Utilities: Subroutines and functions used by dh/dt and pixel-tracking main programs.
- dhdt: Main programs for dh/dt **[v1.0]**
    - dhdt.py: Main program
    - defaults.ini: template configuration file
    - Demo_DEMs: Demo input files
- pixeltrack: Main programs for pixel tracking **[v0.2]**

Detailed Description
--------------------
- Doc/dhdt/README.rst: **[v1.0]** dh/dt documentation
- Doc/pixeltrack/Ampcor_PX: old files, needed to be modified or removed
- Doc/pixeltrack/LandsatPX: **[v0.1]** Landsat pixel tracking documentation
- Doc/pixeltrack/Landsat_PX_examples: some output files mades by v0.1 codes?
- Doc/pixeltrack/SARPixelTracking: **[v0.1]** SAR-imagery pixel tracking documentation

Version History
---------------
The dh/dt **[v1.0]** is now being developed by Whyjay Zheng. Any suggestions/ideas would be
really appreciated. Here's the reference to cite:

- Zheng, W., Pritchard, M. E., Willis, M. J., Tepes, P., Gourmelen, N., Benham, T. J., & 
  Dowdeswell, J. A. (2018). Remote Sensing of Environment Accelerating glacier mass loss 
  on Franz Josef Land, Russian Arctic. Remote Sensing of Environment 211, 357–375. 
  http://doi.org/10.1016/j.rse.2018.04.004

The pixel tracking package may be updated in the near future, but it's not in the priority for now.

The dh/dt **[v0.2]** and the pixel tracking **[v0.2]** was developed by Whyjay Zheng,
William J. Durkin, and Professor Matthew Pritchard, Cornell University.

The dh/dt **[v0.1]** and the pixel tracking **[v0.1]** was developed by Andrew K. 
Melkonian et al. Here is the reference to cite:

- Melkonian, A. K., Willis, M. J., & Pritchard, M. E. (2014). 
  Satellite-derived volume loss rates and glacier speeds for 
  the Juneau Icefield , Alaska. Journal of Glaciology, 
  60(222), 743–760.
