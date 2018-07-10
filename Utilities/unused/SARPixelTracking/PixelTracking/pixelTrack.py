import sys
import os
import re
import math
import fileinput
import time
import calendar
import subprocess

def adjustPhase(fileName,wavelength,width):
 newFileName = fileName;
 index = fileName.rfind("/");
 radarUNWFile = open(fileName, 'rb');
 radarUNWData = scipy.matrix(numpy.fromfile(radarUNWFile,numpy.float32,-1)).reshape(int(width),-1);
 radarUNWData = radarUNWData * float(wavelength) / 4 / numpy.pi;
 radarUNWFile.close();
 if index > -1:
  newFileName = fileName[0:index+1] + "new_" + fileName[index+1:];
 else:
  newFileName = "new_" + fileName;
 radarUNWData = scipy.matrix(radarUNWData,scipy.float32);
 radarUNWData.tofile(newFileName);
 radarUNWData = None;
 return(newFileName);

def ampcor(path,rwin,awin,wsamp,numproc):
 currentDir = os.getcwd();
 cullFindCmd = "find " + path + " -name \"*_cull.off\" -print";
 cullFindStream = os.popen(cullFindCmd);
 cullFindOutput = cullFindStream.read();
 cullFindStream.close();
 cullFindPaths = cullFindOutput.split();
 for i in range(0,len(cullFindPaths)):
  cullFileName = cullFindPaths[i].strip()[cullFindPaths[i].rfind("/")+1:];
  index1 = re.search("\d{6}",cullFileName).start(0);
  index2 = re.search("\d{6}",cullFileName).end(0);
  index3 = re.search("\d{6}",cullFileName[index2:]).start(0)+index2;
  index4 = re.search("\d{6}",cullFileName[index2:]).end(0)+index2;
  date2 = cullFileName[index1:index2];
  date1 = cullFileName[index3:index4];
  findSlc1Cmd = "find " + path + " -name \"" + date1 + ".slc\" -print";
  findSlc1Stream = os.popen(findSlc1Cmd);
  findSlc1Output = findSlc1Stream.read();
  findSlc1Stream.close();
  findSlc1Paths = findSlc1Output.split();
  if len(findSlc1Paths) < 1:
   print("\n***** ERROR, could not find \"" + date1 + ".slc\" anywhere in \"" + RawRawFolder + "\"\n");
   break;
  slc1 = findSlc1Paths[0].strip();
  findSlc2Cmd = "find " + path + " -name \"" + date2 + ".slc\" -print";
  findSlc2Stream = os.popen(findSlc2Cmd);
  findSlc2Output = findSlc2Stream.read();
  findSlc1Stream.close();
  findSlc2Paths = findSlc2Output.split();i
  if len(findSlc2Paths) < 1:
   print("\n***** ERROR, could not find \"" + date2 + ".slc\" anywhere in \"" + RawRawFolder + "\"\n");
   break;
  slc2 = findSlc2Paths[0].strip();
  modAzoCmd = "\ncp -pr azo.pl " + cullFindPaths[i][0:cullFindPaths[i].rfind("/")] + "\n";
  modAzoStream = os.popen(modAzoCmd);
  modAzoStream.close();
  copyAzoMergeCmd = "\ncp -pr azo_merge.pl " + cullFindPaths[i][0:cullFindPaths[i].rfind("/")] + "\n";
  copyAzoMergeStream = os.popen(copyAzoMergeCmd);
  copyAzoMergeStream.close();
  if CPXorRMG == "RMG":
   for line in fileinput.FileInput(cullFindPaths[i][0:cullFindPaths[i].rfind("/")] + "/azo.pl",inplace=1):
    if re.search("Real\sor\sComplex\s+.*=\s+Complex",line):
     temp = re.compile("=\s+Complex");
     line = temp.sub("=  RMG1",line);
    print(line.strip());
   slc1rscFile = open(slc1+".rsc","r");
   while 1:
    line = slc1rscFile.readline();
    if not line:
     break;
    if line.find("FILE_LENGTH") > -1:
     endRefLine = line.split()[1].strip();
    elif line.find("WIDTH") > -1:
     endRefSample = line.split()[1].strip();
   slc1rscFile.close();
   cpxToRmgCmd="";
   if not os.path.exists(slc1[0:slc1.rfind(".")]+".rmg"):
    cpxToRmgCmd = "\ncpx2rmg " + slc1 + " " + slc1[0:slc1.rfind(".")] + ".rmg " + endRefSample + " " + endRefLine + "\n";
   slc2rscFile = open(slc2+".rsc","r");
   while 1:
    line = slc2rscFile.readline();
    if not line:
     break;
    if line.find("FILE_LENGTH") > -1:
     endRefLine = line.split()[1].strip();
    elif line.find("WIDTH") > -1:
     endRefSample = line.split()[1].strip();
   slc2rscFile.close();
   if not os.path.exists(slc2[0:slc2.rfind(".")]+".rmg"):
    cpxToRmgCmd += "\ncpx2rmg " + slc2 + " " + slc2[0:slc2.rfind(".")] + ".rmg " + endRefSample + " " + endRefLine + "\n";
   cpxToRmgCmd += "\ncp -pr " + slc1 + ".rsc " + slc1[0:slc1.rfind(".")] + ".rmg.rsc\n";
   cpxToRmgCmd += "\ncp -pr " + slc2 + ".rsc " + slc2[0:slc2.rfind(".")] + ".rmg.rsc\n";
   #cpxToRmgStream = os.popen(cpxToRmgCmd);
   #cpxToRmgStream.close();
   #pipe = subprocess.Popen(cpxToRmgCmd, shell=True, stdout=subprocess.PIPE).stdout;
   #pipe.close();
   os.system(cpxToRmgCmd);
   slc1 = slc1[0:slc1.rfind(".")] + ".rmg";
   slc2 = slc2[0:slc2.rfind(".")] + ".rmg";
  ampCmd = "\ncd " + cullFindPaths[i][0:cullFindPaths[i].rfind("/")] + "\n";
  ampCmd += "\nperl azo.pl " + slc2 + " " + slc1 + " " + cullFileName[0:cullFileName.rfind(".")] + " " + cullFileName[index1:index4] + "_azo_" + wsamp + "_ " + rwin + " " + awin + " " + wsamp + " " + numproc + "\n";
  ampCmd += "\nperl azo_merge.pl " + cullFileName[index1:index4] + "_azo_" + wsamp + "_" + rwin + "x" + awin + "\n";
  ampCmd += "\ncd " + currentDir + "\n";
  ampStream = os.popen(ampCmd);
  ampStream.close();
 return;

