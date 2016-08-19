#!/bin/python

import os, sys, string, shutil, glob, subprocess, argparse, random
import xml.etree.ElementTree as ET
from datetime import *
import gdal, osr, ogr, gdalconst


print "\n", " ".join(sys.argv), "\n"
 
def main():
    
    #### Set Up Arguments 
    parser = argparse.ArgumentParser(description="Submit ASP job with mosaicking")
    
    #### Positional Arguments
    parser.add_argument('srcdir', help="source stereopair directory")
    parser.add_argument('dstdir', help="destination directory")
    parser.add_argument('epsg', type=int, help="target spatial reference EPSG code")
    parser.add_argument("stereo_params", help="stereo.default file path")
    pos_arg_keys = ('srcdir','dstdir','epsg','stereo_params')
    
    #### Optional Arguments
    parser.add_argument('--qsubscript',
			help="qsub script for cluster submission")
    parser.add_argument('-d', '--dem',
			help="dem to use as seed for mapproject step")
    parser.add_argument('--images', nargs=2,
			help="pair of images in srcdir to run through ASP (no directory structure).  This option precludes job submission.  To submit to a cluster, run the script without this option invoked.")
    parser.add_argument("--wd",
                      help="local working directory for scratch space, must already exist (use when mounted stoage has a slower connection to compute nodes)")
    parser.add_argument("--dem_res", type=float,
		      help="resolution of output DEM in output coordinate system units (default is 4 x mp_res)")
    parser.add_argument("--mp_res", default=1.0, type=float,
		      help="resolution of mapprojection step in output coordinate system units (default=1)")
    parser.add_argument("-e", '--entry_point', choices=["0","1","2","3","4"],
		      help="stereo entry point (0-stereo_pprc,1-stereo_corr,2-stereo_rfne,3-stereo_fltr,4-stereo_tri)")
    parser.add_argument("-t", "--threads", type=int,
		      help="number of threads to use for mapproject and stereo")
    parser.add_argument("-l", "--qsub_resource_request",
                      help="PBS resources requested (mimicks qsub syntax)")
    parser.add_argument("--parallel", choices=['yes','no'], default='no',
			help="run parallel_stereo instead of stereo to use more than 1 node (requires gnu parallel)")
    parser.add_argument("--dryrun", choices=['yes','no'], default='no',
		      help="dry run that runs intersects but does not submit the jobs to qsub")
    parser.add_argument("--save_temps", choices=['yes','no'], default='no',
		      help="save temporary files if --wd is used")

    #### Parse Arguments
    args = parser.parse_args()
    pythonscript = os.path.abspath(sys.argv[0])
    
    #### Verify positional arguments
    srcdir = os.path.abspath(args.srcdir)
    if not os.path.isdir(srcdir):
	parser.error("Srcdir is not a valid directory: %s" %srcdir)
    
    stereo_params = os.path.abspath(args.stereo_params)
    if not os.path.isfile(stereo_params):
	parser.error("Stereo parameter file does not exist: %s" %stereo_params)
	
    dstdir = os.path.abspath(args.dstdir)
    if not os.path.isdir(dstdir):
	os.makedirs(dstdir)
	
    srs = osr.SpatialReference()
    rc = srs.ImportFromEPSG(args.epsg)
    if rc <> 0:
	parser.error("EPSG code cannot be imported by gdal: %i" %args.epsg)
    proj4 = srs.ExportToProj4()
	
    if args.dem is not None:
	if not os.path.isfile(args.dem):
	    parser.error("DEM path is not valid: %s" %args.dem)
	dem = os.path.abspath(args.dem)
    else:
	dem = ''
	
    #### Get -l option and make a var
    qsub_resource_request = ("-l %s" %args.qsub_resource_request) if args.qsub_resource_request is not None else ""
    	
    job_file = os.path.join(dstdir,"job_list.txt")
    
    
    ####################################
    ####  Job Submission Logic
    ###################################
    if args.images is None:
	
	#### Verify qsubscript
	if not args.qsubscript:
	    parser.error("--qsubscript is required for cluster job submission")
	    
	if not os.path.isfile(args.qsubscript):
	    parser.error("Qsub script does not exist: %s" %args.qsubscript)
	
	#### enumerate args (rm args.qsubscript, rm args.qsub_resource_request)
	args_dict = vars(args)
	args_dict['srcdir'] = srcdir
	args_dict['dstdir'] = dstdir
	args_dict['stereo_params'] = stereo_params
	if args.dem is not None:
	    args_dict['dem'] = dem
	
	arg_list = []
	arg_keys_to_remove = ('qsubscript','qsub_resource_request')
	
	for k,v in args_dict.iteritems():
	    if k not in pos_arg_keys and k not in arg_keys_to_remove and v is not None:
		arg_list.append("--%s=%s" %(k,str(v)))
	
	for k in pos_arg_keys:
	    if k not in arg_keys_to_remove:
		arg_list.append(str(args_dict[k]))
		
	arg_str = " ".join(arg_list)
	
	####  Search folder for DG pan images
	imglist = glob.glob(os.path.join(srcdir,"*P1BS*"))
	
	####  For each image, find extent and CATID
	imgdict = {}
	catidlist = []
	intersects = []
	
	print "\nIMAGES"
	for img in imglist:
	    if os.path.splitext(img)[1].upper() in [".NTF",".TIF"]:
		print img
		geom = getGeom(img,args.epsg)
		
		
		#WV02_12OCT272110126-M1BS-103001001CC73700.ntf
		catid = img[-20:-4]
		catidlist.append(catid)
		
		imgdict[img] = (catid,geom)
		print os.path.basename(img), catid, geom
	
	####  Compare extent and CATID, record pair
	print "\nOVERLAPPING PAIRS"
	shpdict = {}
	
	catids = list(set(catidlist))
	catids.sort()
	for img1 in imgdict.keys():
	    catid1, geom1 = imgdict[img1]
	    if catid1 == catids[0]:
		for img2 in imgdict.keys():
		    catid2, geom2 = imgdict[img2]
		    if catid1 != catid2:
			#### compare geoms
			if geom1.Intersects(geom2):
			    print os.path.basename(img1), os.path.basename(img2)
			    
			    igeom = geom1.Intersection(geom2)
			    #print igeom
			    iarea = igeom.GetArea()
			    
			    ugeom = geom1.Union(geom2)
			    uarea = ugeom.GetArea()
			    
			    perc_overlap = iarea/uarea
			    print "\tPercent overlap: %f" %perc_overlap
			    
			    if perc_overlap < 0.15:
				print "\tERROR: Percent overlap too small"
				
			    else:
				intersects.append((img1,img2))
				odpair = "%s_%s" %(os.path.basename(os.path.splitext(img1)[0]),os.path.basename(os.path.splitext(img2)[0]))
				shpdict[odpair]=(igeom,perc_overlap)
	
	####  For each pair, submit qsub job
	print "\nQSUB"
	i = 0
	
	job_list = []
	
	f = open(job_file,'w')
	f.write("JOB,STATUS")
	
	for img1,img2 in intersects:
	    odpair = os.path.join(dstdir,"%s_%s" %(os.path.basename(os.path.splitext(img1)[0]),os.path.basename(os.path.splitext(img2)[0])))
	    status = 0 if os.path.isfile("%s-DEM.tif" %odpair) else 1
	    f.write("\n%s,%i" %(odpair,status))    
	    
	    cmd = r'qsub %s -N Stereo%04i -v p1="%s",p2="--images %s %s %s" "%s"' %(qsub_resource_request, i, pythonscript, img1, img2, arg_str, args.qsubscript)
	    print cmd
	    i += 1
	    if args.dryrun == 'no' and status == 1:
		subprocess.call(cmd,shell=True)
	
	f.close()
	    
	    
	#### Write shpfile of intersections
	shpname = os.path.join(dstdir,os.path.basename(dstdir))
	writeShp(shpname,shpdict,args.epsg)
    
    
    
    ####################################
    ####  Job Execution Logic
    ###################################
    else:

	if args.wd is not None:
	    wd = os.path.abspath(args.wd)
	else:
	    wd = dstdir
	    
	#### Define file names
	img1s = os.path.join(srcdir,os.path.basename(args.images[0]))
	img2s = os.path.join(srcdir,os.path.basename(args.images[1]))
	dstfn_prefix = "%s_%s" %(os.path.basename(os.path.splitext(img1s)[0]),os.path.basename(os.path.splitext(img2s)[0]))
	dstfp = os.path.join(dstdir,"%s-DEM.tif" %dstfn_prefix)
	xml1s = os.path.splitext(img1s)[0]+".xml"
	xml2s = os.path.splitext(img2s)[0]+".xml"
	
	
    
	#### Handle options
	if args.dem_res:
	    dem_res = args.dem_res
	else:
	    dem_res = int(4 * args.mp_res)
    
	if args.entry_point:
	    entry_point = "-e %s" %args.entry_point
	else:
	    entry_point = ""
    
	if args.threads:
	    if args.parallel == 'no':
	        threads = "--threads=%s" %args.threads
	    else:
	        threads = "--threads-singleprocess=%s --threads-multiprocess=%s" %(args.threads,args.threads)
	else:
	    threads = ""
    
	#### Get start time
	stm = datetime.now()
    
	#### Check if target file already exists
	if os.path.isfile(dstfp):
	    print "output DEM already exists"
    
	else:
	    #### make working dir and target dir
	    if not os.path.isdir(dstdir):
		try:
		    os.makedirs(dstdir)
		except OSError:
		    pass
    
	    if not dstdir == wd:
		if not os.path.isdir(wd):
		    try:
			os.makedirs(wd)
		    except OSError:
			pass
    
	    #### change cwd
	    print "Working Dir: %s" %wd
	    os.chdir(wd)
    
    
	    #### If working dir used, copy nitfs to wd
	    if wd != dstdir:
		for f in (img1s,xml1s):
		    if not os.path.isfile(os.path.basename(f)):
			shutil.copy2(f,"%s_L%s" %(dstfn_prefix,os.path.splitext(f)[1]))
				     
		for f in (img2s,xml2s):
		    if not os.path.isfile(os.path.basename(f)):
			shutil.copy2(f,"%s_R%s" %(dstfn_prefix,os.path.splitext(f)[1]))
				     
		img1 = "%s_L%s" %(dstfn_prefix,os.path.splitext(img1s)[1])
		img2 = "%s_R%s" %(dstfn_prefix,os.path.splitext(img2s)[1])
		xml1 = "%s_L.xml" %dstfn_prefix
		xml2 = "%s_R.xml" %dstfn_prefix
    
	    else:
		img1 = img1s
		img2 = img2s
		xml1 = xml1s
		xml2 = xml2s
    
	    #### Determine Overlap Area
	    # get NITF geoms
	    geom1 = getGeom(img1,args.epsg)
	    geom2 = getGeom(img2,args.epsg)
	    igeom = geom1.Intersection(geom2)
	    bbox = igeom.GetEnvelope()
	    print "Bounding Box:", bbox
    
	    
	    #### If no dem supplied, set session to dg
	    if not args.dem:
		map1 = img1
		map2 = img2
		
	    #### If dem supplied, set session to rpc and mapproject
	    else:
		map1 = "%s_L_map.tif" %dstfn_prefix
		map2 = "%s_R_map.tif" %dstfn_prefix
	    
	    
		#### Mapproject
		tm = datetime.now()
		print "%s - Mapprojecting images" %tm.strftime("%d-%b-%Y %H:%M:%S")
		if not os.path.isfile(map1):
		    
		    
		    cmd = 'mapproject -t rpc --t_projwin %f %f %f %f --t_srs \'%s\' %s --tr %f "%s" "%s" "%s" "%s"' %(bbox[0],bbox[2],bbox[1],bbox[3],proj4,threads,args.mp_res,dem,img1,xml1,map1)
		    print cmd
		    rc = subprocess.call(cmd,shell=True)
		    print ("Return code: %i" %rc)
		else:
		    print "Left mapped image already exists: %s" %map1
	
		if not os.path.isfile(map2):
		    cmd = 'mapproject -t rpc --t_projwin %f %f %f %f --t_srs \'%s\' %s --tr %f "%s" "%s" "%s" "%s"' %(bbox[0],bbox[2],bbox[1],bbox[3],proj4,threads,args.mp_res,dem,img2,xml2,map2)
		    print cmd
		    rc = subprocess.call(cmd,shell=True)
		    print ("Return code: %i" %rc)
		else:
		    print "Right mapped image already exists: %s" %map2
    
	    #### Make short named copies of mapped images
	    randint = random.randint(1,999999)
	    map1_short = "%06i_L_map%s" %(randint,os.path.splitext(map1)[1])
	    map2_short = "%06i_R_map%s" %(randint,os.path.splitext(map2)[1])
	
	    for f, f_short in ((map1,map1_short),(map2,map2_short)):
		shutil.copy2(f,f_short)
    
	    #### Call stereo
	    tm = datetime.now()
	    print "%s - Running ASP stereo" %tm.strftime("%d-%b-%Y %H:%M:%S")
	    if not os.path.isfile(dstfn_prefix+"-PC.tif"):
		if args.parallel == 'yes':
		    nodefile = os.path.expandvars("$PBS_NODEFILE")
		    print nodefile
		    cmd = 'parallel_stereo -t dg --nodes-list %s --processes 1 %s -s %s %s %s %s %s %s %s' %(nodefile,entry_point,stereo_params,threads,map1_short,map2_short,xml1,xml2,dstfn_prefix,dem)
		else:
		    cmd = 'stereo -t dg %s -s %s %s %s %s %s %s %s %s' %(entry_point,stereo_params,threads,map1_short,map2_short,xml1,xml2,dstfn_prefix,dem)
		    
		print cmd
		rc = subprocess.call(cmd,shell=True)
		print ("Return code: %i" %rc)
    
	    #### Convert output to DEM
	    tm = datetime.now()
	    print "%s - Converting stereo output to %im DEM" %(tm.strftime("%d-%b-%Y %H:%M:%S"),dem_res)
	    if os.path.isfile(dstfn_prefix+"-PC.tif") and not os.path.isfile("%s-DEM.tif" %(dstfn_prefix)):
		cmd = 'point2dem %s-PC.tif --nodata-value "-9999" --orthoimage %s --errorimage -o %s %s --t_srs \'%s\' -s %i' %(dstfn_prefix,map1,dstfn_prefix,threads,proj4,dem_res)
		print cmd
		rc = subprocess.call(cmd,shell=True)
		print ("Return code: %i" %rc)
    
		#### build pyramids
		tm = datetime.now()
		print "%s - Adding pyramids" %tm.strftime("%d-%b-%Y %H:%M:%S")
		if os.path.isfile("%s-DEM.tif" %dstfn_prefix):
		    cmd = 'gdaladdo "%s-DEM.tif" 2 4 8 16' %(dstfn_prefix)
		    print cmd
		    rc = subprocess.call(cmd,shell=True)
		    print ("Return code: %i" %rc)
    
	    #### Write .prj File
	    if os.path.isfile("%s-DEM.tif" %(dstfn_prefix)):
		prj = srs.ExportToWkt()
		txtpath = "%s-DEM.prj" %(dstfn_prefix)
		txt = open(txtpath,'w')
		txt.write(prj)
		txt.close()
		
	    
	    #### Derive result Filenames
	    result_files = (dstfn_prefix+"-DEM.tif", dstfn_prefix+"-DRG.tif", dstfn_prefix+"-GoodPixelMap.tif", dstfn_prefix+"-IntersectionErr.tif", dstfn_prefix+"-PC.tif", dstfn_prefix+"-stereo.default")
	    print "Result fileames:"
	    print result_files
	    
	    #### if local working dir was used, copy output to target dir
	    if wd != dstdir:
		
		####  If working dir was not target dir and save_temps is True, copy all files to target dir
		if args.save_temps == 'yes':
		    for f in glob.glob(dstfn_prefix+"*"):
			ofp = os.path.join(dstdir,os.path.basename(f))
			shutil.copy2(f,ofp)
		####  If working dir was not target dir and save_temps is False, copy only result files to target dir
		else:
		    for f in result_files:
			ofp = os.path.join(dstdir,os.path.basename(f))
			shutil.copy2(f,ofp)
		
		    #### Rmove all related files from working dir
		    for f in glob.glob(dstfn_prefix+"*"):
			try:
			    os.remove(f)
			except Exception, e:
			    print "Cannot remove file %s: %s" %(wd,e)
	    
	    #### If working dir is same as target dir and save_temps if Flase, remove all files except result files	    
	    elif not args.save_temps == 'yes' :
		for f in glob.glob(dstfn_prefix+"*"):
		    if not f in result_files:
			try:
			    os.remove(f)
			except Exception, e:
			    print "Cannot remove file %s: %s" %(wd,e)
	    
	    #### No matter what options were used, remove short-named mapped image copy	    
	    for f in map1_short,map2_short:
		try:
		    os.remove(f)
		except Exception, e:
		    print "Cannot remove file %s: %s" %(wd,e)
    
    
	    #### Get total time
	    etm = datetime.now()
	    dtm = etm - stm
	    print "Total time = %s" %dtm
    
	    #### Alter job status file
	    if os.path.isfile(job_file) and os.path.isfile(dstfp):
		f = open(job_file[:-4]+"_temp.txt", 'w')
		lines = open(job_file,'r').readlines()
		f.write("JOB,STATUS")
		for line in lines[1:]:
		    lp = line.strip('\n').split(",")
		    if lp[0] == dstfn_prefix:
			f.write("\n%s,0" %tfp)
		    else:
			f.write("\n%s,%s" %(lp[0],lp[1]))
		f.close()
    
		os.rename(job_file[:-4]+"_temp.txt", job_file)


