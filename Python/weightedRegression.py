#!/usr/bin/python


# weightedRegression.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def sort2DList(input_list, column):

	length = len(input_list);
	width  = len(input_list[0]);
	temp   = [];
	output = [];

	for i in range(0, length):
		temp.append((float(input_list[i][column]), input_list[i]));

	temp = sorted(temp);

	for i in range(0, length):
		output.append(temp[i][1]);

	return output;


def weightedRegression(input_elevs_path, output_label, min_year, max_year, upper_threshold, lower_threshold):

	import os;
	import subprocess;

	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";

	first_median_loweststdev = "first";

	upper_label = upper_threshold;

	if upper_label.rfind(".") > 0:
		upper_label = upper_label[ : upper_label.rfind(".")];

	lower_label = lower_threshold;

	if lower_label.rfind(".") > 0:
		lower_label = lower_label[ : lower_label.rfind(".")];

	outfile = open(output_label + "_p" + upper_label + "m" + lower_label + ".txt", "w");
	outfile.write("X     Y     DHDT     DHDT_Sigma     Intercept     Intercept_Sigma     N     Median_Date     Median_Elev     Median_Sigma     First_Date     First_Elev     First_Sigma     Last_Date     Last_Elev     Last_Sigma     Ref_Date     Ref_Elev     Ref_Sigma     Date_Interval\n");

	import datetime;
	import operator;
	import math;
	import scipy;
	import scipy.sparse;
	import scipy.linalg;

	x = "";
	y = "";

	coord = [];

	infile = open(input_elevs_path, "r");


	for line in infile:

		if not line.find(">") > -1:

			elements = line.split();

			x     = elements[0];
			y     = elements[1];
			elev  = elements[2];
			date  = elements[3];
			stdev = elements[4];

			coord.append([date, elev, stdev]);

		else:

#			coord = sorted(coord);
			coord = sort2DList(coord, 0);

			first_date  = coord[0][0];
			first_elev  = coord[0][1];
			first_stdev = coord[0][2];

			#coord = sorted(coord, key=operator.itemgetter(1));
			coord = sort2DList(coord, 1);

			median_date  = coord[len(coord) / 2][0];
			median_elev  = coord[len(coord) / 2][1];
			median_stdev = coord[len(coord) / 2][2];

			coord = sort2DList(coord, 2);

			min_unc_date  = coord[0][0];
			min_unc_elev  = coord[0][1];
			min_unc_stdev = coord[0][2];

			accepted_coord = [];

			for i in range(0, len(coord)):

				cur_date  = coord[i][0];
				cur_elev  = coord[i][1];
				cur_stdev = coord[i][2];

				if float(cur_date) > float(max_year) or float(cur_date) < float(min_year):
					continue;

				ref_date  = first_date;
				ref_elev  = first_elev;
				ref_stdev = first_stdev;

#				ref_date  = min_unc_date;
#				ref_elev  = min_unc_elev;
#				ref_stdev = min_unc_stdev;

#				if float(ref_stdev) == 5 and float(ref_elev) > 1000:
#					ref_elev = str(float(ref_elev) + 2.0);

#				ref_date  = median_date;
#				ref_elev  = median_elev;
#				ref_stdev = median_stdev;

				cur_upper_bound = 0.0;
				cur_lower_bound = 0.0;
				interval	= 0.0;

				if float(ref_date) < float(cur_date):
					interval        = float(cur_date) - float(ref_date);
					cur_upper_bound = float(ref_elev) + interval * float(upper_threshold);
					cur_lower_bound = float(ref_elev) - interval * float(lower_threshold);

				elif float(ref_date) > float(cur_date):
					interval        = float(ref_date) - float(cur_date);
					cur_upper_bound = float(ref_elev) + interval * float(lower_threshold);
					cur_lower_bound = float(ref_elev) - interval * float(upper_threshold);

				else:
					accepted_coord.append(coord[i]);

				if float(cur_elev) > cur_upper_bound or float(cur_elev) < cur_lower_bound:
					continue; 

				accepted_coord.append(coord[i]);

			coord = [];
     
			accepted_coord = sorted(accepted_coord);

			length = len(accepted_coord);

			if len(accepted_coord) < 2 or abs(float(accepted_coord[0][0]) - float(accepted_coord[length - 1][0])) < 1:
				continue;

			xs  = scipy.sparse.lil_matrix((length, 2));
			ys  = scipy.sparse.lil_matrix((length, 1));
			ws  = scipy.sparse.lil_matrix((length, length));
			c_d = scipy.sparse.lil_matrix((length, length));

			ws.setdiag(scipy.ones(length));

			for i in range(0, length):
				xs[i,1]   = float(accepted_coord[i][0]) - float(accepted_coord[0][0]);
				ys[i,0]   = float(accepted_coord[i][1]);
				ws[i,i]   = 1.0 / math.pow(float(accepted_coord[i][2]), 1);
				c_d[i,i] = math.pow(float(accepted_coord[i][2]), 2);

			xs[0,0] = 0.0;
			xs[:,0] = 1;

			dense_xs  = xs.todense();
			dense_ys  = ys.todense();
			dense_ws   = ws.todense();
			dense_c_d = c_d.todense();

			b 	   = scipy.linalg.inv(dense_xs.transpose() * dense_ws * dense_xs) * dense_xs.transpose() * dense_ws * dense_ys;
     			intercept  = float(b[0][0]);
     			dhdt       = float(b[1][0]);
     			c_m        = scipy.linalg.inv(dense_xs.transpose() * scipy.linalg.inv(dense_c_d) * dense_xs);
     			dhdt_stdev = math.sqrt(c_m[1][1]);


     			outfile.write(x + " " + y + " " + str(dhdt) + " " + str(dhdt_stdev) + " " + str(intercept) + " " + str(math.sqrt(c_m[0][0])) + " " + str(length) + " " + accepted_coord[0][0] + " " + accepted_coord[0][1] + " " + accepted_coord[0][2] + " " + accepted_coord[length/2][0] + " " + accepted_coord[length/2][1] + " " + accepted_coord[length/2][2] + " " + accepted_coord[length - 1][0] + " " + accepted_coord[length - 1][1] + " " + accepted_coord[length - 1][2] + " " + ref_date + " " + ref_elev + " " + ref_stdev + " " + str(float(accepted_coord[length - 1][0]) - float(accepted_coord[0][0])) + "\n");

	infile.close();
	outfile.close();

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 6, "\n***** ERROR: weightedRegression.py requires 6 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	weightedRegression(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]);

	exit();

