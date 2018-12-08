#!/usr/bin/python
#
#   Class and functions for log probability math
#
#  inspired by: Numerically Stable Hidden Markov Model Implementation
#           Tobias P. Mann
#         February 21, 2006
#  (pdf available online)
#
#
#   to test:    >python test_logP   log

import numpy as np
import numbers  

SMALLEST_LOG = -1.0E306
NSYMBOLS = 20
STRICT = True 
LZ = np.nan   # our log of zero value 

#  extended natural log
def EL(x):
    assert isinstance(x,numbers.Number), 'EL (log) wrong data type'
    if x < 0.0:
        print 'log problem: ', x
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

# vectorized versions of EE and EL
ELv = np.vectorize(EL)
EEv = np.vectorize(EE)

    
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
        assert isinstance(p,numbers.Number), fs
        assert p >= 0.00, fs
        self.lp = EL(p)
        

    def norm(self):
        pass
        return




    def id(self):
        return 'log'
        
    
    def __float__(self):
        #return 5
        return self.test_val()
    
    def __str__(self):
        #return '{:8.2s}'.format(self.lp)
        return str(self.lp)
    
    def set_val(self,x):
        self.__init__(x)
        
    def test_val(self):  # return a float64 of prob. for testing
        if np.isnan(self.lp):
            return np.float64(0.0)
        return np.float64(np.exp(self.lp))
        
    def __mul__(self, lp2):
        if isinstance(lp2,numbers.Number):
            if lp2 == 0.0:
                return logP(0)
            t = logP(0.5)
            t.lp = self.lp + np.log(lp2)
            return t
        if np.isnan(self.lp) or np.isnan(lp2.lp):
            t = logP(0)
            return t
        else:
            t = logP(0.5)
            t.lp = self.lp + lp2.lp
            return t
    
        
    def __div__(self, lp2):
        if isinstance(lp2,numbers.Number):
            t = logP(0.5)
            t.lp = self.lp - np.log(lp2)
            return t
        if np.isnan(self.lp):
            t = logP(0)
            return t
        if np.isnan(lp2.lp):
            print 'LogP:   DIVIDE BY ZERO'
            t = logP(0)
            t.lp = np.Inf
            return t
        else:
            t = logP(0.5)
            t.lp = self.lp - lp2.lp
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
                t.lp = self.lp + EL(1+np.exp(lp2.lp-self.lp))
            else:
                t.lp =  lp2.lp + EL(1+np.exp(self.lp-lp2.lp))
        return t
     
