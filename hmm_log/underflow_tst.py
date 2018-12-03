#!/usr/bin/python
#
#   Utilities for BT-HMM_
#

import numpy as np
import numbers
from random import *
import matplotlib.pyplot as plt
import editdistance as ed
from tqdm import tqdm
import os
import sys


PASS = '        PASS'
FAIL = '        FAIL'
epsilon = 1.0E-4


class logP:
    def __init__(self,x):
        self.exp = np.int64(0)
        self.mant = np.float64(x)
        #print 'init: ', self.mant, self.exp
        
    def __mul__(self,y):  
        #print 'mul arg y: ', y.mant,' x10^', y.exp
        assert isinstance(y,logP), 'logP().__mul__:  wrong data type'

        np.seterr(under='raise')
        try:
            #print 'trying'
            zm = self.mant * y.mant
        except: 
            print 'I caught exception'
            print 'x = ', self.mant, 'x10^',self.exp
            print 'y = ', y.mant, 'x10^',y.exp
            self.exp += (-200)
            #print 'my type is: ', self
            ap = self.mant
            a = np.float64(ap) * np.float64(1.0E200)
            #a = self.mant
            b = y.mant
            zm = logP(a*b).mant
        
        ze = self.exp + y.exp
        z = logP(zm) # return value
        z.mant = zm
        z.exp = ze
        return z
    
    def norm(self):
        mexp = int(np.log10(self.mant))
        m2 = self.mant
        #print 'norm: ', m2, mexp+self.exp
        self.mant = m2
        self.exp = mexp+self.exp
 
    def __str__(self):
        self.norm()
        return '{:f}x10^{:d}'.format(self.mant,int(self.exp))
    
    def __add__(self,b):
        self.norm
        b.norm
        c = logP(self.mant+b.mant)
        return c





########################################3    TESTS
#
#

print 'Testing logP_scale'


al = logP(1.0)
y = logP(0.1)

a = logP(2.0E-120)
b = logP(2.0E-10)
print 'got here'
c = (a*b)

fs = '   multiplication'
#print 'c:',c
#print 'c pieces: ', c.mant, c.exp
#c.norm()
assert abs(c.mant - 4.0E-130) < epsilon, fs + FAIL
assert c.exp == 0, fs+FAIL

print fs+PASS

fs = '   norm()'
#c.norm()
print c
assert abs(c.mant-0.4)< epsilon, fs +FAIL
assert c.exp == -129 , fs+FAIL

print fs+PASS

print ' Testing underflow catch  ' 

for i in range(350):
    al = al * y 
#print 'r: ', '{:f}'.format(r)

al.norm
fs = '    underflow scaling '
print al.mant, 'x10^',al.exp
assert abs(al.mant - 1.0E-150) < epsilon, fs+FAIL
assert al.exp == -200, fs+FAIL
al.norm()
print 'norm:', al.mant, 'x10^',al.exp

assert abs(al.mant - 1.0) < epsilon, fs+FAIL
assert al.exp == -350, fs+FAIL

print fs+PASS

print 'after undeflow catch:',al.mant, ' x 10^', al.exp




quit()



mexp = np.log10(al.mant)
m2 = al.mant/10**mexp

print m2, ' x 10^', al.exp+mexp

print al

#  addition test:

a = logP(2E-40)
b = logP(3E125)
print a
an = a.norm()
print 'norm: ', an

print '2+3= ', logP(2) + logP(3)

