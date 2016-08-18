
#!/bin/bash

#Please make sure that the following variables are defined in a params file:
#  PAIRS_DIR <- Directory containing east and west velocity grds
#  ICE, ROCK <- Directories of rock and ice outlines
#
# Usage :
# bash remove_ramp.cmd params_landsat.txt
params_file=$1

# Evaluate the variables assigned in params_file
while read var_name
do
  eval `echo $var_name | sed 's/ //g'`
done < $params_file


# Make the names of the east and west grds
read image1 image2 <<< `cat $PAIRS`

#Get rid fo the directory information and parse out the calendar date
image1=`echo $image1 | sed 's:.*/::'`
year1=`echo ${image1:9:4}`
jday1=`echo "${image1:13:3} -1" | bc -l`
caldate1=`date -d "$jday1 days $year1-01-01" +"%Y%m%d"`

image2=`echo $image2 | sed 's:.*/::'`
year2=`echo ${image2:9:4}`
jday2=`echo "${image2:13:3} -1"| bc -l`
caldate2=`date -d "$jday2 days $year2-01-01" +"%Y%m%d"`

echo "$caldate1 $caldate2"

#second half of the name
echo ${caldate2}_${caldate1}_r${REF_X}x${REF_Y}_s${SEARCH_X}x${SEARCH_Y}

#for i in `ls -d /13t1/wjd73/Yahtse_Glacier/ALOS_granules/Path_246/int_071007_070822/`
#do

# first check if this has already been done. If not, do it.
# if [ ! -f $i/${i}_r16x16_s32x32_mag_filt_rr.grd ]; then

#  cd $i
#  echo $i
#  #vel=*r60x120_s100x200_mag.grd
#  vel_ew=`ls *r60x120_s100x200_eastxyz_filt.grd`
#  vel_ns=`ls *r60x120_s100x200_northxyz_filt.grd`

#  grdmask $glacier_outline -N1/NaN/NaN  -Goutside_ice.grd -R${vel_ew} -V
#  grdmask $rock_outline  -NNaN/NaN/1 -Ginside_rock.grd -R${vel_ew} -V

#  grdmath outside_ice.grd inside_rock.grd AND = off_ice.grd

#  grdmath $vel_ew off_ice.grd OR = vel_ew_off_ice.grd
#  grdmath $vel_ns off_ice.grd OR = vel_ns_off_ice.grd

#  grdclip vel_ew_off_ice.grd -Sa3/NaN -Sb-3/NaN -Gvel_ew_off_ice.grd -V
#  grdclip vel_ns_off_ice.grd -Sa3/NaN -Sb-3/NaN -Gvel_ns_off_ice.grd -V


#  python /data/akm/Python/removeTrendNoOutlines.py $vel_ew vel_ew_off_ice.grd -2.5 2.5
#  python /data/akm/Python/removeTrendNoOutlines.py $vel_ns vel_ns_off_ice.grd -2.5 2.5

#  grdmath ${vel_ew:0:29}_r60x120_s100x200_eastxyz_filt_rr.grd ${vel_ew:0:29}_r60x120_s100x200_northxyz_filt_rr.grd HYPOT = ${vel_ew:0:29}_r60x120_s100x200_mag_filt_rr.grd
#  dechunk ${vel_ew:0:29}_r60x120_s100x200_mag_filt_rr.grd

#  rm vel_ew_off_ice.grd vel_ns_off_ice.grd outside_ice.grd inside_rock.grd off_ice.grd

#  cd ..
 #fi

#done