def makeUNW(path,rwin,awin,wsamp):
 findAmpcorInCmd = "\nfind " + path + " -name \"*"+rwin+"x"+awin+".off.bin\" -print\n";
 findAmpcorInStream = os.popen(findAmpcorInCmd);
 findAmpcorInOutput = findAmpcorInStream.read().split();
 findAmpcorInStream.close();
 for i in range(0,len(findAmpcorInOutput)):
  ampcorDir = findAmpcorInOutput[i].strip()[0:findAmpcorInOutput[i].strip().rfind("/")];
  ampcorName = findAmpcorInOutput[i].strip()[0:findAmpcorInOutput[i].strip().rfind(".off")];
  azoRscsCmd = "\nls " + ampcorName[0:ampcorName.rfind("azo")+3]+"*.off.rsc\n";
  azoRscsStream = os.popen(azoRscsCmd);
  azoRscs = azoRscsStream.read().split();
  azoRscsStream.close();
  if len(azoRscs) < 1:
   print("\n***** WARNING, could not find any azo rsc file in \"" + amcporDir + "\", skipping these results\n");
   break; 
  azoRscFile = open(azoRscs[0].strip(),"r");
  da_p = "";
  r_e = "";
  p_h = "";
  dr = "";
  endRefSample = "";
  endRefLine = "";
  while 1:
   line = azoRscFile.readline();
   if not line:
    break;
   elif line.find("RANGE_PIXEL_SIZE") > -1:
    dr = line.split()[1].strip();
   elif line.find("FILE_LENGTH") > -1:
    endRefLine = line.split()[1].strip();
   elif line.find("WIDTH") > -1:
    endRefSample = line.split()[1].strip();
   elif line.find("EARTH_RADIUS") > -1:
    r_e = line.split()[1].strip();
   elif re.search("^HEIGHT\s+",line):
    p_h = line.split()[1].strip();
   elif line.find("AZIMUTH_PIXEL_SIZE") > -1:
    da_p = line.split()[1].strip();
  azoRscFile.close();
  if da_p == "":
   print("\n***** WARNING, could not find parameter \"FILE_LENGTH\" in \"" + azoRscs[0].strip() + "\", skipping these results\n");
   break;
  if da_p == "":
   print("\n***** WARNING, could not find parameter \"WIDTH\" in \"" + azoRscs[0].strip() + "\", skipping these results\n");
   break;
  if da_p == "":
   print("\n***** WARNING, could not find parameter \"AZIMUTH_PIXEL_SIZE\" in \"" + azoRscs[0].strip() + "\", skipping these results\n");
   break;
  if r_e == "":
   print("\n***** WARNING, could not find parameter \"EARTH_RADIUS\" in \"" + azoRscs[0].strip() + "\", skipping these results\n");
   break;
  if p_h == "":
   print("\n***** WARNING, could not find parameter \"HEIGHT\" in \"" + azoRscs[0].strip() + "\", skipping these results\n");
   break;
  if dr == "":
   print("\n***** WARNING, could not find parameter \"RANGE_PIXEL_SIZE\" in \"" + azoRscs[0].strip() + "\", skipping these results\n");
   break;
  try: PYTHON
  except NameError:
   print("\n***** WARNING, \"PYTHON\" not set in parameter file\nCannot make UNW files");
   break;
  try: PyPacks
  except NameError:
   print("\n***** WARNING, \"PyPacks\" not set in parameter file\nCannot make UNW files");
   break;
  genericLoadMakeAzo = PYTHON + "/generic_load_make_azo.py";
  if not os.path.exists(genericLoadMakeAzo):
   print("\n***** WARNING, could not find \"" + genericLoadMakeAzo + "\", cannot make UNW files\n");
   return;
  outputLoadMakeAzo = ampcorDir + "/" + genericLoadMakeAzo[genericLoadMakeAzo.rfind("/")+1:].replace("generic_","");
  genericLoadMakeAzoFile = open(genericLoadMakeAzo,"r");
  outputLoadMakeAzoFile = open(outputLoadMakeAzo,"w");
  while 1:
   line = genericLoadMakeAzoFile.readline();
   if not line:
    break;
   elif re.search("path\.append",line):
    outputLoadMakeAzoFile.write(line.replace("''","'"+PyPacks+"'"));
    break;
   else:
    outputLoadMakeAzoFile.write(line);
  while 1:
   line = genericLoadMakeAzoFile.readline();
   if not line:
    break;
   elif re.search("inpre\s*=\s*\"\"\s*;",line):
    outputLoadMakeAzoFile.write(line.replace("\"\";","\""+ampcorName+".off.bin\";"));
    break;
   else:
    outputLoadMakeAzoFile.write(line);
  while 1:
   line = genericLoadMakeAzoFile.readline();
   if not line:
    break;
   elif re.search("wsamp\s*=\s*;",line):
    outputLoadMakeAzoFile.write(line.replace(";",wsamp+";"));
    break;
   else:
    outputLoadMakeAzoFile.write(line);
  while 1:
   line = genericLoadMakeAzoFile.readline();
   if not line:
    break;
   elif re.search("rwin\s*=\s*;",line):
    outputLoadMakeAzoFile.write(line.replace(";",rwin+";"));
    break;
   else:
    outputLoadMakeAzoFile.write(line);
  while 1:
   line = genericLoadMakeAzoFile.readline();
   if not line:
    break;
   elif re.search("awin\s*=\s*;",line):
    outputLoadMakeAzoFile.write(line.replace(";",awin+";"));
    break;
   else:
    outputLoadMakeAzoFile.write(line);
  while 1:
   line = genericLoadMakeAzoFile.readline();
   if not line:
    break;
   elif re.search("da_p\s*=\s*;",line):
    outputLoadMakeAzoFile.write(line.replace(";",da_p+";"));
    break;
   else:
    outputLoadMakeAzoFile.write(line);
  while 1:
   line = genericLoadMakeAzoFile.readline();
   if not line:
    break;
   elif re.search("r_e\s*=\s*;",line):
    outputLoadMakeAzoFile.write(line.replace(";",r_e+";"));
    break;
   else:
    outputLoadMakeAzoFile.write(line);
  while 1:
   line = genericLoadMakeAzoFile.readline();
   if not line:
    break;
   elif re.search("p_h\s*=\s*;",line):
    outputLoadMakeAzoFile.write(line.replace(";",p_h+";"));
    break;
   else:
    outputLoadMakeAzoFile.write(line);
  while 1:
   line = genericLoadMakeAzoFile.readline();
   if not line:
    break;
   elif re.search("dr\s*=\s*;",line):
    outputLoadMakeAzoFile.write(line.replace(";",dr+";"));
    break;
   else:
    outputLoadMakeAzoFile.write(line);
  while 1:
   line = genericLoadMakeAzoFile.readline();
   if not line:
    break;
   elif re.search("la\s*=\s*",line):
    temp = re.compile("la\s*=\s*");
    line = temp.sub("la = "+Angle,line);
    outputLoadMakeAzoFile.write(line);
    break;
   else:
    outputLoadMakeAzoFile.write(line);
  while 1:
   line = genericLoadMakeAzoFile.readline();
   if not line:
    break;
   elif re.search("width0\s*=\s*;",line):
    outputLoadMakeAzoFile.write(line.replace(";",endRefSample+";"));
    break;
   else:
    outputLoadMakeAzoFile.write(line);
  while 1:
   line = genericLoadMakeAzoFile.readline();
   if not line:
    break;
   elif re.search("length0\s*=\s*;",line):
    outputLoadMakeAzoFile.write(line.replace(";",endRefLine+";"));
    break;
   else:
    outputLoadMakeAzoFile.write(line);
  while 1:
   line = genericLoadMakeAzoFile.readline();
   if not line:
    break;
   elif re.search("azimuth_10rlks.unw",line):
    outputLoadMakeAzoFile.write(line.replace("azimuth_10rlks.unw",ampcorDir+"/azimuth_"+str(int(rwin)/int(wsamp))+"rlks.unw"));
    break;
   else:
    outputLoadMakeAzoFile.write(line);
  while 1:
   line = genericLoadMakeAzoFile.readline();
   if not line:
    break;
   elif re.search("range_10rlks.unw",line):
    outputLoadMakeAzoFile.write(line.replace("range_10rlks.unw",ampcorDir+"/range_"+str(int(rwin)/int(wsamp))+"rlks.unw"));
   else:
    outputLoadMakeAzoFile.write(line);
  outputLoadMakeAzoFile.close();
  genericLoadMakeAzoFile.close();
  #genericLoadMakeAzoCmd = "\nmatlab -nodesktop -nosplash -r "+outputLoadMakeAzo[0:outputLoadMakeAzo.rfind(".")]+"\n";
  genericLoadMakeAzoCmd = "\npython "+outputLoadMakeAzo+"\n";
  genericLoadMakeAzoStream = os.popen(genericLoadMakeAzoCmd);
  genericLoadMakeAzoStream.close();

def beamTable():
 if not os.path.exists(beamAngleTable):
  return;
 beamFile = open(beamAngleTable,"r");
 for line in beamFile:
  [name,angle]=line.strip().split(); 
  beamAngles[name]=angle;
 beamFile.close();
 return;

def findAzimuthPixelSize(path,date):
 currentDir = os.getcwd();
 findSlcCmd = "find " + path + " -name \"" + date + ".slc.rsc\" -print";
 findSlcStream = os.popen(findSlcCmd);
 findSlcOutput = findSlcStream.read();
 findSlcStream.close();
 findSlcOutput = findSlcOutput.split();
 if len(findSlcOutput) < 1:
  findRawCmd = "find " + path + " -name \"" + date + ".raw\" -print";
  findRawStream = os.popen(findRawCmd);
  findRawOutput = findRawStream.read();
  findRawStream.close();
  findRawOutput = findRawOutput.split();
  findHdrCmd = "find " + path + " -name \"hdr*"+date+"*.rsc\" -print";
  findHdrStream = os.popen(findHdrCmd);
  findHdrOutput = findHdrStream.read().split();
  findHdrStream.close();
  if len(findRawOutput) < 1:
   print("\n***** WARNING, could not find \"" + date + ".raw\", necessary to determine azimuth pixel size\n");
   return "-1";
  if not os.path.exists(findRawOutput[0] + ".rsc"):
   print("\n***** WARNING, could not find \"" + date + ".raw.rsc\", necessary to determine azimuth pixel size\n");
   return "-1";
  if len(findHdrOutput) < 1:
   print("\n***** WARNING, could not find \"hdr*"+date+"*.rsc\", necessary to determine azimuth pixel size\n");
   return "-1";
  azimCmd = "\nmkdir " + path + "/" + date + "_APS\n";
  azimCmd += "\ncd " + path + "/" + date + "_APS\n";
  azimCmd += "\nln -s " + findRawOutput[0].strip() + " " + findRawOutput[0].strip()[findRawOutput[0].strip().rfind("/")+1:] + "\n";
  azimCmd += "\nln -s " + findRawOutput[0].strip() + ".rsc " + findRawOutput[0].strip()[findRawOutput[0].strip().rfind("/")+1:] + ".rsc\n";
  azimCmd += "\nln -s "+findHdrOutput[0]+" "+findHdrOutput[0].strip()[findHdrOutput[0].strip().rfind("/")+1:]+"\n";
  azimCmd += "\ndopav.pl . . " + date + " " + date + " \"\"\n";
  azimCmd += "\nroi_prep.pl " + date + " " + orbit + "\n";
  azimCmd += "\ncd " + currentDir + "\n";
  azimStream = os.popen(azimCmd);
  azimStream.close();
  findSlcOutput = [findRawOutput[0][0:findRawOutput[0].rfind("/")]+"_APS/"+date+".slc.rsc"];
 slcRscFile = open(findSlcOutput[0].strip(),"r");
 while 1:
  line = slcRscFile.readline();
  if not line:
   break;
  if line.find("AZIMUTH_PIXEL_SIZE") > -1:
   slcRscFile.close();
   removeAPSCmd = "\nrm -r " + RawRawFolder + "/*_APS\n";
   removeAPSStream = os.popen(removeAPSCmd);
   removeAPSStream.close();
   return line[re.search("\d+\.*\d*",line).start(0):re.search("\d+\.*\d*",line).end(0)];
 slcRscFile.close();
 print("\n***** WARNING, unable to determine azimuth pixel size, using default value of \"5\"\n");
 removeAPSCmd = "\nrm -r " + RawRawFolder + "/*_APS\n";
 removeAPSStream = os.popen(removeAPSCmd);
 removeAPSStream.close();
 return "-1";

def GCF(num):
 temp = num[0];
 for i in range(len(num)-1):
  num1 = temp;
  num2 = num[i+1];
  if num1 < num2:
   num1,num2=num2,num1;
  while num1 - num2:
   num3 = num1 - num2;
   num1 = max(num2,num3);
   num2 = min(num2,num3);
  temp = num1;
 return num1;

def has_value(self, value):
 return value in self.values();

def LCM(num):
 temp = num[0];
 for i in range(len(num)-1):
  num1 = temp;
  num2 = num[i+1];
  t_gcf = GCF([num1,num2]);
  temp = t_gcf * num1/t_gcf * num2/t_gcf;
 return temp;

def makeProcFile(path,date2,date1,angle):
 procFilePath = path + "/int_" + date2 + "_" + date1 + ".proc";
 if os.path.exists(procFilePath):
  print("\n\"" + procFilePath + "\" already exists, skipping\n");
  return;
 intDirPath = path + "/int_" + date2 + "_" + date1;
 procFile = open(procFilePath,"w");
 procFile.write("SarDir1=" + path + "/" + date2 + "\n");
 procFile.write("SarDir2=" + path + "/" + date1 + "\n");
 procFile.write("IntDir="+intDirPath+"\n");
 procFile.write("SimDir="+intDirPath+"/SIM\n");
 procFile.write("GeoDir="+intDirPath+"/GEO\n");
 procFile.write("flattening=orbit\n");
 procFile.write("DEM="+DEM+"\n");
 procFile.write("OrbitType="+orbit+"\n");
 procFile.write("Rlooks_sim=1\n");
 procFile.write("Rlooks_unw=1\n");
 procFile.write("Rlooks_geo=1\n");
 procFile.write("Rlooks_int=1\n");
 pixelRatio = "-1";
 if re.search("\d+",angle):
  azimuthPixelSize = findAzimuthPixelSize(path,date1);
  rangePixelSize = "-1";
  if azimuthPixelSize != "-1":
   findRawCmd = "\nfind " + path + " -name \"" + date1 + ".raw.rsc\" -print\n";
   findRawStream = os.popen(findRawCmd);
   findRawOutput = findRawStream.read().split();
   findRawStream.close();
   if len(findRawOutput) > 0:
    rawRscFile = open(findRawOutput[0].strip(),"r");
    while 1:
     line = rawRscFile.readline();
     if not line:
      break;
     if line.find("RANGE_PIXEL_SIZE") > -1:
      rawRscFile.close();
      rangePixelSize = line[re.search("\d+\.*\d*",line).start(0):re.search("\d+\.*\d*",line).end(0)];
      pixelRatioNum = float(rangePixelSize) / math.sin(math.radians(float(angle))) / float(azimuthPixelSize);
      pixelRatio = str(math.ceil(pixelRatioNum));
      pixelRatio = pixelRatio[0:pixelRatio.rfind(".")];
      break;
    rawRscFile.close();
 if pixelRatio != "-1":
  procFile.write("pixel_ratio="+pixelRatio+"\n");
 procFile.close();

