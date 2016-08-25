rootdir='/data/whyj/Projects/Severnaya_Zemlya/PXtracking'

folders=$(ls -d $rootdir/*fin)

for eachfol in $folders; do
	echo $eachfol
	cd $eachfol/s_ampcor
	#pwd
	ampcor_list=$(ls *.off)
	#echo $ampcor_list
	for eachamp in $ampcor_list; do
		amp_fin=$eachamp
	done
	matlab -nodesktop -r "addpath('/data/whyj/Projects/Severnaya_Zemlya/PXtracking/Codes'); bedrock_offset('$amp_fin'); exit"
	realistic_speed_error.bash bedrock_statistics.txt
done