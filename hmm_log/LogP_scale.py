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


class logP:
    def __init__(self,x):
        self.exp = np.int64(0)
        self.mant = np.float64(x)
        
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
        z = logP(1.0) # dummy var for return val
        z.mant = zm
        z.exp = ze
        return z
 

al = logP(1.0)
y = logP(0.1)

a = logP(2.0E-320)
b = logP(2.0E-10)
print 'got here'
c = a*b
print 'got here 2'
print c.mant, c.exp 

for i in range(350):
    al = al * y 
#print 'r: ', '{:f}'.format(r)

print al.mant, ' x 10^', al.exp

#np.int16(32000) * np.int16(3)