def getPixelRatios(path):
 return; 

def readProcFile(path,date2,date1):
 procCmd = "find " + path + " -name \"*" + date2 + "*" + date1 + "*.proc\" -print";
 procStream = os.popen(procCmd);
 procOutput = procStream.read();
 procFilePath = procOutput.strip().split();
 if len(procFilePath) < 1:
  print("\n***** ERROR, no proc file found for dates \"" + date2 + ", " + date1 + "\" in \"" + path + "\"\n");
  sys.exit();
 if len(procFilePath) > 1:
  print("\n***** WARNING, found more than one proc file for dates \"" + date2 + ", " + date1 + "\", using \"" + procFilePath[0] + "\"\n");
 procStream.close();
 procFile = open(procFilePath[0],"r");
 procHash = {};
 while 1:
  line = procFile.readline();
  if not line:
   break;
  line = line.strip();
  name = "";
  value = "";
  nameAndValue = line.split("=");
  if len(nameAndValue) < 2 or len(nameAndValue[0]) < 1 or len(nameAndValue[1]) < 1:
   print("\n***** ERROR, proc file line format is \"varName=varValue\", \"" + line + "\" does not conform to this format\n");
   sys.exit();
  procHash[nameAndValue[0]] = nameAndValue[1];
 procFile.close();
 return procHash;

def gausshpfilt(data,kernel):
  padSize = numpy.size(kernel,axis=0) / 2;
  temp = numpy.zeros((numpy.size(data,axis=0)+2*padSize,numpy.size(data,axis=1)+2*padSize));
  #fill temp with data values
  for i in range(padSize,numpy.size(temp,axis=0)-padSize):
   for j in range(padSize,numpy.size(temp,axis=1)-padSize):
    temp[i,j] = data[i-padSize,j-padSize];
  #pad left
  for i in range(0,padSize):
   for j in range(padSize,padSize+numpy.size(data,axis=0)):
    temp[j,padSize-1-i] = data[j-padSize,i];
  #pad top
  for i in range(0,padSize):
   for j in range(padSize,padSize+numpy.size(data,axis=1)):
    temp[padSize-1-i,j] = data[i,j-padSize]; 
  #pad right
  for i in range(0,padSize):
   for j in range(padSize,padSize+numpy.size(data,axis=0)):
    temp[j,numpy.size(temp,axis=1)-padSize+i] = data[j-padSize,numpy.size(data,axis=1)-1-i];
  #pad bottom
  for i in range(0,padSize):
   for j in range(padSize,padSize+numpy.size(data,axis=1)):
    temp[numpy.size(temp,axis=0)-padSize+i,j] = data[numpy.size(data,axis=0)-1-i,j-padSize];
  #fill top-left corner
  for i in range(0,padSize):
   for j in range(0, padSize):
    temp[padSize-i-1,padSize-j-1] = int((temp[padSize-i-1,padSize-j] + temp[padSize-i,padSize-j-1]) / 2);
  #fill top-right corner
  for i in range(0,padSize):
   for j in range(0, padSize):
    temp[padSize-i-1,numpy.size(temp,axis=1)-padSize+j] = int((temp[padSize-i-1,numpy.size(temp,axis=1)-padSize+j-1] + temp[padSize-i,numpy.size(temp,axis=1)-padSize+j]) / 2);
  #fill bottom-right corner
  for i in range(0,padSize):
   for j in range(0, padSize):
    temp[numpy.size(temp,axis=0)-padSize+i,numpy.size(temp,axis=1)-padSize+j] = int((temp[numpy.size(temp,axis=0)-padSize+i,numpy.size(temp,axis=1)-padSize+j-1] + temp[numpy.size(temp,axis=0)-padSize+i-1,numpy.size(temp,axis=1)-padSize+j]) / 2);
  #fill bottom-left corner
  for i in range(0,padSize):
   for j in range(0, padSize):
    temp[numpy.size(temp,axis=0)-padSize+i,padSize-j-1] = (temp[numpy.size(temp,axis=0)-padSize+i,padSize-j] + temp[numpy.size(temp,axis=0)-padSize+i-1,padSize-j-1]) / 2;
  #perform convolution
  ghp_data = numpy.zeros((numpy.size(data,axis=0),numpy.size(data,axis=1)));
  for i in range(numpy.size(ghp_data,axis=0)):
   for j in range(numpy.size(ghp_data,axis=1)):
    ghp_data[i,j] = numpy.sum(kernel*temp[i:i+numpy.size(kernel,axis=0),j:j+numpy.size(kernel,axis=1)]);
  return ghp_data;

