#!/bin/bash
# generate param.txt from old version of Pairs
# by Whyjay, 2016 Apr 23

# ==== checking files ====

of=param.txt

if [ -e $of ]
then
    echo "$of already exists!.... exit"
    exit 1
else
	echo "generating $of..."
fi



for i in setup_pixel_tracking.bash smoothing.bash hp300/result_param.txt
do
	if [ -e $i ]
	then
	    echo "checking $i... passed!"
	else
		echo "$i doesn't exist.... exit"
		exit 1
	fi
done

# ==== find necessary items ====

# xxxx='desired'

file1=$(grep file1= setup_pixel_tracking.bash)
file1=${file1#*=}
file1=${file1//\'/}
file2=$(grep file2= setup_pixel_tracking.bash)
file2=${file2#*=}
file2=${file2//\'/}
output_prefix=$(grep output_prefix= setup_pixel_tracking.bash)
output_prefix=${output_prefix#*=}
output_prefix=${output_prefix//\'/}
output_cellsize=$(grep output_cellsize= setup_pixel_tracking.bash)
output_cellsize=${output_cellsize#*=}
output_cellsize=${output_cellsize//\'/}
datedelta=$(grep datedelta= setup_pixel_tracking.bash)
datedelta=${datedelta#*=}
datedelta=${datedelta//\'/}
rootdir=$(grep rootdir= setup_pixel_tracking.bash)
rootdir=${rootdir#*=}
rootdir=${rootdir//\'/}
splitAmpcor=$(grep splitAmpcor= setup_pixel_tracking.bash)
splitAmpcor=${splitAmpcor#*=}
splitAmpcor=${splitAmpcor//\'/}
getEPSG=$(grep getEPSG= setup_pixel_tracking.bash)
getEPSG=${getEPSG#*=}
getEPSG=${getEPSG//\'/}
getGTiffMedian=$(grep getGTiffMedian= setup_pixel_tracking.bash)
getGTiffMedian=${getGTiffMedian#*=}
getGTiffMedian=${getGTiffMedian//\'/}

# xxxx="desired"

snr_threshold_sqrt=$(grep snr_threshold_sqrt= smoothing.bash)
snr_threshold_sqrt=${snr_threshold_sqrt#*=}
snr_threshold_sqrt=${snr_threshold_sqrt//\"/}
snr_threshold_hp300=$(grep snr_threshold_hp300= smoothing.bash)
snr_threshold_hp300=${snr_threshold_hp300#*=}
snr_threshold_hp300=${snr_threshold_hp300//\"/}

# xxxx="de si red"

splitampcor_param=$(grep splitampcor_param= setup_pixel_tracking.bash)
splitampcor_param=${splitampcor_param#*=}
splitampcor_param=${splitampcor_param//\"/}

# xxxx = desied

ampcor_prefix=$(grep ampcor_prefix hp300/result_param.txt)
ampcor_prefix=${ampcor_prefix#*= }

# xxxx = desired(wating to change)

input_image=$(grep input_image hp300/result_param.txt)
input_image=${input_image#*= }
input_image=${input_image//hp300/*}


# ==== start to generate param.txt ====


#echo $file1
#echo $file2
#echo $output_prefix
#echo $output_cellsize
#echo $datedelta
#echo $rootdir
#echo $splitAmpcor
#echo $getEPSG
#echo $getGTiffMedian
#echo $snr_threshold_sqrt
#echo $snr_threshold_hp300
#echo $splitampcor_param
#echo $ampcor_prefix
#echo $input_image

touch $of

echo "# ==== Need to Change for each pair ====" >> $of
echo "" >> $of
echo "file1               = $file1" >> $of
echo "file2               = $file2" >> $of
echo "output_prefix       = $output_prefix" >> $of
echo "output_cellsize     = $output_cellsize" >> $of
echo "datedelta           = $datedelta" >> $of
echo "splitampcor_param   = \"$splitampcor_param\"" >> $of
echo "snr_threshold_sqrt  = $snr_threshold_sqrt" >> $of 
echo "snr_threshold_hp300 = $snr_threshold_hp300" >> $of
echo "" >> $of
echo "# ==== File and Script locations ====" >> $of
echo "" >> $of
echo "rootdir             = $rootdir" >> $of
echo "splitAmpcor         = $splitAmpcor" >> $of
echo "getEPSG             = $getEPSG" >> $of
echo "getGTiffMedian      = $getGTiffMedian" >> $of
echo "" >> $of
echo "# ==== After setup_pixel_tracking.bash ====" >> $of
echo "" >> $of
echo "ampcor_prefix       = $ampcor_prefix" >> $of
echo "input_image         = $input_image" >> $of

cat $of
echo "###############################"
echo "###############################"
read -p "Continue? [Y/n]:" goon
goon=${goon:-y}
if [[ $goon = [Yy] ]]; then
	echo "continue..."
	echo ""
else
	exit 1
fi

#file1               = LC81630032016069LGN00_B8.TIF
#file2               = LC81690022016079LGN00_B8.TIF
#output_prefix       = 19MAR16_09MAR16_SEVZ_VavilovW_res30m
#output_cellsize     = 45
#datedelta           = 0.666666667    # date / resolution
#splitampcor_param   = "13 15 125 125 25 15 2"
#snr_threshold_sqrt  = 10
#snr_threshold_hp300 = 0

# ==== File and Script locations ====

#rootdir             = /data/whyj/Projects/Severnaya_Zemlya/EarthExplorer/BulkOrder/L8OLI_TIRS
#splitAmpcor         = /data/akm/Python/splitAmpcor.py
#getEPSG             = /data/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/getEPSG.py
#getGTiffMedian      = /data/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/getGTiffMedian.py

rm -rf ${output_prefix}*
rm -rf hp300/${output_prefix}*
rm -rf sqrt_shift/${output_prefix}*

scriptdir=$(pwd)
cd $scriptdir/s_ampcor
arg1=$(grep "Reference Image Input" *.in)
arg1=${arg1#*= }
arg1=${arg1/.img/.tif}
arg2=$(grep "Search Image Input" *.in)
arg2=${arg2#*= }
arg2=${arg2/.img/.tif}
arg3=$(grep "Search Pixel" *.in)
arg3=${arg3#*= }
arg3=${arg3:1}
echo "-------------> findCoreg_subpix.bash $arg1 $arg2 $arg3 ../$of"
findCoreg_subpix.bash $arg1 $arg2 $arg3 ../$of

cat ../$of
echo "###############################"
echo "###############################"
read -p "Continue? [Y/n]:" gooon
gooon=${gooon:-y}
if [[ $gooon = [Yy] ]]; then
	echo "continue..."
	echo ""
else
	exit 1
fi

cd $scriptdir/hp300
ampoffToGrd.bash ../$of
cd $scriptdir/sqrt_shift
ampoffToGrd.bash ../$of
cd $scriptdir
smoothing.bash $of
realistic_speed_error.bash $of