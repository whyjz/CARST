#/usr/bin/python
# Originally written by Andrew Melkonian
# Modified by Whyjay Zheng, 2016 Feb 11
#    - fix the issue on 0.5-m resolution


def ampoffToUTM(ampoff_path, ampin_path, ref_hdr_path, output_label):

	import os;
	import subprocess;

	assert os.path.exists(ampoff_path), "\n***** ERROR: " + ampoff_path + " does not exist\n";
	assert os.path.exists(ampin_path), "\n***** ERROR: " + ampin_path + " does not exist\n";
	assert os.path.exists(ref_hdr_path), "\n***** ERROR: " + ref_hdr_path + " does not exist\n";

	mean_x_off = "";
	mean_y_off = "";
	skip       = "";
	inc        = "";
	ul_x       = "";
	ul_y       = "";
	width      = "";
	length     = "";

	infile = open(ampin_path, "r");

    # find value of skip, mean_x_offset, and mean_y_offset
	for line in infile:

		if line.find("Start, End and Skip Lines") > -1:
			elements = line.split();
			skip     = elements[len(elements) - 1];

		elif line.find("Mean Offset") > -1:
			elements = line.split("=");
			mean_x_off, mean_y_off = elements[1].strip().split();
			break;

	infile.close();


	infile = open(ref_hdr_path, "r");

	for line in infile:

		if line.strip().lower().find("samples") > -1:
			elements = line.split("=");
			width    = elements[1].strip();
			
		elif line.strip().lower().find("lines") > -1:
			elements = line.split("=");
			length   = elements[1].strip();
			
		elif line.find("map") > -1:
			elements = line[line.find("{") + 1 : line.find("}")].split(",");
			# inc      = elements[1].replace(",","");           # Whyj modified
			inc      = elements[6].replace(",","");
			ul_x     = elements[3].replace(",","").strip();
			ul_y     = elements[4].replace(",","").strip();
			break;

	infile.close();

	print 'mean_x_off, mean_y_off: ', mean_x_off, mean_y_off
	print 'skip, inc: ', skip, inc
	print 'ul_x, ul_y: ', ul_x, ul_y
	print 'width, length: ', width, length

	# lr_x = str(float(ul_x) + (int(width) / int(skip) - 1) * int(skip));      # whyj modified
	# lr_y = str(float(ul_y) - (int(length) / int(skip) - 1) * int(skip));     # whyj modified

	lr_x = str(float(ul_x) + (int(width)  * float(inc) / int(skip) - 1) * int(skip))
	lr_y = str(float(ul_y) - (int(length) * float(inc) / int(skip) - 1) * int(skip))

	R = "-R" + ul_x + "/" + lr_y + "/" + lr_x + "/" + ul_y + "r";

	infile = open(ampoff_path, "r");

	ew_txt_path = output_label + "_eastxyz.txt";
	ns_txt_path = output_label + "_northxyz.txt";

	ew_txt_file = open(ew_txt_path, "w");
	ns_txt_file = open(ns_txt_path, "w");

	for line in infile:

		if line.find("*") > -1:
			continue;

		x_ind, x_off, y_ind, y_off, snr, c_11, c_22, c_12 = line.strip().split();

		# x_pos = str(float(ul_x) + (((int(x_ind) - 1) * int(inc)) / int(skip)) * int(skip));    # whyj modified
		# y_pos = str(float(ul_y) - (((int(y_ind) - 1) * int(inc)) / int(skip)) * int(skip));    # whyj modified

		x_pos = str(float(ul_x) + (((int(x_ind) - 1) * float(inc)) / int(skip)) * int(skip))
		y_pos = str(float(ul_y) - (((int(y_ind) - 1) * float(inc)) / int(skip)) * int(skip))


		ew_txt_file.write(x_pos + " " + y_pos + " " + str(float(x_off) - float(mean_x_off)) + " " + snr + "\n");
		ns_txt_file.write(x_pos + " " + y_pos + " " + str(float(y_off) - float(mean_y_off)) + " " + snr + "\n");

#		ew_txt_file.write(str(float(ul_x) + (float(x_ind) - 1) * float(inc)) + " " + str(float(ul_y) - (float(y_ind) - 1) * float(inc)) + " " + str(float(x_off) - float(mean_x_off) * float(inc)) + " " + snr + "\n");
#		ns_txt_file.write(str(float(ul_x) + (float(x_ind) - 1) * float(inc)) + " " + str(float(ul_y) - (float(y_ind) - 1) * float(inc)) + " " + str(float(y_off) - float(mean_y_off) * float(inc)) + " " + snr + "\n");

	ew_txt_file.close();
	ns_txt_file.close();

	ew_grd_path = ew_txt_path.replace("txt", "grd");
	ns_grd_path = ns_txt_path.replace("txt", "grd");

	I_str = '%d' % (int(skip) * float(inc) * 1.5)    # whyj modified
	print R, I_str

	# cmd  = "\nxyz2grd " + ew_txt_path + " " + R + " -I" + skip + "= -G" + ew_grd_path + " --IO_NC4_CHUNK_SIZE=c\n";    # whyj modified
	# cmd += "\nxyz2grd " + ns_txt_path + " " + R + " -I" + skip + "= -G" + ns_grd_path + " --IO_NC4_CHUNK_SIZE=c\n";    # whyj modified

	cmd  = "\nxyz2grd " + ew_txt_path + " " + R + " -I" + I_str + "= -G" + ew_grd_path + " --IO_NC4_CHUNK_SIZE=c\n";
	cmd += "\nxyz2grd " + ns_txt_path + " " + R + " -I" + I_str + "= -G" + ns_grd_path + " --IO_NC4_CHUNK_SIZE=c\n";
	cmd += "\nxyz2grd " + ns_txt_path + " " + R + " -I" + I_str + "= -G" + ns_grd_path.replace("northxyz", "snr") + " -i0,1,3 --IO_NC4_CHUNK_SIZE=c\n";
	subprocess.call(cmd, shell=True);
	

	return;



if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 4, "\n***** ERROR: ampoffToUTM.py requires 4 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";
	assert os.path.exists(sys.argv[3]), "\n***** ERROR: " + sys.argv[3] + " does not exist\n";
	
	ampoffToUTM(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]);

	exit();

