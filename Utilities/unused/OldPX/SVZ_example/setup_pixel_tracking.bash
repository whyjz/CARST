#!/bin/bash
# universal "setup pixel tracking" script
# by Whyjay Zheng, 2016 Mar 31
# Last modified: 2016 Apr 22

#
# ---- configfile example ----
#
#
# ----------------------------
#
# usage:
#
# bash setup_pixel_tracking.bash configfile

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

# ==================

scriptdir=$(pwd)
# rootdir='/data/whyj/Projects/Severnaya_Zemlya/EarthExplorer/BulkOrder/L8OLI_TIRS'
#file1='LC81630032016069LGN00_B8.TIF'
#file2='LC81690022016079LGN00_B8.TIf'
#output_prefix='19MAR16_09MAR16_SEVZ_VavilovW_res30m'
#output_cellsize='45'
#datedelta='0.666666667'    # date / resolution
#mean_x_off='0'             # determined by image_coregistar.py
#mean_y_off='0'             # determined by image_coregistar.py
#splitAmpcor='/data/akm/Python/splitAmpcor.py'
#getEPSG='/data/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/getEPSG.py'
#getGTiffMedian='/data/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/getGTiffMedian.py'
filelist="$file1 $file2"
file1_EPSG=$($getEPSG $rootdir/$file1)
file2_EPSG=$($getEPSG $rootdir/$file2)
#splitampcor_param="13 15 125 125 25 15 2"

if [ $file1_EPSG != $file2_EPSG ]
then
    echo "Error: Projection is different!"
    exit 1
elif [ $file1_EPSG = 'EPSG:32647' ]
then
    area=${area:-"382312 8821061 430462 8796161"}
    srs="+proj=utm +zone=47 +datum=WGS84 +units=m +no_defs"
    # 1660 lines
elif [ $file1_EPSG = 'EPSG:32646' ]
then
    area=${area:-"513526 8815141 546701 8794876"}
    srs="+proj=utm +zone=46 +datum=WGS84 +units=m +no_defs"
    # 1351 lines
fi

echo "Projection: $file1_EPSG"

# gaussian high pass threshold wavelength: 300

mkdir hp300
mkdir sqrt_shift
mkdir s_ampcor

subfix=${file1#*.}

for f in $filelist
do
    f_grd=${f/.$subfix/_hp300.grd}
    f_img=${f/.$subfix/_hp300.img}
    gdal_translate -of NetCDF -projwin $area -ot Float32 $rootdir/$f hp300/${f/.$subfix/.grd}
    grdfft hp300/${f/.$subfix/.grd} -Ghp300/$f_grd -F300/- --IO_NC4_CHUNK_SIZE=c
    gdal_translate -of ENVI -a_srs "$srs" hp300/$f_grd hp300/$f_img
    gdal_translate -of GTiff -projwin $area -ot Float32 $rootdir/$f sqrt_shift/${f/.$subfix/.$subfix}
    median=$($getGTiffMedian sqrt_shift/${f/.$subfix/.$subfix})
    gdal_calc.py -A sqrt_shift/${f/.$subfix/.$subfix} --outfile=sqrt_shift/${f/.$subfix/_sqrt_median.img} --format=ENVI --calc="A ** 0.5 - $median ** 0.5"
done

rx=$(echo $splitampcor_param | cut -d " " -f 3)
ry=$(echo $splitampcor_param | cut -d " " -f 4)
sx=$(echo $splitampcor_param | cut -d " " -f 5)
sy=$(echo $splitampcor_param | cut -d " " -f 6)

cd $scriptdir/hp300
python $splitAmpcor ${file1/.$subfix/_hp300.img}       ${file2/.$subfix/_hp300.img}       . $splitampcor_param
ls amp*.in | gawk '{print "ampcor "$1" rdf > "substr($1,0,index($1,"."))"out &\n"}' > run_amp.bash
chmod +x run_amp.bash
#echo "ampcor_prefix   = ampcor_r${rx}x${ry}_s${sx}x${sy}" > result_param.txt
#echo "output_prefix   = ${output_prefix}_hp300" >> result_param.txt
#echo "input_image     = ${file2/.$subfix/_hp300.img}" >> result_param.txt
#echo "output_cellsize = $output_cellsize" >> result_param.txt
#echo "datedelta       = $datedelta" >> result_param.txt
#echo "mean_x_off      = $mean_x_off" >> result_param.txt
#echo "mean_y_off      = $mean_y_off" >> result_param.txt


cd $scriptdir/sqrt_shift
python $splitAmpcor ${file1/.$subfix/_sqrt_median.img} ${file2/.$subfix/_sqrt_median.img} . $splitampcor_param
ls amp*.in | gawk '{print "ampcor "$1" rdf > "substr($1,0,index($1,"."))"out &\n"}' > run_amp.bash
chmod +x run_amp.bash
#echo "ampcor_prefix   = ampcor_r${rx}x${ry}_s${sx}x${sy}" > result_param.txt
#echo "output_prefix   = ${output_prefix}_sqrt_median" >> result_param.txt
#echo "input_image     = ${file2/.$subfix/_sqrt_median.img}" >> result_param.txt
#echo "output_cellsize = $output_cellsize" >> result_param.txt
#echo "datedelta       = $datedelta" >> result_param.txt
#echo "mean_x_off      = $mean_x_off" >> result_param.txt
#echo "mean_y_off      = $mean_y_off" >> result_param.txt

echo "" >> $scriptdir/$configfile
echo "# ==== After setup_pixel_tracking.bash ====" >> $scriptdir/$configfile
echo "" >> $scriptdir/$configfile
echo "ampcor_prefix       = ampcor_r${rx}x${ry}_s${sx}x${sy}" >> $scriptdir/$configfile
echo "input_image         = ${file2/.$subfix/_*.img}" >> $scriptdir/$configfile