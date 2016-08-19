#!/usr/bin/python

from numpy import *

x=arange(0,15)
A=5
B=3
y_true=A*x+B*x**2
y_meas=y_true+2*random.randn(len(x))

def residuals(p,y,x):
 A,B=p
 err=y-A*x-B*x**2
 return err

def peval(x,p):
 return p[0]*x+p[1]*x**2

p0=[1,1]

from scipy.optimize import leastsq

plsq=leastsq(residuals,p0,args=(y_meas,x))

print(plsq[0])

import matplotlib.pyplot as plt
plt.plot(x,peval(x,plsq[0]),x,y_meas,'o',x,y_true)
plt.title('Least-squares fit to noisy data')
plt.legend(['Fit','Noisy','True'])
plt.show()
