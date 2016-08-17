#!/usr/bin/python

import subprocess;

HIREZ="/home/akm26/Documents/Juneau/HiRez/KMLs";
GLACIERS="/home/akm26/Documents/Juneau/GLIMS/Glaciers/Working";
UTM_ZONE="8V";

cmd="\nls "+HIREZ+"/*.kml\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
kmls=pipe.read().split();
pipe.close();

cmd="\nls "+GLACIERS+"/*Glacier_UTM.dat\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
glaciers=pipe.read().split();
pipe.close();

for kml in kmls:
 cmd="\ngrep coordinates "+kml+"\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 line=pipe.read().strip();
 pipe.close();
 line=line[line.find(">")+1:line.find("</")].replace(" ","\n");
 cmd="echo \""+line+"\" | mapproject -Ju8V/1:1 -F -C\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 coords=pipe.read().strip();
 pipe.close();
 name=kml[kml.rfind("/")+1:kml.find(".kml")]+".dat";
 outfile=open(name,"w");
 outfile.write(coords+"\n>\n");
 outfile.close();
 for glacier in glaciers:
  cmd="\ngmtselect "+glacier+" -F"+name+" -m\n";
  pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
  output=pipe.read().strip();
  pipe.close();
  if len(output) > 0 and glacier.find("Unnamed") < 0:
   print(name+" "+glacier+" "+str(len(output)));

exit();
