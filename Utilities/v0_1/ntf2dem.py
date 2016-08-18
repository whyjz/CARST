#!/usr/bin/python


# ntf2dem.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


# Description
# ***********
# Wrapper for StereoPipeline tools that takes raw *.ntf files from a left- and right-hand WorldView stereo-image pair and creates a DEM


# Usage
# *****
# python ntf2dem /path/to/pair/dir/ /path/to/ref_dem.tif utm_zone


# Notes
# *****
# The variable "pbs_header_str" is used throughout to set the resources requested for each command.
# To adjust the resources requested for a particular command, change the "pbs_header_str" directly before that command is run


def ntf2dem(pair_path, ref_dem_path, utm_zone, start_step):

	import math;
	import os;
	import re;
	import subprocess;


#	Check that pair path and reference DEM path exist 

	assert os.path.exists(pair_path), "\n***** ERROR: " + pair_path + " does not exist\n";
	assert os.path.exists(ref_dem_path), "\n***** ERROR: " + ref_dem_path + " does not exist\n";

#	Initialize "steps" hashtable

	steps = {"correct" : 1, "mosaic" : 2, "project" : 3, "stereo_0" : 4, "stereo_1" : 5, "stereo_2" : 6, "stereo_3" : 7, "stereo_4" : 8, "pc2dem" : 9, "ortho" : 10};

#	Check that "start_step" is a valid step

	assert start_step in steps, "\n***** ERROR: \"" + start_step + "\" is not a valid step, please enter one of the following steps or do not enter a step to run all steps: " + str(steps.keys()) + "\n";

	step = steps[start_step];

#	The file "run_this_pair.cmd" (created in the pair directory) will contain all of the "qsub" commands run by this script

	main_cmd_file = open(pair_path + "/run_this_pair.cmd", "w");


#	Max jobs is the maximum number of jobs that can potentially run at once for one pair (NOT the maximum number of jobs submitted)

	MAX_JOBS = 8;


#	Find ntf files in the pair directory, separated by catalog ID into left and right swaths

	contents   = os.listdir(pair_path);
	ntfs       = [item for item in contents if re.search("P1BS.*\.ntf", item)];

	if not ntfs:
		ntfs = [item for item in contents if re.search("M1BS.*\.ntf", item)];

	left_ntfs  = {};	
	right_ntfs = {};	
	left_set   = False;
	right_set  = False;
	jid        = "";

	for ntf in ntfs:

		labels = ntf.split("-");
		cat_id = labels[len(labels) - 1].replace(".ntf", "");

		if not os.path.exists(pair_path + "/" + ntf.replace(".ntf", "_corrected.xml")):
			os.symlink(pair_path + "/" + ntf.replace("ntf", "xml"), pair_path + "/" + ntf.replace(".ntf", "_corrected.xml"));

		if not left_set:
			left_ntfs[cat_id] = [];
			left_ntfs[cat_id].append(ntf);
			left_set = True;

		elif cat_id in left_ntfs:
			left_ntfs[cat_id].append(ntf);
			
		elif not right_set:
			right_ntfs[cat_id] = [];
			right_ntfs[cat_id].append(ntf);
			right_set = True;	

		else:
			right_ntfs[cat_id].append(ntf);

#	Determine date (YYMMMDD), satellite (e.g., "WV01", "QB02") and use these, along with the two catolog IDs, to create a label for this pair

	labels = ntfs[0].split("_");
	sat    = labels[0];
	date   = labels[1][0:7];


#	Set PBS variables for "wv_correct", currently assigns one node per wv_correct command, with 1 processor/core per node

	pbs_header_str = "#PBS -S /bin/csh\n#PBS -N cfd\n#PBS -l select=1:ncpus=1:mpiprocs=1:model=wes\n#PBS -l walltime=0:30:00\n#PBS -j oe\n#PBS -W group_list=s1334\n#PBS -m e\n\nmodule load comp-intel/2015.0.090\nmodule load mpi-sgi/mpt.2.11r13\n\n";

