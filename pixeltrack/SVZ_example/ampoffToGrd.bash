#!/bin/bash
# A Bash script which 
# 1. collects all ampcor *.off files
# 2. make two .xyz files, for east and north offset respectively (4-column: x, y, z, snr)
# 3. transforms .xyz files into .grd files using xyz2grd
# 4. makes a mag.grd (magnuitde: sqrt(east^2 + north^2)) and a snr.grd (Signal-to-Noise ratio)
#
# It works as an improved version of Andrew's code ampoffToUTM.py. 
# The last modification of ampoffToUTM.py (ampoffToUTM_modified.py) was done on 2016 Feb 11 by Whyjay Zheng.
#
# Version 1.0
# by Whyjay Zheng, 2016 Mar 23
# Version 1.01
# by Whyjay Zheng, 2016 Apr 22
#
# ---- configfile example ----
# ==== Need to Change for each pair ====
# 
# file1               = LC81640032013115LGN01_B8.TIF
# file2               = LC81690022013182LGN00_B8.TIF
# output_prefix       = 01JUL13_25APR13_SEVZ_VavilovW_res30m
# output_cellsize     = 45
# datedelta           = 4.466666667    # date / resolution
# splitampcor_param   = "11 15 50 50 10 7 2"
# snr_threshold_sqrt  = 9999
# snr_threshold_hp300 = 0
# 
# ==== File and Script locations ====
# 
# rootdir             = /data/whyj/Projects/Severnaya_Zemlya/EarthExplorer/BulkOrder/L8OLI_TIRS
# splitAmpcor         = /data/akm/Python/splitAmpcor.py
# getEPSG             = /data/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/getEPSG.py
# getGTiffMedian      = /data/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/getGTiffMedian.py
# 
# ==== After setup_pixel_tracking.bash ====
# 
# ampcor_prefix       = ampcor_r50x50_s10x7
# input_image         = LC81690022013182LGN00_B8_*.img
# 
# ==== After findCoreg_subpix.bash ====
# 
# x_median            = -0.055
# y_median            =  0.094
# x_std               =  1.186
# y_std               =  0.920
# x_skewness          =  0.160
# y_skewness          =  0.383
# x_kurtosis          =  3.194
# y_kurtosis          =  2.759
#
# ----------------------------
#
# usage:
#
# bash ampoffToGrd.bash configfile
#

# ==== Parsing ====

configfile=$1

