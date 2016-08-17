#!/usr/bin/python

import math;
import numpy;
import scipy;
import subprocess;
from scipy.io import netcdf;

NUMDIF=3; # number of pixels within TOLERANCE required for noise removal
TOLERANCE="0.1"; # required tolerance for noise removal, 0.1 means within 10% of velmax
VEL="2.0";


eastxyz_grd_path="07182004104621_06152004082555_eastxyz.grd";
northxyz_grd_path="07182004104621_06152004082555_northxyz.grd";
mag_grd_path="07182004104621_06152004082555_mag.grd";


# Filtering and Noise Removal...

eastxyz_filtered_grd_path = eastxyz_grd_path.replace(".grd","_filtered.grd");
eastxyz_filtered_ps_path  = eastxyz_filtered_grd_path.replace("grd","ps");
northxyz_filtered_grd_path = northxyz_grd_path.replace(".grd","_filtered.grd");
northxyz_filtered_ps_path  = northxyz_filtered_grd_path.replace("grd","ps");
mag_filtered_grd_path = mag_grd_path.replace(".grd","_filtered.grd");
mag_filtered_ps_path  = mag_filtered_grd_path.replace("grd","ps");


# Read grid files

f=netcdf.netcdf_file(eastxyz_grd_path,"r",False);
x=f.variables["x"].data;
y=f.variables["y"].data;
eastvel=f.variables["z"].data[:];
f.close();

f=netcdf.netcdf_file(northxyz_grd_path,"r",False);
northvel=f.variables["z"].data[:];
f.close();

length=y.shape[0];
width=x.shape[0];

#eastvel=eastxyz.reshape(1,length*width);
#northvel=northxyz.reshape(1,length*width);


# Remove edges...

print("\nRemoving edges...\n");

eastvel[0,:] = scipy.nan;
northvel[0,:] = scipy.nan;

eastvel[:,0] = scipy.nan;
northvel[:,0] = scipy.nan;

eastvel[length-1,:] = scipy.nan;
northvel[length-1,:] = scipy.nan;

eastvel[:,width-1] = scipy.nan;
northvel[:,width-1] = scipy.nan;


# Remove unreasonably fast velocities...
print("\nRemoving unreasonably fast velocities...\n");
for i in range(1,length-1):
    for j in range(1,width-1):
        if abs(eastvel[i][j]) > float(VEL) or abs(northvel[i][j]) > float(VEL):
            eastvel[i][j]  = scipy.nan;
            northvel[i][j] = scipy.nan;

# Remove lone pixels recursively...
print("\nRemoving lone pixels recursively...\n");
loners = 1;
iterations = 0;

def remloners(eastvel,northvel,iterations,loners):
    '''function REMLONERS recursively removes lone pixels

    lone pixels are defined as pixels with NaN values on 3 or more sides
    
        eastvel  = east  velocities
        northvel = north velocities
        iterations = number of iterations so far
        loners = number of lone pixels found and removed during each iteration'''

    if loners > 0:
        loners = 0;
        iterations = iterations + 1;
        (xmax,ymax) = eastvel.shape;

        for i in range(1,xmax-1):
            for j in range(1,ymax-1):
                if not (math.isnan(eastvel[i][j]) and math.isnan(northvel[i][j])):
                    borders = 4;

                    if math.isnan(eastvel[i][j+1]) or math.isnan(northvel[i][j+1]):
                        borders = borders - 1;
                    if math.isnan(eastvel[i][j-1]) or math.isnan(northvel[i][j-1]):
                        borders = borders - 1;
                    if math.isnan(eastvel[i+1][j]) or math.isnan(northvel[i+1][j]):
                        borders = borders - 1;
                    if math.isnan(eastvel[i-1][j]) or math.isnan(northvel[i-1][j]):
                        borders = borders - 1;

                    if borders < 2:
                        # pixel i,j is a loner
                        eastvel[i][j]  = scipy.nan;
                        northvel[i][j] = scipy.nan;
                        loners = loners + 1;

        print("Successfully removed "+str(loners)+" lone pixels\n");

        (eastvel,northvel,iterations,loners) = remloners(eastvel,northvel,iterations,loners);

    return (eastvel,northvel,iterations,loners);

(eastvel,northvel,iterations,loners) = remloners(eastvel,northvel,iterations,loners);
print("aster_pixel_tracking.py ran through "+str(iterations)+" of remloners.py");

# Remove remaining noise...
print("\nRemoving remaining noise...\n");
noisy = 1;
iterations = 0;
span = float(VEL)*float(TOLERANCE);


