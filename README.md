[![DOI:10.5281/zenodo.3475693](https://zenodo.org/badge/58771687.svg)](http://dx.doi.org/10.5281/zenodo.3475693)

Cryosphere And Remote Sensing Toolkit (CARST)
=============================================

This package analyzes satellite images, particularly SAR and optical images, and monitor changes of glaciers and ice caps through time. CARST toolkit has two main scripts: elevation changes (also known as dh/dt) and feature tracking. You can also import carst with python for using its various modules.

Dependencies
------------------------------
Required packages:

- python >= 3.0
- scipy
- gdal
- shapely
- rasterio
- geopandas
- matplotlib
- scikit-image

Optional package:
- ISCE >= 2.0.0 (built with your python, required for feature tracking)

Installation
------------------------------
`pip install carst`

CLI
------------------------------
- `$ dhdt.py --help`
- `$ featuretrack.py --help`

Using CARST in Python
------------------------------

`import carst`

`from carst import SingleRaster`

<!---
Folder Structure
----------------
- doc: Documentation
- Utilities: Subroutines and functions used by dh/dt and pixel-tracking main programs.
- dhdt: Main programs for dh/dt **[v1.0]**
    - dhdt.py: Main program
    - defaults.ini: template configuration file
    - Demo_DEMs: Demo input files
- pixeltrack: Main programs for pixel tracking **[v1.0]**
    - pixeltrack.py: main program
    - defaults.ini: template configuration file
    - Demo_Data: Demo input files
-->

Documentation
--------------------
- `doc/dhdt.rst`: dh/dt documentation
- `doc/featuretrack.rst`: feature tracking documentation

Versions & How to cite CARST
---------------

**Citing CARST software**:

- Zheng, W., Durkin, W. J., Melkonian, A. K., & Pritchard, M. E. (2021, March 9). Cryosphere And Remote 
  Sensing Toolkit (CARST) v2.0.0a1 (Version v2.0.0a1). Zenodo. http://doi.org/10.5281/zenodo.3475693

In addtional to citing this package, we also recommend that you cite one or more of these papers based on what park of CARST you use.

CARST dh/dt **[v1.0 and after]**:

- Zheng, W., Pritchard, M. E., Willis, M. J., Tepes, P., Gourmelen, N., Benham, T. J., & 
  Dowdeswell, J. A. (2018). Remote Sensing of Environment Accelerating glacier mass loss 
  on Franz Josef Land, Russian Arctic. Remote Sensing of Environment 211, 357–375. 
  http://doi.org/10.1016/j.rse.2018.04.004

CARST feature tracking **[v1.0 and after]**: 

- Zheng, W., Pritchard, M. E., Willis, M. J., & Stearns, L. A. (2019). The possible transition 
  from glacial surge to ice stream on Vavilov Ice Cap. Geophysical Research Letters, 46, 
  13892– 13902. https://doi.org/10.1029/2019GL084948

CARST **[v0.2]**:

- Willis, M. J., Zheng, W., Durkin, W. J., Pritchard, M. E., Ramage, J. M., 
  Dowdeswell, J. A., … Porter, C. C. (2018). Massive destabilization of an Arctic ice cap. 
  Earth and Planetary Science Letters, 502, 146–155. http://doi.org/10.1016/j.epsl.2018.08.049

CARST **[v0.1]**:

- Melkonian, A. K., Willis, M. J., & Pritchard, M. E. (2014). 
  Satellite-derived volume loss rates and glacier speeds for 
  the Juneau Icefield , Alaska. Journal of Glaciology, 
  60(222), 743–760. https://doi.org/10.3189/2014JoG13J181
  
How to contribute
---------------
We welcome any suggestions/ideas; a pull request would be always appreciated. 