#	Create command files for "wv_correct", there will be "MAX_JOBS" command files, with "files_per_job" wv_correct commands per job (last command file may have less)

	jobs           = {};
	files_per_job  = int(math.ceil(len(ntfs) / float(MAX_JOBS)));
	num_jobs       = int(math.ceil(len(ntfs) / float(files_per_job)));
	count          = 0;
	cor_left_tifs  = [];
	cor_right_tifs = [];
	correct_jids   = "";

	for i in range(0, num_jobs):

		job_name = "correct_" + str(i);
		job_ext  = ".cmd";
		job_path = pair_path + "/" + job_name + job_ext;

		jobs[job_path] = pbs_header_str;

		for j in range(0, files_per_job):

			if count < len(ntfs):

				jobs[job_path] += "wv_correct " + pair_path + "/" + ntfs[count] + " " + pair_path + "/" + ntfs[count].replace("ntf", "xml") + " " + pair_path + "/" + ntfs[count].replace(".ntf", "_corrected.tif")  + "\n\n";
				elements        = ntfs[count].split("-");
				cat_id          = elements[len(elements) - 1].replace(".ntf", "");
				
				if cat_id in left_ntfs:
					cor_left_tifs.append(pair_path + "/" + ntfs[count].replace(".ntf", "_corrected.tif"));

				else:
					cor_right_tifs.append(pair_path + "/" + ntfs[count].replace(".ntf", "_corrected.tif"));

				count += 1;

		if step < 2:
			outfile  = open(job_path, "w");
			outfile.write(jobs[job_path]);
			outfile.close();

#		This is where the wv_correct command files are actually submitted, the job ID is read so that the mosaic commands wait for wv_correct jobs to finish

		cmd  = "\nqsub -q normal -N " + job_name + " " + job_path + "\n";

		if step < 2:
			pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout; 
			jid  = pipe.read().strip();
			pipe.close();
			correct_jids += jid + ":";
			main_cmd_file.write("\nqsub -q normal -N " + job_name + " " + job_path + " &\n\n");

	if correct_jids:
		correct_jids = correct_jids[ : len(correct_jids) - 1];


#	Run each of the two mosaic jobs (one for left-hand images, one for right-hand) on one node using 2 processors, wait for wv_correct jobs to finish before running

	pbs_header_str = "#PBS -S /bin/csh\n#PBS -N cfd\n#PBS -l select=1:ncpus=2:mpiprocs=2:model=has\n#PBS -l walltime=1:00:00\n#PBS -j oe\n#PBS -W group_list=s1334\n#PBS -m e\n\nmodule load comp-intel/2015.0.090\nmodule load mpi-sgi/mpt.2.11r13\n\n";

	mosaic_left_tif = cor_left_tifs[0].replace(".tif", "_mosaic.r100.tif");
	mosaic_left_cmd = pbs_header_str + "\ndg_mosaic --output-prefix " + mosaic_left_tif.replace(".r100.tif", "") + " --input-nodata-value -32768 --output-nodata-value -32768 --preview ";

	for tif in cor_left_tifs:
		mosaic_left_cmd += tif + " ";

	mosaic_left_cmd += "\n\n";

	if step < 3:	
		outfile = open(pair_path + "/mosaic_left.cmd", "w");
		outfile.write(mosaic_left_cmd);
		outfile.close();

	mosaic_right_tif = cor_right_tifs[0].replace(".tif", "_mosaic.r100.tif");
	mosaic_right_cmd = pbs_header_str + "\ndg_mosaic --output-prefix " + mosaic_right_tif.replace(".r100.tif", "") + " --input-nodata-value -32768 --output-nodata-value -32768 --preview ";

	for tif in cor_right_tifs:
		mosaic_right_cmd += tif + " ";

	mosaic_right_cmd += "\n\n";

	if step < 3:
		outfile = open(pair_path + "/mosaic_right.cmd", "w");
		outfile.write(mosaic_right_cmd);
		outfile.close();

	mosaic_jids = "";

	if step < 3:

		cmd = "\nqsub -q normal -N mosaic_l " + pair_path + "/mosaic_left.cmd\n";

		if correct_jids:
			cmd  = "\nqsub -q normal -W depend=afterok:" + correct_jids + " -N mosaic_l " + pair_path + "/mosaic_left.cmd\n";

		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		mosaic_jids = pipe.read().strip() + ":";
		pipe.close();
	
		main_cmd_file.write("\nqsub -q normal -W depend=afterok:" + correct_jids + " -N mosaic_l " + pair_path + "/mosaic_left.cmd\n\n");

		cmd  = "\nqsub -q normal -N mosaic_r " + pair_path + "/mosaic_right.cmd\n";

		if correct_jids:
			cmd  = "\nqsub -q normal -W depend=afterok:" + correct_jids + " -N mosaic_r " + pair_path + "/mosaic_right.cmd\n";

		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		mosaic_jids += pipe.read().strip();
		pipe.close();

		main_cmd_file.write("\nqsub -q normal -W depend=afterok:" + correct_jids + " -N mosaic_r " + pair_path + "/mosaic_right.cmd\n\n");


