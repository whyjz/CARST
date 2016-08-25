#!/usr/bin/python

import sys;

name1=sys.argv[1];
name2=sys.argv[2];

file1=open(name1,"r");
file2=open(name2,"r");

for line1 in file1:
 line1=line1.strip();
 line2=file2.readline();
 line2=line2.strip();
 print(line1+" "+line2);

file1.close();
file2.close();

sys.exit();
