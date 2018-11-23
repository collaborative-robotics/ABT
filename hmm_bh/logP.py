#!/usr/bin/python
#
#   Class and functions for log probability math
#

import numpy as np
import numbers  

NSYMBOLS = 20
STRICT = True

LZ = np.nan   # our log of zero value

epsilon = 1.0E-4

#  extended natural log
def EL(x):
    #print 'EL(x) rcvd: ', x, type(x)
    assert isinstance(x,numbers.Number), 'EL (log) wrong data type'
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

def elog(X):
    #assert np.sum(X >= 0.0) == len(X), 'elog(x): Attempted log of x < 0'
    y = np.zeros(np.shape(X))  # just so y is same size as X
    for i,x in enumerate(X):
        #print 'elog(): ',i,x
        if x < 0.0:
            print 'log arg < 0.0 - stopping'
            quit()
        if (x == 0):
            y[i] = LZ
        else:
            y[i] = np.log(x)
    return y 
    
def eexp(X):
    y = np.zeros(np.shape(X))
    for i,x in enumerate(X):
        if (np.isnan(x)):
            y[i] = 0
        else:
            y[i] = np.exp(x)
    return y
    

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
        self.lp = ELv(p) 
        
    def P(self):
        return EEv(self.lp)
    
    def __str__(self):
        #return '{:8.2s}'.format(self.lp)
        return str(self.lp)
    
    def __float__(self):
        return float(self.lp)

    
    def __mul__(self, lp2):
        if self.lp == LZ or lp2.lp == LZ:
            return LZ
        else:
            return self.lp + lp2.lp
    
    def __add__(self, lp2):
        t = logP(.5)
        if self.lp==LZ or lp2.lp == LZ:
            if self.lp == LZ:
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
            if len(np.shape(Pm)) != 2:
                print 'LogPv() wrong shape'
                quit()
        self.m = np.zeros(np.shape(Pm))
        for (i,j),p in np.ndenumerate(Pm):
            self.m[i,j] = logP(p)
        #self.lp = np.array(map(logP, map(logP, Pm)))
        #self.lp = np.array(map(logP, map(logP, Pm)))
        #print '-- init Pm'
        #print np.shape(Pm) , '--->',np.shape(self.lp)
        
    def __getitem__(self,tuple):
        #print '========'
        #print self.lp
        #print np.shape(self.lp)
        #print t, self.lp[t] 
    
        t = logP(0.5)
        t.lp = self.m[tuple]
        return t
    
                #def __str__(self):
                    #stmp = ''
                    #for x in self.v:
                        ##print 'str: ', x
                        #stmp += '{:10s} '.format(x)
                    #return stmp
        
    def __str__(self):
        ############3    How to output matrix as string?????/
        rc = np.shape(self.lp)[0]
        cc = np.shape(self.lp)[1]
        for r in range(rc):
            stmp = ''
            for c in range(cc):
                stmp += '{:10f}'.format(self[r,c].lp)
            stmp += '\n'
        return stmp
        
                    
                    #def __add__(self, P):
                        #t = logPv(np.ones(len(self.v)))
                        #print 'logPv add/t: ', t
                        #for i,p in enumerate(P.v):
                            #t.v[i] = self[i] + p
                        #return t
    
    
    def __add__(self, P):
        t = logPm(np.ones(np.shape(P)))
        for (i,j), p in np.ndenumerate(P):
            t.m[i,j] = self.m[i,j] + p
        return t
    
    
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
            #assert p < 1.00, fs
            assert p > 0.00, fs
            self.v.append(logP(p))
        
    def __getitem__(self,i):
        #print '========'
        #print self.lp
        #print i
        #t = logP(0.5)
        #t.lp = self.lp[i]
        #return t
        return self.v[i]
    
    def __setitem__(self,p, i):
        #print '========'
        #print self.lp
        #print i
        self.v[i] = p
        
    def __str__(self):
        stmp = ''
        for x in self.v:
            #print 'str: ', x
            stmp += '{:10s} '.format(x)
        return stmp
        
    
    def __add__(self, P):
        t = logPv(np.ones(len(self.v)))
        print 'logPv add/t: ', t
        for i,p in enumerate(P.v):
            t.v[i] = self[i] + p
        return t
    
    
          
        
        
#################################################################################################
#
#     TESTS
#

