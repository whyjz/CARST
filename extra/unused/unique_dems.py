import sys;

name=sys.argv[1];

infile=open(name,"r");
for line in infile:
 if line.find(">") < 0:
  continue;
 line=line.strip();
 elements=line.split();
 julian_days=elements[3];
 
infile.close();


exit();
