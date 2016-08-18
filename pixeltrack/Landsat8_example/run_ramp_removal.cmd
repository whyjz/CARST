
#!/bin/bash

# This script assigns all of the variables needed for ramp_removal.cmd located
# in CARST/Utils/Bash/ramp_removal.cmd

export CARST_DIR=/data/wjd73/CARST
ice_outline=$PWD/OUTLINES/StEliasMtn_utm7v_ice.gmt
rock_outline=$PWD/OUTLINES/StEliasMtn_utm7v_rock.gmt


for vel_dir in `echo 20160803203709_20160718203706`
do

  cd $vel_dir

  U=`ls *r32x32_s32x32_eastxyz.grd`
  V=`ls *r32x32_s32x32_northxyz.grd`
  
  bash $CARST_DIR/Utilities/Bash/ramp_removal.sh $ice_outline $rock_outline $U $V

  cd ..
done

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