def geocode(path):
 currentDir = os.getcwd();
 azosCmd = "find " + path + " \( -name \"azimuth*.unw\" -o -name \"range*.unw\" \) -print";
 azosStream = os.popen(azosCmd);
 azosOutput = azosStream.read();
 azoFilePaths = azosOutput.split();
 azosStream.close();
 for i in range(0,len(azoFilePaths)):
  finalGeocodeCmd = "";
  azoDir = azoFilePaths[i][0:azoFilePaths[i].rfind("/")];
  if not os.path.exists(azoDir + "/log"):
   print(azoDir[i] + "/log");
   print("\n***** WARNING, could not find \"log\" file for : \"" + azoFilePaths[i] + "\"\nAzo unw files must have \"log\" file in same directory, skipping \""+azoFilePaths[i].strip()+"\"\n");
   continue;
  logFile = open(azoDir + "/log","r");
  azoLine = "";
  while 1:
   line = logFile.readline();
   if not line:
    break;
   if CPXorRMG == "CPX":
    if re.search("azo\.pl\s+\S+\.slc\s+\S+\.slc",line):
     azoLine = line[line.find("azo.pl"):].strip();
   else:
    if re.search("azo\.pl\s+\S+\.rmg\s+\S+\.rmg",line):
     azoLine = line[line.find("azo.pl"):].strip();
  logFile.close();
  if azoLine == "":
   print("\n***** WARNING, could not locate necessary azo parameters in log file \"" + azoDir + "/log\", skipping \""+azoFilePaths[i].strip()+"\"\n");
   continue;
  azoParameters = azoLine.split();
  if len(azoParameters) < 7:
   print("\n***** WARNING, could not locate necessary azo parameters on this line: \"" + line + "\"\nin log file \"" + azoDir + "/log\", skipping \""+azoFilePaths[i].strip()+"\"\n");
   continue;
  rwin = azoParameters[5].strip();
  awin = azoParameters[6].strip();
  if re.search("\D",rwin) or re.search("\D",awin):
   print("\n***** WARNING, \"" + rwin + " " + awin + "\" in log file  \"" + azoDir + "/log\" not valid parameters, must contain only digits, skipping \""+azoFilePaths[i].strip()+"\"\n");
   continue;
  if len(azoParameters) > 7 and not re.search("\D",azoParameters[7].strip()):
   skip = azoParameters[7].strip();
  else:
   skip = "1";
  date2 = azoParameters[1].strip()[azoParameters[1].strip().rfind("/")+1:azoParameters[1].strip().rfind(".")];
  date1 = azoParameters[2].strip()[azoParameters[2].strip().rfind("/")+1:azoParameters[2].strip().rfind(".")];
  procHash = readProcFile(RawRawFolder,date2,date1);
  pixelRatio = "5";
  if not procHash.has_key("pixel_ratio"):
   print("\nParameter \"pixel_ratio\" not found in proc file, using default value of 5\n");
  else:
   pixelRatio = procHash["pixel_ratio"];
  if not procHash.has_key("DEM"):
   print("\n***** WARNING, Parameter \"DEM\" not found in proc file, skipping \""+azoFilePaths[i].strip()+"\"\n");
   continue;
  else:
   DEM = procHash["DEM"];
   if not os.path.exists(DEM):
    print("\n***** WARNING, Parameter \"DEM\", value \"" + DEM + "\" not found, skipping \""+azoFilePaths[i].strip()+"\"\n");
    continue;
  if not os.path.exists(azoDir + "/SIM"):
   print("\n***** WARNING, \"SIM/\" not found in \"" + azoDir + "\", skipping \""+azoFilePaths[i].strip()+"\"\n");
   continue;
  if not os.path.exists(azoDir + "/GEO"):
   print("\n***** WARNING, \"GEO/\" not found in \"" + azoDir + "\", skipping \""+azoFilePaths[i].strip()+"\"\n");
   continue;
  geocodeCmd = "\ncd " + azoDir + "\n";
  ldRange = str(int(rwin)/int(skip));
  ldAzimuth = str(int(awin)/int(skip));
  if not os.path.exists(azoFilePaths[i][:azoFilePaths[i].rfind("/")] + "/" + date2 + "_" + ldRange + "rlks.slc.rsc"):
   geocodeCmd += "\nperl " + ROIPAC + "/look.pl " + date2 + ".slc " + ldRange + " " + ldAzimuth + "\n";
  geocodeCmd += "\ncp -pr " + date2 + "_" + ldRange + "rlks.slc.rsc " + azoFilePaths[i][azoFilePaths[i].rfind("/")+1:] + ".rsc\n";
  offToGeocode = azoFilePaths[i].strip();
  offToPixelRatio = str(int(rwin)/int(skip)/int(pixelRatio));
  if azoFilePaths[i].find("range") > -1:
   radarUNWFindCmd = "\nfind " + azoFilePaths[i][0:azoFilePaths[i].rfind("/")] + " -name \"radar*.unw\" -print\n";
   radarUNWFindStream = os.popen(radarUNWFindCmd);
   radarUNWFindOutput = radarUNWFindStream.read().split();
   radarUNWFindStream.close();
   if len(radarUNWFindOutput) < 1:
    print("\n***** WARNING, could not find any \"radar*.unw\" in \"" + azoFilePaths[i][0:azoFilePaths[i].rfind("/")] + "\", skipping \""+azoFilePaths[i].strip()+"\"\n");
    continue;
   radarUNW = radarUNWFindOutput[0].strip();
   if not os.path.exists(radarUNWFindOutput[0].strip()+".rsc"):
    print("\n***** WARNING, could not find any \"" + radarUNW + ".rsc\" in \"" + azoFilePaths[i][0:azoFilePaths[i].rfind("/")] + "\", skipping \""+azoFilePaths[i].strip()+"\"\n");
    continue;
   lcm = LCM([int(rwin)/int(skip)*int(pixelRatio),int(awin)/int(skip)]);
   #geocodeCmd += "\nperl " + ROIPAC + "/look.pl " + radarUNW + " " + str(lcm/int(pixelRatio)) + " " + str(lcm/int(pixelRatio)) + "\n";
   lookDownRadarCmd = "\nperl " + ROIPAC + "/look.pl " + radarUNW + " " + str(lcm/int(pixelRatio)) + " " + str(lcm/int(pixelRatio)) + "\n";
   lookDownRadarStream = os.popen(lookDownRadarCmd);
   lookDownRadarStream.close();
   radarLDUNW = radarUNW[0:radarUNW.rfind(".unw")] + "_" + str(lcm/int(pixelRatio)) + "rlks.unw";
   radarLDUNWRSCFile = open(radarLDUNW+".rsc","r");
   width = "";
   wavelength = "";
   while 1:
    line = radarLDUNWRSCFile.readline();
    if not line:
     break;
    if line.find("WIDTH") > -1:
     widthNameValue = line.split();
     if len(widthNameValue) > 1:
      width = widthNameValue[1];
    if line.find("WAVELENGTH") > -1:
     wavelengthNameValue = line.split();
     if len(wavelengthNameValue) > 1:
      wavelength = wavelengthNameValue[1];
   if width == "":
    print("\n***** WARNING, could not find \"WIDTH\" in \"" + radarLDUNW + ".rsc\", skipping \""+azoFilePaths[i].strip()+"\"\n");
    continue;
   if wavelength == "":
    print("\n***** WARNING, could not find \"WAVELENGTH\" in \"" + radarLDUNW + ".rsc\", skipping \""+azoFilePaths[i].strip()+"\"\n");
    continue;
   wavelengthFloatMeters = float(wavelength);
   wavelengthFloatCentimeters = 100 * wavelengthFloatMeters;
   wavelengthCentimeters = str(wavelengthFloatCentimeters);
   rmgToMagPhsCmd = "\nrmg2mag_phs " + radarLDUNW + " " + radarLDUNW + ".mag " + radarLDUNW + ".phs " + width + "\n";
   rmgToMagPhsStream = os.popen(rmgToMagPhsCmd);
   rmgToMagPhsStream.close();
   newRadarLDUNWPHS = adjustPhase(radarLDUNW+".phs",wavelengthCentimeters,width);
   geocodeCmd += "\nmag_phs2rmg " + radarLDUNW + ".mag " + newRadarLDUNWPHS + " " + radarLDUNW + " " + width + "\n";
  if int(awin)/int(rwin) != int(pixelRatio):
   lcm = LCM([int(rwin)/int(skip)*int(pixelRatio),int(awin)/int(skip)]);
   ldRangeOff = str(lcm/int(pixelRatio)/(int(rwin)/int(skip)));
   ldAzimuthOff = str(lcm/(int(awin)/int(skip)));
   tempUnw = "temp_" + offToGeocode[offToGeocode.rfind("/")+1:offToGeocode.rfind("_")] + ".unw";
   geocodeCmd += "\ncp -pr " + offToGeocode[offToGeocode.rfind("/")+1:] + " " + tempUnw + "\n";
   geocodeCmd += "\ncp -pr " + date2 + "_" + ldRange + "rlks.slc.rsc " + tempUnw + ".rsc\n";
   geocodeCmd += "\nperl " + ROIPAC + "/look.pl " + tempUnw + " " + ldRangeOff + " " + ldAzimuthOff + "\n";
   tempUnw = tempUnw[0:tempUnw.rfind(".unw")] + "_" + ldRangeOff + "rlks.unw";
   offToGeocode = tempUnw;
   offToPixelRatio = str(lcm/int(pixelRatio));
  if azoFilePaths[i].find("range") > -1:
   newRangeUNW = offToGeocode[0:offToGeocode.rfind("/")] + "/new_" + offToGeocode[offToGeocode.rfind("/")+1:];
   geocodeCmd += "\nperl " + ROIPAC + "/add_rmg.pl " + offToGeocode + " " + radarLDUNW + " " + newRangeUNW + " -1 1\n";
   offToGeocode = newRangeUNW;
  geocodeCmd += "\nperl " + ROIPAC + "/make_geomap.pl ./GEO " + offToGeocode + " azm.trans " + orbit + " " + DEM + " " + date2 + "-" + date1 + "_SIM.aff " + offToPixelRatio + " " + date2 + " yes ./SIM\n";
  geocodeCmd += "\nperl " + ROIPAC +"/geocode.pl ./GEO/azm.trans " + offToGeocode  + " geo_" + azoFilePaths[i][azoFilePaths[i].rfind("/")+1:azoFilePaths[i].rfind("_")] + "_" + date2 + "-" + date1 + ".unw\n";
  geocodeCmd += "\ncd " + currentDir + "\n";
  finalGeocodeCmd += geocodeCmd;
  geocodeStream = os.popen(finalGeocodeCmd);
  geocodeStream.close();

def generateProfiles(path):
 currentDir = os.getcwd();
 profilesCmd = "find " + path + " -name \"*.distance\" -print";
 profilesStream = os.popen(profilesCmd);
 profilesOutput = profilesStream.read();
 profilesStream.close();
 profiles = profilesOutput.split();
 xyzCmd = "find " + path + " -name \"northxyz.txt\" -print";
 xyzStream = os.popen(xyzCmd);
 xyzOutput = xyzStream.read();
 xyzStream.close();
 xyzCmd = "find " + path + " -name \"eastxyz.txt\" -print";
 xyzStream = os.popen(xyzCmd);
 xyzOutput = xyzOutput + xyzStream.read();
 xyzStream.close();
 xyzCmd = "find " + path + " -name \"magxyz.txt\" -print";
 xyzStream = os.popen(xyzCmd);
 xyzOutput = xyzOutput + xyzStream.read();
 xyzStream.close();
 xyzFileList = xyzOutput.split();
 for i in range(0,len(xyzFileList)):
  xyzPath = xyzFileList[i].strip()[0:xyzFileList[i].strip().rfind("/")];
  xyzFileName = xyzFileList[i].strip()[xyzFileList[i].strip().rfind("/")+1:];
  xyzName = xyzFileName[0:xyzFileName.find(".")];
  gridCmd = "";
  if not os.path.exists(xyzPath + "/" + xyzName + ".grd"):
   gridCmd = gridCmd + "\npython grid.py " + xyzFileList[i].strip() + "\n";
   gridCmdStream = os.popen(gridCmd);
   gridCmdOutput = gridCmdStream.read();
   gridCmdStream.close();
  #for i in range(0,len(profiles)):
  # genProfileCmd = "\ncd " + xyzPath + "\ngrdtrack " + profiles[i] + " -G" + xyzName + ".grd > " + profiles[i][profiles[i].rfind("/")+1:profiles[i].find(".")] + "_" + xyzName + ".txt\ncd " + currentDir + "\n";
  # print(genProfileCmd);
   #genProfileStream = os.popen(genProfileCmd);
   #genProfileStream.close();

def generatePNGs(path):
 currentDir = os.getcwd();
 findGRDsCmd = "find " + path + " -name \"*.grd\" -print";
 findGRDsStream = os.popen(findGRDsCmd);
 findGRDsOutput = findGRDsStream.read().split();
 findGRDsStream.close();
 pngCmd = "";
 for i in range(0,len(findGRDsOutput)):
  psName = findGRDsOutput[i][0:findGRDsOutput[i].rfind(".")] + ".ps";
  psPath = findGRDsOutput[i][0:findGRDsOutput[i].rfind("/")];
  pngName = findGRDsOutput[i][0:findGRDsOutput[i].rfind(".")] + ".png";
  if os.path.exists(psName) and not os.path.exists(pngName):
   pngCmd += "\ncd " + psPath + "\nps2raster -A -TG " + psName + "\ncd " + currentDir + "\n";
 if pngCmd != "":
  pngStream = os.popen(pngCmd);
  pngStream.close();

def getAffineTrans(path):
 currentDir = os.getcwd();
 procFindCmd = "find " + path + " -name \"int*.proc\" -print";
 procFindStream = os.popen(procFindCmd);
 procFindOutput = procFindStream.read().split();
 procFindStream.close();
 affineCmd = "";
 if len(procFindOutput) > 0:
  for i in range(0,len(procFindOutput)):
   procDir = procFindOutput[i].strip()[0:procFindOutput[i].strip().rfind("/")];
   affineCmd += "\ncd " + procDir + "\n";
   affineCmd += "\nperl " + ROIPAC + "/process_2pass.pl " + procFindOutput[i].strip() + " offsets done_sim_removal\n";
   affineCmd += "\ncd " + currentDir + "\n";
 if affineCmd != "":
  affineStream = os.popen(affineCmd);
  affineStream.close();

def getGRDCorners(path):
 currentDir = os.getcwd();
 findGRDsCmd = "find " + path + " -name \"*.grd\" -print";
 findGRDsStream = os.popen(findGRDsCmd);
 findGRDsOutput = findGRDsStream.read().split();
 findGRDsStream.close();
 for i in range(0,len(findGRDsOutput)):
  grdPath = findGRDsOutput[i][0:findGRDsOutput[i].rfind("/")];
  grdName = findGRDsOutput[i][findGRDsOutput[i].rfind("/")+1:findGRDsOutput[i].rfind(".")];
  if not os.path.exists(grdPath + "/" + grdName + "_corners.dat"):
   grdinfoCmd = "\ngrdinfo " + findGRDsOutput[i].strip() + "\n";
   grdinfoStream = os.popen(grdinfoCmd);
   grdinfoOutput = grdinfoStream.read();
   grdinfoStream.close();
   x_min = grdinfoOutput[grdinfoOutput.find("x_min:")+6:grdinfoOutput.find("x_max:")].strip();
   x_max = grdinfoOutput[grdinfoOutput.find("x_max:")+6:grdinfoOutput.find("x_inc:")].strip();
   y_min = grdinfoOutput[grdinfoOutput.find("y_min:")+6:grdinfoOutput.find("y_max:")].strip();
   y_max = grdinfoOutput[grdinfoOutput.find("y_max:")+6:grdinfoOutput.find("y_inc:")].strip();
   cornersFileName = grdPath + "/" + grdName + "_corners.dat";
   cornersFile = open(cornersFileName,"w");
   cornersFile.write(x_min + " " + y_min + " LL\n");
   cornersFile.write(x_max + " " + y_max + " TR\n");
   cornersFile.write(x_min + " " + y_max + " TL\n");
   cornersFile.write(x_max + " " + y_min + " LR\n");
   cornersFile.close()

