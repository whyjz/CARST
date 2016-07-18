#!/bin/bash
# Determine the variance of each ICESat-corrected WV DEM (part 1)
# by WhyJ, Feb 17 2016

xyzfile='/data/whyj/Projects/Franz_Josef_Land/Source/Shapefile_ICESAT_classification/Output_and_statistics/ICESAT_FJL_UTM40_BR_SP_SS_RemovedOutlier.txt'
wvlist='/data/whyj/Projects/Franz_Josef_Land/dHdt/Regression/Hooker/availableWV.txt'
wv_rootdir='/data/whyj/Projects/Franz_Josef_Land/DEM_Aligned/WV_3m'
outputfile='/data/whyj/Projects/Franz_Josef_Land/dHdt/Regression/Hooker/grdtrack_output.txt'

wvfiles=''
for keyword in $(cat $wvlist)
do
	p1=${keyword:0:7}
	p2=${keyword:7:4}
	p3=${keyword:11:4}
	wvfiles="${wvfiles} $(ls $wv_rootdir/$p1*$p2*$p3*.tif)"
done

Gstring=''
for wv_f in $wvfiles
do
	Gstring="$Gstring -G$wv_f"
done

grdtrack $xyzfile $Gstring > $outputfile
