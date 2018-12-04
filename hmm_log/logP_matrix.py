#!/usr/bin/python
#
#   Class and functions for log probability math
#

import numpy as np
import numbers
from logP_log import *
from logP_scale import *

NSYMBOLS = 20
STRICT = True 
    
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
    

ELv = np.vectorize(EL)
EEv = np.vectorize(EE)

    
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
        
        imax = -1
        for i,x in enumerate(self.v):
            #print 'i,x:', i,x
            if not np.isnan(x.lp): 
                if x.lp > max:
                    max = x.lp
                    imax = i
        t = logP(0.5)
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
    
    
          