def generateKML(path):
 findPNGsCmd = "find " + path + " -name \"*.png\" -print";
 findPNGsStream = os.popen(findPNGsCmd);
 findPNGsOutput = findPNGsStream.read().split();
 findPNGsStream.close();
 #for i in range(0,len(findPNGsOutput)):
 # print(findPNGsOutput[i]);

def createMatlabGetXYZ(matlabPath,ampcorInFilePath):
 startRefSample = "";
 endRefSample = "";
 skipRefSample = ""; 
 startRefLine = "";
 endRefLine = "";
 skipRefLine = "";
 ampcorInFile = open(ampcorInFilePath,"r");
 ampcorDir = ampcorInFilePath[0:ampcorInFilePath.rfind("/")];
 ampcorName = ampcorInFilePath[0:ampcorInFilePath.rfind(".")];
 cornersFilePath = ampcorDir + "/corners.dat";
 cornersFile = open(cornersFilePath,"r");
 ul_long = "";
 ul_lat = "";
 while 1:
  line = cornersFile.readline();
  if not line:
   break;
  line = line.strip();
  if line.find("ul_long") > -1:
   ul_long = line.split("=")[1];
  elif line.find("ul_lat") > -1:
   ul_lat = line.split("=")[1];
 cornersFile.close();
 while 1:
  line = ampcorInFile.readline();
  if not line:
   break;
  if line.find("Start, End and Skip Samples in Reference Image") > -1:
   line = line.strip().split("=");
   sampleInfo = line[1].split();
   startRefSample = sampleInfo[0];
   endRefSample = sampleInfo[1];
   skipRefSample = sampleInfo[2];
  elif line.find("Start, End and Skip Lines in Reference Image") > -1:
   line = line.strip().split("=");
   lineInfo = line[1].split();
   startRefLine = lineInfo[0];
   endRefLine = lineInfo[1];
   skipRefLine = lineInfo[2];
 ampcorInFile.close();
 matlabFile = open(matlabPath,"r");
 outputMatlabFile = open(ampcorDir + "/getxyzs.m","w");
 while 1:
  line = matlabFile.readline();
  if not line:
   break;
  elif re.search("rwin\s*=\s*;",line):
   outputMatlabFile.write(line.replace(";",skipRefSample+";"));
   break;
  else:
   outputMatlabFile.write(line);
 while 1:
  line = matlabFile.readline();
  if not line:
   break;
  elif re.search("awin\s*=\s*;",line):
   outputMatlabFile.write(line.replace(";",skipRefLine+";"));
   break;
  else:
   outputMatlabFile.write(line);
 while 1:
  line = matlabFile.readline();
  if not line:
   break;
  elif re.search("load\s*;",line):
   outputMatlabFile.write(line.replace(";",ampcorName[ampcorName.rfind("/")+1:]+".off;"));
   break;
  else:
   outputMatlabFile.write(line);
 while 1:
  line = matlabFile.readline();
  if not line:
   break;
  elif re.search("indat\s*=\s*;",line):
   outputMatlabFile.write(line.replace(";",ampcorName[ampcorName.rfind("/")+1:]+";"));
   break;
  else:
   outputMatlabFile.write(line);
 while 1:
  line = matlabFile.readline();
  if not line:
   break;
  elif re.search("width0\s*=\s*;",line):
   outputMatlabFile.write(line.replace(";",endRefSample+";"));
   break;
  else:
   outputMatlabFile.write(line);
 while 1:
  line = matlabFile.readline();
  if not line:
   break;
  elif re.search("length0\s*=\s*;",line):
   outputMatlabFile.write(line.replace(";",endRefLine+";"));
   break;
  else:
   outputMatlabFile.write(line);
 while 1:
  line = matlabFile.readline();
  if not line:
   break;
  elif re.search("ul_long\s*=\s*;",line):
   outputMatlabFile.write(line.replace(";",ul_long+";"));
   break;
  else:
   outputMatlabFile.write(line);
 while 1:
  line = matlabFile.readline();
  if not line:
   break;
  elif re.search("ul_lat\s*=\s*;",line):
   outputMatlabFile.write(line.replace(";",ul_lat+";"));
   break;
  else:
   outputMatlabFile.write(line);
 while 1:
  line = matlabFile.readline();
  if not line:
   break;
  elif re.search("x_step\s*=\s*;",line):
   outputMatlabFile.write(line.replace(";",str(15*int(skipRefSample))+";"));
   break;
  else:
   outputMatlabFile.write(line);
 while 1:
  line = matlabFile.readline();
  if not line:
   break;
  elif re.search("y_step\s*=\s*",line):
   outputMatlabFile.write(line.replace(";",str(15*int(skipRefLine))+";"));
  else:
   outputMatlabFile.write(line);
 outputMatlabFile.close();
 matlabFile.close();
 currentDir = os.getcwd();
 getXYZCmd = "\ncd " + ampcorDir + "\nmatlab -nodesktop -nosplash -r getxyzs\ncd " + currentDir;
 getXYZCmdStream = os.popen(getXYZCmd);
 getXYZCmdStream.close();

t1 = time.time();

beamAngles={};
beamAngleTable="beam_angle_table.dat";
beamTable();
programName = "pixelTrack.pl";
parameterFilePath = "";
steps = "uncompress_raw_raw/setup/make_raw/make_int_dirs_and_procs/baselines/offsets/ampcor/make_unw/affine/geocode/optical_raw/gausshp_filt/get_xyzs/profiles/kml/test";

if len(sys.argv) > 2:
 parameterFilePath = sys.argv[1];
 startStep = sys.argv[2];
 start = startStep;
 if not os.path.isfile(parameterFilePath):
  print("\n***** ERROR, parameter file \"" + parameterFilePath + "\" does not exist\n");
  sys.exit();
 if steps.find(start) == -1:
  print("\n***** ERROR, \"" + start + "\" is not a valid name for a step\nValid step names: " + steps + "\n");
  sys.exit();
 if len(sys.argv) > 3:
  endStep = sys.argv[3];
  if steps.find(endStep) == -1:
   print("\n***** ERROR, \"" + endStep + "\" is not a valid name for a step\nValid step names: " + steps + "\n");
   sys.exit();
 else:
  endStep = "";
else:
 if len(sys.argv) < 2:
  print("\n***** ERROR, please include paremter file as command line argument\n" + programName + " usage: $python " + programName + " paremeter_file_path start_step [end_step]\n");
  sys.exit();
 else:
  print("\n***** ERROR, please include step to start at\n" + programName + " usage: $python " + programName + " paremeter_file_path start_step [end_step]\n");
  sys.exit();

parameterFile = open(parameterFilePath,"r");
while 1:
 line = parameterFile.readline();
 if not line:
  break;
 line = line.strip();
 name = "";
 value = "";
 nameAndValue = line.split("=");
 if len(nameAndValue) < 2 or len(nameAndValue[0]) < 1 or len(nameAndValue[1]) < 1:
  print("\n***** ERROR, parameter file line format is \"varName=varValue\", \"" + line + "\" does not conform to this format\n");
  sys.exit();
 name = nameAndValue[0];
 value = nameAndValue[1];
 vars()[name] = value;
parameterFile.close();
try: DataType
except NameError:
 print("\n***** WARNING, variable \"DataType\" not set in parameter file\nUsing ERS as data type");
 DataType = "ERS";
if DataType.find("ERS") > -1:
 orbit = "ODR";
elif re.search("r\.*sat",DataType.lower()):
 orbit = "HDR";
elif re.search("envisat",DataType.lower()):
 orbit = "DOR";
elif re.search("alos",DataType.lower()):
 orbit = "HDR";
try: RawRawFolder
except NameError:
 print("\n***** ERROR, variable \"RawRawFolder\" not set in parameter file\n");
 sys.exit();
if not os.path.isdir(RawRawFolder):
 print("\n***** ERROR, raw-raw folder \"" + RawRawFolder + "\" does not exist\n");
 sys.exit();
elif len(os.listdir(RawRawFolder)) < 1:
 print("\n***** ERROR, raw-raw folder \"" + RawRawFolder + "\" is empty\n");
 sys.exit();
try: ROIPAC
except NameError:
 print("\n***** ERROR, variable \"ROIPAC\" not set in parameter file\nMust specify ROIPAC directory\n");
 sys.exit();
if not os.path.isdir(ROIPAC):
 print("\n***** ERROR, \"" + ROIPAC + "\" does not exist or is not directory\n");
 sys.exit();
elif len(os.listdir(ROIPAC)) < 1:
 print("\n***** ERROR, \"" + ROIPAC + "\" is empty\n");
 sys.exit();
try: Angle
except NameError:
 print("\n***** Warning, variable \"Angle\" not set in parameter file\nUsing default value of 23 degrees (ERS)\n");
 Angle = "23";
try: 
 PyPacks;
 if PyPacks.find(",") > -1:
  PyPacksList = PyPacks.split(",");
  for pack in PyPacksList:
   sys.path.append(pack);
 else:
  sys.path.append(PyPacks);
 try:
  import numpy;
  import scipy;
  import pylab;
 except ImportError:
  print("\n***** WARNING, scipy/numpy/pylab not found in \"" + PyPacks + "\"\nWill NOT be able to generate pixel-tracking results or remove topography from range offsets\n");
except NameError:
 print("\n***** WARNING, variable \"PyPacks\" not set in parameter file\nIf scipy/numpy not in standard location will NOT be able to generate pixel-tracking results or remove topography from range offsets\n");


if start == "uncompress_raw_raw":
 untarred = 0;

 while 1:
  
# Find compressed, raw files

  findCompRawFilesCmd = "\nfind " + RawRawFolder + " \( -name \"*.bz2\" -o -name \"*.bzip2\" -o -name \"*.tar\" -o -name \"*.zip\" -o -name \"*.gz\" -o -name \"*.gzip\" -o -name \"*.tgz\" \) -print\n";
  findCompRawFilesStream = os.popen(findCompRawFilesCmd);
  compRawFiles = findCompRawFilesStream.read().split();
  findCompRawFilesStream.close();

