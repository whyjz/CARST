#!/bin/bash
# Prepare input for weightedRegression.py (Andrew's code) instead using aggregate.py (Andrew's code)
# by WhyJ, Feb 18 2016

wvlist='/data/whyj/Projects/Franz_Josef_Land/dHdt/Regression/Hooker/availableWV.txt'
wv_rootdir='/data/whyj/Projects/Franz_Josef_Land/DEM_Aligned/WV_3m'
outputdir='/data/whyj/Projects/Franz_Josef_Land/dHdt/Regression/Hooker'

wvfiles=''
for keyword in $(cat $wvlist)
do
	p1=${keyword:0:7}
	p2=${keyword:7:4}
	p3=${keyword:11:4}
	wvfiles="${wvfiles} $(ls $wv_rootdir/$p1*$p2*$p3*.tif)"
done

for wv_f in $wvfiles
do
	fname=${wv_f##*/}
	gdal_translate -of XYZ -tr 30 30 -projwin 409643 8918091 423840 8901992 $wv_f $outputdir/${fname/.tif/_clipped.xyz}
done

xyzfiles=$(ls $outputdir/*_clipped.xyz)

awk '{print $1, $2, $3, 2011.6219, 0.579438}' $outputdir/11AUG16* > $outputdir/11AUG16.txt
awk '{print $1, $2, $3, 2012.5492, 0.647260}' $outputdir/12JUL20* > $outputdir/12JUL20.txt
awk '{print $1, $2, $3, 2013.2932, 0.570123}' $outputdir/13APR18* > $outputdir/13APR18.txt
awk '{print $1, $2, $3, 2013.2959, 0.551240}' $outputdir/13APR19* > $outputdir/13APR19.txt
awk '{print $1, $2, $3, 2014.2493, 0.509941}' $outputdir/14APR02* > $outputdir/14APR02.txt

#echo > $outputdir/test.txt
#
while IFS='' read -r line || [[ -n "$line" ]]; do
	echo ">" >> $outputdir/test.txt
    #echo $line >> $outputdir/test.txt
done < $(ls $outputdir/11AUG*_clipped.xyz)

xyzfiles2="$(ls $outputdir/1??????.txt) $outputdir/larger_than_sign.txt"

paste -d"\n" $xyzfiles2 > $outputdir/input_for_dhdt.txt