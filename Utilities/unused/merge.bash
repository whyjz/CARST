#!/bin/bash
# Prep for Ampcor input
# compiled by WhyJ, 2016 Feb 26
# Waiting for combining with setup_pixel_tracking.bash in SEVZ (ex. Imagery/Tile5*/setup*.bash)

splitAmpcor_code='/data/akm/Python/splitAmpcor.py'

location="Wilczek"
images1=$(ls /data/whyj/Projects/Franz_Josef_Land/Imagery/E_Wilczek/12MAY02/*03[12][08]*rpcmapped_1m.tif)
images1_ID="12MAY02-83FE600"
images2=$(ls /data/whyj/Projects/Franz_Josef_Land/Imagery/E_Wilczek/12JUN11/*531[45]*rpcmapped_1m.tif)
images2_ID="12JUN11-B990500"
extent="575918 8955211 584540 8933324"
outputdir='/data/whyj/Projects/Franz_Josef_Land/PXtracking/Ampcor/WV/Tile2_WilczekSouth'

outputimg1="$outputdir/${images1_ID}_${location}_clipped.img"
outputimg2="$outputdir/${images2_ID}_${location}_clipped.img"
#gdal_merge.py -o $outputimg1 -of ENVI -ul_lr $extent -n "-9999" -a_nodata -9999 $images1
#gdal_merge.py -o $outputimg2 -of ENVI -ul_lr $extent -n "-9999" -a_nodata -9999 $images2

python $splitAmpcor_code ${images1_ID}_${location}_clipped.img ${images2_ID}_${location}_clipped.img $outputdir 32 1 100 100 75 75 30 
ls amp*.in | gawk '{print "\nampcor "$1" rdf > "substr($1,0,index($1,"."))"out &\n"}' > run_amp.bash
chmod u+x run_amp.bash