# When none are found (or tar files already untarred), break out of loop  
  
  if len(compRawFiles) < 1 or untarred == 1:
   break;

# When compressed files found, check extension and uncompress using appropriate program
 
  untarred = 1;
  uncompressCmd = "";
  for path in compRawFiles:

#  Do not try to uncompress files that have been archived   
   if re.search("ARCHIVE/",path):
    continue;

   extension = path[path.rfind(".")+1:].strip();
   if re.search("b+.*z+.*2+.*",extension) != None:
    uncompressCmd += "\nbunzip2 " + path + "\n";
    untarred = 0;
   elif re.search("tar",extension) != None:
    uncompressCmd = uncompressCmd + "\ntar -C " + RawRawFolder + " -xvf " + path + "\n";
   elif re.search("^t*gz",extension) != None:
    uncompressCmd += "\ngunzip " + path + "\n";
    untarred = 0;
   elif re.search("^zip",extension) != None:
    uncompressCmd += "\nunzip " + path + " -d "+path[0:path.rfind("/")]+"\n";
    untarred = 0;
   else:
    untarred = 0;
  uncompressStream = os.popen(uncompressCmd);
  uncompressStream.close();
  print(uncompressCmd);

# Move any remaining compressed files into "ARCHIVE" folder

 findCompRawFilesCmd = "\nfind " + RawRawFolder + " \( -name \"*.bz2\" -o -name \"*.bzip2\" -o -name \"*.tar\" -o -name \"*.zip\" -o -name \"*.gz\" -o -name \"*.gzip\" -o -name \"*.tgz\" \) -print\n";
 findCompRawFilesStream = os.popen(findCompRawFilesCmd);
 compRawFiles = findCompRawFilesStream.read().split();
 findCompRawFilesStream.close();
 if not os.path.exists(RawRawFolder + "/ARCHIVE"):
  os.mkdir(RawRawFolder + "/ARCHIVE");
 moveCmd = "";
 for path in compRawFiles:
  moveCmd += "\nmv "+path+" "+RawRawFolder+"/ARCHIVE\n";
 if moveCmd != "":
  moveStream = os.popen(moveCmd);
  moveStream.close();
  print(moveCmd);
 start = "setup";
 if start == endStep:
  logFile = open("pixelTrackLog.txt","a");
  logFile.write("\n***** pixelTrack.py for parameters \""+parameterFilePath+"\" - Started at \""+startStep+"\", ended at \""+endStep+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-t1)));
  logFile.close();
  print("\nReached end step \"" + endStep + "\", exiting...\n");
  sys.exit();

if start == "setup":   
 if DataType.lower().find("alos") > -1:
  findLeaderFilesCmd = "find " + RawRawFolder + " -name \"LED*\" -print";
 elif DataType.lower().find("envisat") > -1:
  findLeaderFilesCmd = "find " + RawRawFolder + " -name \"*.N1*\" -print";
 elif DataType.lower().find("ers") > -1:
  findLeaderFilesCmd = "find " + RawRawFolder + " \( -name \"*.ldr\" -o -name \"LEA*.001\" \) -print";
 else:
  findLeaderFilesCmd = "find " + RawRawFolder + " -name \"*.ldr\" -print";
 findLeaderFilesCmdStream = os.popen(findLeaderFilesCmd);
 findLeaderFilesOutput = findLeaderFilesCmdStream.read(); 
 findLeaderFilesCmdStream.close();
 leaderFiles = findLeaderFilesOutput.split();
 sarNumber = {}; 
 existingSARLeaderFiles = {};
 rawRawFolderContents = os.listdir(RawRawFolder);
 for i in range(0,len(rawRawFolderContents)):
  if re.search("^\d\d\d\d\d\d$",rawRawFolderContents[i]):
   dateFolderContents = os.listdir(RawRawFolder + "/" + rawRawFolderContents[i]);
   if re.search("ers|r.*sat",DataType.lower()):
    for j in range(0,len(dateFolderContents)):
     tempPath = RawRawFolder + "/" + rawRawFolderContents[i] + "/" + dateFolderContents[j];
     if dateFolderContents[j].find("SARLEADER") > -1 and os.path.islink(tempPath):
      if os.path.exists(tempPath):
       existingSARLeaderFiles[os.path.realpath(tempPath)] = tempPath;
      else:
       os.unlink(tempPath);
 for i in range(0,len(leaderFiles)):
  dateName="";
  extension = leaderFiles[i][leaderFiles[i].rfind("."):];
  leaderFile = open(leaderFiles[i],"rb");
  while 1:
   line = leaderFile.readline();
   if not line:
    break;
   searchExp = "\s\d\d\d\d\d\d\d\d";
   if DataType.lower().find("alos") > -1:
    searchExp = "\s\d{20}\s";
   elif re.search("envisat",DataType.lower()):
    searchExp = "SENSING_START";
   if re.search(searchExp,line):
    index = re.search(searchExp,line).start(0);
    if re.search("envisat",DataType.lower()):
     date = line.split("=")[1];
     dayMonthYear=date.split()[0];
     dayMonthYear=dayMonthYear.strip("\"");
     [day,month,year]=dayMonthYear.split("-");
     year=year[2:];
     month=month[0]+month[1].lower()+month[2].lower();
     month=str(list(calendar.month_abbr).index(month));
     if int(month) < 10:
      month="0"+month;
     dateName=year+month+day;
    else:
     dateName = line[index:index+9].strip();
     dateName = dateName[2:8];
    if not os.path.isdir(RawRawFolder + "/" + dateName):
     makeDateDirCmd = "mkdir " + RawRawFolder + "/" + dateName;
     makeDateDirCmdStream = os.popen(makeDateDirCmd);
     makeDateDirCmdStream.close();
    if not existingSARLeaderFiles.has_key(leaderFiles[i]):
     if not sarNumber.has_key(dateName):
      sarNumber[dateName] = 1;
     else:
      sarNumber[dateName] = sarNumber[dateName] + 1;
     sarNumberStr = str(sarNumber[dateName])
     if sarNumber[dateName] < 10:
      sarNumberStr = "0" + sarNumberStr;
     tempPath = RawRawFolder + "/" + dateName + "/SARLEADER" + sarNumberStr;
     if re.search("alos",DataType.lower()) or re.search("envisat",DataType.lower()):
      tempPath = RawRawFolder + "/" + dateName + "/" + leaderFiles[i][leaderFiles[i].rfind("/"):].strip();
     while has_value(existingSARLeaderFiles,tempPath):
      sarNumber[dateName] = sarNumber[dateName] + 1;
      sarNumberStr = str(sarNumber[dateName]);
      if sarNumber[dateName] < 10:
       sarNumberStr = "0" + sarNumberStr;
      tempPath = RawRawFolder + "/" + dateName + "/SARLEADER" + sarNumberStr;
      if re.search("alos",DataType.lower()) or re.search("envisat",DataType.lower()):
       tempPath = RawRawFolder + "/" + dateName + "/" + leaderFiles[i][leaderFiles[i].rfind("/"):].strip();
     os.symlink(leaderFiles[i],tempPath);
     existingSARLeaderFiles[leaderFiles[i]] = tempPath;
    break;
  leaderFile.close();
  rawFileName = "rawness";
  if re.search("envisat",DataType.lower()):
   continue;
  elif DataType.lower().find("alos") > -1:
   rawFileName =  leaderFiles[i][leaderFiles[i].rfind("/")+1:].replace("LED","");
   findRawCmd = "\nfind "+RawRawFolder+" -name \"IMG*"+rawFileName+"*\" -print\n";
   findRawStream = os.popen(findRawCmd);
   findRawOutput = findRawStream.read().strip();
   findRawStream.close();
   rawFileName = findRawOutput;
  elif re.search("LEA.*\.001",leaderFiles[i]):
   rawFileName =  leaderFiles[i].replace("LEA","DAT");
  else:
   rawFileName = leaderFiles[i][0:leaderFiles[i].find(".ldr")] + ".raw";
   if not os.path.exists(rawFileName):
    rawFileName = rawFileName[0:rawFileName.find(".raw")] + ".RAW";
    if not os.path.exists(rawFileName):
     rawFileName = rawFileName[0:rawFileName.find(".RAW")] + ".Raw";
  if not os.path.exists(rawFileName):
   if DataType.lower().find("alos") > -1:
    print("\n***** WARNING, could not find corresponding raw file for leader file \"" + leaderFiles[i] + "\"\nPlease make sure the raw file is in the same directory and is named \"IMG*"+leaderFiles[i].replace("LED","")+"\"\n");
   else:
    print("\n***** WARNING, could not find corresponding raw file for leader file \"" + leaderFiles[i] + "\"\nPlease make sure the raw file is in the same directory and has the extension \".raw\"\n");
   continue;
  tempImagePath="";
  if re.search("SARLEADER",existingSARLeaderFiles[leaderFiles[i]]):
   tempImagePath = existingSARLeaderFiles[leaderFiles[i]].replace("SARLEADER","IMAGERY");
  if re.search("alos",DataType.lower()):
   tempImagePath = RawRawFolder + "/" + dateName + "/" + rawFileName[rawFileName.rfind("/")+1:].strip();
  if not os.path.exists(tempImagePath):
   os.symlink(rawFileName,tempImagePath);
 start = "make_raw";
 if start == endStep:
  logFile = open("pixelTrackLog.txt","a");
  logFile.write("\n***** pixelTrack.py for parameters \""+parameterFilePath+"\" - Started at \""+startStep+"\", ended at \""+endStep+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-t1)));
  logFile.close();
  print("\nReached end step \"" + endStep + "\", exiting...\n");
  sys.exit();

