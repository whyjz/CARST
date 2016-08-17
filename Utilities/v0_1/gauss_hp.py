# Andrew K. Melkonian

import multiprocessing;
import numpy;
import scipy;
import scipy.ndimage;
import scipy.signal;
import struct;
import sys;


def calculate(func, args):
    result = func(*args)
    return '%s says that %s%s = %s' % (
        multiprocessing.current_process().name,
        func.__name__, args, result
        )


def calculatestar(args):
    return calculate(*args)


def gausshp(a,b,i,j):
    if i % 1000 == 0 and j % 1000 == 0:
        print(i);
    hpfilt_dat=scipy.ndimage.convolve(a,b);


if __name__ == '__main__':
    print("Heyoh");
    mapinfo="";

    name=sys.argv[1];
    
    infile=open(name,"rb");
    indat=scipy.matrix(numpy.fromfile(infile,dtype=numpy.uint8,count=-1,sep=""));
    infile.close();

    hdr=name+".hdr";
    infile=open(hdr,"r");
    for line in infile:
        if line.find("samples") > -1:
            samples=int(line[line.find("=")+1:].strip());
        elif line.find("lines") > -1:
            lines=int(line[line.find("=")+1:].strip());
        elif line.find("map info") > -1:
            mapinfo=line.strip();
    infile.close();

    indat=numpy.reshape(indat,(lines,samples));

    kernel=scipy.matrix([[-0.0000,-0.0007,-0.0024,-0.0007,-0.0000],
                         [-0.0007,-0.0314,-0.1131,-0.0314,-0.0007],
                         [-0.0024,-0.1131,0.5933,-0.1131,-0.0024],
                         [-0.0007,-0.0314,-0.1131,-0.0314,-0.0007],
                         [-0.0000,-0.0007,-0.0024,-0.0007,-0.0000]]);

    #outdat=scipy.cast[scipy.uint8](scipy.ndimage.convolve(indat,kernel));
    outdat=scipy.cast[scipy.float32](scipy.ndimage.convolve(scipy.cast[scipy.float32](indat),scipy.cast[scipy.float32](kernel)));

    #maximum=scipy.ndimage.measurements.maximum(outdat);
    #minimum=scipy.ndimage.measurements.minimum(outdat);
    #mean=scipy.mean(outdat);
    #stdv=scipy.std(outdat);
    #low_bound=mean-2.0*stdv;
    #high_bound=mean+2.0*stdv;
    #outdat[outdat>high_bound]=high_bound;
    #outdat[outdat<low_bound]=low_bound;
    #outdat=outdat-low_bound;
    #high_bound=high_bound-low_bound;
    #stretch=255.0/high_bound;
    #outdat=outdat*stretch;

    outdat.tofile(name+"_gauss");

    print("Done");

    #outdat=scipy.cast[scipy.uint8](scipy.ndimage.correlate(indat,indat[10000:10032,10000:10032]));

    #outdat.tofile("test_correlate");

    exit();

