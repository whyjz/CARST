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

- python >= 3.0, with the following modules installed 
    - numpy 
    - scipy
    - matplotlib
    - shapely
    - gdal

- All scripts are pythonized, i.e. it should work fine on any Python-supported platforms (e.g. Windows, Linux).

pixel tracking **[v1.0]**:

- ISCE >= 2.0.0 (built with your python)
- python >= 3.0, with the following modules installed
    - numpy 
    - scipy
    - gdal
    - geopandas
    - shapely

Folder Structure
----------------
- Doc: Documentation
- Utilities: Subroutines and functions used by dh/dt and pixel-tracking main programs.
- dhdt: Main programs for dh/dt **[v1.0]**
    - dhdt.py: Main program
    - defaults.ini: template configuration file
    - Demo_DEMs: Demo input files
- pixeltrack: Main programs for pixel tracking **[v1.0]**
    - pixeltrack.py: main program
    - defaults.ini: template configuration file
    - Demo_Data: Demo input files

Detailed Description
--------------------
- dhdt/README.rst: **[v1.0]** dh/dt documentation
- pixeltrack/README.rst: **[v1.0]** pixel tracking documentation

Version History
---------------
The dh/dt **[v1.0]**  and the pixel tracking **[v1.0]** is now being developed by 
Whyjay Zheng. Any suggestions/ideas would be really appreciated. 
Here's the reference to cite for dh/dt **[v1.0]**:

- Zheng, W., Pritchard, M. E., Willis, M. J., Tepes, P., Gourmelen, N., Benham, T. J., & 
  Dowdeswell, J. A. (2018). Remote Sensing of Environment Accelerating glacier mass loss 
  on Franz Josef Land, Russian Arctic. Remote Sensing of Environment 211, 357–375. 
  http://doi.org/10.1016/j.rse.2018.04.004

Here's the reference to cite for pixel tracking **[v1.0]**: 

- Willis, M. J., Zheng, W., Durkin, W. J., Pritchard, M. E., Ramage, J. M., 
  Dowdeswell, J. A., … Porter, C. C. (2018). Massive destabilization of an Arctic ice cap. 
  Earth and Planetary Science Letters, 502, 146–155. http://doi.org/10.1016/j.epsl.2018.08.049

The dh/dt **[v0.2]** and the pixel tracking **[v0.2]** was developed by Whyjay Zheng,
William J. Durkin, and Professor Matthew Pritchard, Cornell University.

The dh/dt **[v0.1]** and the pixel tracking **[v0.1]** was developed by Andrew K. 
Melkonian et al. Here is the reference to cite:

- Melkonian, A. K., Willis, M. J., & Pritchard, M. E. (2014). 
  Satellite-derived volume loss rates and glacier speeds for 
  the Juneau Icefield , Alaska. Journal of Glaciology, 
  60(222), 743–760.
