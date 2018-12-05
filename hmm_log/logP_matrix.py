#!/usr/bin/python
#
#   Class and functions for log probability math
#

import numpy as np
import numbers
import importlib
#

SMALLEST_LOG = -1.0E306
NSYMBOLS = 20
STRICT = True


######################   Two modules to support the LogP() api
#
#
global logP
def logP_Matrix_init(str):
    global logP
    if str=='log':
        #from logP_log import *
        importlib.import_module('logP_log')
    elif str=='scale':
        #from logP_scale import *
        importlib.import_module('logP_scale')
    else:
        print 'unknown logP module ... quitting'
        quit()
    return
    
###########
#
#  a matrix of logP() instances
#
class logPm():
    global logP
    def __init__(self, Pm):
        rc,cc = np.shape(Pm)
        if STRICT:
            fs = 'LogPm() wrong shape:'
            assert isinstance(Pm, np.ndarray),fs
            assert len(np.shape(Pm)) == 2, fs
        self.m = np.zeros((rc,cc))
        fs = 'bad input to logPm()'
        for r in range(rc):
            for c in range(cc):
                p = Pm[r,c]
                assert isinstance(p,numbers.Number), fs
                self.m[r,c] = logP(p)
        
    def __getitem__(self,tpl):
        t = logP(0.5)
        t.set_val(self.m[tpl])
        return t
    
        
    def __setitem__(self,t,p):
        self.m[t] = p
        
    def __str__(self):
        rc = np.shape(self.m)[0]
        cc = np.shape(self.m)[1]
        stmp = '[ \n['
        for r in range(rc): 
            for c in range(cc):
                stmp += str(self.m[r,c]) + ' '
            stmp += ' ]\n'
        return stmp + ' ]'
        
    
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
    global logP
    def __init__(self, Pv):
        if False:
            if len(np.shape(Pv)) != 1:
                print 'LogPv() wrong shape'
                quit()
        self.v = []
        for i,p in enumerate(Pv):
            fs = 'bad input to logPv()'
            assert isinstance(p,numbers.Number), fs
            self.v.append(logP(p))
        
    # return argmax, max for a logP vector
    def maxlv(self):
        vmax = SMALLEST_LOG
        imax = -1
        for i,x in enumerate(self.v):
            print 'maxlv: ', i,x.test_val(), vmax
            if x.test_val() > vmax:
                vmax = x.test_val()
                imax = i
        assert not np.isnan(vmax), 'maxlv() Somethings wrong!'
        t = logP(vmax)
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
    
    
          
