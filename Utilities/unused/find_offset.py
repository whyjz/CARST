#!/usr/bin/python

import math;
import sys;

#First input is reference "hdr" file, second input is search "hdr" file

ref_img=sys.argv[1];
search_img=sys.argv[2];

ref_img_samples="";
ref_img_lines="";
search_img_samples="";
search_img_lines="";
firstHDR = ref_img;
secondHDR = search_img;
firstHDRFile = open(firstHDR,"r");
secondHDRFile = open(secondHDR,"r");
firstUTM1="";
firstUTM2="";
secondUTM1="";
secondUTM2="";
for line in firstHDRFile:
 if line.find("samples") > -1:
  info = line.split("=");
  ref_img_samples = info[1].strip();
 elif line.find("lines") > -1:
  info = line.split("=");
  ref_img_lines = info[1].strip();
 elif line.find("map info") > -1:
  info = line.split();
  firstUTM1 = info[6].replace(",","");
  firstUTM2 = info[7].replace(",","");
firstHDRFile.close();
for line in secondHDRFile:
 if line.find("samples") > -1:
  info = line.split("=");
  search_img_samples = info[1].strip();
 elif line.find("lines") > -1:
  info = line.split("=");
  search_img_lines = info[1].strip();
 if line.find("map info") > -1:
  info = line.split();
  secondUTM1 = info[6].replace(",","");
  secondUTM2 = info[7].replace(",","");
secondHDRFile.close();
# Change "15.0" to whatever the resolution is of the images you are trying to correlate
utm_offset1=(float(firstUTM1)-float(secondUTM1))/15.0;
utm_offset2=(float(secondUTM2)-float(firstUTM2))/15.0;
#utm_offset1=(float(firstUTM1)-float(secondUTM1))/0.5;
#utm_offset2=(float(secondUTM2)-float(firstUTM2))/0.5;
#utm_offset1=(float(firstUTM1)-float(secondUTM1))/0.48709659351;
#utm_offset2=(float(secondUTM2)-float(firstUTM2))/0.48709659351;
if utm_offset1%1 < 0.5:
 utm_offset1=int(math.floor(utm_offset1));
else:
 utm_offset1=int(math.ceil(utm_offset1));
if utm_offset2%1 < 0.5:
 utm_offset2=int(math.floor(utm_offset2));
else:
 utm_offset2=int(math.ceil(utm_offset2));
ul_long="";
ul_lat="";
erence_window_size_samples=32;
erence_window_size_lines=32;
ref_img_start_sample="";
ref_img_start_line="";
ref_img_end_sample=ref_img_samples;
ref_img_end_line=ref_img_lines;
if utm_offset1 < 0:
 ref_img_start_sample=str(abs(utm_offset1)+1);
else:
 ref_img_start_sample="1";
 ref_img_end_sample=str(int(ref_img_samples)-utm_offset1+erence_window_size_samples);
if utm_offset2 < 0:
 ref_img_start_line=str(abs(utm_offset2)+1);
else:
 ref_img_start_line="1";
 ref_img_end_line=str(int(ref_img_lines)-utm_offset2+erence_window_size_lines);

print("Start, End Lines in Reference Image: "+ref_img_start_line+" "+ref_img_end_line);
print("Start, End Samples in Reference Image: "+ref_img_start_sample+" "+ref_img_end_sample);
print("Mean Offset Between Reference and Search Images Samples/Lines: "+str(utm_offset1)+" "+str(utm_offset2));

exit();