#	Run each "mapproject" command on one node using 24 processors, wait for mosaic jobs to finish before running

	prj_left_tif   = mosaic_left_tif.replace(".r100.tif", "_rpcmapped_1m.tif");
	prj_right_tif  = mosaic_right_tif.replace(".r100.tif", "_rpcmapped_1m.tif");
	prj_jids       = "";

	pbs_header_str = "#PBS -S /bin/csh\n#PBS -N cfd\n#PBS -l select=1:ncpus=1:mpiprocs=1:model=has\n#PBS -l walltime=2:30:00\n#PBS -j oe\n#PBS -W group_list=s1334\n#PBS -m e\n\nmodule load comp-intel/2015.0.090\nmodule load mpi-sgi/mpt.2.11r13\n\n";

	project_left_cmd = pbs_header_str + "\nmapproject --t_srs '+proj=utm +zone=" + utm_zone + " +north +datum=WGS84 +ellipsoid=WGS84 +units=meters' -t rpc --tr=1 --threads=1 " + ref_dem_path + " " + mosaic_left_tif + " " + mosaic_left_tif.replace("tif","xml") + " " + prj_left_tif + "\n\n"; 

	if step < 4:

		outfile = open(pair_path + "/prj_left.cmd", "w");
		outfile.write(project_left_cmd);
		outfile.close();

		cmd  = "\nqsub -q normal -N prj_left " + pair_path + "/prj_left.cmd\n";

		if mosaic_jids:
			cmd  = "\nqsub -q normal -W depend=afterok:" + mosaic_jids + " -N prj_left " + pair_path + "/prj_left.cmd\n";

		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		prj_jids = pipe.read().strip() + ":";
		pipe.close();

		main_cmd_file.write("\nqsub -q normal -W depend=afterok:" + mosaic_jids + " -N prj_left " + pair_path + "/prj_left.cmd\n\n");

	project_right_cmd = pbs_header_str + "\nmapproject --t_srs '+proj=utm +zone=" + utm_zone + " +north +datum=WGS84 +ellipsoid=WGS84 +units=meters' -t rpc --tr=1 --threads=1 " + ref_dem_path + " " + mosaic_right_tif + " " + mosaic_right_tif.replace("tif","xml") + " " + prj_right_tif + "\n\n"; 

	if step < 4:

		outfile = open(pair_path + "/prj_right.cmd", "w");
		outfile.write(project_right_cmd);
		outfile.close();

		cmd  = "\nqsub -q normal -N prj_right " + pair_path + "/prj_right.cmd\n";

		if mosaic_jids:
			cmd  = "\nqsub -q normal -W depend=afterok:" + mosaic_jids + " -N prj_right " + pair_path + "/prj_right.cmd\n";

		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		prj_jids += pipe.read().strip();
		pipe.close();

		main_cmd_file.write("\nqsub -q normal -W depend=afterok:" + mosaic_jids + " -N prj_right " + pair_path + "/prj_right.cmd\n\n");


#	Set output directory name and label for stereo command output (same as output directory name) to date_sat_leftcatid_rightcatid_PAIR, e.g. "14MAR23_WV02_103001002E465700_103001002F1DFF00_PAIR"

	output_label = date + "_" + sat + "_" + str(left_ntfs.keys()[0]) + "_" + str(right_ntfs.keys()[0]) + "_PAIR";
	output_dir   = pair_path + "/" + output_label; 


