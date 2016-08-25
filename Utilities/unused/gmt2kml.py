#!/usr/bin/python


# gmt2kml.py
# Author: Andrew Kenneth Melkonian
# All rights reserved


def gmt2kml(gmt_path):

	import os;

	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";

	gmt_name = gmt_path[gmt_path.rfind("/") + 1 : gmt_path.rfind(".")];
	kml_path = gmt_name + "_polygon.kml";
	print(kml_path);

	outfile = open(kml_path, "w");

	outfile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
	outfile.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\" xmlns:gx=\"http://www.google.com/kml/ext/2.2\" xmlns:kml=\"http://www.opengis.net/kml/2.2\" xmlns:atom=\"http://www.w3.org/2005/Atom\">\n");
	outfile.write("<Document>\n");
	outfile.write("	<name>" + gmt_name + "</name>\n");
	outfile.write("	<StyleMap id=\"msn_ylw-pushpin\">\n");
	outfile.write("		<Pair>\n");
	outfile.write("			<key>normal</key>\n");
	outfile.write("			<styleUrl>#sn_ylw-pushpin</styleUrl>\n");
	outfile.write("		</Pair>\n");
	outfile.write("		<Pair>\n");
	outfile.write("			<key>highlight</key>\n");
	outfile.write("			<styleUrl>#sh_ylw-pushpin</styleUrl>\n");
	outfile.write("		</Pair>\n");
	outfile.write("	</StyleMap>\n");
	outfile.write("	<Style id=\"sn_ylw-pushpin\">\n");
	outfile.write("		<IconStyle>\n");
	outfile.write("			<scale>1.1</scale>\n");
	outfile.write("			<Icon>\n");
	outfile.write("				<href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>\n");
	outfile.write("			</Icon>\n");
	outfile.write("			<hotSpot x=\"20\" y=\"2\" xunits=\"pixels\" yunits=\"pixels\"/>\n");
	outfile.write("		</IconStyle>\n");
	outfile.write("	</Style>\n");
	outfile.write("	<Style id=\"sh_ylw-pushpin\">\n");
	outfile.write("		<IconStyle>\n");
	outfile.write("			<scale>1.3</scale>\n");
	outfile.write("			<Icon>\n");
	outfile.write("				<href>http://maps.google.com/mapfiles/kml/pushpin/ylw-pushpin.png</href>\n");
	outfile.write("			</Icon>\n");
	outfile.write("			<hotSpot x=\"20\" y=\"2\" xunits=\"pixels\" yunits=\"pixels\"/>\n");
	outfile.write("		</IconStyle>\n");
	outfile.write("	</Style>\n");
	outfile.write("       <Placemark>\n");
	outfile.write("        <name>CDI</name>\n");
	outfile.write("        <LineString>\n");
	outfile.write("         <tessellate>1</tessellate>\n");
	outfile.write("         <coordinates>");

	infile = open(gmt_path,"r");
	line   = infile.readline();

	while 1:

		line = infile.readline().strip();

		if not line:
			break;

		if line.find(">") > -1:
			outfile.write("          </coordinates>\n");
			outfile.write("         </LineString>\n");
			outfile.write("       </Placemark>\n");
			outfile.write("       <Placemark>\n");
			outfile.write("        <name>CDI</name>\n");
			outfile.write("        <LineString>\n");
			outfile.write("         <tessellate>1</tessellate>\n");
			outfile.write("         <coordinates>\n");
			continue;

		elements = line.split();

		if line.find("#") < 0:
			outfile.write(elements[0] + "," + elements[1] + " ");

	infile.close();

	outfile.write("         </coordinates>\n");
	outfile.write("        </LineString>\n");
	outfile.write("	</Placemark>\n");
	outfile.write("</Document>\n");
	outfile.write("</kml>\n");
	outfile.close();

	return;


if __name__ == "__main__":
	
	import os;
	import sys;
	
	assert len(sys.argv) > 1, "\n***** ERROR: gmt2kml.py requires one argument, " + str(len(sys.argv) - 1) + " given\n";
	assert os.path.exists(sys.argv[1]), "\n***** ERROR: " + sys.argv[1] + " does not exist\n";
	
	gmt2kml(sys.argv[1]);

	exit();

