#!/usr/bin/python

from numpy import *

x=arange(0,5)
x2=arange(0,5)
A=5
B=3
y_true=A*x+B*x2
y_meas=y_true+2*random.randn(len(x))

def residuals(p,y,x,x2):
 [A,B]=p
 err=y-A*x-B*x2
 return err

def peval(x,x2,p):
 [A,B]=p
 return A*x+B*x2

p0=[5,3]

from scipy.optimize import leastsq

plsq=leastsq(residuals,p0,args=(y_meas,x,x2))

print(plsq[0])

import matplotlib.pyplot as plt
plt.plot(x,peval(x,x2,plsq[0]),x,y_meas,'o',x,y_true)
plt.title('Least-squares fit to noisy data')
plt.legend(['Fit','Noisy','True'])
plt.show()
