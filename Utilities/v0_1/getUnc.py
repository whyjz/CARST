#!/usr/bin/python


def getUnc(unc_grd_path, corr_width):

	assert os.path.exists(unc_grd_path), "\n***** ERROR: " + unc_grd_path + " does not exist\n";

	name = unc_grd_path[unc_grd_path.rfind("/") + 1 : unc_grd_path.rfind(".")];

	import subprocess;

	cmd  = "\ngrdvolume " + unc_grd_path + "\n";
	pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout;
	info = pipe.read().split();
	pipe.close();

	unc_area   = float(info[1]);
	unc_volume = float(info[2]);

	mass_unc  = (1.96 * unc_volume / ( (unc_area / (corr_width**2) )**0.5 * 0.9))**2;
	
#	2012-2013/2014
	#mass_unc += (0.02408261003910003 * unc_area)**2;
	#mass_unc += (0.011054433634353034 * unc_area)**2;
	
#	1952-2013/2014
	mass_unc += (0.023959339292700024 * unc_area)**2;
	mass_unc = mass_unc**0.5 / 1e9;
	
	dhdt_unc = 1e9 * mass_unc / unc_area;

#	mass_unc   = str((1.96 * unc_volume / ( (unc_area / (corr_width**2) )**0.5) + fixed_rate * unc_area) * 0.9 / 1e9);
#	dhdt_unc   = str((1.96 * unc_volume / ( (unc_area / (corr_width**2) )**0.5) + fixed_rate * unc_area) * 0.9 / unc_area);

	print("\n" + name + "   Mass Change Rate Uncertainty (Gt/yr): " + str(mass_unc) + "   Average Mass Balance Uncertainty (m w.e./yr): " + str(dhdt_unc));


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 2, "\n***** ERROR: getUnc.py requires at least 2 arguments, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";

	getUnc(sys.argv[1], float(sys.argv[2]));

	exit();

