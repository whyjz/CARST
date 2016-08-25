#/usr/bin/python

import re;
import subprocess;

cmd="\nfind . -name \"*nti21_cut.grd\"\n";
pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
ntis=pipe.read().split();
pipe.close();

for nti in ntis:
 jday=nti[nti.find(".A")+6:nti.find(".A")+9];
 vdir=nti[nti.find("/")+1:nti.rfind("/")];
 image="data_more/"+nti[nti.rfind("/")+1:nti.find("_cut")]+".grd";
 cmd="\ngrdinfo "+nti+"\n";
 pipe=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
 info=pipe.read().strip();
 pipe.close();
 zmax=info[re.search("z_max:\s*",info).end(0):re.search("z_max:\s*\S*\s*",info).end(0)].strip();
 if zmax != "0":
  print(jday+" "+zmax+" "+vdir+" "+image);
 #if zmax != "0" and float(zmax) > -0.861:
  #print(nti+" "+zmax);


exit();

"""



exit();
"""
