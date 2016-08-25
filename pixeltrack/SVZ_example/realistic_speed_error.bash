#!/bin/bash
# making a realistic speed uncertainty map
# by Whyjay, 2016 Apr 11
# last modified: 2016 Apr 22
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
# ----------------------------
#
# usage:
#
# bash realistic_speed_error.bash configfile

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

# ==== Start ====

gdal_calc.py -A ./hp300/${output_prefix}_hp300_easterr.tif -B ./hp300/${output_prefix}_hp300_snr.tif \
             -C ./sqrt_shift/${output_prefix}_sqrt_median_easterr.tif -D ./sqrt_shift/${output_prefix}_sqrt_median_snr.tif \
             --outfile="${output_prefix}_easterr_smooth1.tif" \
             --calc="(D >= $snr_threshold_sqrt) * C + numpy.logical_and(D < $snr_threshold_sqrt, B >= 0) * A"
gdal_calc.py -A ./hp300/${output_prefix}_hp300_northerr.tif -B ./hp300/${output_prefix}_hp300_snr.tif \
             -C ./sqrt_shift/${output_prefix}_sqrt_median_northerr.tif -D ./sqrt_shift/${output_prefix}_sqrt_median_snr.tif \
             --outfile="${output_prefix}_northerr_smooth1.tif" \
             --calc="(D >= $snr_threshold_sqrt) * C + numpy.logical_and(D < $snr_threshold_sqrt, B >= 0) * A"

alpha="${output_prefix}_east_smooth3.tif"
beta="${output_prefix}_north_smooth3.tif"
BSx=$(echo $x_std $datedelta | awk '{print ($1/$2)}')
BSy=$(echo $y_std $datedelta | awk '{print ($1/$2)}')
Salpha="${output_prefix}_easterr_smooth1.tif"
Sbeta="${output_prefix}_northerr_smooth1.tif"

for i in $alpha $beta $Salpha $Sbeta
do
	if [ -e $i ]
	then
		echo "Checking file $i ... passed!"
	else
		echo "Cannot Find $i ... forcing exit"
		exit 1
	fi
done
echo "Checking BSx = $BSx"
echo "Checking BSy = $BSy"

EPSG=$($getEPSG $Salpha)
matlab -nojvm -r "addpath('/13t1/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/'); smooth_step2_forerr('$Salpha', '$EPSG'); exit"
EPSG=$($getEPSG $Sbeta)
matlab -nojvm -r "addpath('/13t1/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/'); smooth_step2_forerr('$Sbeta', '$EPSG'); exit"

Salpha="${output_prefix}_easterr_smooth3.tif"
Sbeta="${output_prefix}_northerr_smooth3.tif"

gdal_calc.py -A $alpha -B $beta -C $Salpha -D $Sbeta \
             --outfile="${output_prefix}_magerr_smooth3.tif" \
             --calc="( (A ** 2 * (C ** 2 + $BSx ** 2) + B ** 2 * (D ** 2 + $BSy ** 2)) / (A ** 2 + B ** 2) ) ** 0.5"





#gdal_calc.py -A $alpha -B $beta -C $Salpha -D $Sbeta \
#             --outfile="../test.tif" \
#             --calc="A + B +C + D"
