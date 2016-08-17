#!/usr/bin/python

import os;
import re;
import subprocess;
import sys;

step=sys.argv[1];

cdir=os.getcwd();

if step == "ers2raw":
 cmd="\nfind . -name \"ER0*.tar\"\n"; 
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 files=pipe.read().split();
 pipe.close();

 for item in files:
  directory=item[:item.rfind("/")];
  ers_file=item[item.rfind("/")+1:];
  cmd="\ncd "+directory+"\n";
  cmd+="\ntar xvf "+ers_file+"\n";
  cmd+="\ncd "+cdir+"\n";
  subprocess.call(cmd,shell=True);

elif step == "makeraw":
 cmd="\nfind . -name \"SAR*\"\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 files=pipe.read().split();
 pipe.close();

 for item in files:
  if item.find(".ps") > -1:
   cmd="\nrm "+item+"\n";
   subprocess.call(cmd,shell=True);
   continue;
  already_done=False;
  directory=item[:item.rfind("/")];
  contents=os.listdir(directory);
  for ers_file in contents:
   if re.search("\.raw$",ers_file):
    already_done=True;
  if already_done:
   continue;
  sar_file=item[item.rfind("/")+1:];
  cmd="\ncd "+directory+"\n";
  cmd+="\nperl /home/akm26/Documents/Russia/NovZ/ERS/make_raw_ers.pl ODR "+sar_file+" "+directory[directory.rfind("/")+1:]+"\n";
  cmd+="\ncd "+cdir+"\n";
  subprocess.call(cmd,shell=True);

elif step == "proc_int":
 
 cmd="\nls */*.raw\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 raws=pipe.read().split();
 pipe.close();

 dates=[];
 for raw in raws:
  date=raw[raw.rfind("/")+1:raw.rfind(".")];
  dates.append(date);

 for date1 in dates:
  for date2 in dates:
   if long(date1)-long(date2) == 1:
    int_dir="";
    if long(date1) > long(date2):
     int_dir="int_"+date1+"_"+date2;
    else:
     int_dir="int_"+date2+"_"+date1;
    if not os.path.exists(int_dir):
     cmd="\nmkdir "+int_dir+"\n";
     cmd+="\nmkdir "+int_dir+"/GEO\n";
     cmd+="\nmkdir "+int_dir+"/SIM\n";
     subprocess.call(cmd,shell=True);




