#!/usr/bin/python
#
#   Utilities for BT-HMM_
#

import numpy as np
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
    if x < 0.0:
        print 'log arg < 0.0 - stopping'
        quit()
    if (x == 0):
        y = LZ
    else:
        y = np.log(x)
    return y
#  extended exp()
def EE(x):
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

#  BH idea:
#    (overload * and + )!!
class logP():
    def __init__(self,p):
        self.lp = ELv(p)
        self.shape = np.shape(p)
        
    def P(self):
        return EEv(self.lp)
    
    def __getitem__(self,r,c=0):
        if len(self.shape) == 2:
            return self.lp[r,c]
        elif len(self.shape) == 1:
            return self.lp[r]
    
    def __mul__(self, lp2):
        if self.lp == LZ or lp2.lp == LZ:
            return LZ
        else:
            return self.lp + lp2.lp
    
    def __add__(self, lp2):
        if self.lp==LZ or lp2.lp == LZ:
            if self.lp == LZ:
                return lp2.lp
            else:
                return self.lp
        else:
            if self.lp > lp2.lp:
                return self.lp + ELv(1+np.exp(lp2.lp-self.lp))
            else:
                return  lp2.lp + ELv(1+np.exp(self.lp-lp2.lp))
        

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
        alpha = logP(self.Pi)
        logA = logP(self.transmat_)
        logB = logP(self.emissionprob_)
        for y in Y:
            tmpsum = logP(LZ)
            for st in range(self.N):
                for prev_st in range(self.N):
                    tmpsum += logA[prev_st,st] * alpha[prev_st]
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
    #print y
    fs = ' elog() test FAIL'
    assert y[0] - 1.0 < epsilon, fs
    assert y[1] - 2.0 < epsilon, fs
    assert np.isnan(y[2]), fs
    assert y[3] - 0.5 < epsilon, fs
    assert ELv(e*e)-2.0 < epsilon, fs
    print ' elog() tests    PASSED'
    
    # eexp()
    fs = ' eexp() test  FAIL'
    assert  EEv(1)-e < epsilon, fs
    y = EEv([2, 0, LZ, -1])
    print y
    assert y[0]-e*e < epsilon, fs
    assert y[1]-1.0 < epsilon, fs
    assert y[2]-0.0 < epsilon, fs
    assert y[3]-1/e < epsilon, fs

    assert EEv(1) - e < epsilon, fs
    
    y = EEv([[e, 0],[LZ, 1]])
    assert y[1,1]-e < epsilon, fs
    print ' eexp() tests    PASSED'

    ###################################
    # test logP class and operator overlays
    x = logP(0.5)
    y = logP(0.5)
    z = x + y
    fs = 'logP() class tests    FAIL'
    assert x+y-1.0 < epsilon, fs
    x = logP([0.1, 0.2, 0.3])
    y = logP([0.9, 0.8, 0.7])
    z = x + y
    
    print EEv(z)
    

    quit()
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
    
        
        
