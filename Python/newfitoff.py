#!/usr/bin/python

import scipy
import scipy.optimize
import subprocess
import sys
#import matplotlib.pyplot as plt

def residuals(p,y,x0,x1,x2,x3,x4,x5):
 err=y-p[0]*x0-p[1]*x1-p[2]*x2-p[3]*x3-p[4]*x4-p[5]*x5
 return err

def peval(x0,x1,x2,x3,x4,x5,p):
 return p[0]*x0+p[1]*x1+p[2]*x2+p[3]*x3+p[4]*x4+p[5]*x5

date1=sys.argv[1]
date2=sys.argv[2]

name1=date1 + "-" + date2 + "_ampcor.off"
name2=date1 + "-" + date2 + "_cull.off"

a=scipy.loadtxt(name1)
b=scipy.loadtxt(name2)

#plt.figure(1)
#plt.plot(scipy.matrix(a[:,0]).T,scipy.matrix(a[:,3]).T,'.',label='alloff')
#plt.plot(scipy.matrix(b[:,0]).T,scipy.matrix(b[:,3]).T,'r.',label='ROI_PAC cull')
#plt.legend()

x=a[:,0]
y=a[:,2]
dx=a[:,1]
dy=a[:,3]

np=scipy.size(a, axis=0)

id=scipy.arange(0,np)
mx=scipy.matrix(x[id]).T
my=scipy.matrix(y[id]).T
d=dy[id]
all=a[id]

p0=scipy.ones(6)
for i in scipy.arange(0,3):
 G=scipy.hstack((scipy.matrix(scipy.ones(scipy.size(mx))).T,mx,my,scipy.multiply(mx,my),scipy.power(mx,2),scipy.power(my,2)))

 plsq=scipy.optimize.leastsq(residuals,p0,args=(d,scipy.ones(scipy.size(mx)),scipy.asarray(mx)[:,0],scipy.asarray(my)[:,0],scipy.asarray(scipy.multiply(mx,my))[:,0],scipy.asarray(scipy.power(mx,2))[:,0],scipy.asarray(scipy.power(my,2))[:,0]))
 res=d-peval(scipy.ones(scipy.size(mx)),scipy.asarray(mx)[:,0],scipy.asarray(my)[:,0],scipy.asarray(scipy.multiply(mx,my))[:,0],scipy.asarray(scipy.power(mx,2))[:,0],scipy.asarray(scipy.power(my,2))[:,0],plsq[0])
 mod=plsq[0]
 synth=G*scipy.matrix(mod).T
 cutoff=res.std(axis=0,ddof=1)
 id=scipy.nonzero(abs(res)>cutoff)
 id2=scipy.nonzero(abs(res)<=cutoff)

 #plt.figure(i+2)
 #plt.plot(mx,d,'b.',label='alloff')
 #plt.plot(mx[id2],synth[id2],'.',label='fit',color='lightgreen')
 #plt.plot(mx[id],d[id],'r.',label='cull #'+str(i+1))
 #plt.legend()
 
 mx=mx[id2]
 my=my[id2]
 d=d[id2]
 all=all[id2]

subprocess.call("mv " +  name2 + " oldcull.off", shell=True);

fid=open(name2,'w')

form="%8d%10.3f%8d%12.3f%11.5f%11.6f%11.6f%11.6f"
scipy.savetxt(fid,all,fmt=form)

fid.close();

#plt.show()
#plt.close()

exit()
