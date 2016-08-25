Cryosphere And Remote Sensing Toolkit (CARST)
=============================================

The toolkit provides useful python and bash scripts that
use satellite imagery, particularly SAR and
optical images, to monitor changes of glaciers
and ice caps through time. The toolkit has two main
approaches: ice elevation changes (also known as dh/dt) 
and pixel tracking.


Required Software
------------------

dh/dt:

- python, with numpy and matplotlib installed
- gdal

pixel tracking:

- ROI_PAC
- python
- matlab
- perl
- gdal
- GMT

Currently all provided scripts, which connect each step, are written in bash.

Folder Structure
----------------
- Doc: Documentation
- Utilities: **[v0.2]** Subroutines and functions used by dh/dt and pixel-tracking main programs.
- dhdt: Main programs for dh/dt **[v0.2]**
  - dhdt.py: Main program
  - Demo_DEMs: Demo input files
- pixeltrack: Main programs for pixel tracking **[v0.2]**

Detailed Description
--------------------
- Doc/dhdt/v0_1: **[v0.1]** dh/dt documentation
- Doc/dhdt/README.rst: **[v0.2 or later changes]** dh/dt documentation
- Doc/pixeltrack/Ampcor_PX: old files, needed to be modified or removed
- Doc/pixeltrack/LandsatPX: **[v0.1]** Landsat pixel tracking documentation
- Doc/pixeltrack/Landsat_PX_examples: some output files mades by v0.1 codes?
- Doc/pixeltrack/SARPixelTracking: **[v0.1]** SAR-imagery pixel tracking documentation

Version History
---------------

The project v0.2 is now being developed by William J. Durkin, Whyjay Zheng, 
and Professor Matthew Pritchard, Cornell University.

The initial version (0.1) was developed by Andrew K. Melkonian et al.
Reference to cite:

- Melkonian, A. K., Willis, M. J., & Pritchard, M. E. (2014). 
  Satellite-derived volume loss rates and glacier speeds for 
  the Juneau Icefield , Alaska. Journal of Glaciology, 
  60(222), 743–760.