#	Run step 0 of stereo (pre-processing) on one node using 2 processors, waits until mapproject commands are finished

	pbs_header_str = "#PBS -S /bin/csh\n#PBS -N cfd\n#PBS -l select=1:ncpus=2:mpiprocs=2:model=has\n#PBS -l walltime=2:00:00\n#PBS -j oe\n#PBS -W group_list=s1334\n#PBS -m e\n\nmodule load comp-intel/2015.0.090\nmodule load mpi-sgi/mpt.2.11r13\n\n";

	stereo_0_cmd = pbs_header_str + "\nparallel_stereo --processes 2 --threads-multiprocess 2 --threads-singleprocess 2 --entry-point 0 --stop-point 1 --nodes-list $PBS_NODEFILE " + prj_left_tif + " " + prj_right_tif + " " + mosaic_left_tif.replace("tif", "xml") + " " + mosaic_right_tif.replace("tif", "xml") + " " + output_dir + "/" + output_label + " " + ref_dem_path + "\n\n"; 
	stereo_0_jid = "";

	if step < 5:

		outfile = open(pair_path + "/stereo_0.cmd", "w");
		outfile.write(stereo_0_cmd);
		outfile.close();

		cmd  = "\nqsub -q normal -N stereo_0 " + pair_path + "/stereo_0.cmd\n";

		if prj_jids:
			cmd  = "\nqsub -q normal -W depend=afterok:" + prj_jids + " -N stereo_0 " + pair_path + "/stereo_0.cmd\n";

		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		stereo_0_jid = pipe.read().strip();
		pipe.close();

		main_cmd_file.write("\nqsub -q normal -W depend=afterok:" + prj_jids + " -N stereo_0 " + pair_path + "/stereo_0.cmd\n\n");


#	Run step 1 of stereo (correlation) on 12 nodes using 24 processors each, waits until step 0 is finished

	pbs_header_str = "#PBS -S /bin/csh\n#PBS -N cfd\n#PBS -l select=12:ncpus=24:mpiprocs=24:model=has\n#PBS -l walltime=2:00:00\n#PBS -j oe\n#PBS -W group_list=s1334\n#PBS -m e\n\nmodule load comp-intel/2015.0.090\nmodule load mpi-sgi/mpt.2.11r13\n\n";

	stereo_1_cmd = pbs_header_str + "\nparallel_stereo --processes 24 --threads-multiprocess 24 --threads-singleprocess 24 --entry-point 1 --stop-point 2 --nodes-list $PBS_NODEFILE " + prj_left_tif + " " + prj_right_tif + " " + mosaic_left_tif.replace("tif", "xml") + " " + mosaic_right_tif.replace("tif", "xml") + " " + output_dir + "/" + output_label + " " + ref_dem_path + "\n\n"; 
	stereo_1_jid = "";

	if step < 6:

		outfile = open(pair_path + "/stereo_1.cmd", "w");
		outfile.write(stereo_1_cmd);
		outfile.close();

		cmd  = "\nqsub -q normal -N stereo_1 " + pair_path + "/stereo_1.cmd\n";

		if stereo_0_jid:
			cmd  = "\nqsub -q normal -W depend=afterok:" + stereo_0_jid + " -N stereo_1 " + pair_path + "/stereo_1.cmd\n";

		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		stereo_1_jid = pipe.read().strip();
		pipe.close();

		main_cmd_file.write("\nqsub -q normal -W depend=afterok:" + stereo_0_jid + " -N stereo_1 " + pair_path + "/stereo_1.cmd\n\n");


