#!/usr/bin/python

import subprocess;
import sys;

SEARCH_X="200";
SEARCH_Y="200";
REF_X="100";
REF_Y="100";
STEP="30";

reference=sys.argv[1];
search=sys.argv[2];
nproc=sys.argv[3];

ref_hdr=reference[:reference.rfind(".")]+".hdr";
search_hdr=search[:search.rfind(".")]+".hdr";

ref_samples="";
ref_lines="";

infile=open(ref_hdr,"r");
for line in infile:
 if line.find("samples") > -1:
  elements=line.split();
  ref_samples=elements[len(elements)-1].strip();
 if line.find("lines") > -1:
  elements=line.split();
  ref_lines=elements[len(elements)-1].strip();
infile.close();

search_samples="";
search_lines="";

infile=open(search_hdr,"r");
for line in infile:
 if line.find("samples") > -1:
  elements=line.split();
  search_samples=elements[len(elements)-1].strip();
 if line.find("lines") > -1:
  elements=line.split();
  search_lines=elements[len(elements)-1].strip();
infile.close();

cmd="\npython find_offset.py "+ref_hdr+" "+search_hdr+"\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
output=pipe.read().strip().split();
pipe.close();

mean_x=output[4];
mean_y=output[5];

for i in range(1,int(nproc)+1):
 lines_proc=int(ref_lines)/int(nproc)/int(REF_Y)*int(REF_Y);

 yoffset=0;
 if int(mean_y) < 0:
  yoffset=-1*int(mean_y);

 firstline=str((i-1)*lines_proc+1+int(REF_Y)/2+yoffset);
 lastline=str(int(firstline)+lines_proc-1);

 firstpix="1";
 if int(mean_x) < 0:
  firstpix=str(1-int(mean_x));

 outfile=open("ampcor_aster_"+str(i)+".in","w");
 outfile.write("                  AMPCOR INPUT FILE\n");
 outfile.write("\n");
 outfile.write("DATA TYPE\n");
 outfile.write("\n");
 outfile.write("Data Type for Reference Image Real or Complex                   (-)    =  Real   ![Complex , Real]\n");
 outfile.write("Data Type for Search Image Real or Complex                      (-)    =  Real   ![Complex , Real]\n");
 outfile.write("\n");
 outfile.write("INPUT/OUTPUT FILES\n");
 outfile.write("\n");
 outfile.write("Reference Image Input File                                      (-)    =  "+reference+"\n");
 outfile.write("Search Image Input File                                         (-)    =  "+search+"\n");
 outfile.write("Match Output File                                               (-)    =  ampcor_aster_"+str(i)+".off\n");
 outfile.write("\n");
 outfile.write("MATCH REGION\n");
 outfile.write("\n");
 outfile.write("Number of Samples in Reference/Search Images                    (-)    =  "+ref_samples+" "+search_samples+"\n");
 outfile.write("Start, End and Skip Lines in Reference Image                    (-)    =  "+firstline+" "+lastline+" "+STEP+"\n");
 outfile.write("Start, End and Skip Samples in Reference Image                  (-)    =  "+firstpix+" "+ref_samples+" "+STEP+"\n");
 outfile.write("\n");
 outfile.write("MATCH PARAMETERS\n");
 outfile.write("\n");
 outfile.write("Reference Window Size Samples/Lines                             (-)    = "+REF_X+" "+REF_Y+"\n");
 outfile.write("Search Pixels Samples/Lines                                     (-)    = "+SEARCH_X+" "+SEARCH_Y+"\n");
 outfile.write("Pixel Averaging Samples/Lines                                   (-)    =  1 1\n");
 outfile.write("Covariance Surface Oversample Factor and Window Size            (-)    =  64 16\n");
 outfile.write("Mean Offset Between Reference and Search Images Samples/Lines   (-)    =  "+mean_x+" "+mean_y+"\n");
 outfile.write("\n");
 outfile.write("MATCH THRESHOLDS AND DEBUG DATA\n");
 outfile.write("\n");
 outfile.write("SNR and Covariance Thresholds                                   (-)    =  0 10000000000\n");
 outfile.write("Debug and Display Flags T/F                                     (-)    =  f f\n");
 outfile.close();

exit();
