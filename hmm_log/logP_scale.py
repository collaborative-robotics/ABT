#!/usr/bin/python
#
#   Utilities for BT-HMM_
#

import numpy as np
import numbers 


SMALLEST_LOG = -1.0E306

 
#  Class for scaled probabilities
#   to test:    >python test_logP   scale
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
    def __init__(self,p): 
        if isinstance(p,logP):
            self = p
            return
        fs = 'logP_scale() __init__ bad input' 
        assert isinstance(p,numbers.Number), fs
        assert p >= 0.00, fs
        self.exp = np.int64(0)
        self.mant = np.float64(p)
        
    def norm(self):
        if self.mant == 0.0:
            mexp = 0.0
            m2 = 0.0
        elif self.mant == np.Inf:
            mexp = np.Inf
            m2 = np.Inf
        else:
            mexp = int(np.log10(self.mant))
            m2 = self.mant/10**mexp
        self.mant = m2
        self.exp = mexp+self.exp
        
    def id(self):
        return 'scale'
    
    def __float__(self):
        #return 5
        return self.test_val()
    
    def __str__(self):
        self.norm()
        if self.mant == np.Inf:
            return 'Inf'
        else:
            return '{:f}x10^{:d}'.format(self.mant,int(self.exp))
        
    def set_val(self,x):
        self.__init__(x)
    
    def test_val(self):  # return a float64 for testing
        return np.float64(self.mant*10.00**self.exp)

    
    def __div__(self,y):  
        DEBUG = True
        if isinstance(y,numbers.Number):  # case of logP * float
            if np.log(y) < SMALLEST_LOG:
                return logP(np.Inf)
            yval = y
            ye = 0
        else:                             # case of logP * logP
            assert isinstance(y,logP), 'logP().__mul__:  wrong data type'
            yval = y.mant
            ye = y.exp
        
        np.seterr(under='raise')
        try:
            #print 'self.mant, yval', self.mant, yval
            zm = self.mant / yval
        except: 
            if DEBUG:
                print 'I caught exception'
                print 'x = ', self.mant, 'x10^',self.exp
                print 'y = ', y.mant, 'x10^',y.exp
            self.exp += (-200)
            a = np.float64(self.mant) * np.float64(1.0E200)
            b = yval
            zm = logP(a/b).mant        
        ze = self.exp - ye       # logarithmic division
        z = logP(0.5) # return value
        z.mant = zm
        z.exp = ze
        return z
    
    def __mul__(self,y):  
        DEBUG = True
        if isinstance(y,numbers.Number):  # case of logP * float
            yval = y
            ye = 0
        else:                             # case of logP * logP
            assert isinstance(y,logP), 'logP().__mul__:  wrong data type'
            yval = y.mant
            ye = y.exp
        
        np.seterr(under='raise')
        try:
            zm = self.mant * yval
        except: 
            if DEBUG:
                print 'I caught exception'
                print 'x = ', self.mant, 'x10^',self.exp
                print 'y = ', y.mant, 'x10^',y.exp
            self.exp += (-200)
            ap = self.mant
            a = np.float64(ap) * np.float64(1.0E200)
            b = yval
            zm = logP(a*b).mant
        
        ze = self.exp + ye
        z = logP(zm) # return value
        z.mant = zm
        z.exp = ze
        return z
    
    def __add__(self,b):
        self.norm
        b.norm
        c = logP(self.mant+b.mant)
        return c

