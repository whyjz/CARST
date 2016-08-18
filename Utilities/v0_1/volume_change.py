#!/usr/bin/python

import sys;

# Accumulation report
ac=sys.argv[1];
# Ablation report
ab=sys.argv[2];
# Accumulation uncertainties
ac_unc=sys.argv[3];
# Ablation uncertainties
ab_unc=sys.argv[4];

vol=0.0;
area=0.0;
act_vol=0.0;
act_area=0.0;
vol_ac=0.0;
area_ac=0.0;
act_vol_ac=0.0;
act_area_ac=0.0;
vol_ab=0.0;
area_ab=0.0;
act_vol_ab=0.0;
act_area_ab=0.0;
vol_unc=0.0;
area_unc=0.0;
act_vol_unc=0.0;
act_area_unc=0.0;
vol_ac_unc=0.0;
area_ac_unc=0.0;
act_vol_ac_unc=0.0;
act_area_ac_unc=0.0;
vol_ab_unc=0.0;
area_ab_unc=0.0;
act_vol_ab_unc=0.0;
act_area_ab_unc=0.0;

infile=open(ac,"r");
for line in infile:
 if line.find("Accumulation") > -1 and line.find("nan") < 0:
  elements=line.split();
  area_ac=area_ac+float(elements[1]);
  vol_ac=vol_ac+float(elements[3]);
  act_area_ac=act_area_ac+float(elements[2]);
  act_vol_ac=act_vol_ac+float(elements[4]);
infile.close();

vol=vol+vol_ac;
area=area+area_ac;
act_vol=act_vol+act_vol_ac;
act_area=act_area+act_area_ac;

infile=open(ab,"r");
for line in infile:
 if line.find("Ablation") > -1 and line.find("nan") < 0:
  elements=line.split();
  area_ab=area_ab+float(elements[1]);
  vol_ab=vol_ab+float(elements[3]);
  act_area_ab=act_area_ab+float(elements[2]);
  act_vol_ab=act_vol_ab+float(elements[4]);
infile.close();

vol=vol+vol_ab;
area=area+area_ab;
act_vol=act_vol+act_vol_ab;
act_area=act_area+act_area_ab;

infile=open(ac_unc,"r");
for line in infile:
 if line.find("Accumulation") > -1 and line.find("nan") < 0:
  elements=line.split();
  area_ac_unc=area_ac_unc+float(elements[1]);
  vol_ac_unc=vol_ac_unc+float(elements[3]);
  act_area_ac_unc=act_area_ac_unc+float(elements[2]);
  act_vol_ac_unc=act_vol_ac_unc+float(elements[4]);
infile.close();

vol_unc=vol_unc+vol_ac_unc;
area_unc=area_unc+area_ac_unc;
act_vol_unc=act_vol_unc+act_vol_ac_unc;
act_area_unc=act_area_unc+act_area_ac_unc;

infile=open(ab_unc,"r");
for line in infile:
 if line.find("Ablation") > -1 and line.find("nan") < 0:
  elements=line.split();
  area_ab_unc=area_ab_unc+float(elements[1]);
  vol_ab_unc=vol_ab_unc+float(elements[3]);
  act_area_ab_unc=act_area_ab_unc+float(elements[2]);
  act_vol_ab_unc=act_vol_ab_unc+float(elements[4]);
infile.close();

vol_unc=vol_unc+vol_ab_unc;
area_unc=area_unc+area_ab_unc;
act_vol_unc=act_vol_unc+act_vol_ab_unc;
act_area_unc=act_area_unc+act_area_ab_unc;

print("Accumulation (using basin average to fill in basins): "+str(area_ac/1000000.)+" "+str(vol_ac/1000000000.)+" "+str(1.96*vol_ac_unc/(area_ac_unc/(810.*810.))**0.5/1000000000));
print("Accumulation (actual coverage): "+str(act_area_ac/1000000.)+" "+str(act_vol_ac/1000000000.)+" "+str(1.96*act_vol_ac_unc/(act_area_ac_unc/(810.*810.))**0.5/1000000000));

print("Ablation (using basin average to fill in basins): "+str(area_ab/1000000.)+" "+str(vol_ab/1000000000.)+" "+str(1.96*vol_ab_unc/(area_ab_unc/(810.*810.))**0.5/1000000000));
print("Ablation (actual coverage): "+str(act_area_ab/1000000.)+" "+str(act_vol_ab/1000000000.)+" "+str(1.96*act_vol_ab_unc/(act_area_ab_unc/(810.*810.))**0.5/1000000000));

print("Icefield (using basin average to fill in basins): "+str(area/1000000.)+" "+str(vol/1000000000.)+" "+str(1.96*vol_unc/(area_unc/(810.*810.))**0.5/1000000000));
print("Icefield (actual coverage): "+str(act_area/1000000.)+" "+str(act_vol/1000000000.)+" "+str(1.96*act_vol_unc/(act_area_unc/(810.*810.))**0.5/1000000000));

exit();
