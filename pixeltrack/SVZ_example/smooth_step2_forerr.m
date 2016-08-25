function smooth_step2_forerr(step1_smoothed_file, crs)
%SMOOTH_STEP2 smoothes a geotiff file (for error file).
% based on the algorithm of Fahnestock et al. (2015): Landsat 8 image processing
% step1_smoothed_file: filename
% crs: 'EPSG:XXXX'
% version 1.0
% last modified by Whyjay Zheng, 2016 Apr 23

addpath('/13t1/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/')

[A, R] = geotiffread(step1_smoothed_file);

A(abs(A) < eps) = NaN;

B = A;
B(~all(isnan(A),2), ~all(isnan(A),1)) = inpaint_nans(double(A(~all(isnan(A),2), ~all(isnan(A),1))));

geotiffwrite(strrep(step1_smoothed_file, 'smooth1', 'smooth3'), B, R, 'CoordRefSysCode', crs)
