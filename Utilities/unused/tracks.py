#!/usr/bin/python

import sys;

extent=[34.,38.,94.,96.,0.5];

print(extent);

x=extent[0];
y=extent[2];

while 1:
 if x > extent[3]:
  break;
 while 1:
 x=x+extent[4];

sys.exit();
