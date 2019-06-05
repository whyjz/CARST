#!/bin/bash
# smoothing a geotiff
# by Whyjay, 2016 Mar 31
# last modified: 2016 Apr 22
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
# bash smoothing.bash configfile
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

# =================

#output_prefix='28MAR16_23MAR16_SEVZ_VavilovW_res30m'
#snr_threshold_sqrt="9999"
#snr_threshold_hp300="0"

#getEPSG='/data/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/getEPSG.py'
east_hp300="hp300/${output_prefix}_hp300_eastxyz.tif"
north_hp300="hp300/${output_prefix}_hp300_northxyz.tif"
snr_hp300="hp300/${output_prefix}_hp300_snr.tif"
#magerr_hp300="hp300/${output_prefix}_hp300_magerr.tif"
east_sqrt="sqrt_shift/${output_prefix}_sqrt_median_eastxyz.tif"
north_sqrt="sqrt_shift/${output_prefix}_sqrt_median_northxyz.tif"
snr_sqrt="sqrt_shift/${output_prefix}_sqrt_median_snr.tif"
#magerr_sqrt="sqrt_shift/${output_prefix}_sqrt_median_magerr.tif"

gdal_calc.py -A $east_hp300 -B $snr_hp300 -C $east_sqrt -D $snr_sqrt --outfile="${output_prefix}_east_smooth1.tif" \
             --calc="(D >= $snr_threshold_sqrt) * C + numpy.logical_and(D < $snr_threshold_sqrt, B >= $snr_threshold_hp300) * A"
EPSG=$($getEPSG ${output_prefix}_east_smooth1.tif)

matlab -nojvm -r "addpath('/13t1/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/'); smooth_step2('${output_prefix}_east_smooth1.tif', '$EPSG'); exit"

gdal_calc.py -A $north_hp300 -B $snr_hp300 -C $north_sqrt -D $snr_sqrt --outfile="${output_prefix}_north_smooth1.tif" \
             --calc="(D >= $snr_threshold_sqrt) * C + numpy.logical_and(D < $snr_threshold_sqrt, B >= $snr_threshold_hp300) * A"
EPSG=$($getEPSG ${output_prefix}_north_smooth1.tif)

matlab -nojvm -r "addpath('/13t1/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/'); smooth_step2('${output_prefix}_north_smooth1.tif', '$EPSG'); exit"

# ====

#gdal_calc.py -A $magerr_hp300 -B $snr_hp300 -C $magerr_sqrt -D $snr_sqrt --outfile="${output_prefix}_magerr_smooth1.tif" \
#             --calc="(D >= $snr_threshold_sqrt) * C + numpy.logical_and(D < $snr_threshold_sqrt, B >= $snr_threshold_hp300) * A"

gdal_calc.py -A ${output_prefix}_east_smooth3.tif -B ${output_prefix}_north_smooth3.tif --outfile="${output_prefix}_mag_smooth3.tif" \
             --calc="(A ** 2 + B ** 2) ** 0.5"