if start == "make_raw":
 try: ROIPAC
 except NameError:
  print("\n***** ERROR, variable \"ROIPAC\" not set in parameter file\nMust specify ROIPAC directory\n");
  sys.exit();
 makeRawCmd = "";
 makeRawScript = "make_raw.pl";
 if re.search(".*ers.*",DataType.lower()):
  makeRawScript = "make_raw_ASF.pl";
 elif re.search("r.*sat",DataType.lower()):
  makeRawScript = "make_raw_RSAT-CEOS.pl";
 elif re.search("envisat",DataType.lower()):
  makeRawScript = "make_raw_envi.pl";
 elif re.search("alos",DataType.lower()):
  makeRawScript = "make_raw_alos.pl";
 rawRawFolderContents = os.listdir(RawRawFolder);
 for i in range(0,len(rawRawFolderContents)):
  if re.search("^\d\d\d\d\d\d$",rawRawFolderContents[i]):
   dateFolderContents = os.listdir(RawRawFolder + "/" + rawRawFolderContents[i]);
   for j in range(0,len(dateFolderContents)):
    findStr = "SARLEADER";
    if re.search("alos",DataType.lower()):
     findStr = "LED";
    elif re.search("envisat",DataType.lower()):
     findStr="ASA_";
    if dateFolderContents[j].find(findStr) > -1:
     currentDir = os.getcwd();
     if re.search("alos",DataType.lower()):
      makeRawCmd = makeRawCmd + "\ncd " + RawRawFolder + "/" + rawRawFolderContents[i] + "\nperl " + ROIPAC + "/" + makeRawScript + " IMG " + rawRawFolderContents[i] + "\ncd " + currentDir + "\n";
     elif re.search("envisat",DataType.lower()):
      makeRawCmd = makeRawCmd + "\ncd " + RawRawFolder + "/" + rawRawFolderContents[i] + "\nperl " + ROIPAC + "/" + makeRawScript + " " + dateFolderContents[j].strip() + " " + orbit + " " + rawRawFolderContents[i] + "\ncd " + currentDir + "\n";
     elif re.search("r.*sat",DataType.lower()):
      makeRawCmd = makeRawCmd + "\ncd " + RawRawFolder + "/" + rawRawFolderContents[i] + "\nperl " + ROIPAC + "/" + makeRawScript + " " + dateFolderContents[j].strip() + " " + rawRawFolderContents[i] + "\ncd " + currentDir + "\n";
     else:
      makeRawCmd = makeRawCmd + "\ncd " + RawRawFolder + "/" + rawRawFolderContents[i] + "\nperl " + ROIPAC + "/" + makeRawScript + " " + orbit + " " + dateFolderContents[j].strip() + " " + rawRawFolderContents[i] + "\ncd " + currentDir + "\n";
     break;
 makeRawCmdStream = os.popen(makeRawCmd);
 makeRawCmdStream.close();
 start = "make_int_dirs_and_procs";
 if start == endStep:
  logFile = open("pixelTrackLog.txt","a");
  logFile.write("\n***** pixelTrack.py for parameters \""+parameterFilePath+"\" - Started at \""+startStep+"\", ended at \""+endStep+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-t1)));
  logFile.close();
  print("\nReached end step \"" + endStep + "\", exiting...\n");
  sys.exit();

if start == "make_int_dirs_and_procs":
 try: MinDateInterval
 except NameError:
  print("\nMinDateInterval not set in parameter file, using 1\n");
  MinDateInterval = "1";
 try: MaxDateInterval
 except NameError:
  print("\nMaxDateInterval not set in parameter file, using 72\n");
  MaxDateInterval = "72";
 rawRawFolderContents = os.listdir(RawRawFolder);
 dates = [];
 for i in range(0,len(rawRawFolderContents)):
  if re.search("^\d\d\d\d\d\d$",rawRawFolderContents[i]):
   dates.append(rawRawFolderContents[i].strip());
 intDirCmd = "";
 try: DEM
 except NameError:
  print("\n***** WARNING, variable \"DEM\" not set in parameter file\n");
  DEM = "";
 for i in range(0,len(dates)):
  for j in range(i+1,len(dates)):
   makeIntDirCmdJI = "\nmkdir " + RawRawFolder + "/int_" + dates[j] + "_" + dates[i] + "\n";
   makeIntDirCmdIJ = "\nmkdir " + RawRawFolder + "/int_" + dates[i] + "_" + dates[j] + "\n";
   if int(dates[i][0:2]) > 70:
    yearI = "19" + dates[i][0:2];
   else:
    yearI = "20" + dates[i][0:2];
   if int(dates[j][0:2]) > 70:
    yearJ = "19" + dates[j][0:2];
   else:
    yearJ = "20" + dates[j][0:2];
   monthI = dates[i][2:4];
   monthJ = dates[j][2:4];
   dayI = dates[i][4:6];
   dayJ = dates[j][4:6];
   dateSecondsICmd = "\ndate +\"%s\" -d \"" + yearI + "-" + monthI + "-" + dayI + " 00:00:00\"\n";
   dateSecondsIStream = os.popen(dateSecondsICmd);
   dateSecondsI = dateSecondsIStream.read().strip();
   dateSecondsJCmd = "\ndate +\"%s\" -d \"" + yearJ + "-" + monthJ + "-" + dayJ + " 00:00:00\"\n";
   dateSecondsJStream = os.popen(dateSecondsJCmd);
   dateSecondsJ = dateSecondsJStream.read().strip();
   dateSecondsDifference = int(dateSecondsJ) - int(dateSecondsI);
   dateDaysDifference = dateSecondsDifference / (60*60*24);
   if abs(dateDaysDifference) >= int(MinDateInterval) and abs(dateDaysDifference) <= int(MaxDateInterval):
    if dateSecondsJ > dateSecondsI:
     if not os.path.exists(RawRawFolder + "/int_" + dates[j] + "_" + dates[i]):
      intDirCmd += makeIntDirCmdJI;
      makeProcFile(RawRawFolder,dates[j],dates[i],Angle);
    else:
     if not os.path.exists(RawRawFolder + "/int_" + dates[i] + "_" + dates[j]):
      intDirCmd += makeIntDirCmdIJ;
      makeProcFile(RawRawFolder,dates[i],dates[j],Angle);
 intDirStream = os.popen(intDirCmd);
 intDirStream.close();
 start = "baselines";
 if start == endStep:
  logFile = open("pixelTrackLog.txt","a");
  logFile.write("\n***** pixelTrack.py for parameters \""+parameterFilePath+"\" - Started at \""+startStep+"\", ended at \""+endStep+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-t1)));
  logFile.close();
  print("\nReached end step \"" + endStep + "\", exiting...\n");
  sys.exit();

if start == "baselines":
 currentDir = os.getcwd();
 findProcFilesCmd = "find " + RawRawFolder + " -name \"*.proc\" -print";
 findProcFilesStream = os.popen(findProcFilesCmd);
 findProcFilesOutput = findProcFilesStream.read();
 findProcFilesStream.close();
 procFiles = findProcFilesOutput.split();
 baselinesCmd = "\ncd " + RawRawFolder + "\n";
 for i in range(0,len(procFiles)):
  baselinesCmd += "\nprocess_2pass.pl " + procFiles[i].strip() + " raw orbbase\n"; 
 baselinesCmd += "\ncd " + currentDir + "\n";
 baselinesStream = os.popen(baselinesCmd);
 baselinesStream.close();
 start = "offsets";
 if start == endStep:
  logFile = open("pixelTrackLog.txt","a");
  logFile.write("\n***** pixelTrack.py for parameters \""+parameterFilePath+"\" - Started at \""+startStep+"\", ended at \""+endStep+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-t1)));
  logFile.close();
  print("\nReached end step \"" + endStep + "\", exiting...\n");
  sys.exit();

if start == "offsets":
 try: MaxBaseline
 except NameError:
  print("\nMaxBaseline not set in parameter file, using +/-500\n");
  MaxBaseline = "500";
 currentDir = os.getcwd();
 baselinesCmd = "find " + RawRawFolder + " -name \"*baseline*.rsc\" -print";
 baselinesStream = os.popen(baselinesCmd);
 baselinesOutput = baselinesStream.read();
 baselinesStream.close();
 baselineFiles = baselinesOutput.split();
 offsetsCmd = "";
 for i in range(0,len(baselineFiles)):
  baselineFile = open(baselineFiles[i].strip(),"r");
  while 1:
   line = baselineFile.readline();
   if not line:
    break;
   if line.find("P_BASE") > -1:
    print(line.split()[1].strip());
    baselineNum = float(line.split()[1].strip());
    if abs(baselineNum) > abs(float(MaxBaseline)):
     break;
    line = baselineFile.readline();
    if line and line.find("P_BASE") > -1:
     baselineNumStr = line.split()[1].strip();
     if not re.search("[^\.\d]",baselineNumStr):
      baselineNum = float(line.split()[1].strip());
      if abs(baselineNum) > abs(float(MaxBaseline)):
       break;
    offsetsCmd += "\ncd " + RawRawFolder + "\n";
    offsetsCmd += "\nprocess_2pass.pl " + baselineFiles[i].strip()[0:baselineFiles[i].rfind("/")] + ".proc orbbase offsets\n";
    offsetsCmd += "\ncd " + currentDir + "\n";
  baselineFile.close();
 offsetsStream = os.popen(offsetsCmd);
 offsetsStream.close();
 start = "ampcor";
 if start == endStep:
  logFile = open("pixelTrackLog.txt","a");
  logFile.write("\n***** pixelTrack.py for parameters \""+parameterFilePath+"\" - Started at \""+startStep+"\", ended at \""+endStep+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-t1)));
  logFile.close();
  print("\nReached end step \"" + endStep + "\", exiting...\n");
  sys.exit();

if start == "ampcor": 
 try: rwin
 except NameError:
  print("\n***** WARNING, variable \"rwin\" not set in parameter file\nUsing default value of \"40\"");
  rwin = "40";
 try: awin
 except NameError:
  print("\n***** WARNING, variable \"awin\" not set in parameter file\nUsing default value of \"40\"");
  awin = "40";
 try: wsamp
 except NameError:
  print("\n***** WARNING, variable \"wsamp\" not set in parameter file\nUsing default value of \"4\"");
  wsamp = "4";
 try: numproc
 except NameError:
  print("\n***** WARNING, variable \"numproc\" not set in parameter file\nUsing default value of \"1\"");
  numproc = "1"; 
 try:
  CPXorRMG
  if CPXorRMG != "RMG" and CPXorRMG != "CPX":
   print("\n***** WARNING, \"" + CPXorRMG + "\" not a valid value for \"CPXorRMG\"\nUsing \"RMG\" for ampcor");
   CPXorRMG = "RMG";
 except NameError:
  print("\n***** WARNING, variable \"CPXorRMG\" not set in parameter file\nUsing \"RMG\" for ampcor");
  CPXorRMG = "RMG";
 ampcor(RawRawFolder,rwin,awin,wsamp,numproc);
 start = "make_unw"; 
 if start == endStep:
  logFile = open("pixelTrackLog.txt","a");
  logFile.write("\n***** pixelTrack.py for parameters \""+parameterFilePath+"\" - Started at \""+startStep+"\", ended at \""+endStep+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-t1)));
  logFile.close();
  print("\nReached end step \"" + endStep + "\", exiting...\n");
  sys.exit();

