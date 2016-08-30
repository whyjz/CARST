# first created and copied from landsatPX.py: Aug 19 2016
# Authors: Andrew K. Melkonian, William J. Durkin, Whyjay Zheng

import sys
import os
# sys.path.insert(0, os.path.abspath('../Utilities/Python'))        # for all modules
sys.path.insert(0, os.path.abspath(os.path.dirname(sys.argv[0])) + '/../Utilities/Python')        # for all modules
# import re
# import subprocess
from UtilTIF import SingleTIF
from UtilConfig import ConfParams
# from UtilFit import TimeSeriesDEM
# from splitAmpcor import splitAmpcor
# from getxyzs import getxyzs
# import datetime

if len(sys.argv) < 2:
    print('Error: Usage: pixeltrack.py config_file')
    sys.exit(1)

# ==== Read ini file ====

inipath = sys.argv[1]
ini = ConfParams(inipath)
ini.ReadParam()
ini.VerifyParam()
imgpairlist = ini.GetImgPair(delimiter=' ')

# print(imgpairlist)
# imgpairlist = pair_hash
#    i.e. imgpair = [[<SingleTIF>, <SingleTIF>], [<SingleTIF>, <SingleTIF>], ...]
#                            1st pair          ,          2nd pair         , ...

# skip the date input first
# skip sorting the first and the second (default is that the first is the earlier)
# skip dealing with different projection
# skip creating new folder based on its date

# fixed parameters
ini.gdalwarp['of'] = 'ENVI'
ini.gdalwarp['ot'] = 'Float32'


# ==== warp all DEMs using gdalwarp ====

for imgpair in imgpairlist:
    if not ini.gdalwarp['te']:
        extent = [img.GetExtent() for img in imgpair]
        intersection = [max(extent[0][0], extent[1][0]), 
                        min(extent[0][1], extent[1][1]), 
                        min(extent[0][2], extent[1][2]), 
                        max(extent[0][3], extent[1][3])]
        intersection_te = [intersection[i] for i in [0, 3, 2, 1]]
        ini.gdalwarp['te'] = '{:f} {:f} {:f} {:f}'.format(*intersection_te)
    if not ini.gdalwarp['t_srs']:
        ini.gdalwarp['t_srs'] = '"' + imgpair[0].GetProj4() + '"'

    for img in imgpair:
        img.Unify(ini.gdalwarp)

    ampcor_label = "r" +  ini.splitampcor['ref_x']    + "x" + ini.splitampcor['ref_y']    +\
                   "_s" + ini.splitampcor['search_x'] + "x" + ini.splitampcor['search_y']





# print(ini.gdalwarp['of'])
# print(ini.gdalwarp['ot'])






# print(imgpairlist[0][0].fpath)
# img = SingleTIF(imgpairlist[0][0])
# print(imgpairlist[0][0].GetExtent())
# print(imgpairlist[0][0].GetProj4())


