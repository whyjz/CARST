#! /bin/csh
# modified to run make_slc_tsx in $INT_BIN for release EJF 2013/5/10
# changed to use newer make_slc_csk program in $MY_BIN EJF 2012/08/21
# changed to use new version of make_raw_csk.py in $CSK_DIR EJF 2011/12/31
# modified for SLC products EJF 2011/7/1
# run Walter's make_raw_csk.py EJF 2011/01/10
# usage: make_slc_csk.csh CSK* $date

# modified by whyjay 2016/5/12

set scene=$1
set date=$2

# uses these libraries under Linux
#setenv LD_LIBRARY_PATH $BOOST_ROOT/lib:$HDF5_DIR/lib
setenv LC_ALL C    #whyjay

echo ====1st====
echo --- $scene
echo --- $date

#$INT_BIN/make_slc_tsx --input $scene --prefix $date             # whyjay
/home/matt/MY_BIN/make_slc_tsx --input $scene --prefix $date     # whyjay

echo ====2nd====

# need to do get_peg_info, etc.
#$INT_SCR/get_height.pl $date                                    # whyjay
/home/matt/MY_BIN/get_height.pl $date                            # whyjay

echo ====3rd====

# and take looks
$INT_SCR/look.pl $date.slc 16                                     # whyjay
#/home/matt/MY_BIN/look.pl $date.slc 16                           # whyjay