def remnoise(eastvel,northvel,iterations,span,numdif,noisy):
    '''function REMNOISE recursively removes remaining noise
       
    noise is defined as pixels which have less than some required percentage of neighboring pixels which are within a specified tolerance
        eastvel  = east  velocities
        northvel = north velocities
        iterations = number of times remnoise has been run
        span   = +- range of velocities defined as "similar" enough
        numdif = number of pixels within tolerance required
        noisy  = number of noisy pixels found and removed during each iteration'''

    if noisy > 0:
        noisy = 0;
        iterations = iterations + 1;
        (xmax,ymax) = eastvel.shape;
        remlater=scipy.zeros((xmax,ymax));

        for i in range(1,xmax-1):
            for j in range(1,ymax-1):
                if (not math.isnan(eastvel[i][j])) or not (math.isnan(northvel[i][j])):

                    similarities = 0; # number of similar bordering pixels

                    if abs(abs(eastvel[i][j])-abs(eastvel[i+1][j])) < span and abs(abs(northvel[i][j])-abs(northvel[i+1][j])) < span:
                        similarities = similarities + 1;
                    if abs(abs(eastvel[i][j])-abs(eastvel[i-1][j])) < span and abs(abs(northvel[i][j])-abs(northvel[i-1][j])) < span:
                        similarities = similarities + 1;
                    if abs(abs(eastvel[i][j])-abs(eastvel[i][j+1])) < span and abs(abs(northvel[i][j])-abs(northvel[i][j+1])) < span:
                        similarities = similarities + 1;
                    if abs(abs(eastvel[i][j])-abs(eastvel[i][j-1])) < span and abs(abs(northvel[i][j])-abs(northvel[i][j-1])) < span:
                        similarities = similarities + 1;
                    if abs(abs(eastvel[i][j])-abs(eastvel[i+1][j+1])) < span and abs(abs(northvel[i][j])-abs(northvel[i+1][j+1])) < span:
                        similarities = similarities + 1;
                    if abs(abs(eastvel[i][j])-abs(eastvel[i+1][j-1])) < span and abs(abs(northvel[i][j])-abs(northvel[i+1][j-1])) < span:
                        similarities = similarities + 1;
                    if abs(abs(eastvel[i][j])-abs(eastvel[i-1][j+1])) < span and abs(abs(northvel[i][j])-abs(northvel[i-1][j+1])) < span:
                        similarities = similarities + 1;
                    if abs(abs(eastvel[i][j])-abs(eastvel[i-1][j-1])) < span and abs(abs(northvel[i][j])-abs(northvel[i-1][j-1])) < span:
                        similarities = similarities + 1;

                    if similarities <= numdif:
                        # pixel i,j is noisy
                        remlater[i][j]=1;
                        noisy = noisy + 1;

        for i in range(1,(xmax-1)):
            for j in range(1,(ymax-1)):
                if remlater[i][j] == 1:
                    eastvel[i][j]=scipy.nan;
                    northvel[i][j]=scipy.nan;

        print("Successfully removed "+str(noisy)+" noisy pixels\n");

        (eastvel,northvel,iterations,span,numdif,noisy) = remnoise(eastvel,northvel,iterations,span,numdif,noisy);

    return(eastvel,northvel,iterations,span,numdif,noisy);

(eastvel,northvel,iterations,span,numdif,noisy) = remnoise(eastvel,northvel,iterations,span,NUMDIF,noisy);
#print(span,numdif);
print("aster_pixel_tracking.py ran through "+str(iterations)+" of remnoise.py\n");

#cmd="\cp -p "+eastxyz_grd_path+" "+eastxyz_filtered_grd_path+"\n";
#cmd+="\cp -p "+northxyz_grd_path+" "+northxyz_filtered_grd_path+"\n";
#subprocess.call(cmd,shell=True);

out_f=netcdf.netcdf_file(eastxyz_filtered_grd_path,"w",True);
out_f.createDimension("x",x.shape[0]);
out_x=out_f.createVariable("x","f",("x",));
out_x[:]=x[:];
out_x._attributes["actual_range"]=scipy.array([x.min(), x.max()]);
out_f.createDimension("y",y.shape[0]);
out_y=out_f.createVariable("y","f",("y",));
out_y[:]=y[:];
out_y._attributes["actual_range"]=scipy.array([y.min(), y.max()]);
data_out=scipy.arange(x.shape[0]*y.shape[0]);
data_out.shape=(y.shape[0],x.shape[0]);
out_z=out_f.createVariable("z",scipy.dtype("float32").char,("y","x"));
out_z._attributes["actual_range"]=scipy.array([scipy.nanmin(eastvel), scipy.nanmax(eastvel)]);
out_z[:]=eastvel[:];
out_z._attributes["_FillValue"]="nan";
out_f.flush();
out_f.sync();
out_f.close();





