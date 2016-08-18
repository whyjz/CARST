#!/usr/bin/python

import subprocess;
import sys;

date=sys.argv[1];

cmd="\ndate +\"%s\" -d \"1858-11-17 00:00:00\"\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
julian_date=pipe.read();
pipe.close();
julian_date=julian_date.strip();

seconds=str(float(date)*60.*60.*24.+float(julian_date));

cmd="\ndate +%m%d%Y%H%M%S -d \"UTC 1970-01-01 "+str(seconds)+" secs\"\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
date=pipe.read();
pipe.close();

print(date);

exit();