if start == "make_unw":
 try: rwin
 except NameError:
  print("\n***** WARNING, variable \"rwin\" not set in parameter file\nUsing default value of \"40\"");
  rwin = "40";
 try: awin
 except NameError:
  print("\n***** WARNING, variable \"awin\" not set in parameter file\nUsing default value of \"40\"");
  awin = "40";
 try: wsamp
 except NameError:
  print("\n***** WARNING, variable \"wsamp\" not set in parameter file\nUsing default value of \"4\"");
  wsamp = "4";
 try: numproc
 except NameError:
  print("\n***** WARNING, variable \"numproc\" not set in parameter file\nUsing default value of \"1\"");
  numproc = "1";
 makeUNW(RawRawFolder,rwin,awin,wsamp);
 start = "affine";
 if start == endStep:
  logFile = open("pixelTrackLog.txt","a");
  logFile.write("\n***** pixelTrack.py for parameters \""+parameterFilePath+"\" - Started at \""+startStep+"\", ended at \""+endStep+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-t1)));
  logFile.close();
  print("\nReached end step \"" + endStep + "\", exiting...\n");
  sys.exit();


if start == "affine":
 getAffineTrans(RawRawFolder);
 start = "geocode";
 if start == endStep:
  logFile = open("pixelTrackLog.txt","a");
  logFile.write("\n***** pixelTrack.py for parameters \""+parameterFilePath+"\" - Started at \""+startStep+"\", ended at \""+endStep+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-t1)));
  logFile.close();
  print("\nReached end step \"" + endStep + "\", exiting...\n");
  sys.exit();

if start == "geocode":
 start = "";
 geocode(RawRawFolder); 
 if start == endStep:
  logFile = open("pixelTrackLog.txt","a");
  logFile.write("\n***** pixelTrack.py for parameters \""+parameterFilePath+"\" - Started at \""+startStep+"\", ended at \""+endStep+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-t1)));
  logFile.close();
  print("\nReached end step \"" + endStep + "\", exiting...\n");  
  sys.exit();


#*****OPTICAL*****

if start == "optical_raw":
 try:
  import pyhdf.SD;
  try: Band
  except NameError:
   print("\n***** WARNING, variable \"Band\" not set in parameter file\nUsing default band \"3N\"\n");
   Band = "3N";
  findHDFCmd = "\nfind "+RawRawFolder+" -name \"*.hdf\" -print\n";
  findHDFStream = os.popen(findHDFCmd);
  findHDFOutput = findHDFStream.read().split();
  findHDFStream.close();
  for fileName in findHDFOutput: 
   hdfFile = pyhdf.SD.SD(fileName);
   num_datasets = hdfFile.info()[0];
   for i in range(0,int(num_datasets)):
    ds = hdfFile.select(i);
    if ds.info()[0].find("ImageData") > -1:
     dim = ds.dim(0);
     samples = str(dim.info()[1]);
     dim2 = ds.dim(1);
     lines = str(dim2.info()[1]);
     if dim.info()[0].find("Band"+Band) > -1:
      out = ds[:];
      if not os.path.exists(RawRawFolder+"/band"+Band):
       os.mkdir(RawRawFolder+"/band"+Band);
      print(RawRawFolder+"/band"+Band+"/"+fileName[fileName.rfind("/"):fileName.rfind(".hdf")]+".b"+Band);
      outfile = open(RawRawFolder+"/band"+Band+fileName[fileName.rfind("/"):fileName.rfind(".hdf")]+".b"+Band, 'wb');
      out = numpy.array(out,numpy.float32);
      out.tofile(outfile);
      outfile.close();
      outfile = open(RawRawFolder+"/band"+Band+fileName[fileName.rfind("/"):fileName.rfind(".hdf")]+".b"+Band+".met","w");
      outfile.write("samples="+samples+"\n");
      outfile.write("lines="+lines+"\n");
      outfile.close();
    ds.endaccess()
   hdfFile.end();
 except ImportError:
  print("\n***** ERROR, \"pyhdf\" module not found, cannot perform this step\n"); 
 start = "";
 if start == endStep:
  logFile = open("pixelTrackLog.txt","a");
  logFile.write("\n***** pixelTrack.py for parameters \""+parameterFilePath+"\" - Started at \""+startStep+"\", ended at \""+endStep+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-t1)));
  logFile.close();
  print("\nReached end step \"" + endStep + "\", exiting...\n");
  sys.exit();

if start == "gausshp_filt":
 bandDirsCmd = "\nfind " + RawRawFolder + " -name \"band*\" -print\n";
 bandDirsStream = os.popen(bandDirsCmd);
 bandDirs = bandDirsStream.read().split();
 bandDirsStream.close();
 bandFiles = [];
 for bandDir in bandDirs:
  if os.path.isdir(bandDir):
   bandDirFiles = os.listdir(bandDir);
   for bandFile in bandDirFiles:
    if re.search("\.b.*\.met",bandFile) > -1:
     bandFiles.append(bandDir+"/"+bandFile[0:bandFile.rfind(".met")]);
 for fileName in bandFiles:
  samples = "";
  lines = "";
  metfile = open(fileName+".met","r");
  for line in metfile:
   if line.find("samples") > -1:
    samples = line.strip().split("=")[1];
   if line.find("lines") > -1:
    lines = line.strip().split("=")[1];
  metfile.close();
  infile = open(fileName,"rb");
  indat = scipy.fromfile(infile,scipy.float32,-1).reshape(int(samples),int(lines));
  infile.close();
  gausshpkernel = numpy.asarray([[-0.0000,-0.0007,-0.0024,-0.0007,-0.0000],[-0.0007,-0.0314,-0.1131,-0.0314,-0.0007],[-0.0024,-0.1131,0.5933,-0.1131,-0.0024],[-0.0007,-0.0314,-0.1131,-0.0314,-0.0007],[-0.0000,-0.0007,-0.0024,-0.0007,-0.0000]]);
  #gausshpkernel = numpy.asarray([[-0.0000,-0.0000,-0.0000,-0.0000,-0.0000],[-0.0000,-0.0000,1.0000,-0.0000,-0.0000],[-0.0000,1.0000,-4.0000,1.0000,-0.0000],[-0.0000,-0.0000,1.0000,-0.0000,-0.0000],[-0.0000,-0.0000,-0.0000,-0.0000,-0.0000]]);
  temp = gausshpfilt(indat,gausshpkernel);
  outfile = open(fileName[0:fileName.rfind(".b")]+"_ghp"+fileName[fileName.rfind(".b"):], 'wb');
  out = numpy.array(temp,numpy.float32);
  out.tofile(outfile);
  outfile.close();
 start = "";
 if start == endStep:
  logFile = open("pixelTrackLog.txt","a");
  logFile.write("\n***** pixelTrack.py for parameters \""+parameterFilePath+"\" - Started at \""+startStep+"\", ended at \""+endStep+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-t1)));
  logFile.close();
  print("\nReached end step \"" + endStep + "\", exiting...\n");
  sys.exit();


if start == "get_xyzs":
 try: MATLAB
 except NameError:
  print("\n***** ERROR, variable \"MATLAB\" not set in parameter file\nMust specify MATLAB directory\n");
  sys.exit();
 findAmpcorFilesCmd = "find " + RawRawFolder + " -name \"*mp*.in\" -print";
 findAmpcorCmdStream = os.popen(findAmpcorFilesCmd);
 findAmpcorOutput = findAmpcorCmdStream.read();
 findAmpcorCmdStream.close();
 ampcorFiles = findAmpcorOutput.split();
 confirmedAmpcorFiles = [];
 for i in range(0,len(ampcorFiles)):
  ampcorFile = open(ampcorFiles[i],"r");
  ampcorFileName = ampcorFiles[i][0:ampcorFiles[i].rfind(".")];
  ampcorPath = ampcorFiles[i][0:ampcorFiles[i].rfind("/")];
  if not (os.path.exists(ampcorFileName + ".off")):
   continue;
  while 1:
   line = ampcorFile.readline();
   if not line:
    break;
   if line.lower().find("ampcor") > -1:
    confirmedAmpcorFiles.append(ampcorFiles[i]);
    sedCmd = "sed -e '/\*/d' " + ampcorFileName + ".off > " + ampcorPath + "/temp";
    sedCmdStream = os.popen(sedCmd);
    sedCmdStream.close();
    diffCmd = "diff " + ampcorFileName + ".off " + ampcorPath + "/temp";
    diffCmdStream = os.popen(diffCmd);
    diffCmdOutput = diffCmdStream.read();
    diffCmdStream.close();
    if diffCmdOutput == "":
     removeTmpCmd = "rm " + ampcorPath + "/temp";
     removeTmpCmdStream = os.popen(removeTmpCmd);
     removeTmpCmdStream.close();
    else:
     mvCmd = "\nmv " + ampcorFileName + ".off " + ampcorFileName + ".off.old\nmv " + ampcorPath + "/temp " + ampcorFileName + ".off\n";
     mvCmdStream = os.popen(mvCmd);
     mvCmdStream.close();
    createMatlabGetXYZ(MATLAB + "/generic_getxyzs.m",ampcorFiles[i]);
    break;
 start = "";
 if start == endStep:
  logFile = open("pixelTrackLog.txt","a");
  logFile.write("\n***** pixelTrack.py for parameters \""+parameterFilePath+"\" - Started at \""+startStep+"\", ended at \""+endStep+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-t1)));
  logFile.close();
  print("\nReached end step \"" + endStep + "\", exiting...\n");
  sys.exit();

if start == "profiles":
 start = "";
 generateProfiles(RawRawFolder);
 if start == endStep:
  logFile = open("pixelTrackLog.txt","a");
  logFile.write("\n***** pixelTrack.py for parameters \""+parameterFilePath+"\" - Started at \""+startStep+"\", ended at \""+endStep+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-t1)));
  logFile.close();
  print("\nReached end step \"" + endStep + "\", exiting...\n");
  sys.exit();

if start == "kml":
 start = "";
 generatePNGs(RawRawFolder);
 getGRDCorners(RawRawFolder);
 generateKML(RawRawFolder);
 if start == endStep:
  logFile = open("pixelTrackLog.txt","a");
  logFile.write("\n***** pixelTrack.py for parameters \""+parameterFilePath+"\" - Started at \""+startStep+"\", ended at \""+endStep+"\", time elapsed to completion: " + ("%.3f seconds\n" % (time.time()-t1)));
  logFile.close();
  print("\nReached end step \"" + endStep + "\", exiting...\n");
  sys.exit();
