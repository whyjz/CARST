#!/bin/bash
# find the offset between two  Landsat 8 images (subset of small area)
# by Whyjay, 2015 Apr 1
#                                                          This is ../param.txt
#                                                          v
# findCoreg_subpix.bash file1 file2 search_win_in_ampcor configfile
#                                             ^
#                                             This can be determined by max(image_coregstar.py) + 2
# last modified: May 18, 2016

file1=$1
file2=$2
offset=$3
configfile=$4
step=$5
step=${step:-2}
refwin=$((offset * 5))
splitampcor_param="1 15 $refwin $refwin $offset $offset $step"
ampcor_str="ampcor_r${refwin}x${refwin}_s${offset}x${offset}"
filelist="$file1 $file2"
getGTiffMedian='/13t1/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/getGTiffMedian.py'
splitAmpcor='/13t1/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes/andrew_codes/splitAmpcor.py'

for f in $filelist
do
    median=$($getGTiffMedian $f)
    gdal_calc.py -A $f --outfile=${f/.*/.img} --format=ENVI --calc="A ** 0.5 - $median ** 0.5"
done

$splitAmpcor ${file1/.*/.img} ${file2/.*/.img} . $splitampcor_param
echo "starting to do ampcor..."
ampcor ${ampcor_str}_1.in rdf > ${ampcor_str}_1.out
echo "ampcor finished!"
awk '{print $2}' ${ampcor_str}_1.off > xcoor.txt
awk '{print $4}' ${ampcor_str}_1.off > ycoor.txt

# matlab -nojvm -r "x=load('xcoor.txt');y=load('ycoor.txt');disp('x, y median:');disp(median(x));disp(median(y));disp('x, y mean:');disp(mean(x));disp(mean(y));exit"

sed -i "s/\*\*\*\*\*\*\*\*\*\*/nan/g" ${ampcor_str}_1.off
matlab -nodesktop -r "addpath('/data/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes'); bedrock_offset('${ampcor_str}_1.off'); exit"

echo "" >> $configfile
echo "# ==== After findCoreg_subpix.bash ====" >> $configfile
echo "" >> $configfile
cat bedrock_statistics.txt >> $configfile 
