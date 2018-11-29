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
            if len(np.shape(Pm)) != 2:
                print 'LogPm() wrong shape:'
                print Pm
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
        
    def __setitem__(self,i,j,p):
        #print '========'
        #print self.lp
        #print i
        self.m[i,j] = p
        
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
    #print y
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
    #print 'x: ', type(x)
    assert isinstance(x, logP), 'logP() returns wrong type'
    
    ##############################
    #
    #  logP __add__()
    
    z = x + y
    assert isinstance(z,logP), 'logP() __add__ returns wrong type'
    
    logsum = np.log(0.25 + 0.25)
    
    fs = 'logP() __add__'
    assert abs(z.lp-logsum) < epsilon, fs+FAIL
    assert abs((x+y).lp-logsum) < epsilon, fs+FAIL
    print fs+PASS
    
    ##############################
    #
    #  logP __mull__()
    x = logP(0.25)
    y = logP(0.25)
    z = x * y
    assert isinstance(z,logP), 'logP() __mul__ returns wrong type'
    logprod = np.log(0.25*0.25)
    
    fs = 'logP() __mul__ '
    assert abs(z.lp-logprod) < epsilon, fs+FAIL
    assert abs((x*y).lp-logprod) < epsilon, fs+FAIL
    z = x * logP(0)
    assert np.isnan(z.lp), fs+FAIL
    print fs+PASS
    
    #############################
    #
    #  logP += A*B
    #

    x = logP(0.25)
    y = logP(0.25)
    t = logP(0.25)
    t += x*y
    fs = 'logP() combined add and times'
    assert isinstance(t, logP),fs+FAIL
    assert np.exp(t.lp)== 0.25*0.25+0.25 ,fs+FAIL
    print fs+PASS
    
    
    print 'logP classes          PASS'
     
    ####################################################
    #  logP for vectors 
    #
    x = logPv([e, e*e, e*e*e])
    y = logPv([e*e, e, 1/e])
    
    fs = 'logPv returns wrong type'
    assert isinstance(x[0], logP), fs
    assert isinstance(y[2], logP), fs
    
    #print '---'
    #print x
    #print y
    #print '----'
    
    fs = 'logPv() instantiation    FAIL'
    assert abs(y[0].lp -  2.0) < epsilon, fs
    assert abs(y[1].lp -  1.0) < epsilon, fs
    assert abs(y[2].lp - -1.0) < epsilon, fs
    z = x + y
    assert isinstance(z[0],logP), 'logPv() __add__ returns wrong type'
    #print 'Z;', z, type(z)
    #print '' 
    
    # let's exponentiate sums and check them
    m = []
    for l in z.v:
        m.append(EE(l.lp))
    m = np.array(m)

    #print 'm;',m
    fs = 'logPv() addition tests '
    #print 'compare: ', m[0], (e+e*e)
    assert abs(m[0] - (e+e*e)) < epsilon, fs + 'FAIL'
    assert abs(m[1] - (e+e*e)) < epsilon, fs + 'FAIL'
    assert abs(m[2] - (e*e*e + 1/e)) < epsilon, fs + 'FAIL'
    
    print fs + '         PASS'
   
   
    fs = 'logPv() vector * vector multiply'
    
    x = logPv([e, e*e, e*e*e])
    y = logPv([e*e, e, 1/e])
    
    t = x*y
    print t, type(t)
    assert t.v[0].lp == 3.0, fs + FAIL
    assert t.v[1].lp == 3.0, fs + FAIL
    assert t.v[2].lp == 2.0, fs + FAIL
    
    print 'logPv() Tests  ' + PASS
    
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
    #print x[0,0], type(x.m[0,0])
    assert isinstance(x.m[0,0], numbers.Number), fs
    assert isinstance(y, logPm), fs
    assert isinstance(y[2,1], logP), fs
    
    #print '---'
    #print x
    #print y
    #print '----'
    
    fs = 'logPm() instantiation    FAIL'
    assert abs(y[1,0].lp - 2.0)  < epsilon, fs
    assert abs(y[2,1].lp - 1.0)  < epsilon, fs
    assert abs(y[1,2].lp - -1.0) < epsilon
    
    print 'logPm() instantiation            PASSED'
    
    print 'Starting matrix addition tests ...'
    z = x + y

    #print 'z = x+y: ',z 
    #print ''
     
    
    #m = EEv(z)  # let's exponentiate sums and check them
    m = logPm(0.5*np.ones((3,3)))
    for i in [0,1,2]:
        for j in [0,1,2]:
            m.m[i,j] = logP(EE(z.m[i,j]))
    
    
    fs = 'EEv(z) matrix argument:  '
    assert np.shape(m.m) == (3,3), fs + 'FAIL'
    
    print fs + '             PASS'
    
    #print 'm;',m
    fs = 'logPm  __add__() '
    #print m[0,0].lp, logP(e+e*e).lp
    assert abs(m[0,0].lp - np.log(e+e*e)) < epsilon, fs + 'FAIL'
    assert abs(m[0,1].lp - np.log(e+e*e)) < epsilon, fs + 'FAIL'
    assert abs(m[0,2].lp - np.log(e*e*e + 1/e)) < epsilon, fs + 'FAIL'
    print fs + '         PASS'
    
    
    ###################################################################
    #
    #  math combining vector, matrix, getitem, etc.
    #
    
    fs = 'logPx mixed math tests'

    s = logP(0.5)
    v = logPv([1.0, 0.5, 0.25, e])
    m = logPm([[1.0, 0.5, 0.25, e],
               [1.0, 0.5, 0.25, e],
               [1.0, 0.5, 0.25, e]])

    n = logPv(np.ones(4))
    
    t = logP(0) + logP(0)
    assert np.isnan(t.lp), fs+FAIL
    t = s + v[1]
    assert np.exp(t.lp) == 1.0, fs+FAIL
    t = v[0] + m[1,1]
    assert np.exp(t.lp) == 1.5, fs+FAIL
    t = s + n[2]
    assert np.exp(t.lp) == 1.5, fs+FAIL
    t = logP(0) + n[2]
    assert np.exp(t.lp) == 1.0, fs+FAIL
    t = logP(0) * n[2]
    assert np.isnan(t.lp), fs+FAIL

 
    print fs+PASS
    
    
    print '\n\n           logPx() --  ALL TESTS PASS \n\n'
    
     