def writeShp(shp,d,epsg):


    OGR_DRIVER = "ESRI Shapefile"    
    ogrDriver = ogr.GetDriverByName(OGR_DRIVER)

    if os.path.isfile(shp+'.shp'):
        ogrDriver.DeleteDataSource(shp+'.shp')

    shapefile = ogrDriver.CreateDataSource(shp + '.shp')

    if shapefile is not None:
        givenProjection = osr.SpatialReference()
        givenProjection.ImportFromEPSG(epsg)
    
        desiredProjection = osr.SpatialReference()
        desiredProjection.ImportFromEPSG(4326)
    
        coordinateTransformer = osr.CoordinateTransformation(givenProjection, desiredProjection)  
    
        shpn = os.path.basename(shp)
        layer = shapefile.CreateLayer(shpn, desiredProjection, ogr.wkbPolygon)
    
        field = ogr.FieldDefn("Filename", ogr.OFTString)
        field.SetWidth(250)
        layer.CreateField(field)
    
        field = ogr.FieldDefn("Overlap", ogr.OFTReal )
        layer.CreateField(field)
    
        filenames = d.keys()
        for name in filenames:
            geometry, overlap = d[name]
        
            feature = ogr.Feature(layer.GetLayerDefn())
            feature.SetField("Filename", name)
            feature.SetField("Overlap", overlap)
        
            geometry.Transform(coordinateTransformer)
            feature.SetGeometry(geometry)
        
            layer.CreateFeature(feature)
    else:
        print "Cannot create shapefile: %s" %shpname


