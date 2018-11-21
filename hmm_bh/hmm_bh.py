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

epsilon = 1.0E-4


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
        alphaL = np.log(self.Pi.copy())   # starting state probs. 
        for y in Y:
            tmpsum = 0.0   
            for st in range(self.N):  # do for each state 
                for prev_st in range(self.N): # sum over previous states 
                    tmpsum += self.transmat_[prev_st,st]*alpha[prev_st] 
                alpha[st] = self.emissionprob_[st,y] * tmpsum
                prev_st = st
        return alpha
            
        
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
    
        
        
