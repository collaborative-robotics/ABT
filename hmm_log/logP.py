#!/usr/bin/python
#
#   Class and functions for log probability math
#

import numpy as np
import numbers  

NSYMBOLS = 20
STRICT = True

PASS = '        PASS'
FAIL = '        FAIL'

LZ = np.nan   # our log of zero value

epsilon = 1.0E-4

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


ELv = np.vectorize(EL)
EEv = np.vectorize(EE)

#def elog(X):
    ##assert np.sum(X >= 0.0) == len(X), 'elog(x): Attempted log of x < 0'
    #y = np.zeros(np.shape(X))  # just so y is same size as X
    #for i,x in enumerate(X):
        ##print 'elog(): ',i,x
        #if x < 0.0:
            #print 'log arg < 0.0 - stopping'
            #quit()
        #if (x == 0):
            #y[i] = LZ
        #else:
            #y[i] = np.log(x)
    #return y 
    
#def eexp(X):
    #y = np.zeros(np.shape(X))
    #for i,x in enumerate(X):
        #if (np.isnan(x)):
            #y[i] = 0
        #else:
            #y[i] = np.exp(x)
    #return y
    

#  Class for log probabilities
#
#  Algorithms from hmm_scaling_revised.pdf 
#     Tobias P. Mann, UW, 2006
#
#    usage:  x = logP(0.5)
#       yields x = ln(0.5) etc.
#       this is for scalars!
#    to use with vectors use:
##     v = map(logP, [ .5, .3, .9, 1.0, 0] )
#     v is a vector of LogP's
#  BH idea:
#    (overload * and + )!!
class logP():
    def __init__(self,p):
        fs = 'logP() __init__ bad input'
        #print 'logP init: ', p
        #assert p <= 1.00, fs
        assert p >= 0.00, fs
        self.lp = EL(p) 
        
    def P(self):
        return EEv(self.lp)
    
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
    
###########
#
#  a matrix of logP() instances
#
class logPm():
    def __init__(self, Pm):
        if STRICT:
            fs = 'LogPm() wrong shape:'
            assert len(np.shape(Pm)) == 2, fs
        self.m = np.zeros(np.shape(Pm))
        for (i,j),p in np.ndenumerate(Pm):
            self.m[i,j] = logP(p)
        #self.lp = np.array(map(logP, map(logP, Pm)))
        #self.lp = np.array(map(logP, map(logP, Pm)))
        #print '-- init Pm'
        #print np.shape(Pm) , '--->',np.shape(self.lp)
        
    def __getitem__(self,tpl):
        #print '========'
        #print self.lp
        #print np.shape(self.lp)
        #print t, self.lp[t] 
    
        t = logP(0.5)
        t.lp = self.m[tpl]
        return t
    
                #def __str__(self):
                    #stmp = ''
                    #for x in self.v:
                        ##print 'str: ', x
                        #stmp += '{:10s} '.format(x)
                    #return stmp
        
    def __setitem__(self,t,p):
        #print '========'
        #print self.lp
        #print i
        self.m[t] = p
        
    def __str__(self):
        ############3    How to output matrix as string?????/
        rc = np.shape(self.m)[0]
        cc = np.shape(self.m)[1]
        stmp = '[ \n['
        for r in range(rc): 
            for c in range(cc):
                stmp += str(self.m[r,c]) + ' '
            stmp += ' ]\n'
        return stmp + ' ]'
        
                    
                    #def __add__(self, P):
                        #t = logPv(np.ones(len(self.v)))
                        #print 'logPv add/t: ', t
                        #for i,p in enumerate(P.v):
                            #t.v[i] = self[i] + p
                        #return t
    
    
    def __add__(self, P):
        sp = np.shape(P.m)
        assert sp == np.shape(self.m), 'logPm() add: ???' 
        t = logPm(0.5*np.ones(sp))
        rc = sp[0]
        cc = sp[1]
        for r in range(rc):
            for c in range(cc):
                t.m[r,c] = self[r,c] + P[r,c]
        return t
    
    def __shape__(self):
        return np.shape(self.m)
    
    
#    LogP vectors
#    this should be a list of logP() instances
class logPv():
    def __init__(self, Pv):
        #assert insinstance(Pv, numbers.Number), 'logPv() bad input vector'
        if False:
            if len(np.shape(Pv)) != 1:
                print 'LogPv() wrong shape'
                quit()
        #self.lp = np.zeros(np.shape(Pv))
        #v = np.ones(len(Pv))
        self.v = []
        for i,p in enumerate(Pv):
            fs = 'bad input to logPv()'
            assert isinstance(p,numbers.Number), fs
            self.v.append(logP(p))
        
    # return argmax, max for a logP vector
    def maxlv(self):
        SMALLEST_LOG = -1.0E306
        max = SMALLEST_LOG
        t = logP(0.5)
        imax = -1
        for i,x in enumerate(self.v):
            #print 'i,x:', i,x
            if not np.isnan(x.lp): 
                if x.lp > max:
                    max = x.lp
                    imax = i
        t.lp = max
        if  imax < 0:
            # we saw all nan's 
            #print 'all nans in maxlv()'
            return 0,logP(0)
        assert imax >= 0, 'maxlv() Somethings wrong!'
        return imax, t
    
    def __getitem__(self,i):
        return self.v[i]
    
    def __setitem__(self,i,p):
        self.v[i] = p
        
    def __str__(self):
        stmp = ''
        for x in self.v:
            #print 'str: ', x
            stmp += '{:10s} '.format(x)
        return stmp
        
    
    def __add__(self, P):
        t = logPv(np.ones(len(self.v)))
        #print 'logPv add/t: ', t
        for i,p in enumerate(P.v):
            t.v[i] = self[i] + p
        return t
    
    
    def __mul__(self, P):
        t = logPv(np.ones(len(self.v)))
        #print 'logPv mul/t: ', t
        for i,p in enumerate(P.v):
            t.v[i] = self[i] * p
        return t
    
    
          
