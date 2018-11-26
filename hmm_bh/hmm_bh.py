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

#sudo pip install scikit-learn  # dep for hmmlearn
#pip install -U --user hmmlearn
#from hmmlearn import hmm
import random as random
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
        return '{:8s}'.format(self.lp)
    
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
    
class logPm():
    def __init__(self, Pm):
        if STRICT:
            if len(np.shape(Pm)) != 2:
                print 'LogPv() wrong shape'
                quit()
        self.lp = np.zeros(np.shape(Pm))
        for (i,j),p in np.ndenumerate(Pm):
            self.lp[i,j] = logP(p)
        #self.lp = np.array(map(logP, map(logP, Pm)))
        #self.lp = np.array(map(logP, map(logP, Pm)))
        print '-- init Pm'
        print np.shape(Pm) , '--->',np.shape(self.lp)
        
    def __getitem__(self,tuple):
        #print '========'
        #print self.lp
        #print np.shape(self.lp)
        #print t, self.lp[t] 
    
        t = logP(0.5)
        t.lp = self.lp[tuple]
        return t
    
    def __str__(self):
        ############3    How to output matrix as string?????/
        rc = np.shape(self.lp)[0]
        cc = np.shape(self.lp)[1]
        for r in range(rc):
            stmp = ''
            for c in range(cc):
                stmp += '{:8s}'.format(self.lp[r,c])
        return stmp
        
    
    def __add__(self, P):
        return self + P
    
    
class logPv():
    def __init__(self, Pv):
        if False:
            if len(np.shape(Pv)) != 1:
                print 'LogPv() wrong shape'
                quit()
        self.lp = np.zeros(np.shape(Pv))
        for i,p in enumerate(Pv):
            self.lp[i] = logP(p) 
        
    def __getitem__(self,i):
        #print '========'
        #print self.lp
        #print i
        #t = logP(0.5)
        #t.lp = self.lp[i]
        #return t
    
    def __setitem__(self,p, i):
        #print '========'
        #print self.lp
        #print i
        self.i = p
        
    def __str__(self):
        stmp = ''
        for v in self.lp:
            stmp += '{:8.2f}'.format(v)
        return stmp
        
    
    def __add__(self, P):
        t = logPv(np.ones(len(self.lp)))
        print 'logPv add/t: ', t
        for i,p in enumerate(P):
            t[i] = self[i] + p
        return t
    
    
         

class hmm():
    def __init__(self,nstates):
        if nstates < 2:
            self._error('HMM must have at least 2 states')
        self.N = nstates
        self.Pi = np.zeros(nstates)
        self.Pi[0] = 1.0      # by default always start in state 1
        self.transmat_ = np.zeros((nstates,nstates))
        self.emissionprob_ = np.ones((self.N,NSYMBOLS))* 1/float(NSYMBOLS)  # default Uniform
        self.names = []
        self.typestring = 'hmm_bh'
        for i in range(self.N):
            self.names.append('-noname-')
            
    # Forward algorithm for multiple runouts
    #def forwardM(self, X, lengths):
        #for i, l in enumerate(lengths):
            
            #for st in range(self.N):
                
    # forward algorithm for a single runout
    def forwardS(self, Y): # go through the emissions 
        alpha = self.Pi.copy()   # starting state probs. 
        for y in Y:
            tmpsum = 0.0   
            for st in range(self.N):  # do for each state 
                for prev_st in range(self.N): # sum over previous states 
                    tmpsum += self.transmat_[prev_st,st]*alpha[prev_st] 
                alpha[st] = self.emissionprob_[st,y] * tmpsum
                prev_st = st
        return alpha
            
    # Log-based forward algorithm for a single runout
    def forwardSL(self, Y): 
        alpha = logPv(self.Pi)
        logA =  logPm(self.transmat_)
        logB =  logPm(self.emissionprob_)
        for y in Y:
            tmpsum = logP(0)
            for st in range(self.N):
                for prev_st in range(self.N):
                    a = logA[prev_st,st] 
                    b = alpha[prev_st]
                    tmpsum +=  a * b
                alpha[st] = logB[st,y] * tmpsum
                prev_st = st
        return eexp(alpha)
            
        
    def sample(self,m): 
        states = []
        emissions = []
        # initial starting state
        state, p = self.pick_from_vec(self.Pi)
        states.append(state)
        print 'initial state: ',state
        # main loop
        for i in range(m):
            # generate emission
            em, p = self.pick_from_vec(self.emissionprob_[state,:])
            emissions.append(em)
            # find next state
            state, p = self.pick_from_vec(self.transmat_[state])
            #print 'next state: ', state
            states.append(state)
        
        # generate a final emission
        em, p = self.pick_from_vec(self.emissionprob_[state,:])
        emissions.append(em)
        return (states, emissions)



