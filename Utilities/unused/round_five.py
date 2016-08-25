#!/usr/bin/python

import sys;

num=float(sys.argv[1]);

if num%5 != 0:
 num=num-num%5+5;

print(int(num));

exit();
