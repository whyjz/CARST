#!/usr/bin/python

import subprocess;
import sys;

PATH="/home/emgolos/ICESAT/";
points={};
edge_points=[];

cmd="\nfind "+PATH+" -name \"*_List*\"\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
lists=pipe.read().split();
pipe.close();

thresh="0.000277";

for item in lists:
 print(item);
 area=item[:item.rfind("/")];
 infile=open(item,"r");
 for entry in infile:
  if entry.strip() == "":
   continue;
  print(entry);
  j=0;
  datfile=open(area+"/"+entry.strip(),"r");
  for line in datfile:
   if j > 9:
    continue;
   edge=False;
   line=line.strip();
   elements=line.split();
   hash_entry=elements[6]+" "+elements[5]+" ";
   for i in range(0,5):
    hash_entry+=elements[i]+" ";
   for i in range(7,len(elements)):
    hash_entry+=elements[i]+" ";
   hash_entry=hash_entry.strip();
   lon=elements[6].strip();
   lon_range_up=lon;
   lon_range_down=lon;
   lon_hash=lon;
   index=lon.rfind(".")+3;
   if index > 0 and index < len(lon):
    lon_hash=lon_hash[:index];
    lon_range_up=str(float(lon)+float(thresh));
    lon_range_down=str(float(lon)-float(thresh));
    if lon_range_up[:index] != lon_hash or lon_range_down[:index] != lon_hash:
     edge=True;
   lat=elements[5].strip();
   lat_range_up=lat;
   lat_range_down=lat;
   lat_hash=lat;
   index=lat.rfind(".")+3;
   if index > 0 and index < len(lat):
    lat_hash=lat_hash[:index];
    lat_range_up=str(float(lat)+float(thresh));
    lat_range_down=str(float(lat)-float(thresh));
    if lat_range_up[:index] != lat_hash or lat_range_down[:index] != lat_hash:
     edge=True;
   #hash_entry=hash_entry+" "+lon_range_up+" "+lon_range_down+" "+lat_range_up+" "lat
   if edge:
    edge_points.append(hash_entry);
    continue;
   key=lon_hash+" "+lat_hash;
   if key not in points:
    points[key]=hash_entry;
   else:
    points[key]=points[key]+"\n"+hash_entry;
   j=j+1;
  datfile.close();
 infile.close();

close_points={};
entries=[];
for key in points:
  entries=points[key].split("\n");
  i=0;
  for i in range(0,len(entries)):
   elements=entries[i].strip().split();
   lon=elements[0].strip();
   lat=elements[1].strip();
   for j in range(i+1,len(entries)):
    elements=entries[j].strip().split();
    other_lon=elements[0].strip();
    other_lat=elements[1].strip();
    distance=((float(lon)-float(other_lon))**2+(float(lat)-float(other_lat))**2)**0.5;
    if distance <= float(thresh):
     key=lon+" "+lat;
     if key not in close_points:
      close_points[lon+" "+lat]=entries[j].strip();
     else:
      close_points[lon+" "+lat]+="\n"+entries[j].strip();
     key=other_lon+" "+other_lat;
     if key not in close_points:
      close_points[other_lon+" "+other_lat]=entries[i].strip();
     else:
      close_points[other_lon+" "+other_lat]+="\n"+entries[i].strip();

for key in close_points:
 print(close_points[key]);

exit();

