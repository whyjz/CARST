#!/usr/bin/python

'''Overlap module for NTF (JPEG2000) files
Created by Andrew Melkonian, 2014'''

import os
import re;
import subprocess
import sys;


# Global variables
MIN_OVERLAP = 1.0  # [km^2]
UTM_ZONE = "41X";

if len(sys.argv) > 2:

    image1 = sys.argv[1];
    image2 = sys.argv[2];
    ice = sys.argv[3];

    '''Returns: True if image1 and image2 overlap; False otherwise.

    Only returns True if images overlap over regions with data
    and over glacial areas, over an area greater than MIN_OVERLAP

    ice = appropriate ice outlines for this utm zone and archipelago

    Preconditions: image1 and image2 are paths to .ntf files (gdalinfo input cannot be parsed otherwise)'''

    interval = '240'  # resampling interval (in m)

    cmd = "\ngdalinfo " + image1 + "\n";
    pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
    info = pipe.read().strip();
    pipe.close();

    image1_ul = info[re.search("UpperLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0):re.search("UpperLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];
    elements = image1_ul.split(",");
    image1_ulx = elements[0];
    image1_uly = elements[1];

    image1_ur = info[re.search("UpperRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0):re.search("UpperRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];
    elements = image1_ur.split(",");
    image1_urx = elements[0];
    image1_ury = elements[1];

    image1_ll = info[re.search("LowerLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0):re.search("LowerLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];
    elements = image1_ll.split(",");
    image1_llx = elements[0];
    image1_lly = elements[1];

    image1_lr = info[re.search("LowerRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0):re.search("LowerRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];
    elements = image1_lr.split(",");
    image1_lrx = elements[0];
    image1_lry = elements[1];

    cmd = "\ngdalinfo " + image2 + "\n";
    pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
    info = pipe.read().strip();
    pipe.close();

    image2_ul = info[re.search("UpperLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0):re.search("UpperLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];
    elements = image2_ul.split(",");
    image2_ulx = elements[0];
    image2_uly = elements[1];

    image2_ur = info[re.search("UpperRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0):re.search("UpperRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];
    elements = image2_ur.split(",");
    image2_urx = elements[0];
    image2_ury = elements[1];

    image2_ll = info[re.search("LowerLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0):re.search("LowerLeft,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];
    elements = image2_ll.split(",");
    image2_llx = elements[0];
    image2_lly = elements[1];

    image2_lr = info[re.search("LowerRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(",info).end(0):re.search("LowerRight,\s+Info=\s*\(\d+\.*\d*,\d+\.*\d*\)\s+->\s+\(\d+\.*\d*\s*,\s*\d+\.*\d*",info).end(0)];
    elements = image2_lr.split(",");
    image2_lrx = elements[0];
    image2_lry = elements[1];

    xmin = str(min(float(image1_ulx),float(image1_llx),float(image2_ulx),float(image2_llx)));
    xmax = str(max(float(image1_urx),float(image1_lrx),float(image2_urx),float(image2_lrx)));
    ymin = str(min(float(image1_lly),float(image1_lry),float(image2_lly),float(image2_lry)));
    ymax = str(max(float(image1_uly),float(image1_ury),float(image2_uly),float(image2_ury)));

    cmd = "\necho \"" + xmin + " " + ymin + "\n" + xmax + " " + ymax + "\"";
    cmd += " | mapproject -Ju" + UTM_ZONE + "/1:1 -F -C\n";
    pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
    bounds = pipe.read().split();
    pipe.close();

    xmin = bounds[0];
    ymin = bounds[1];
    xmax = bounds[2];
    ymax = bounds[3];

    R = "-R" + xmin + "/" + ymin + "/" + xmax + "/" + ymax + "r";

    cmd = "\necho \"" + image1_ulx + " " + image1_uly + "\n" + image1_urx + " " + image1_ury + "\n" + image1_llx + " " + image1_lly + "\n" + image1_lrx + " " + image1_lry + "\"";
    cmd += " | mapproject -Ju" + UTM_ZONE + "/1:1 -F -C ";
    cmd += " | grdmask -Gimage1.grd -I" + interval + "= " + R + " -NNaN/NaN/1\n";
    subprocess.call(cmd,shell=True);

    cmd = "\necho \"" + image2_ulx + " " + image2_uly + "\n" + image2_urx + " " + image2_ury + "\n" + image2_llx + " " + image2_lly + "\n" + image2_lrx + " " + image2_lry + "\"";
    cmd += " | mapproject -Ju" + UTM_ZONE + "/1:1 -F -C ";
    cmd += " | grdmask -Gimage2.grd -I" + interval + "= " + R + " -NNaN/NaN/1\n";
    subprocess.call(cmd,shell=True);

    cmd = "\ngrdmask " + ice + " -Gice_mask.grd -I" + interval + "= " + R + " -NNaN/NaN/1 -m\n";
    cmd += "\ngrdmath image1.grd ice_mask.grd OR = image1.grd\n";
    cmd += "\ngrdmath image2.grd ice_mask.grd OR = image2.grd\n";
    cmd += "\ngrdmath image1.grd image2.grd OR = image_overlap.grd\n";
    subprocess.call(cmd,shell=True);

    cmd = "\ngrdvolume image_overlap.grd\n";
    pipe = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE).stdout;
    volume_info = pipe.read().split();
    pipe.close();

    #if float(volume_info[0])/1e6 > MIN_OVERLAP:
    print(image1 + " " + image2 + " " + volume_info[0]);

    cmd = "\nrm image1.grd image2.grd image_overlap.grd ice_mask.grd\n";
    subprocess.call(cmd,shell=True);

    exit();

