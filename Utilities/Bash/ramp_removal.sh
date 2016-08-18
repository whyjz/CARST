
#!/bin/bash

# This script assigns all of the variables needed for ramp_removal.cmd located
# in CARST/Utils/Bash/ramp_removal.cmd

#CARST_DIR Needs to be defined as a global variable
# e.g., export CARST_DIR=/home/user/CARST
ice_outline=$1
rock_outline=$2


vel_ew=$3
vel_ns=$4

ls $vel_ew
grdmask $ice_outline -N1/NaN/NaN  -Goutside_ice.grd -R${vel_ew} -V
grdmask $rock_outline  -NNaN/NaN/1 -Ginside_rock.grd -R${vel_ew} -V

grdmath outside_ice.grd inside_rock.grd AND = off_ice.grd

grdmath $vel_ew off_ice.grd OR = vel_ew_off_ice.grd
grdmath $vel_ns off_ice.grd OR = vel_ns_off_ice.grd

grdclip vel_ew_off_ice.grd -Sa3/NaN -Sb-3/NaN -Gvel_ew_off_ice.grd -V
grdclip vel_ns_off_ice.grd -Sa3/NaN -Sb-3/NaN -Gvel_ns_off_ice.grd -V


python $CARST_DIR/Utilities/Python/removeTrendNoOutlines.py $vel_ew vel_ew_off_ice.grd -2.5 2.5
python $CARST_DIR/Utilities/Python/removeTrendNoOutlines.py $vel_ns vel_ns_off_ice.grd -2.5 2.5

grdmath  ${vel_ew%.grd}_rr.grd ${vel_ns%.grd}_rr.grd HYPOT --IO_NC4_CHUNK_SIZE=c = ${vel_ew%east*}mag_rr.grd

#clean up
rm *clipped* *off_ice* *outside_ice* *inside_rock*

