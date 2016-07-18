#!/bin/bash
# making a realistic speed uncertainty map
# by Whyjay, 2016 Apr 11
#
# ---- configfile example ----
# x_median           =  0.281
# y_median           = -0.023
# x_std              =  0.664
# y_std              =  0.574
# x_skewness         = -0.273
# y_skewness         =  0.956
# x_kurtosis         =  9.542
# y_kurtosis         = 10.870
# datedelta          = 0.466666667
# input_prefix       = 06APR16_30MAR16_SEVZ_VavilovW_res30m
# snr_threshold_sqrt = 10
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

gdal_calc.py -A ../hp300/${input_prefix}_hp300_easterr.tif -B ../hp300/${input_prefix}_hp300_snr.tif \
             -C ../sqrt_shift/${input_prefix}_sqrt_median_easterr.tif -D ../sqrt_shift/${input_prefix}_sqrt_median_snr.tif \
             --outfile="../${input_prefix}_easterr_smooth1.tif" \
             --calc="(D >= $snr_threshold_sqrt) * C + numpy.logical_and(D < $snr_threshold_sqrt, B >= 0) * A"
gdal_calc.py -A ../hp300/${input_prefix}_hp300_northerr.tif -B ../hp300/${input_prefix}_hp300_snr.tif \
             -C ../sqrt_shift/${input_prefix}_sqrt_median_northerr.tif -D ../sqrt_shift/${input_prefix}_sqrt_median_snr.tif \
             --outfile="../${input_prefix}_northerr_smooth1.tif" \
             --calc="(D >= $snr_threshold_sqrt) * C + numpy.logical_and(D < $snr_threshold_sqrt, B >= 0) * A"

alpha="../${input_prefix}_east_smooth3.tif"
beta="../${input_prefix}_north_smooth3.tif"
BSx=$(echo $x_std $datedelta | awk '{print ($1/$2)^2}')
BSy=$(echo $y_std $datedelta | awk '{print ($1/$2)^2}')
Salpha="../${input_prefix}_easterr_smooth1.tif"
Sbeta="../${input_prefix}_northerr_smooth1.tif"

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

gdal_calc.py -A $alpha -B $beta -C $Salpha -D $Sbeta \
             --outfile="../${input_prefix}_realistic_magerr.tif" \
             --calc="( (A ** 2 * (C ** 2 + $BSx ** 2) + B ** 2 * (D ** 2 + $BSy ** 2)) / (A ** 2 + B ** 2) ) ** 0.5"

#gdal_calc.py -A $alpha -B $beta -C $Salpha -D $Sbeta \
#             --outfile="../test.tif" \
#             --calc="A + B +C + D"