"""
try:


    # for test, all the parameters are given here.
    # ========================================================
    # UTM_ZONE        = '5'
    # UTM_LETTER      = 'na'
    # BAND            = 'na' 
    # ICE             = 'na/na' 
    # ROCK            = 'na/na' 
    # IMAGE_DIR       = 'na/na'
    # METADATA_DIR    = './Landsat8_example/IMAGES'
    # PAIRS_DIR       = './Landsat8_example'
    # PROCESSORS      = '16'
    # RESOLUTION      = '15'
    # SATELLITE       = 'na'
    # SNR_CUTOFF      = 'na'
    # DEM             = 'na'
    # PREFILTER       = 'False'
    # REF_X           = '32'
    # REF_Y           = '32'
    # SEARCH_X        = '32'
    # SEARCH_Y        = '32'
    # STEP            = '8'
    # M_SCRIPTS_DIR   = 'na'
    # VEL_MAX         = 'na'
    # TOL             = 'na'
    # NUMDIF          = 'na'
    # SCALE           = 'na'
    # PAIRS           = './Landsat8_example/landsat8_2016_200_216.txt'
    # GNU_PARALLEL    = 'False'
    # NODE_LIST       = 'None'
    # ========================================================




    for pair in pairs_hash:

        image1_path = pair[0]
        image2_path = pair[1]
        # image1_path = './Landsat8_example/IMAGES/LC80630182016200LGN00_B8_yahtse.TIF'

        image1_name = image1_path[image1_path.rfind("/") + 1 : image1_path.rfind("_")];
        image2_name = image2_path[image2_path.rfind("/") + 1 : image2_path.rfind("_")];
        # image1_name = 'LC80630182016200LGN00_B8'

        image1_metadata_path = METADATA_DIR + "/" + image1_name + "_MTL.txt";
        image2_metadata_path = METADATA_DIR + "/" + image2_name + "_MTL.txt";
        # image1_metadata_path = './Landsat8_example/IMAGES/LC80630182016200LGN00_B8_MTL.txt'
        # the official LS8 metadata filename is LC80630182016200LGN00_MTL.txt

        if not os.path.exists(image1_metadata_path):
            print("\n***** WARNING: \"" + image1_metadata_path + "\" not found, make sure full path is provided, skipping...\n");
            continue;

        if not os.path.exists(image2_metadata_path):
            print("\n***** WARNING: \"" + image2_metadata_path + "\" not found, make sure full path is provided, skipping...\n");
            continue;

        # ============ GET time and date from METADATA ==========
        image1_time = "";
        image1_date = "";

        infile = open(image1_metadata_path, "r");

        for line in infile:

            if line.find("DATE_ACQUIRED") > -1:
                label, image1_date = line.split("=");
                image1_date = image1_date.strip();
                image1_date = image1_date.replace("-","");

            if line.find("SCENE_CENTER_TIME") > -1:
                label, image1_time = line.split("=");
                image1_time = image1_time.strip();
                image1_time = image1_time.replace("\"","");
                image1_time = image1_time.replace(":","")[0:6];

        infile.close();
        # image1_time = '203706'   original: "20:37:06.3391580Z"
        # image1_date = '20160718' original: "2016-07-18"

        image2_time = "";
        image2_date = "";

        infile = open(image2_metadata_path, "r");

        for line in infile:

            if line.find("DATE_ACQUIRED") > -1:
                label, image2_date = line.split("=");
                image2_date = image2_date.strip();
                image2_date = image2_date.replace("-","");

            if line.find("SCENE_CENTER_TIME") > -1:
                label, image2_time = line.split("=");
                image2_time = image2_time.strip();
                image2_time = image2_time.replace("\"","");
                image2_time = image2_time.replace(":","")[0:6];

        infile.close();
        # =======================================================

        image1_link_path = image1_path[image1_path.rfind("/") + 1 : ];
        image2_link_path = image2_path[image2_path.rfind("/") + 1 : ];
        # image1_link_path = 'LC80630182016200LGN00_B8_yahtse.TIF'

        early_image_path = image2_link_path;
        later_image_path = image1_link_path;
        early_date       = image2_date + image2_time;
        later_date       = image1_date + image1_time;

        if image2_date > image1_date:
            early_image_path = image1_link_path;
            later_image_path = image2_link_path;
            early_date       = image1_date + image1_time;
            later_date       = image2_date + image2_time;

        pair_label = later_date + "_" + early_date;
        pair_path  = PAIRS_DIR + "/" + pair_label;

        image1_link_path  = pair_path + "/" + image1_link_path;
        image2_link_path  = pair_path + "/" + image2_link_path;
        early_image_path  = pair_path + "/" + early_image_path;
        later_image_path  = pair_path + "/" + later_image_path;
        # image1_link_path = './20160803203709_20160718203706/LC80630182016200LGN00_B8_yahtse.TIF'
        # image2_link_path = './20160803203709_20160718203706/LC80630182016216LGN00_B8_yahtse.TIF'
        # early_image_path = image 1 link path in this case
        # later_image_path = image 2 link path in this case
        # pair_path = './20160803203709_20160718203706'

        # =========== make working folder and symlinks ==========
        if not os.path.exists(pair_path):
            os.mkdir(pair_path);

        if not os.path.exists(image1_link_path):
            os.symlink(image1_path, image1_link_path);

        if not os.path.exists(image2_link_path):
            os.symlink(image2_path, image2_link_path);
        # =======================================================

        # We do not do the prefilter right now 
        # ======================================
        if PREFILTER == "True":

            early_ghp_path = pair_path + "/" + early_image_path[early_image_path.rfind("/") + 1 : early_image_path.rfind(".")] + "_ghp_stretch.img"; 
            later_ghp_path = pair_path + "/" + later_image_path[later_image_path.rfind("/") + 1 : later_image_path.rfind(".")] + "_ghp_stretch.img"; 

#           if not os.path.exists(early_ghp_path) or not os.path.exists(later_ghp_path):
#               print("\n***** WARNING: \"" + early_ghp_path + " or " + later_ghp_path + " not found, plese open \"idlde\" and run the commands:\n\n \
#                      envi\n \
#                      gausshighpassfiltergausstretch,\"" + early_link_path + "\"\n \
#                      gausshighpassfiltergausstretch,\"" + later_link_path + "\"\n\n \
#                      Skipping this pair...\n");
#               continue;
#
            early_image_path = early_ghp_path;
            later_image_path = later_ghp_path;

        # ======================================
        early_cut_path = early_image_path[ : early_image_path.rfind(".")] + "_cut.img";
        later_cut_path = later_image_path[ : later_image_path.rfind(".")] + "_cut.img";
        # early_cut_path = './20160803203709_20160718203706/LC80630182016200LGN00_B8_yahtse_cut.img'

        # ========= Generate *_cut.img ==========
        if not os. path.exists(early_cut_path):
            cmd  = "\ngdal_translate -of ENVI -ot Float32 -projwin " + ul_x + " " + ul_y + " " + lr_x + " " + lr_y + " " + early_image_path + " " + early_cut_path + "\n";
            subprocess.call(cmd, shell=True);

        if not os.path.exists(later_cut_path):
            cmd = "\ngdal_translate -of ENVI -ot Float32 -projwin " + ul_x + " " + ul_y + " " + lr_x + " " + lr_y + " " + later_image_path + " " + later_cut_path + "\n";
            subprocess.call(cmd,shell=True);

        if not os.path.exists(early_cut_path) or not os.path.exists(later_cut_path):
            print("\n***** ERROR: \"gdal_translate\" to cut images to common region unsuccessful skipping \"" + pair_label + "...\n");
        # =======================================

        # generate ampcor input using splitAmpcor.py
        if not os.path.exists(pair_path + "/ampcor_" + ampcor_label + "_1.in"):
            print("\nRunning \"splitAmpcor.py\" to create \"ampcor\" input files...\n");
            splitAmpcor(early_cut_path, later_cut_path, pair_path, PROCESSORS, RESOLUTION, REF_X, REF_Y, SEARCH_X, SEARCH_Y, STEP); 

        else:
            print("***** \"" + pair_path + "/ampcor_" + ampcor_label + "_1.in\" already exists, assuming \"ampcor\" input files already made...\n");

        # [Part 1] This is for pre-running case: if there's no xxxxxxx_1.off, the program will run run_amp.cmd and exits
        if not os.path.exists(pair_path + "/ampcor_" + ampcor_label + "_1.off"):

            
            # write something to run_amp.cmd
            amp_file = open(pair_path+"/run_amp.cmd", 'w')
            amps_complete = open(pair_path+"/amps_complete.txt", 'w')
            amps_complete.close()
            for i in range(1, int(PROCESSORS) + 1):
                # there used to be a path issue and now fixed - WJ
                amp_file.write("(ampcor " + "ampcor_" + ampcor_label + "_" + str(i) + ".in rdf > " + "ampcor_" + ampcor_label + "_" + str(i) + ".out; echo " + str(i) + " >> amps_complete.txt) &\n")
            amp_file.close()        


            # Options for processing with gnu parallel or as backgrounded processes
            if GNU_PARALLEL == "True":
                print("\n\"ampcor\" running as " + PROCESSORS + " separate processes, this step may take several hours to complete...\n");
                # For what ever reason, ampcor will not run unless it is executed from within the pair_path. 
                # This is a slopy fix of just hopping in and out of the pair_path to run ampcor
                cmd  = "cd "+pair_path+"\n";
                if NODE_LIST == "None":
                    cmd += '''\nawk '{$NF=""; print $0}' run_amp.cmd | parallel --workdir $PWD\n''';
                else:
                    print("Using node file "+NODE_LIST)
                    cmd += '''\nawk '{$NF=""; print $0}' run_amp.cmd | parallel --sshloginfile ''' + NODE_LIST + ''' --workdir $PWD\n''';
                cmd += "cd ../\n";
                subprocess.call(cmd, shell=True);
                print("After all ampcor processes have completed, please rerun the landsatPX.py script.\n")
                sys.exit(0)

            # If not using gnu parallel, this try block will gracefully exit the script and give instructions
            # the next step
            elif GNU_PARALLEL == "False":
                cmd  = "cd " + pair_path + "\n";
                cmd += "bash run_amp.cmd\n";
                cmd += "cd ../\n" 
                subprocess.call(cmd, shell=True);

                print("\n\"ampcor\" running as " + PROCESSORS + " separate processes, this step may take several hours to complete...\n");
                print("After all ampcor processes have completed, please rerun the landsatPX.py script.\n")
                sys.exit(0)
                   
        # [Part 2] If the program detects xxxxxxx_1.off, it will think that ampcor has finished (by runnning run_amp.cmd).
        pair_done = True;

        # ======== Check if all ampcor has finished =========
        with open(pair_path+"/amps_complete.txt") as ac:
            amps_comp_num = ac.readlines()
        
        if len(amps_comp_num) < int(PROCESSORS):
            print("\n***** It looks like not all ampcor processes have completed.")
            print("     Skipping....")
            sys.exit(1)
        # ===================================================

        #for i in range(1, int(PROCESSORS) + 1):

        #   infile = open(pair_path + "/ampcor_" + ampcor_label + "_" + str(i) + ".in", "r");

        #   for line in infile:

        #       if line.find("Start, End and Skip Lines in Reference Image") > -1:
        #           end_line = line.split("=")[1].split()[1];

        #   infile.close();

        #   last_line_processed = tail(pair_path + "/ampcor_" + ampcor_label + "_" + str(i) + ".off", 1).split()[2];

                        # Checks if the .off files have completed. This does not work correctly now, so I will write a different section 
                        # soon.
            #if (int(end_line) - int(last_line_processed)) > (int(REF_Y) + int(SEARCH_Y) + 2000):
            #   print("\n***** ERROR, last line processed in \"" + pair_path + "/ampcor_" + ampcor_label + "_" + str(i) + ".off\" is " \
            #          + last_line_processed + ", last line to be processes is " + end_line + ", the difference is greater than the \
            #          search window size in lines plus the reference window size in lines (" \
            #          + str(int(REF_Y) + int(SEARCH_Y)) + "), pair might still be processing, skipping...\n"); 
            #   pair_done = False;

        #if not pair_done:
        #   return;
               
        print("\n***** Offset files in \"" + pair_path + "\" appear to have finished processing, composing results...\n");

        # ==== cat all output to ampcor_label.off ====
        if os.path.exists(pair_path + "/ampcor_" + ampcor_label + ".off"):
            print("\n***** \"" + pair_path + "/ampcor_" + ampcor_label + ".off\" already exists, assuming it contains all offsets for this run...\n");

        else:

            cat_cmd = "\ncat ";

            for i in range(1, int(PROCESSORS) + 1):
                cmd = "\nsed -i '/\*/d' " + pair_path + "/ampcor_" + ampcor_label + "_" + str(i) + ".off\n";
                cat_cmd += pair_path + "/ampcor_" + ampcor_label + "_" + str(i) + ".off ";
                subprocess.call(cmd, shell=True);

            cat_cmd += "> " + pair_path + "/ampcor_" + ampcor_label + ".off\n";
            subprocess.call(cat_cmd, shell=True);
        # ============================================

        # get ref samples and lines number 
        ref_samples = "";
        ref_lines   = "";

        infile = open(early_cut_path.replace(".img",".hdr"), "r");

        for line in infile:

            if line.lower().find("samples") > -1:
                ref_samples = line.split("=")[1].strip();

            if line.lower().find("lines") > -1:
                ref_lines = line.split("=")[1].strip();

        infile.close();
        # ref_samples = '1698'
        # ref_lines = '1087'

        east_name      = pair_label + "_" + ampcor_label + "_eastxyz";
        north_name     = pair_label + "_" + ampcor_label + "_northxyz";
        mag_name       = pair_label + "_" + ampcor_label + "_mag";
        east_xyz_path  = pair_path + "/" + east_name + ".txt";
        north_xyz_path = pair_path + "/" + north_name + ".txt";

        if not os.path.exists(east_xyz_path):
            print("\n***** \"getxyzs.py\" running to create E-W and N-S ASCII files with offsets (in m) in the third column and SNR in the 4th column\n \
               ***** NOTE: E-W MAY BE FLIPPED DEPENDING ON HEMISPHERE, PLEASE CHECK MANUALLY...\n");
            # This will generate a lot of warnings when using python 3...
            # anyway, it's generating 20160803203709_20160718203706_r32x32_s32x32_eastxyz.txt
            #                     and 20160803203709_20160718203706_r32x32_s32x32_northxyz.txt
            getxyzs(pair_path, ampcor_label, STEP, STEP, "1", RESOLUTION, ref_samples, ref_lines, ul_x, ul_y, pair_label);

        else:
            print("\n***** \"" + east_xyz_path + "\" already exists, assuming E-W and N-S ASCII offsets (in m) files created properly for this run...\n");

        east_grd_path  = pair_path + "/" + east_name + ".grd";
        north_grd_path = pair_path + "/" + north_name + ".grd";
        mag_grd_path   = pair_path + "/" + mag_name + ".grd";
        snr_grd_path   = pair_path + "/" + north_name.replace("north", "snr") + ".grd";

        R = "-R" + ul_x + "/" + lr_y + "/" + lr_x + "/" + ul_y + "r";
        # R = '-R465067.5/6665272.5/490537.5/6681577.5r'

        if not os.path.exists(east_grd_path):
            print("\n***** Creating \"" + east_grd_path + "\" and \"" + north_grd_path + "\" using \"xyz2grd\"...\n");
            early_datetime = datetime.datetime(int(early_date[0:4]), int(early_date[4:6]), int(early_date[6:8]), \
                               int(early_date[8:10]), int(early_date[10:12]), int(early_date[12:14]));
            later_datetime = datetime.datetime(int(later_date[0:4]), int(later_date[4:6]), int(later_date[6:8]), \
                               int(later_date[8:10]), int(later_date[10:12]), int(later_date[12:14]));
            day_interval   = str((later_datetime - early_datetime).total_seconds() / (60. * 60. * 24.));
            # early_datetime = datetime.datetime(2016, 7, 18, 20, 37, 6)
            # later_datetime = datetime.datetime(2016, 8, 3, 20, 37, 9)
            # day_interval = '16.00003472222222'
            cmd  = "\nxyz2grd " + east_xyz_path + " " + R + " -G" + east_grd_path + " -I" + str(int(STEP) * int(RESOLUTION)) + "=\n";
            cmd += "\nxyz2grd " + north_xyz_path + " " + R + " -G" + north_grd_path + " -I" + str(int(STEP) * int(RESOLUTION)) + "=\n";
            cmd += "\ngawk '{print $1\" \"$2\" \"$4}' " + north_xyz_path + " | xyz2grd " + R + " \
                -G" + snr_grd_path + " -I" + str(int(STEP) * int(RESOLUTION)) + "=\n";
            cmd += "\ngrdmath " + east_grd_path + " " + day_interval + " DIV --IO_NC4_CHUNK_SIZE=c = " + east_grd_path + "\n";
            cmd += "\ngrdmath " + north_grd_path + " " + day_interval + " DIV --IO_NC4_CHUNK_SIZE=c = " + north_grd_path + "\n";
            cmd += "\ngrdmath " + north_grd_path + " " + east_grd_path + " HYPOT --IO_NC4_CHUNK_SIZE=c = " + mag_grd_path + "\n";
            subprocess.call(cmd, shell=True);
            # please note that xxxxx_snrxyz.grd only counts the error from fitting a cross-correlation peak.
            # it does not include the offset between ref image and search image, which is also can be a significant source of errors.
            #
            # The unit in mag, north, east is pixel/day.

        else:
            print("\n***** \"" + east_grd_path + "\" already exists, assuming m/day velocity grids already made for this run...\n"); 
                               
               
    sys.exit(0)

except IOError:
    # this is caused when run_cmd has a bad path issue. will fix in the future update.
    message  = "     Please run ampcors by excecuting the following commands:\n\n"
    message += "     cd " + pair_path + "\n"
    message += "     bash run_amp.cmd\n\n"
    message += "     This may take several hours to complete.\n"
    message += "     After all ampcor processes have completed, please rerun the landsatPX.py script"

    n = max([len(i) for i in message.split('\n')])
    print("*"*n + "*****")
    print(message)
    print("*"*n + "*****")
"""