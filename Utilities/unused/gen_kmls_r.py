#!/usr/bin/python

import math;
import os;
import re;
import subprocess;
import sys;

UTM_ZONE="18F";

def makeKML(name):
 cmd="\ngrep \"grdimage\" "+name+".ps\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 info=pipe.read();
 pipe.close();
 print(info);
 #xmin=info[re.search("-R",info).end(0):re.search("-R\d+\.*\d*",info).end(0)].strip();
 #xmax=info[re.search("-R\d+\.*\d*/",info).end(0):re.search("-R\d+\.*\d*/\d+\.*\d*",info).end(0)].strip();
 #ymin=info[re.search("-R\d+\.*\d*/\d+\.*\d*/",info).end(0):re.search("-R\d+\.*\d*/\d+\.*\d*/\d+\.*\d*",info).end(0)].strip();
 #ymax=info[re.search("-R\d+\.*\d*/\d+\.*\d*/\d+\.*\d*/",info).end(0):re.search("-R\d+\.*\d*/\d+\.*\d*/\d+\.*\d*/\d+\.*\d*",info).end(0)].strip();
 xmin=info[re.search("-R",info).end(0):re.search("-R\d+\.*\d*",info).end(0)].strip();
 ymin=info[re.search("-R\d+\.*\d*/",info).end(0):re.search("-R\d+\.*\d*/\d+\.*\d*",info).end(0)].strip();
 xmax=info[re.search("-R\d+\.*\d*/\d+\.*\d*/",info).end(0):re.search("-R\d+\.*\d*/\d+\.*\d*/\d+\.*\d*",info).end(0)].strip();
 ymax=info[re.search("-R\d+\.*\d*/\d+\.*\d*/\d+\.*\d*/",info).end(0):re.search("-R\d+\.*\d*/\d+\.*\d*/\d+\.*\d*/\d+\.*\d*",info).end(0)].strip();
 ul_lat=ymax;
 ul_long=xmin;
 ll_lat=ymin;
 ll_long=ul_long;
 lr_lat=ll_lat;
 lr_long=xmax;
 ur_lat=ul_lat;
 ur_long=lr_long;
 utm_file=open("utm_coords.txt","w");
 utm_file.write(ul_long+","+ul_lat+"\n"+ll_long+","+ll_lat+"\n"+lr_long+","+lr_lat+"\n"+ur_long+","+ur_lat);
 utm_file.close();
 mapproject_cmd="\nmapproject utm_coords.txt -Ju"+UTM_ZONE+"/1:1 -F -C -I --D_FORMAT=%.8f\n";
 pipe=subprocess.Popen(mapproject_cmd,shell=True,stdout=subprocess.PIPE).stdout;
 geo_coords=pipe.read().split();
 pipe.close();
 os.remove("utm_coords.txt");
 cmd="\ngrep \" -P\" "+name+".ps\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 info=pipe.read();
 pipe.close();
 kml_file=open(name+".kml","w");
 kml_file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
 kml_file.write("<kml xmlns=\"http://earth.google.com/kml/2.1\"\n");
 kml_file.write(" xmlns:gx=\"http://www.google.com/kml/ext/2.2\">\n");
 kml_file.write("<Document>\n");
 kml_file.write("<name>"+name+"</name>\n");
 kml_file.write("<open>1</open>\n");
 kml_file.write("<GroundOverlay>\n");
 kml_file.write("<name>"+name+"</name>\n");
 kml_file.write("<description>"+name+"</description>\n");
 kml_file.write("<Icon>\n");
 kml_file.write("<href>"+name+".png</href>\n");
 kml_file.write("<viewBoundScale>0.75</viewBoundScale>\n");
 kml_file.write("</Icon>\n");
 kml_file.write("<gx:LatLonQuad>\n");
 if info.find(" -P") > -1:
  if float(geo_coords[2]) > 180.0:
   kml_file.write("<coordinates>"+str(-360.0+float(geo_coords[2]))+","+geo_coords[3]+" "+str(-360.0+float(geo_coords[4]))+","+geo_coords[5]+" "+str(-360.0+float(geo_coords[6]))+","+geo_coords[7]+" "+str(-360.0+float(geo_coords[0]))+","+geo_coords[1]+"</coordinates>\n");
  else:
   kml_file.write("<coordinates>"+geo_coords[2]+","+geo_coords[3]+" "+geo_coords[4]+","+geo_coords[5]+" "+geo_coords[6]+","+geo_coords[7]+" "+geo_coords[0]+","+geo_coords[1]+"</coordinates>\n");
 else:
  if float(geo_coords[2]) > 180.0:
   kml_file.write("<coordinates>"+str(-360.0+float(geo_coords[0]))+","+geo_coords[1]+" "+str(-360.0+float(geo_coords[2]))+","+geo_coords[3]+" "+str(-360.0+float(geo_coords[4]))+","+geo_coords[5]+" "+str(-360.0+float(geo_coords[6]))+","+geo_coords[7]+"</coordinates>\n");
  else:
   kml_file.write("<coordinates>"+geo_coords[0]+","+geo_coords[1]+" "+geo_coords[2]+","+geo_coords[3]+" "+geo_coords[4]+","+geo_coords[5]+" "+geo_coords[6]+","+geo_coords[7]+"</coordinates>\n");
 kml_file.write("</gx:LatLonQuad>\n");
 kml_file.write("</GroundOverlay>\n");
 kml_file.write("</Document>\n");
 kml_file.write("</kml>\n");
 kml_file.close();
 return;

psfile=sys.argv[1];
name=psfile[:psfile.rfind(".")];

png=name+".png";
if not os.path.exists(png):
 cmd="\ngrep \" -P\" "+name+".ps\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 info=pipe.read();
 pipe.close();
 if info.find(" -P") > -1:
  cmd="\nps2raster -A -P -TG "+psfile+"\n";
 else:
  cmd="\nps2raster -A -TG "+psfile+"\n";
 subprocess.call(cmd,shell=True);
if not os.path.exists(name+".kml"):
 makeKML(name);

exit;