#	Run step 2 of stereo (refinement) on 12 nodes using 24 processors each, wait until step 1 finishes

	pbs_header_str = "#PBS -S /bin/csh\n#PBS -N cfd\n#PBS -l select=12:ncpus=24:mpiprocs=24:model=has\n#PBS -l walltime=4:00:00\n#PBS -j oe\n#PBS -W group_list=s1334\n#PBS -m e\n\nmodule load comp-intel/2015.0.090\nmodule load mpi-sgi/mpt.2.11r13\n\n";

	stereo_2_cmd = pbs_header_str + "\nparallel_stereo --processes 24 --threads-multiprocess 24 --threads-singleprocess 24 --entry-point 2 --stop-point 3 --nodes-list $PBS_NODEFILE " + prj_left_tif + " " + prj_right_tif + " " + mosaic_left_tif.replace("tif", "xml") + " " + mosaic_right_tif.replace("tif", "xml") + " " + output_dir + "/" + output_label + " " + ref_dem_path + "\n\n"; 
	stereo_2_jid = "";

	if step < 7:

		outfile = open(pair_path + "/stereo_2.cmd", "w");
		outfile.write(stereo_2_cmd);
		outfile.close();

		cmd  = "\nqsub -q normal -N stereo_2 " + pair_path + "/stereo_2.cmd\n";

		if stereo_1_jid:
			cmd  = "\nqsub -q normal -W depend=afterok:" + stereo_1_jid + " -N stereo_2 " + pair_path + "/stereo_2.cmd\n";

		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		stereo_2_jid = pipe.read().strip();
		pipe.close();

		main_cmd_file.write("\nqsub -q normal -W depend=afterok:" + stereo_1_jid + " -N stereo_2 " + pair_path + "/stereo_2.cmd\n\n");


#	Run step 3 of stereo (filtering, hole-filling) on one node using 24 processors, wait until step 2 finishes

	pbs_header_str = "#PBS -S /bin/csh\n#PBS -N cfd\n#PBS -l select=1:ncpus=24:mpiprocs=24:model=has\n#PBS -l walltime=3:00:00\n#PBS -j oe\n#PBS -W group_list=s1334\n#PBS -m e\n\nmodule load comp-intel/2015.0.090\nmodule load mpi-sgi/mpt.2.11r13\n\n";

	stereo_3_cmd = pbs_header_str + "\nparallel_stereo --processes 24 --threads-multiprocess 24 --threads-singleprocess 24 --nodes-list $PBS_NODEFILE --entry-point 3 --stop-point 4 " + prj_left_tif + " " + prj_right_tif + " " + mosaic_left_tif.replace("tif", "xml") + " " + mosaic_right_tif.replace("tif", "xml") + " " + output_dir + "/" + output_label + " " + ref_dem_path + "\n\n"; 
	stereo_3_jid = "";

	if step < 8:

		outfile = open(pair_path + "/stereo_3.cmd", "w");
		outfile.write(stereo_3_cmd);
		outfile.close();

		cmd  = "\nqsub -q normal -N stereo_3 " + pair_path + "/stereo_3.cmd\n";

		if stereo_2_jid:
			cmd  = "\nqsub -q normal -W depend=afterok:" + stereo_2_jid + " -N stereo_3 " + pair_path + "/stereo_3.cmd\n";

		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		stereo_3_jid = pipe.read().strip();
		pipe.close();

		main_cmd_file.write("\nqsub -q normal -W depend=afterok:" + stereo_2_jid + " -N stereo_3 " + pair_path + "/stereo_3.cmd\n\n");


#	Run step 4 of stereo (triangulation) on one node using 24 processors, wait until step 3 of stereo finishes

	pbs_header_str = "#PBS -S /bin/csh\n#PBS -N cfd\n#PBS -l select=1:ncpus=24:mpiprocs=24:model=has\n#PBS -l walltime=4:00:00\n#PBS -j oe\n#PBS -W group_list=s1334\n#PBS -m e\n\nmodule load comp-intel/2015.0.090\nmodule load mpi-sgi/mpt.2.11r13\n\n";

	stereo_4_cmd = pbs_header_str + "\nstereo --threads 0 --entry-point 4 " + prj_left_tif + " " + prj_right_tif + " " + mosaic_left_tif.replace("tif", "xml") + " " + mosaic_right_tif.replace("tif", "xml") + " " + output_dir + "/" + output_label + " " + ref_dem_path + "\n\n"; 
	stereo_4_jid = "";

	if step < 9:

		outfile = open(pair_path + "/stereo_4.cmd", "w");
		outfile.write(stereo_4_cmd);
		outfile.close();

		cmd  = "\nqsub -q normal -N stereo_4 " + pair_path + "/stereo_4.cmd\n";

		if stereo_3_jid:
			cmd  = "\nqsub -q normal -W depend=afterok:" + stereo_3_jid + " -N stereo_4 " + pair_path + "/stereo_4.cmd\n";

		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		stereo_4_jid = pipe.read().strip();
		pipe.close();

		main_cmd_file.write("\nqsub -q normal -W depend=afterok:" + stereo_3_jid + " -N stereo_4 " + pair_path + "/stereo_4.cmd\n\n");


