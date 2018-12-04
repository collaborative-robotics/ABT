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


SMALLEST_LOG = -1.0E306

 
#  Class for scaled probabilities
#
#  Algorithms for scaled HMM prob computations
#    'super floating point' class
#
#    usage:  x = logP(0.5)
#       yields x = ln(0.5) etc.
#       this is for scalars
# 
#    (overload * and + )
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
        if self.mant == 0.0:
            mexp = 0.0
            m2 = 0.0
        else:
            mexp = int(np.log10(self.mant))
            m2 = self.mant/10**mexp
        #print 'norm: ', m2, mexp+self.exp
        self.mant = m2
        self.exp = mexp+self.exp
        
    def __float__(self):
        return self.test_val()
    
    def set_val(self,x):
        self.__init__(x)
    
    def test_val(self):  # return a float64 for testing
        return np.float64(self.mant*10**self.exp)
    
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

if __name__ == '__main__':

    print 'Testing logP_scale'

    print '    Testing instantiation' 

    a = logP(2.0E-120)
    b = logP(2.0E-10)

    fs = '  instantiation '
    assert abs(a.mant-2.0E-120)<epsilon, fs+FAIL
    assert abs(a.exp)<epsilon, fs+FAIL
    print fs+PASS

    print '  Testing  Multiplication'
    fs = '       multiplication'
    c = (a*b)
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

    al = logP(1.0)
    y = logP(0.1)
    for i in range(350):
        al = al * y 
    #print 'r: ', '{:f}'.format(r)

    al.norm
    fs = '    underflow, norm,  scaling '
    print al.mant, 'x10^',al.exp
    assert abs(al.mant - 1.0E-150) < epsilon, fs+FAIL
    assert al.exp == -200, fs+FAIL
    al.norm()
    print 'norm:', al.mant, 'x10^',al.exp
    assert abs(al.mant - 1.0) < epsilon, fs+FAIL
    assert al.exp == -350, fs+FAIL

    print fs+PASS

    print 'after underflow catch:',al.mant, ' x 10^', al.exp

    print '  testing addition'

    fs = '  addition test  '
    
    #  addition test:
    

    c = logP(2) + logP(3)

    print '2+3= ', c
    assert abs(c.mant-5.0)< epsilon, fs+FAIL
    assert abs(c.exp) < epsilon, fs+FAIL

    print fs+PASS

    print '\n\n                 ALL TESTS PASSED'

