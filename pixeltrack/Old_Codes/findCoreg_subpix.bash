#!/bin/bash
# find the offset between two  Landsat 8 images (subset of small area)
# by Whyjay, 2015 Apr 1
# findCoreg_subpix.bash file1 file2 search_win_in_ampcor
#                                             ^
#                                             This can be determined by max(image_coregstar.py) + 1

file1=$1
file2=$2
offset=$3
refwin=$((offset * 5))
splitampcor_param="1 15 $refwin $refwin $offset $offset 2"
ampcor_str="ampcor_r${refwin}x${refwin}_s${offset}x${offset}"
filelist="$file1 $file2"
getGTiffMedian='/data/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/getGTiffMedian.py'
splitAmpcor='/data/akm/Python/splitAmpcor.py'

for f in $filelist
do
    median=$($getGTiffMedian $f)
    gdal_calc.py -A $f --outfile=${f/.tif/.img} --format=ENVI --calc="A ** 0.5 - $median ** 0.5"
done

$splitAmpcor ${file1/.tif/.img} ${file2/.tif/.img} . $splitampcor_param
echo "starting to do ampcor..."
ampcor ${ampcor_str}_1.in rdf > ${ampcor_str}_1.out
echo "ampcor finished!"
awk '{print $2}' ${ampcor_str}_1.off > xcoor.txt
awk '{print $4}' ${ampcor_str}_1.off > ycoor.txt

matlab -nojvm -r "x=load('xcoor.txt');y=load('ycoor.txt');disp('x, y median:');disp(median(x));disp(median(y));disp('x, y mean:');disp(mean(x));disp(mean(y));exit"
