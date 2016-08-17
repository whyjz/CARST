#!/usr/bin/python

import os;
import re;
import subprocess;
import sys;

tar_dir=sys.argv[1];

if os.path.isdir(tar_dir):
 find_tars_cmd="\nfind "+tar_dir+" -name \"*.tar\" -print\n";
 pipe=subprocess.Popen(find_tars_cmd,shell=True,stdout=subprocess.PIPE).stdout;
 tars_list=pipe.read().split();
 pipe.close();
 #j=0;
 for tar in tars_list:
  tar_subdir=tar[0:tar.rfind("/")];
  current_dir=os.getcwd();
  subprocess.call("\ncd "+tar_subdir+"\n",shell=True);
  tar_subdir_contents=os.listdir(tar_subdir);
  tar_subdir_contents_hash={}
  for item in tar_subdir_contents:
   tar_subdir_contents_hash[item]=item;
  uncompress_tar_cmd="\ntar -xf "+tar+"\n";
  subprocess.call(uncompress_tar_cmd,shell=True);
  find_xml_cmd="\nfind "+tar_subdir+" \( -name \"*.xml\" -o -name \"*.XML\" \) -print\n";
  pipe=subprocess.Popen(find_xml_cmd,shell=True,stdout=subprocess.PIPE).stdout;
  xml_list=pipe.read().split();
  pipe.close();
  if len(xml_list) < 1:
   new_tar_subdir_contents=os.listdir(tar_subdir);
   for item in new_tar_subdir_contents:
    if not item in tar_subdir_contents_hash:
     rm_tar_item_cmd="\nrm -r "+item+"\n";
     subprocess.call(rm_tar_item_cmd,shell=True);
   subprocess.call("\ncd "+current_dir+"\n",shell=True);
   continue;
  xml_path=xml_list[0];
  i=1;
  while re.search("README",xml_path):
   if len(xml_list) > i:
    xml_path=xml_list[i];
    i+=1;
   else:
    break;
  if re.search("README",xml_path):
   new_tar_subdir_contents=os.listdir(tar_subdir);
   for item in new_tar_subdir_contents:
    if not item in tar_subdir_contents_hash:
     rm_tar_item_cmd="\nrm -r "+item+"\n";
     subprocess.call(rm_tar_item_cmd,shell=True);
   subprocess.call("\ncd "+current_dir+"\n",shell=True);
   continue;
  xml_file=open(xml_path,"r");
  coords=8;
  ul_lon="";
  ul_lat="";
  ll_lon="";
  ll_lat="";
  ur_lon="";
  ur_lat="";
  lr_lon="";
  lr_lat="";
  for line in xml_file:
   if re.search("ULLAT",line):
    index1=re.search("<ULLAT>",line).end(0);
    index2=re.search("</ULLAT>",line).start(0);
    ul_lat=line[index1:index2];
    coords-=1;
   elif re.search("ULLON",line):
    index1=re.search("<ULLON>",line).end(0);
    index2=re.search("</ULLON>",line).start(0);
    ul_lon=line[index1:index2];
    coords-=1;
   elif re.search("URLAT",line):
    index1=re.search("<URLAT>",line).end(0);
    index2=re.search("</URLAT>",line).start(0);
    ur_lat=line[index1:index2];
    coords-=1;
   elif re.search("URLON",line):
    index1=re.search("<URLON>",line).end(0);
    index2=re.search("</URLON>",line).start(0);
    ur_lon=line[index1:index2];
    coords-=1;
   elif re.search("LRLAT",line):
    index1=re.search("<LRLAT>",line).end(0);
    index2=re.search("</LRLAT>",line).start(0);
    lr_lat=line[index1:index2];
    coords-=1;
   elif re.search("LRLON",line):
    index1=re.search("<LRLON>",line).end(0);
    index2=re.search("</LRLON>",line).start(0);
    lr_lon=line[index1:index2];
    coords-=1;
   elif re.search("LLLAT",line):
    index1=re.search("<LLLAT>",line).end(0);
    index2=re.search("</LLLAT>",line).start(0);
    ll_lat=line[index1:index2];
    coords-=1;
   elif re.search("LLLON",line):
    index1=re.search("<LLLON>",line).end(0);
    index2=re.search("</LLLON>",line).start(0);
    ll_lon=line[index1:index2];
    coords-=1;
   if coords == 0:
    break;
  xml_file.close();
  if coords != 0:
   new_tar_subdir_contents=os.listdir(tar_subdir);
   for item in new_tar_subdir_contents:
    if not item in tar_subdir_contents_hash:
     rm_tar_item_cmd="\nrm -r "+item+"\n";
     subprocess.call(rm_tar_item_cmd,shell=True);
   subprocess.call("\ncd "+current_dir+"\n",shell=True);
   continue;
  find_jpg_cmd="\nfind "+tar_subdir+" \( -name \"*.jpg\" -o -name \"*.JPG\" -o -name \"*.jpeg\" -o -name \"*.JPEG\" \) -print\n";
  pipe=subprocess.Popen(find_jpg_cmd,shell=True,stdout=subprocess.PIPE).stdout;
  jpg_list=pipe.read().split();
  pipe.close();
  jpg_path="";
  for item in jpg_list:
   if re.search("browse",item.lower()) and not re.search("trimmed",item.lower()):
    jpg_path=item;
  if jpg_path == "":
   new_tar_subdir_contents=os.listdir(tar_subdir);
   for item in new_tar_subdir_contents:
    if not item in tar_subdir_contents_hash:
     rm_tar_item_cmd="\nrm -r "+item+"\n";
     subprocess.call(rm_tar_item_cmd,shell=True);
   subprocess.call("\ncd "+current_dir+"\n",shell=True);
   continue;
  jpg_name=jpg_path[jpg_path.rfind("/")+1:];
  cp_jpg_cmd="\ncp "+jpg_path+" "+jpg_name+"\n";
  subprocess.call(cp_jpg_cmd,shell=True);
  jpg_trim_name=jpg_name[0:jpg_name.lower().rfind(".jpg")]+"_trimmed.jpg";
  jpg_trim_cmd="\nconvert -trim "+jpg_name+" "+jpg_trim_name+"\n";
  subprocess.call(jpg_trim_cmd,shell=True);
  tar_subdir_contents_hash[jpg_trim_name]=jpg_trim_name;
  if float(ul_lat) < float(ll_lat):
   temp_lat=ul_lat;
   temp_lon=ul_lon;
   ul_lat=ll_lat;
   ul_lon=ll_lon;
   ll_lat=temp_lat;
   ll_lon=temp_lon;
  if float(ur_lat) < float(lr_lat):
   temp_lat=ur_lat;
   temp_lon=ur_lon;
   ur_lat=lr_lat;
   ur_lon=lr_lon;
   lr_lat=temp_lat;
   lr_lon=temp_lon;
  if float(ul_lon) > float(ur_lon):
   temp_lat=ul_lat;
   temp_lon=ul_lon;
   ul_lat=ur_lat;
   ul_lon=ur_lon;
   ur_lat=temp_lat;
   ur_lon=temp_lon;
  if float(ll_lon) > float(lr_lon):
   temp_lat=ll_lat;
   temp_lon=ll_lon;
   ll_lat=lr_lat;
   ll_lon=lr_lon;
   lr_lat=temp_lat;
   lr_lon=temp_lon;
  kml_file=open(tar[tar.rfind("/")+1:tar.rfind(".")]+".kml","w");
  kml_file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
  kml_file.write("<kml xmlns=\"http://earth.google.com/kml/2.1\"\n");
  kml_file.write(" xmlns:gx=\"http://www.google.com/kml/ext/2.2\">\n");
  kml_file.write("<Document>\n");
  kml_file.write("<name>"+tar[tar.rfind("/")+1:tar.rfind(".")]+"</name>\n");
  kml_file.write("<open>1</open>\n");
  kml_file.write("<GroundOverlay>\n");
  kml_file.write("<name>"+tar[tar.rfind("/")+1:tar.rfind(".")]+"</name>\n");
  kml_file.write("<description>"+tar[tar.rfind("/")+1:tar.rfind(".")]+"</description>\n");
  kml_file.write("<Icon>\n");
  kml_file.write("<href>"+jpg_trim_name+"</href>\n");
  kml_file.write("<viewBoundScale>0.75</viewBoundScale>\n");
  kml_file.write("</Icon>\n");
  kml_file.write("<gx:LatLonQuad>\n");
  kml_file.write("<coordinates>"+ll_lon+","+ll_lat+" "+lr_lon+","+lr_lat+" "+ur_lon+","+ur_lat+" "+ul_lon+","+ul_lat+"</coordinates>\n");
  kml_file.write("</gx:LatLonQuad>\n");
  kml_file.write("</GroundOverlay>\n");
  kml_file.write("</Document>\n");
  kml_file.write("</kml>\n");
  kml_file.close();
  tar_subdir_contents_hash[tar[tar.rfind("/")+1:tar.rfind(".")]+".kml"]=tar[tar.rfind("/")+1:tar.rfind(".")]+".kml";
  new_tar_subdir_contents=os.listdir(tar_subdir);
  for item in new_tar_subdir_contents:
   if not item in tar_subdir_contents_hash:
    rm_tar_item_cmd="\nrm -r "+item+"\n";
    subprocess.call(rm_tar_item_cmd,shell=True);
  subprocess.call("\ncd "+current_dir+"\n",shell=True);
  #j+=1;
  #if j == 2:
  # break;
else:
 print("\""+tar_dir+"\" is not an existing directory\n");

exit;