while IFS='= ' read lhs rhs
do
    if [[ ! $lhs =~ ^\ *# && -n $lhs ]]; then
        rhs="${rhs%%\#*}"    # Del in line right comments
        rhs="${rhs%%*( )}"   # Del trailing spaces
        rhs="${rhs%\"*}"     # Del opening string quotes 
        rhs="${rhs#\"*}"     # Del closing string quotes 
        declare $lhs="$rhs"
    fi
done < $configfile

# ==== get Projection ====

EPSG=$($getEPSG $input_image)

if [ $EPSG = 'EPSG:32647' ]
then
    srs="+proj=utm +zone=47 +datum=WGS84 +units=m +no_defs"
elif [ $EPSG = 'EPSG:32646' ]
then
    srs="+proj=utm +zone=46 +datum=WGS84 +units=m +no_defs"
elif [ $EPSG = 'EPSG:32645' ]
then
    srs="+proj=utm +zone=45 +datum=WGS84 +units=m +no_defs"
else
    echo "Cannot Find EPSG!... forcing exit"
    exit 1
fi

# ==== Determine folder category ====

script_dir=$(pwd)
script_dir=${script_dir##*/}
if [ $script_dir = 'hp300' ]
then
    output_prefix=${output_prefix}_hp300
elif [ $script_dir = 'sqrt_shift' ]
then
    output_prefix=${output_prefix}_sqrt_median
else
    echo "Folder not correct!... forcing exit"
    exit 1
fi

# ==== Find necessary params ====

cat ${ampcor_prefix}_*.off > ${ampcor_prefix}.off

# inc_x and inc_y should be the same, and you must have ${ampcor_prefix}_1.in

#from configfile read x_median and y_median instead of from ${ampcor_prefix}_1.in
# x_median=$(grep "Mean Offset" ${ampcor_prefix}_1.in | cut -d "=" -f 2 | awk '{print $1}')
# y_median=$(grep "Mean Offset" ${ampcor_prefix}_1.in | cut -d "=" -f 2 | awk '{print $1}')

inc=$(gdalinfo $input_image | grep "Pixel Size" | awk -F "[(),]" '{print $2}')

ul_x=$(gdalinfo $input_image | grep "Origin" | awk -F "[(),]" '{print $2}')   # should be equal to x0, just in case
ul_y=$(gdalinfo $input_image | grep "Origin" | awk -F "[(),]" '{print $3}')   # should be equal to y1, just in case

x0=$(gdalinfo $input_image | grep "Lower Left" | awk -F "[(),]" '{print $2}' | sed 's/ //g')
y0=$(gdalinfo $input_image | grep "Lower Left" | awk -F "[(),]" '{print $3}' | sed 's/ //g')
x1=$(gdalinfo $input_image | grep "Upper Right" | awk -F "[(),]" '{print $2}' | sed 's/ //g')
y1=$(gdalinfo $input_image | grep "Upper Right" | awk -F "[(),]" '{print $3}' | sed 's/ //g')

# ==== making xyz files ====

awk -v ul_x=$ul_x -v ul_y=$ul_y -v inc=$inc -v x_median=$x_median -v y_median=$y_median \
   '{OFMT = "%f";  print ul_x + ($1- 1) * inc, ul_y - ($3- 1) * inc, $2 - x_median, $5, $6}' \
   ${ampcor_prefix}.off > ${output_prefix}_eastxyz.txt

awk -v ul_x=$ul_x -v ul_y=$ul_y -v inc=$inc -v x_median=$x_median -v y_median=$y_median \
   '{OFMT = "%f";  print ul_x + ($1- 1) * inc, ul_y - ($3- 1) * inc, $4 - y_median, $5, $7}' \
   ${ampcor_prefix}.off > ${output_prefix}_northxyz.txt

# ==== XYZ To Grd ====

xyz2grd ${output_prefix}_eastxyz.txt  -R$x0/$x1/$y0/$y1 -I${output_cellsize}= -G${output_prefix}_eastxyz.grd  --IO_NC4_CHUNK_SIZE=c
xyz2grd ${output_prefix}_northxyz.txt -R$x0/$x1/$y0/$y1 -I${output_cellsize}= -G${output_prefix}_northxyz.grd --IO_NC4_CHUNK_SIZE=c
xyz2grd ${output_prefix}_northxyz.txt -R$x0/$x1/$y0/$y1 -I${output_cellsize}= -G${output_prefix}_snr.grd -i0,1,3 --IO_NC4_CHUNK_SIZE=c
xyz2grd ${output_prefix}_eastxyz.txt  -R$x0/$x1/$y0/$y1 -I${output_cellsize}= -G${output_prefix}_easterr.grd  -i0,1,4 --IO_NC4_CHUNK_SIZE=c
xyz2grd ${output_prefix}_northxyz.txt -R$x0/$x1/$y0/$y1 -I${output_cellsize}= -G${output_prefix}_northerr.grd -i0,1,4 --IO_NC4_CHUNK_SIZE=c

grdmath ${output_prefix}_eastxyz.grd  -$datedelta DIV --IO_NC4_CHUNK_SIZE=c = ${output_prefix}_eastxyz.grd
grdmath ${output_prefix}_northxyz.grd $datedelta DIV --IO_NC4_CHUNK_SIZE=c = ${output_prefix}_northxyz.grd
grdmath ${output_prefix}_easterr.grd  SQRT $datedelta DIV --IO_NC4_CHUNK_SIZE=c = ${output_prefix}_easterr.grd
grdmath ${output_prefix}_northerr.grd SQRT $datedelta DIV --IO_NC4_CHUNK_SIZE=c = ${output_prefix}_northerr.grd

for i in ${output_prefix}_eastxyz.grd ${output_prefix}_northxyz.grd ${output_prefix}_easterr.grd ${output_prefix}_northerr.grd ${output_prefix}_snr.grd
do
    gdal_translate -of GTiff -a_srs "$srs" $i ${i/.grd/.tif}
done

gdal_calc.py -A ${output_prefix}_eastxyz.tif -B ${output_prefix}_northxyz.tif --outfile=${output_prefix}_mag.tif --calc="(A ** 2 + B ** 2) ** 0.5"
#gdal_calc.py -A ${output_prefix}_eastxyz.tif -B ${output_prefix}_northxyz.tif -C ${output_prefix}_easterr.tif -D ${output_prefix}_northerr.tif \
#             --outfile=${output_prefix}_magerr.tif --calc="((A ** 2 * C ** 2 + B ** 2 * D ** 2) / (A ** 2 + B ** 2)) ** 0.5"

#grdmath ${output_prefix}_eastxyz.grd ${output_prefix}_northxyz.grd HYPOT --IO_NC4_CHUNK_SIZE=c = ${output_prefix}_mag.grd
#grdmath ${output_prefix}_eastxyz.grd ${output_prefix}_northxyz.grd HYPOT --IO_NC4_CHUNK_SIZE=c = ${output_prefix}_mag.grd