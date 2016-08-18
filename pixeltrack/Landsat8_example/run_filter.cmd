#!/bin/bash

# This file sets things up to run the matlab post-filter
# Please use the same parameter file that was used for running the pixel-tracking script
# e.g., bash run_filter.cmd params.txt

export CARST_DIR=/data/wjd73/CARST

params_file=$1

# Evaluate the variables assigned in params_file
while read var_name
do
  eval `echo $var_name | sed 's/ //g'`
done < $params_file

for vel_dir in `echo 20160803203709_20160718203706`
do
  cd $vel_dir

  U=`ls *r32x32_s32x32_eastxyz.grd`
  V=`ls *r32x32_s32x32_northxyz.grd`
  echo $U $V
  pwd
  echo "addpath('$CARST_DIR/Utilities/Matlab'); noiseremoval($VEL_MAX, $TOL, $NUMDIF, '$U', '$V')"
  matlab -r -nodisplay -nojvm "addpath('$CARST_DIR/Utilities/Matlab'); noiseremoval($VEL_MAX, $TOL, $NUMDIF, '$U', '$V');"
 
  cd ..    
done
    
   
    