if __name__ == '__main__':
    print '\n\n  Testing logP() class and related ...\n\n'
    
    #####################################
    # test basic log functions
    e = np.exp(1)
    
    y = ELv([e, e*e, 0, np.sqrt(e)])
    
    assert isinstance(y[0], float), 'ELv returns wrong type'
    #print y
    fs = ' elog() test FAIL'
    assert abs(y[0] - 1.0) < epsilon, fs
    assert abs(y[1] - 2.0) < epsilon, fs
    assert np.isnan(y[2]), fs
    assert abs(y[3] - 0.5) < epsilon, fs
    assert abs(ELv(e*e)-2.0) < epsilon, fs
    print ' elog() tests    PASSED'
    
    # eexp()
    fs = ' eexp() test  FAIL'
    assert  abs(EEv(1)-e) < epsilon, fs
    y = EEv([2, 0, LZ, -1])
    print y
    assert abs(y[0]-e*e) < epsilon, fs
    assert abs(y[1]-1.0) < epsilon, fs
    assert abs(y[2]-0.0) < epsilon, fs
    assert abs(y[3]-1/e) < epsilon, fs

    assert abs(EEv(1) - e) < epsilon, fs
    
    y = EEv([[e, 0],[LZ, 1]])
    assert abs(y[1,1]-e) < epsilon, fs
    print ' eexp() tests    PASSED'

    ###################################
    # test logP classes and operator overlays
    x = logP(0.25)
    y = logP(0.25)
    
    # make sure stuff returns right types
    print 'x: ', type(x)
    assert isinstance(x, logP), 'logP() returns wrong type'
    
    z = x + y
    assert isinstance(z,logP), 'logP() __add__ returns wrong type'
    
    logsum = np.log(0.25 + 0.25)
    
    fs = 'logP() __add__    FAIL'
    assert abs(z.lp-logsum) < epsilon, fs
    assert abs((x+y).lp-logsum) < epsilon, fs
    
    print 'logP classes          PASS'
     
    ####################################################
    #  logP for vectors 
    #
    x = logPv([e, e*e, e*e*e])
    y = logPv([e*e, e, 1/e])
    
    fs = 'logPv returns wrong type'
    assert isinstance(x[0], logP), fs
    assert isinstance(y[2], logP), fs
    
    print '---'
    print x
    print y
    print '----'
    
    fs = 'logPv() instantiation    FAIL'
    assert abs(y[0].lp -  2.0) < epsilon, fs
    assert abs(y[1].lp -  1.0) < epsilon, fs
    assert abs(y[2].lp - -1.0) < epsilon, fs
    z = x + y
    assert isinstance(z[0],logP), 'logPv() __add__ returns wrong type'
    print 'Z;', z, type(z)
    print '' 
    
    # let's exponentiate sums and check them
    m = []
    for l in z.v:
        m.append(EE(l.lp))
    m = np.array(m)

    print 'm;',m
    fs = 'logPv  FAIL'
    print 'compare: ', m[0], (e+e*e)
    assert abs(m[0] - (e+e*e)) < epsilon, fs
    assert abs(m[1] - (e+e*e)) < epsilon, fs
    assert abs(m[2] - (e*e*e + 1/e)) < epsilon, fs
    
    print 'logPv() tests            PASS'
   
    
    #######################################
    #
    #   test logPm  - matrix version
    #
     #  logP for matrices 
    x = logPm([
        [e, e*e, e*e*e],
        [e, e*e, e*e*e],
        [e, e*e, e*e*e]  ])
    y = logPm([
        [e*e, e, 1/e],
        [e*e, e, 1/e],
        [e*e, e, 1/e]  ])
    
    fs = 'logPm returns wrong type'
    assert np.shape(x.m) == (3,3), fs
    print x[0,0], type(x.m[0,0])
    assert isinstance(x.m[0,0], numbers.Number), fs
    assert isinstance(y, logPm), fs
    assert isinstance(y[2,1], logP), fs
    
    print '---'
    print x
    print y
    print '----'
    
    fs = 'logPm() instantiation    FAIL'
    print '>>', y[1,0].lp, 2.0
    assert abs(y[1,0].lp - 2.0) < epsilon, fs
    
    print '>>', y[2,1].lp, 0.0
    assert abs(y[2,1].lp - 1.0) < epsilon, fs
    assert abs(y[1,2].lp - -1.0) < epsilon
    z = x + y
    print 'Z;',z 
    print ''
    
    v = z[1]   # first row of matrix
    m = EEv(z)  # let's exponentiate sums and check them
    
    print 'm;',m
    fs = 'logPm  FAIL'
    print m[0].lp, logP(e+e*e).lp
    assert abs(m[0].lp - np.log(e+e*e)) < epsilon, fs
    assert abs(m[1].lp - np.log(e+e*e)) < epsilon, fs
    assert abs(m[2].lp - np.log(e*e*e + 1/e)) < epsilon, fs
    
    print 'logPm() tests            PASS'
    
     
