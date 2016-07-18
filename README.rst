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

- python
- matlab
- gdal
- GMT

pixel tracking:

- ROI_PAC
- python
- matlab
- perl
- gdal
- GMT

Currently all provided scripts, which connect each step, are written in bash.

File Structure
---------------
- Doc: Documentation
- Utilities: Subroutines and functions used by dh/dt and pixel-tracking main programs.
- dhdt: Main programs for dh/dt
- pixeltrack: Main programs for pixel tracking

Version History
---------------

The initial version (1.0) was developed by Andrew K. Melkonian.
Reference to cite:

- Melkonian, A. K., Willis, M. J., & Pritchard, M. E. (2014). 
  Satellite-derived volume loss rates and glacier speeds for 
  the Juneau Icefield , Alaska. Journal of Glaciology, 
  60(222), 743–760.

The project is now being developed by William J. Durkin, Whyjay Zheng, and Professor Matthew Pritchard, Cornell University.