##########################################################################
#
#   Utility functions
#                
    def vec_normalize(self, v): 
        sum = np.sum(v)
        return v/sum
        
    def pick_from_vec(self,vector):
        if STRICT:
            vector = self.vec_normalize(vector)
            self.row_check(vector,len(vector))
            
        r = random.random()
        P = 0.0
        for i in range(len(vector)):
            P += vector[i]
            if r<=P:
                return (i, vector[i])
        self._error('invalid prob vector')
            
    def check(self):
        sh = np.shape(self.transmat_)
        if (sh[0] != self.N or sh[1] != self.N):
            self.error(' transmat_ wrong size')
        sh = np.shape(self.emissionprob_)
        if (sh[0] != self.N or sh[1] != NSYMBOLS):
            self.error(' emissionprob_ wrong size')
        for r in range(self.N):
            self.row_check(self.transmat_[r],self.N)
        sum = 0.0
        for st in range(self.N):
            self.row_check(self.emissionprob_[st,:],NSYMBOLS)
        self.row_check(self.Pi,self.N)
                
            
    def row_check(self,row,m):
        valid = True
        #print 'row_check:', row
        sum = 0.0
        for c in range(m):
            t = row[c]
            if t > 1.0 or  t < 0.0 :
                print 'illegal probability found'
                valid = False
            sum += t
        if abs(sum-1.0) > epsilon:
            valid = False
        if not valid:
            print row
            print 'Sum: ', sum
            self._error('a vector failed row check: sum != 1.0')
        return True
        
        
    def _error(self,msg):
        print 'hmm class (hmm_bh): ' + msg
        quit()
        
        
        
#################################################################################################
#
#     TESTS
#

if __name__ == '__main__':
    print '\n\n  Testing hmm_bh class...\n\n'
    
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
    for l in z.lp:
        m.append(EE(l))
    m = np.array(m)

    print 'm;',m
    fs = 'logPv  FAIL'
    print 'compare: ', m[0], (e+e*e)
    assert abs(m[0] - (e+e*e)) < epsilon, fs
    assert abs(m[1] - (e+e*e)) < epsilon, fs
    assert abs(m[2] - (e*e*e + 1/e)) < epsilon, fs
    
    print 'logPv() tests            PASS'
    quit()
    
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
    assert isinstance(x[0,0], logP), fs
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
    
    
    ###################################3
    # test pick_from_vec
    
    m = hmm(10)
    vector = [0,0,0,.333,.333,.333, 0,0,0]  # note sum = 0.9990000
    #optional if not STRICT:
    #vector = m.vec_normalize(vector)
    for i in range(10000):  # this really tests sum=1.000000
        x,p = m.pick_from_vec(vector)
        assert (x >1 and  x <= 5), 'failure of test_pic_from_vec'
    print 'test_pic_from_vec() test passed'
        
    ntest =  5
    m = hmm(ntest)
    m.transmat_ = np.array([[.5,.5,0,0,0],[0,.6,.4,0,0],[0,0,.75,.25,0],[0,0,0,0.8,0.2],[0,0,0,0,1.0]])
    for i in range(ntest):
        mu = 3*(i+1)
        for j in range(NSYMBOLS):
            m.emissionprob_[i,j] = 0.0
            if j>mu and j<=(mu+2):
                m.emissionprob_[i,j] = 1/float(2)
                
    #m.emissionprob_[2,120] = 0.001
    
    print 'testing hmm with ', ntest, ' states'
    m.check()
    print 'Model setup tests passed'
        
    st, em = m.sample(20)
    print st
    print em
    assert len(st) == len(em), 'Emissions dont match states from sample()'
    
    print '\n\nTest valid sample outputs:'
    for i,s in enumerate(st):
        #print 'checking: ' , i, s, em[i]
        if m.emissionprob_[s,em[i]] < epsilon:
            m._error('invalid emission detected')
    print 'got valid emissions'
    print 'state estimate: '
    print m.forwardS(em)
    print m.forwardSL(em)
    
        
        
