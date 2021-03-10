#!/usr/bin/python

import os;
import re;
import subprocess;

infile=open("volcano_list.txt","r");

for line in infile:
 line=line.strip();
 elements=line.split();
 lat=elements[0].strip();
 lon=elements[1].strip();
 flat=float(lat);
 flon=float(lon);
 R="-R"+str(flon-0.1)+"/"+str(flon+0.1)+"/"+str(flat-0.1)+"/"+str(flat+0.1);
 lat=lat.replace("-","");
 lat=lat.replace(".","");
 lon=lon.replace("-","");
 lon=lon.replace(".","");
 lat=lat+"S";
 lon=lon+"W";
 vdir="NTIs/Volcano"+lat+lon;
 if not os.path.exists(vdir):
  cmd="\nmkdir "+vdir+"\n";
  subprocess.call(cmd,shell=True);
 #cmd="\nls Data/geo*nti21*grd\n";
 cmd="\nls nti/geo*nti22*grd\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 images=pipe.read().strip().split();
 pipe.close();
 for image in images:
  grid=vdir+"/"+image[image.rfind("/"):image.rfind(".grd")]+"_cut.grd";
  jday=grid[grid.rfind("/"):][19:22]; 
  cmd="\ngrdcut "+image+" "+R+" -G"+grid+"\n";
  subprocess.call(cmd,shell=True);
  if os.path.exists(grid):
   cmd="\ngrdinfo "+grid+"\n";
   pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
   info=pipe.read().strip();
   pipe.close();
   zmax=info[re.search("z_max:\s*",info).end(0):re.search("z_max:\s*\S*\s*",info).end(0)].strip();
   if zmax != "0":
    print(jday+" "+zmax+" "+vdir+" "+image);


infile.close();

exit();