def getGeom(img,epsg):
    
    geom = None
    
    ds = gdal.Open(img,gdalconst.GA_ReadOnly)
    if ds is not None:   
                
        ####  Get extent from GCPs
        num_gcps = ds.GetGCPCount()
        bands = ds.RasterCount
        
        if num_gcps == 4:
            gcps = ds.GetGCPs()
            proj = ds.GetGCPProjection()
            
            gcp_dict = {}
        
            id_dict = {"UpperLeft":1,
                       "1":1,
                       "UpperRight":2,
                       "2":2,
                       "LowerLeft":4,
                       "4":4,
                       "LowerRight":3,
                       "3":3}
            
            for gcp in gcps:
                gcp_dict[id_dict[gcp.Id]] = [float(gcp.GCPPixel), float(gcp.GCPLine), float(gcp.GCPX), float(gcp.GCPY), float(gcp.GCPZ)]
                
            poly_wkt = 'POLYGON (( %f %f, %f %f, %f %f, %f %f, %f %f ))' %(gcp_dict[1][2],gcp_dict[1][3],gcp_dict[2][2],gcp_dict[2][3],gcp_dict[3][2],gcp_dict[3][3],gcp_dict[4][2],gcp_dict[4][3],gcp_dict[1][2],gcp_dict[1][3])
            
            
        else:
            xsize = ds.RasterXSize
            ysize = ds.RasterYSize
            proj = ds.GetProjectionRef()
            gtf = ds.GetGeoTransform()
        
            minx = gtf[0]
            maxx = minx + xsize * gtf[1]
            maxy = gtf[3]
            miny = maxy + ysize * gtf[5]
            
            poly_wkt = 'POLYGON (( %f %f, %f %f, %f %f, %f %f, %f %f ))' %(minx,miny,minx,maxy,maxx,maxy,maxx,miny,minx,miny)
        
        ####  Create geometry object
        geom = ogr.CreateGeometryFromWkt(poly_wkt)
        #print proj
        
        #### Create srs objects
        s_srs = osr.SpatialReference(proj)
        t_srs = osr.SpatialReference()
        t_srs.ImportFromEPSG(epsg)
        st_ct = osr.CoordinateTransformation(s_srs,t_srs)
        
        #### Transform geometry to target srs
        if not s_srs.IsSame(t_srs):
            geom.Transform(st_ct)
        
    return geom

if __name__ == '__main__':
    main()
