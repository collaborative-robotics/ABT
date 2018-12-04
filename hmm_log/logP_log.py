#!/usr/bin/python
#
#   Class and functions for log probability math
#

import numpy as np
import numbers  

NSYMBOLS = 20
STRICT = True 
LZ = np.nan   # our log of zero value 

#  extended natural log
def EL(x):
    #print 'EL(x) rcvd: ', x, type(x)
    #if np.isnan(x):
        #return LZ
    assert isinstance(x,numbers.Number), 'EL (log) wrong data type'
    #print 'EL arg:', x
    if x < 0.0:
        print 'log problem: ', x
    #print 'EL(x): got', x
    assert x >= 0.0,  'log arg < 0.0 - stopping'
    if (x == 0.0):
        y = LZ
    else:
        y = np.log(x)
    return y
    
#  extended exp()
def EE(x):
    assert isinstance(x,numbers.Number), 'EE (exp) wrong data type'
    if (np.isnan(x)):
        y = 0
    else:
        y = np.exp(x)
    return y

#  Class for log probabilities
#
#  Algorithms from hmm_scaling_revised.pdf 
#     Tobias P. Mann, UW, 2006
#
#    usage:  x = logP(0.5)
#       yields x = ln(0.5) etc.
#       this is for scalars
#
#    use logPv and logPm classes for 
#      vectors and mats.
class logP():
    def __init__(self,p):
        fs = 'logP() __init__ bad input'
        #print 'logP init: ', p
        #assert p <= 1.00, fs
        assert p >= 0.00, fs
        self.lp = EL(p) 
        
    def P(self):
        return EE(self.lp)
    
    def test_val(self):  # return a float64 for testing
        f = np.float64(EE(self.lp))
        return f
    
    def __str__(self):
        #return '{:8.2s}'.format(self.lp)
        return str(self.lp)
    
    def __float__(self):
        return float(self.lp)

    
    def __mul__(self, lp2):
        if np.isnan(self.lp) or np.isnan(lp2.lp):
            t = logP(0)
            return t
        else:
            t = logP(0.5)
            t.lp = self.lp + lp2.lp
            return t
    
    def __add__(self, lp2):
        t = logP(.5)
        if np.isnan(self.lp) or np.isnan(lp2.lp):
            if np.isnan(self.lp):
                return lp2
            else:
                return self
        else:
            if self.lp > lp2.lp:
                t.lp = self.lp + ELv(1+np.exp(lp2.lp-self.lp))
            else:
                t.lp =  lp2.lp + ELv(1+np.exp(self.lp-lp2.lp))
        return t
     