exit();

# Write grid files...
cmd ="\nxyz2grd "+eastvel+" "+R+" -G"+eastxyz_filtered_grd_path+" -I120=\n";
cmd+="\nxyz2grd "+northvel+" "+R+" -G"+northxyz_filtered_grd_path+" -I120=\n";
subprocess.call(cmd,shell=True);

cmd ="\ngrdmath "+northxyz_filtered_grd_path+" "+eastxyz_filtered_grd_path+" HYPOT = "+mag_filtered_grd_path+"\n";
subprocess.call(cmd,shell=True);

cmd ="\ngrdimage "+northxyz_filtered_grd_path+" -Jx1:"+scale+" "+R+" -C"+vel_cpt_path+" -Q -P -K > "+northxyz_filtered_ps_path+"\n";
cmd+="\npsxy "+ICE+" -J -R -W1p,black -O -m >> "+northxyz_filtered_ps_path+"\n";
cmd+="\ngrdimage "+eastxyz_filtered_grd_path+" -Jx1:"+scale+" "+R+" -C"+vel_cpt_path+" -Q -P -K > "+eastxyz_filtered_ps_path+"\n";
cmd+="\npsxy "+ICE+" -J -R -W1p,black -O -m >> "+eastxyz_filtered_ps_path+"\n";
cmd+="\ngrdimage "+mag_filtered_grd_path+" -Jx1:"+scale+" "+R+" -C"+vel_cpt_path+" -Q -P -K > "+mag_filtered_ps_path+"\n";
cmd+="\npsxy "+ICE+" -J -R -W1p,black -O -m >> "+mag_filtered_ps_path+"\n";
subprocess.call(cmd,shell=True);


# Magnitude Calculation and Masking
eastxyz_filtered_masked_grd_path = eastxyz_filtered_grd_path.replace(".grd","_masked.grd");
eastxyz_filtered_masked_ps_path  = eastxyz_filtered_masked_grd_path.replace("grd","ps");
northxyz_filtered_masked_grd_path = northxyz_filtered_grd_path.replace(".grd","_masked.grd");
northxyz_filtered_masked_ps_path  = northxyz_filtered_masked_grd_path.replace("grd","ps");
mag_filtered_masked_grd_path = mag_filtered_grd_path.replace(".grd","_masked.grd");
mag_filtered_masked_ps_path  = mag_filtered_masked_grd_path.replace("grd","ps");
mask_grd_path=eastxyz_grd_path.replace("eastxyz","mask");

#cmd ="\ngrdmask "+ICE+" -R"+mag_grd_path+" -NNaN/NaN/1 -G"+mask_grd_path+" -m\n";
#cmd+="\ngrdmath "+eastxyz_filtered_grd_path+" "+mask_grd_path+" OR = "+eastxyz_filtered_masked_grd_path+"\n";
#cmd+="\ngrdmath "+northxyz_filtered_grd_path+" "+mask_grd_path+" OR = "+northxyz_filtered_masked_grd_path+"\n";
#cmd+="\ngrdmath "+mag_filtered_grd_path+" "+mask_grd_path+" OR = "+mag_filtered_masked_grd_path+"\n";
#subprocess.call(cmd,shell=True);

#cmd ="\ngrdimage "+eastxyz_filtered_masked_grd_path+" -Jx1:"+scale+" "+R+" -C"+vel_cpt_path+" -Q -P > "+eastxyz_filtered_masked_ps_path+"\n";
#cmd+="\ngrdimage "+northxyz_filtered_masked_grd_path+" -Jx1:"+scale+" "+R+" -C"+vel_cpt_path+" -Q -P > "+northxyz_filtered_masked_ps_path+"\n";
#cmd+="\ngrdimage "+mag_filtered_masked_grd_path+" -Jx1:"+scale+" "+R+" -C"+vel_cpt_path+" -Q -P > "+mag_filtered_masked_ps_path+"\n";
#subprocess.call(cmd,shell=True);


print("\nPair Separation = "+str(day_sep)+" days\n");

print("\nPixel Tracking is complete\n");

exit();


