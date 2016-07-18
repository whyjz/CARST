import os
import glob
import math

def makeParamFiles(A,B):
  dayA  = (A[13:16])
  yearA = (A[9:13])
  dayB  = (B[13:16])
  yearB = (B[9:13])

  file1 = open("landsat8_" + yearB +"_"+dayA+"_"+dayB+".txt","w")
  file1.write(os.path.realpath(A) +" "+ os.path.realpath(B))
  file1.close()


  file2 = open("params_landsat8_"+yearB+"_to_"+dayA+"_to_"+dayB+"_r32x32_s32x32.txt","w")

   
  # Change these parameters for each section as needed
  file2.write("UTM_ZONE        = 40 \n\
               UTM_LETTER      = X \n\
               BAND            = B8 \n\
               ICE             = /13t1/wjd73/Glacier_outlines/central_alaska_range/central_alaska_range_utm_ice.gmt \n\
               ROCK            = /13t1/wjd73/Glacier_outlines/central_alaska_range/central_alaska_range_utm_rock.gmt \n\
               IMAGE_DIR       = /13t1/wjd73/Franz_Joseph/Landsat8/IMAGES\n\
               METADATA_DIR    = /13t1/wjd73/Franz_Joseph/Landsat8/IMAGES\n\
               PAIRS_DIR       = /13t1/wjd73/Franz_Joseph/Landsat8/Pairs\n\
               PROCESSORS      = 20\n\
               RESOLUTION      = 15\n\
               SATELLITE       = Landsat8\n\
               SNR_CUTOFF      = 0\n\
               DEM	        = /13t1/wjd73/Franz_Joseph/DEM/FJLREGION_DEM.tif\n\
               PREFILTER       = False\n\
               REF_X           = 32\n\
               REF_Y           = 32\n\
               SEARCH_X        = 32\n\
               SEARCH_Y        = 32\n\
               STEP            = 8\n\
               M_SCRIPTS_DIR   = /13t1/wjd73/MATLAB/Adam_Cleaner\n\
               VEL_MAX         = 5\n\
               TOL             = 0.3\n\
               NUMDIF          = 3\n\
               SCALE           = 1500000\n\
               PAIRS           = /13t1/wjd73/Franz_Joseph/Landsat8/Pairs/"+file1.name+"\n")
  file2.close() 


  file3 = open("px_landsat8_"+yearB+"_"+dayA+"_to_"+dayB+".cmd","w")
  file3.write("python /home/wjd73/Python/landsatPX.py " + file2.name+"\n")
  file3.close()

  


def daydiff(A,B):
  dayA = int(A[13:16])
  yearA = int(A[9:13])
  dayB = int(B[13:16])
  yearB = int(B[9:13])

  diff =(dayB - (dayA -(yearB-yearA)*365))

  #print(str(dayA) +"\t" +str(yearA) +"\t" + str(dayB) + "\t" +str(yearB))
  #print diff
  return diff

###################################################
def main():
  scenelist = glob.glob("*B8.TIF")
  scenelist.sort()

  for i in range(len(scenelist) -1):
    A = scenelist[i]
    B = scenelist[i+1]
    #print(A + "\t" + B)
    diff = daydiff(A,B)
    if (diff <= 48):
       print(A + "\t" + B + "\t" + str(diff))
       makeParamFiles(A,B)


main()
    
  
