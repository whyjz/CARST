#!/usr/bin/python

import sys;

hv_dates={};
date="";
file=open("hvornot.txt","r");
for line in file:
 if line.find(":") > -1:
  date=line;
 if line.find("HV") > -1:
  if not date in hv_dates:
   hv_dates[date[:6]]=date[:6];
file.close();

print(hv_dates);

sys.exit();