#	Create DEM and orthorectified image using "point2dem" command run on 4 nodes using 8 processors each, wait until step 4 of stereo is finished

	pbs_header_str = "#PBS -S /bin/csh\n#PBS -N cfd\n#PBS -l select=4:ncpus=8:mpiprocs=8:model=has\n#PBS -l walltime=3:00:00\n#PBS -j oe\n#PBS -W group_list=s1334\n#PBS -m e\n\nmodule load comp-intel/2015.0.090\nmodule load mpi-sgi/mpt.2.11r13\n\n";

	pc2dem_cmd = pbs_header_str + "\npoint2dem " + output_dir + "/" + output_label + "-PC.tif --threads=8 --t_srs '+proj=utm +zone=" + utm_zone + " +north +datum=WGS84 units=meter' --nodata-value=-9999 --orthoimage " + prj_left_tif + " --dem-spacing=3 --tif-compress=None\n\n";

	if step < 10:

		outfile = open(pair_path + "/pc2dem.cmd", "w");
		outfile.write(pc2dem_cmd);
		outfile.close();

		cmd  = "\nqsub -q normal -N pc2dem " + pair_path + "/pc2dem.cmd\n";

		if stereo_4_jid:
			cmd  = "\nqsub -q normal -W depend=afterok:" + stereo_4_jid + " -N pc2dem " + pair_path + "/pc2dem.cmd\n";

		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		pc2dem_jid = pipe.read().strip();
		pipe.close();
	
		main_cmd_file.write("\nqsub -q normal -W depend=afterok:" + stereo_4_jid + " -N pc2dem " + pair_path + "/pc2dem.cmd\n");


#	Create orthorectified image using "point2dem" command run on 4 nodes using 8 processors each, wait until step 4 of stereo is finished

	pbs_header_str = "#PBS -S /bin/csh\n#PBS -N cfd\n#PBS -l select=8:ncpus=8:mpiprocs=8:model=has\n#PBS -l walltime=7:00:00\n#PBS -j oe\n#PBS -W group_list=s1334\n#PBS -m e\n\nmodule load comp-intel/2015.0.090\nmodule load mpi-sgi/mpt.2.11r13\n\n";

	ortho_cmd = pbs_header_str + "\npoint2dem " + output_dir + "/" + output_label + "-PC.tif --threads 0 --t_srs '+proj=utm +zone=" + utm_zone + " +north +datum=WGS84 units=meter' --no-dem --nodata-value=-9999 --dem-spacing=1 --hole-fill-mode=2 --hole-fill-num-smooth-iter=4 --orthoimage-hole-fill-len=2100 --remove-outliers --orthoimage " + prj_left_tif + " --tif-compress=None\n\n";

	if step < 11:

		outfile = open(pair_path + "/ortho.cmd", "w");
		outfile.write(ortho_cmd);
		outfile.close();

		cmd  = "\nqsub -q normal -N ortho " + pair_path + "/ortho.cmd\n";

		if pc2dem_jid:
			cmd  = "\nqsub -q normal -W depend=afterok:" + pc2dem_jid + " -N ortho " + pair_path + "/ortho.cmd\n";

		pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
		ortho_jid = pipe.read().strip();
		pipe.close();
	
		main_cmd_file.write("\nqsub -q normal -W depend=afterok:" + pc2dem_jid + " -N ortho " + pair_path + "/ortho.cmd\n");

	main_cmd_file.close();

	return;


if __name__ == "__main__":

        import os;
        import sys;

        assert len(sys.argv) > 3, "\n***** ERROR: ntf2dem.py requires at least 3 arguments, " + str(len(sys.argv) - 1) + " given\n";
        assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
        assert os.path.exists(sys.argv[2]), "\n***** ERROR: " + sys.argv[2] + " does not exist\n";

	start_step = "correct";

	if len(sys.argv) > 4:
		start_step = sys.argv[4];

        ntf2dem(sys.argv[1], sys.argv[2], sys.argv[3], start_step);

        exit();

