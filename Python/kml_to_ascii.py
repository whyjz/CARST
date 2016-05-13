#!/usr/bin/python

import re;
import sys;

name=sys.argv[1];

file=open(name,"r");

coords_str="";

while 1:
 line=file.readline().strip();
 if not line:
  break;
 if re.search("\d+\.*\d*\s*,\s*\d+\.*\d*",line):
  coords_str=line+"\n";

file.close();

coords=coords_str.split();

for item in coords:
 print(item.replace(","," "));

exit();
