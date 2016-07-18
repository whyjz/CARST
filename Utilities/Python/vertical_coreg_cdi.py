#!/usr/bin/python

import math;
import os;
import re;
import subprocess;
import sys;

GDAL="/home/akm26/Downloads/gdal-1.7.2/apps/";
ICE="/home/akm26/Documents/CDI/GLIMS/Glaciers/CDI_UTM_ICE.dat";
ROCK="/home/akm26/Documents/CDI/GLIMS/Glaciers/CDI_UTM_ROCK.dat";
UTM_ZONE="19F";
SRTM="/home/akm26/Documents/CDI/SRTM/SRTM_CDI_clipped.grd";
SRTM_ROCK_MASK="/home/akm26/Documents/CDI/SRTM/SRTM_CDI_clipped_rock_mask.grd";
RESOLUTION="90";
# Low bound set to 30 because height of Lago Fagnano is 28 m
LOW_BOUND="30";
# High bound set to 3000 because maximum height of SRTM is 2556 m
HIGH_BOUND="3000";

def main():
 cmd="\ngmtset D_FORMAT %.8f\n";
 subprocess.call(cmd,shell=True);
 cmd="\ngrdinfo "+SRTM+"\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 info=pipe.read();
 pipe.close();
 srtm_min_x=info[re.search("x_min: ",info).end(0):re.search("x_min: \d+\.*\d*",info).end(0)];
 srtm_max_x=info[re.search("x_max: ",info).end(0):re.search("x_max: \d+\.*\d*",info).end(0)];
 srtm_min_y=info[re.search("y_min: ",info).end(0):re.search("y_min: \d+\.*\d*",info).end(0)];
 srtm_max_y=info[re.search("y_max: ",info).end(0):re.search("y_max: \d+\.*\d*",info).end(0)];
 if not os.path.exists(SRTM_ROCK_MASK):
  cmd="\ngrdmask "+ICE+" -F -Gice_complement.grd -R"+SRTM+" -I"+RESOLUTION+" -N1/NaN/NaN -m\n";
  cmd+="\ngrdmask "+ROCK+" -F -Grock_in_ice.grd -R"+SRTM+" -I"+RESOLUTION+" -NNaN/NaN/1 -m\n";
  cmd+="\ngrdmath rock_in_ice.grd ice_complement.grd AND = "+SRTM_ROCK_MASK+"\n";
  cmd+="\nrm rock_in_ice.grd ice_complement.grd\n";
  subprocess.call(cmd,shell=True);
 dir=sys.argv[1];
 for line in os.listdir(dir):
  line=line.strip();
  if re.search("^coreg_to_landsat_\d{14}_DEM$",line):
   name=line[re.search("\d{14}",line).start(0):re.search("\d{14}",line).end(0)];
   print(name);
   if os.path.exists(name+"_final_trend_removed.grd"):
    print(name+"_final_trend_removed.grd already exists");
    continue;
   index=len(line);
   if line.rfind(".") > -1:
    index=line.rfind(".");
   grd_name=line[:index]+".grd";
   if not os.path.exists(grd_name):
    cmd="\n"+GDAL+"gdal_translate -of GMT "+dir+"/"+line+" "+grd_name+"\n";
    subprocess.call(cmd,shell=True);
   cleaned_grd=line+"_cleaned.grd";
   if not os.path.exists(cleaned_grd):
    cmd="\ngrdclip "+grd_name+" -Sb"+LOW_BOUND+"/NaN -Sa"+HIGH_BOUND+"/NaN -G"+cleaned_grd+"\n";
    subprocess.call(cmd,shell=True);
   cmd="\ngrdinfo "+cleaned_grd+"\n";
   pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
   info=pipe.read();
   pipe.close();
   min_x=info[re.search("x_min: ",info).end(0):re.search("x_min: \d+\.*\d*",info).end(0)];
   max_x=info[re.search("x_max: ",info).end(0):re.search("x_max: \d+\.*\d*",info).end(0)];
   min_y=info[re.search("y_min: ",info).end(0):re.search("y_min: \d+\.*\d*",info).end(0)];
   max_y=info[re.search("y_max: ",info).end(0):re.search("y_max: \d+\.*\d*",info).end(0)];
   new_min_x=srtm_min_x;
   new_max_x=srtm_max_x;
   new_min_y=srtm_min_y;
   new_max_y=srtm_max_y;
   if min_x > srtm_min_x:
    new_min_x=str(-math.floor((float(srtm_min_x)-float(min_x))/float(RESOLUTION))*float(RESOLUTION)+float(srtm_min_x));
    new_min_x=new_min_x[:new_min_x.rfind(".")]+srtm_min_x[srtm_min_x.rfind("."):];
   if max_x < srtm_max_x:
    new_max_x=str(float(srtm_max_x)-math.ceil((float(srtm_max_x)-float(max_x))/float(RESOLUTION))*float(RESOLUTION));
    new_max_x=new_max_x[:new_max_x.rfind(".")]+srtm_max_x[srtm_max_x.rfind("."):];
   if min_y > srtm_min_y:
    new_min_y=str(-math.floor((float(srtm_min_y)-float(min_y))/float(RESOLUTION))*float(RESOLUTION)+float(srtm_min_y));
    new_min_y=new_min_y[:new_min_y.rfind(".")]+srtm_min_y[srtm_min_y.rfind("."):];
   if max_y < srtm_max_y:
    new_max_y=str(float(srtm_max_y)-math.ceil((float(srtm_max_y)-float(max_y))/float(RESOLUTION))*float(RESOLUTION));
    new_max_y=new_max_y[:new_max_y.rfind(".")]+srtm_max_y[srtm_max_y.rfind("."):];
   R="-R"+new_min_x+"/"+new_max_x+"/"+new_min_y+"/"+new_max_y;
   #Using grdfilter instead of grdsample per p.c. Paul Wessel
   cmd="\ngrdfilter "+cleaned_grd+" -D0 -Fg"+RESOLUTION+" -I"+RESOLUTION+" -G"+cleaned_grd[:cleaned_grd.find(".grd")]+"_filt.grd\n";
   subprocess.call(cmd,shell=True);
   cleaned_grd=cleaned_grd[:cleaned_grd.find(".grd")]+"_filt.grd";
   if new_min_x == srtm_min_x:
    new_min_x=str(long(srtm_min_x[:srtm_min_x.find(".")])+1);
   if new_max_x == srtm_max_x:
    new_max_x=srtm_max_x[:srtm_max_x.find(".")];
   if new_min_y == srtm_min_y:
    new_min_y=str(long(srtm_min_y[:srtm_min_y.find(".")])+1);
   if new_max_y == srtm_max_y:
    new_max_y=srtm_max_y[:srtm_max_y.find(".")];
   R="-R"+new_min_x+"/"+new_max_x+"/"+new_min_y+"/"+new_max_y;
   cmd="\ngrdcut "+SRTM+" -G"+name+"_SRTM.grd "+R+"\n";
   cmd+="\ngrdcut "+SRTM_ROCK_MASK+" "+R+" -Gbedrock_only.grd\n";
   cmd+="\ngrdmath "+cleaned_grd+" bedrock_only.grd MUL = "+name+"_bedrock_only.grd\n";
   cmd+="\ngrdmath "+name+"_SRTM.grd bedrock_only.grd MUL = "+name+"_SRTM_bedrock_only.grd\n";
   cmd+="\ngrdclip "+name+"_SRTM_bedrock_only.grd -Sb"+LOW_BOUND+"/NaN -Sa"+HIGH_BOUND+"/NaN -G"+name+"_SRTM_bedrock_only.grd\n";
   print(cmd);
   subprocess.call(cmd,shell=True);
   cmd="\ngrdinfo "+name+"_SRTM_bedrock_only.grd\n";
   pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
   grdinfo=pipe.read();
   pipe.close();
   max_z_index1=re.search("z_max: ",grdinfo).end(0);
   max_z_index2=max_z_index1+re.search("\s",grdinfo[max_z_index1:]).start(0);
   max_z=grdinfo[max_z_index1:max_z_index2].strip();
   #Clip ASTER bedrock elevations again based on max z value in SRTM
   cmd="\ngrdclip "+name+"_bedrock_only.grd -Sa"+str(float(max_z)+50)+"/NaN -G"+name+"_bedrock_only.grd\n";
   cmd+="\ngrdmath "+name+"_bedrock_only.grd "+name+"_SRTM_bedrock_only.grd SUB = "+name+"_SRTM_bedrock_only_sub.grd\n";
   cmd+="\ngrdmath "+name+"_SRTM_bedrock_only_sub.grd MEAN = test\n";
   subprocess.call(cmd,shell=True);
   cmd="\ngrdinfo test\n";
   pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
   grdinfo=pipe.read();
   pipe.close();
   mean_index1=re.search("z_min: ",grdinfo).end(0);
   mean_index2=mean_index1+re.search("\s",grdinfo[mean_index1:]).start(0);
   mean=grdinfo[mean_index1:mean_index2];
   cmd="\ngrd2xyz "+name+"_SRTM_bedrock_only_sub.grd | gawk '{print $3}' | pshistogram -JX7i/5i -W1 -Gblack > "+name+"_first_diff_hist.ps\n";
   cmd+="\nmakecpt -Cpanoply -T-100/100/1 -I > diff.cpt\n";
   cmd+="\ngrdimage "+name+"_SRTM_bedrock_only_sub.grd -JX7i -Cdiff.cpt > "+name+"_first_diff.ps\n";
   cmd+="\ngrdclip "+name+"_SRTM_bedrock_only_sub.grd -Sa100/NaN -Sb-100/NaN -G"+name+"_SRTM_bedrock_only_sub.grd\n";
   cmd+="\ngrd2xyz "+name+"_SRTM_bedrock_only_sub.grd | gawk '{print $3}' | pshistogram -JX7i/5i -W1 -Gblack > "+name+"_after_first_clip_hist.ps\n";
   cmd+="\ngrdimage "+name+"_SRTM_bedrock_only_sub.grd -JX7i -Cdiff.cpt > "+name+"_after_first_clip.ps\n";
   subprocess.call(cmd,shell=True);
   counter=0;
   mean="";
   while counter < 10:
    cmd="\ngrdmath "+name+"_SRTM_bedrock_only_sub.grd MEAN = test\n";
    subprocess.call(cmd,shell=True);
    cmd="\ngrdinfo test\n";
    pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
    grdinfo=pipe.read();
    pipe.close();
    mean_index1=re.search("z_min: ",grdinfo).end(0);
    mean_index2=mean_index1+re.search("\s",grdinfo[mean_index1:]).start(0);
    mean=grdinfo[mean_index1:mean_index2];
    cmd="\ngrdmath "+name+"_SRTM_bedrock_only_sub.grd STD = test\n";
    subprocess.call(cmd,shell=True);
    cmd="\ngrdinfo test\n";
    pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
    grdinfo=pipe.read();
    pipe.close();
    std_index1=re.search("z_min: ",grdinfo).end(0);
    std_index2=std_index1+re.search("\s",grdinfo[std_index1:]).start(0);
    sigma=grdinfo[std_index1:std_index2];
    print("Current Mean Difference: "+mean);
    print("Standard Deviation: "+sigma);
    sigmaplus=str(float(mean)+2*float(sigma));
    sigmaminus=str(float(mean)-2*float(sigma));
    #Clip difference grid at +/- 2 standar deviations from mean of difference grid
    cmd="\ngrdclip "+name+"_SRTM_bedrock_only_sub.grd -Sb"+sigmaminus+"/NaN -Sa"+sigmaplus+"/NaN -G"+name+"_SRTM_bedrock_only_sub_cleaned.grd\n";
    if os.path.exists("bedrock_clipped_trend.grd") and not os.path.exists("bedrock_clipped_trend_final.grd"):
     cmd+="\nmv bedrock_clipped_trend.grd bedrock_clipped_trend_final.grd\n";
    #Fit planar trend to difference grid
    cmd+="\ngrdtrend "+name+"_SRTM_bedrock_only_sub_cleaned.grd -N3 -Tbedrock_clipped_trend.grd -V\n";
    if os.path.exists("bedrock_clipped_trend.grd") and os.path.exists("bedrock_clipped_trend_final.grd"):
     cmd+="\ngrdmath bedrock_clipped_trend_final.grd bedrock_clipped_trend.grd ADD = bedrock_clipped_trend_final.grd\n";
    if os.path.exists(name+"_AST_br_trend_3sigma_removed.grd"):
     cmd+="\ngrdmath "+name+"_AST_br_trend_3sigma_removed.grd bedrock_clipped_trend.grd SUB = "+name+"_ASTER_bedrock_only_sub.grd\n";
    else:
     cmd+="\ngrdmath "+name+"_bedrock_only.grd bedrock_clipped_trend.grd SUB = "+name+"_ASTER_bedrock_only_sub.grd\n"; 
    cmd+="\ngrdmath "+name+"_ASTER_bedrock_only_sub.grd "+name+"_SRTM_bedrock_only_sub_cleaned.grd OR = "+name+"_AST_br_trend_3sigma_removed.grd\n";
    cmd+="\ngrdmath "+name+"_AST_br_trend_3sigma_removed.grd "+name+"_SRTM_bedrock_only.grd SUB = "+name+"_SRTM_bedrock_only_sub.grd\n";
    subprocess.call(cmd,shell=True);
    counter+=1;
   cmd="\ngrdmath "+cleaned_grd+" bedrock_clipped_trend_final.grd SUB = "+name+"_final_trend_removed.grd\n";
   cmd+="\ngrdimage "+name+"_SRTM_bedrock_only_sub.grd -JX7i -Cdiff.cpt > "+name+"_last_diff.ps\n";
   cmd+="\ngrd2xyz "+name+"_SRTM_bedrock_only_sub.grd | gawk '{print $3}' | pshistogram -JX7i/5i -W1 -Gblack > "+name+"_final_bedrock_diff_hist.ps\n";
   cmd+="\ngrd2xyz "+name+"_final_trend_removed.grd | gawk '{print $3}' | pshistogram -JX7i/5i -W1 -Gblack > "+name+"_final_diff_hist.ps\n";
   cmd+="\ngrdmath "+cleaned_grd+" "+name+"_SRTM.grd SUB = "+name+"_final_diff.grd\n";
   cmd+="\ngrdimage "+name+"_final_diff.grd -JX7i -Cdiff.cpt > "+name+"_final_diff.ps\n";
   cmd+="\ngrdmath "+name+"_final_trend_removed.grd "+name+"_SRTM.grd SUB = "+name+"_final_trend_removed_diff.grd\n";
   cmd+="\ngrdimage "+name+"_final_trend_removed_diff.grd -JX7i -Cdiff.cpt > "+name+"_final_trend_removed_diff.ps\n";
   cmd+="\nrm bedrock* test ice_* "+cleaned_grd+"\n";
   subprocess.call(cmd,shell=True); 

if __name__ == "__main__":
 main();

exit;
