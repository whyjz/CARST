#!/bin/bash
# Make the same region of specified area in Franz Josef Land from multiple DEMs 
# by WhyJ, Jan 23 2016
# output resolution: 90m

# ---- inputs ----
    # WV DEM files
wv_rootdir='/data/whyj/Projects/Franz_Josef_Land/DEM_ICESatAligned/WV_3m'
wv_files=`ls --color=never -p $wv_rootdir/11AUG16*WV01*DEM1*.tif $wv_rootdir/12JUN21*WV01*DEM1*.tif $wv_rootdir/12JUL20*WV01*DEM2*.tif $wv_rootdir/13APR18*WV01*DEM1*.tif /data/whyj/Projects/Franz_Josef_Land/Output/WV2014_new_corrected3m/14APR02*WV02*50C800*DEM1*.tif`
    # output folder
output_dir='/data/whyj/Projects/Franz_Josef_Land/Lab/number_of_elevation/dhdt_matlab'
    # extent
extent='409934.567506 8917320.43249 423129.102975 8902119.12357'

# ---- clip to file ----
echo ====================================
echo ========== Program Starts ==========
echo ====================================
for wv_f in $wv_files 
do
    wv_f_title=${wv_f##*/}
    newfile_name=${wv_f_title/.tif/areahooker.tif}
    gdal_translate -projwin $extent -of GTiff $wv_f $output_dir/$newfile_name
    gdalwarp -tr 15 15 -overwrite -dstnodata -9999 $output_dir/$newfile_name $output_dir/${newfile_name/-3m/-15m}
done
