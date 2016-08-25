#!/usr/bin/python

import os;
import re;
import subprocess;
import sys;

DATA_TYPE="ALOS";

cmd="\nls\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
list=pipe.read().split();
pipe.close();

if DATA_TYPE.lower().find("alos") > -1:
 search_str="\s\d{20}\s";

for item in list:
 if not re.search("^led",item.lower()):
  continue;
 item=item.strip();
 file = open(item,"rb");
 while 1:
  line = file.readline();
  if not line:
   break;
  if re.search(search_str,line):
   line=line[re.search(search_str,line).start(0):re.search(search_str,line).end(0)].strip();
   date=line[2:8];
   if not os.path.exists(date):
    cmd="\nmkdir "+date+"\n";
    subprocess.call(cmd,shell=True);
   index=re.search("\d",item).start(0);
   track=item[index:index+9];
   cmd="\nmv *"+track+"*H1* "+date+"\n"; 
   subprocess.call(cmd,shell=True);

 file.close();

cmd="\nls\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
list=pipe.read().split();
pipe.close();

dates=[];
for item in list:
 if re.search("^\d{6}",item):
  item=item.strip();
  dates.append(item);
  cmd="\nls "+item+"\n";
  pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
  out=pipe.read().lower().split();
  pipe.close();
  raw_present=False;
  for file_name in out:
   if re.search("\.raw$",file_name):
    raw_present=True;
    break;
  if not raw_present:
   wc_code="";
   for file_name in out:
    if re.search("^img.*hv.*",file_name): 
     wc_code="FBD2FBS";
     break;
   cmd="\ncd "+item+"\nmake_raw_alos.pl IMG "+item+" "+wc_code+"\ncd ..\n";
   subprocess.call(cmd,shell=True);

exit();

dates.sort(reverse=True);
for i in range(0,len(dates)):
 for j in range(i+1,len(dates)):
  int_dir="int_"+dates[i]+"_"+dates[j];
  if not os.path.exists(int_dir):
   cmd="\nmkdir "+int_dir+"\ncd "+int_dir+"\nmkdir GEO\nmkdir SIM\n";
   subprocess.call(cmd,shell=True);
  if not os.path.exists(int_dir+".proc"):
   out_file=open(int_dir+".proc","w");
   out_file.write("SarDir1="+dates[i]+"\n");
   out_file.write("SarDir2="+dates[j]+"\n");
   out_file.write("IntDir=int_"+dates[i]+"_"+dates[j]+"\n");
   out_file.write("SimDir=int_"+dates[i]+"_"+dates[j]+"/SIM\n");
   out_file.write("GeoDir=int_"+dates[i]+"_"+dates[j]+"/GEO\n");
   out_file.write("flattening         = topo \n");
   out_file.write("\n");
   out_file.write("FilterStrength     = 0.4\n");
   out_file.write("UnwrappedThreshold = 0.05\n");
   out_file.write("Threshold_mag      = 0.0\n");
   out_file.write("Threshold_ph_grd   = 0.0\n");
   out_file.write("Rlooks_int         = 4\n");
   out_file.write("Rlooks_unw         = 16 \n");
   out_file.write("Rlooks_sim         = 4\n");
   out_file.write("Rlooks_geo         = 4 \n");
   out_file.write("pixel_ratio        = 2 \n");
   out_file.write("BaslineOrder       = QUAD\n");
   out_file.write("\n");
   out_file.write("OrbitType=HDR\n");
   out_file.close();

cmd="\nls .\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
list=pipe.read().split();
pipe.close();

for item in list:
 if re.search("^int_",item) and not re.search("\.proc",item):
  item=item.strip();
  cmd="\nls "+item+"\n";
  pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
  out=pipe.read();
  pipe.close();
  if not re.search("baseline",out) and os.path.exists(item+".proc"):
   cmd="\nprocess_2pass.pl "+item+".proc raw orbbase\n";
   subprocess.call(cmd,shell=True);

exit();
