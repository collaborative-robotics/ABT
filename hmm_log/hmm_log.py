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

from logP import *

#sudo pip install scikit-learn  # dep for hmmlearn
#pip install -U --user hmmlearn
#from hmmlearn import hmm
import random as random
NSYMBOLS = 40
STRICT = True

LZ = np.nan   # our log of zero value

epsilon = 1.0E-4
FAIL = '          FAIL'
PASS = '          PASS'

###########   replace with import logP.py

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
        #alpha = logPv(self.Pi) * logPv(self.emissionprob_[:,Y[0]].T)  # starting state probs.
        #print 'forwardS: lenY:', len(Y)
        alpha = np.ones((len(Y),self.N))
        for i in range(self.N):
            alpha[0,i] = self.Pi[i] * self.emissionprob_[i, Y[0]]
            
        ai = 1
        for jj,y in enumerate( Y[1:]):
            #print '    iter, ai:', jj,ai
            tmpsum = 0.0   
            for st in range(self.N):  # do for each state 
                for prev_st in range(self.N): # sum over previous states 
                    tmpsum += self.transmat_[prev_st,st]*alpha[ai-1,prev_st] 
                alpha[ai,st] = self.emissionprob_[st,y] * tmpsum
                prev_st = st
            ai += 1
        return alpha 
            
    # Log-based forward algorithm for a single runout
    def forwardSL(self, Y, alpha=None): 
        #'''       Y = all observations concatenated
                #alpha = starting LOG probability of each state
        #'''
        #alpha = logPv(self.Pi)
        if alpha is None:
            alpha = logPm(np.ones((len(Y), self.N)))
            for j in range(self.N):
                alpha[0,j] = logP(self.Pi[j]) * logP(self.emissionprob_[j,Y[0]])
                                                  
        #print 'forwardSL debug:'
        #print '  alpha', alpha
        logA =  logPm(self.transmat_)
        logB =  logPm(self.emissionprob_)
        ai = 1
        for y in Y[1:]:  # emission sequence
            tmpsum = logP(0)
            for st in range(self.N):
                for prev_st in range(self.N):
                    a = logA[prev_st,st] 
                    b = alpha[ai-1,prev_st]
                    #print 'a: ', np.shape(a), type(a), a.lp
                    #print 'b: ', np.shape(b), type(b), b
                    tmpsum +=  a * b
                    #print 'tmpsum: ',tmpsum.lp
                c = logB[st,y] 
                #print 'c: ', np.shape(c), type(c), c
                alpha[ai,st] = c * tmpsum
                prev_st = st
            ai += 1 
        v = np.ones((len(Y),self.N))
        if i in range(len(Y)):
            for j in range(self.N):
                v[i,j] = np.exp(alpha.m[i,j])
        return v, alpha
            
            
    #  Backward Algorithm
    #
    def backwardSL(self, Y):
        T = len(Y)
        print Y
        logA =  logPm(self.transmat_)
        logB =  logPm(self.emissionprob_)
        beta = logPv(np.ones(self.N))
        print len(Y)
        for k in range(1,T):
            t = T-k-1
            print 't: ', t, Y[t]
            for i in range(self.N):
                b = logP(0)
                for j in range(self.N):
                    a1 = logA[i,j] 
                    a2 = logB[j,Y[t+1]]
                    a3 = beta[j]
                    b += logA[i,j]*logB[j,Y[t+1]]*beta[j]
                beta[i] = b
            print beta    
        return beta
            
    # 
    #  gamma term
    #
    #def gamma(alpha, beta)
    
    
    # Log-based forward algorithm for multiple runouts
    '''
    
     !!!  not reallly a useful computation  !!!
       #Y = all observations concatenated
       #L = list of runout lengths.
       
       #returns:  v = vector of probabilities for each state 
                 #alpha = vector of log probabilities for each state
    '''
    def forwardNSL(self, Y,L):
        i = 0 
        alpha = logPv(self.Pi) * logPv(self.emissionprob_[:,Y[0]])
        for l in L:
            y = Y[i:i+l]
            v, alpha = self.forwardSL(y,alpha)  #  update alpha from each sequence
            i = i+l+1 
        return v,alpha
    
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
        print 'model check:'
        sh = np.shape(self.transmat_)
        if (sh[0] != self.N or sh[1] != self.N):
            self.error(' transmat_ wrong size')
        sh = np.shape(self.emissionprob_)
        if (sh[0] != self.N or sh[1] != NSYMBOLS):
            self.error(' emissionprob_ wrong size')
        for r in range(self.N):
            self.row_check(self.transmat_[r],self.N)
        sum = 0.0
        print 'got here'
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
#################################################################################################
#################################################################################################
#
#     TESTS
#

if __name__ == '__main__':
    print '\n\n  Testing hmm_bh class...\n\n'
    
    #####################################
    # test basic log functions
    e = np.exp(1)
    m = logP(e)
    
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
    assert x.lp == np.log(0.25), 'logP() returns wrong value'
    print x
    #assert str(x) == '0.25', 'FAIL'
    
    #################################
    #
    #  test addition for logP() scalar
    #
    z = x + y
    assert isinstance(z,logP), 'logP() __add__ returns wrong type'
    
    logsum = np.log(0.25 + 0.25)
    
    fs = 'logP() __add__    FAIL'
    assert abs(z.lp-logsum) < epsilon, fs
    assert abs((x+y).lp-logsum) < epsilon, fs
    
    print 'logP classes          PASS'
     
    ####################################################################
    #
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
    
    fs = 'logPv() instantiation'
    assert abs(y.v[0].lp -  2.0) < epsilon, fs + FAIL
    assert abs(y.v[1].lp -  1.0) < epsilon, fs + FAIL
    assert abs(y.v[2].lp - -1.0) < epsilon, fs + FAIL
    print fs + PASS
    
    ############# 
    #  test addition of logP() vectors
    #
    z = x + y
    assert isinstance(z[0],logP), 'logPv() __add__ returns wrong type'
    print 'Z;', z, type(z)
    print '' 
    
    assert z.v[0].lp != 0, 'addition fail'
    
    v = np.ones(3)
    for i,x in enumerate(z.v):
        v[i] = np.exp(x.lp)
        
    print 'v; ', v
    
    #m = EEv(v)  # let's exponentiate sums and check them
    m = v
    print 'm;',m
    fs = 'logPv  addition' 
    print z[0].lp, np.log(e+e*e)
    assert abs(z.v[0].lp - np.log(e+e*e)) < epsilon, fs + FAIL
    assert abs(z.v[1].lp - np.log(e+e*e)) < epsilon, fs + FAIL
    assert abs(z.v[2].lp - np.log(e*e*e + 1/e)) < epsilon, fs + FAIL
    print fs + PASS
    
    print fs + PASS
    
   
    fs = 'logPv() vector * vector multiply'
    
    x = logPv([e, e*e, e*e*e])
    y = logPv([e*e, e, 1/e])
    
    t = x*y
    print t, type(t)
    assert t.v[0].lp == 3.0, fs + FAIL
    assert t.v[1].lp == 3.0, fs + FAIL
    assert t.v[2].lp == 2.0, fs + FAIL
    
    
    print 'logPv() tests            PASS'    
    
    
    #######################################
    #
    #   test logPm  - matrix version
    #
     #  logP for matrices 
    x = logPm(np.array([
        [e, e*e, e*e*e],
        [e, e*e, e*e*e],
        [e, e*e, e*e*e]  ]))
    y = logPm(np.array([
        [e*e, e, 1/e],
        [e*e, e, 1/e],
        [e*e, e, 1/e]  ]))
    
    fs = 'logPm return type'
    print fs, ':',type(x[0,0])
    assert isinstance(x[0,0], logP), fs + FAIL
    assert isinstance(y[2,1], logP), fs + FAIL
    print fs+PASS
    
    print '---'
    print x
    print y
    print '----'
    
    fs = 'logPm() instantiation'
    print '>>', y[1,0].lp, 2.0
    assert abs(y[1,0].lp - 2.0) < epsilon, fs + FAIL
    
    print '>>', y[2,1].lp, 0.0
    assert abs(y[2,1].lp - 1.0) < epsilon, fs + FAIL
    assert abs(y[1,2].lp - -1.0) < epsilon, fs + FAIL
    
    print fs + PASS
    
    
    z = x + y
    print 'Z;',z 
    print ''
    
    assert isinstance(z,logPm), ' logPm() __add__ returns wrong type'
    m = np.ones(3)
    r = 0
    for c in range(3):
        m[c] = z[r,c].lp  # first row of z
    
    print 'm;',m
    fs = 'logPm  addition '
    print m[0], logP(e+e*e).lp
    assert abs(m[0] - np.log(e+e*e)) < epsilon, fs + FAIL
    assert abs(m[1] - np.log(e+e*e)) < epsilon, fs + FAIL
    assert abs(m[2] - np.log(e*e*e + 1/e)) < epsilon, fs + FAIL
    
    print fs + PASS    
    
    
    print '\n\n      All LogPx() tests     PASSED \n\n'
    
    
    
    #########################################################################
    #########################################################################
    
    ###################################
    # hmm class tests 
    
    # test pic_from_vect(v)
    m = hmm(10)
    vector = [0,0,0,.333,.333,.333, 0,0,0]  # note sum = 0.9990000
    #optional if not STRICT:
    #vector = m.vec_normalize(vector)
    fs = 'test pic_from_vec'
    for i in range(10000):  # this really tests sum=1.000000
        x,p = m.pick_from_vec(vector)
        assert (x >1 and  x <= 5), fs+FAIL
    print fs+PASS
        
    
    ######################################
    #
    #  test model setups for hmm
    #
    
    A5 = np.array([[.5,.5,0,0,0],[0,.6,.4,0,0],[0,0,.75,.25,0],[0,0,0,0.8,0.2],[0,0,0,0,1.0]])
    pv = [0.5, 0.5, 0.7, 0.65, 0.8, 0.5, 0.3,0.6,0.7, 1.0]
    
    A10 = np.zeros((10,10))
    
    nsim_samples = 14
    nsim_rollouts = 1
    
    for r in range(10):
        A10[r,r] = pv[r]
        if(r+1 < 10):
            A10[r,r+1] = 1.0-A10[r,r]
                    
    for ntest in [5,10]:
        fs =  '\n\ntesting hmm with ' + str(ntest) + ' states'
        print fs
        m = hmm(ntest)
        if ntest == 5:
            m.transmat_ = A5
        else:
            m.transmat_ = A10
        
        w = 6
        for i in range(ntest):
            mu = 0.5*w*(i+1)
            for j in range(NSYMBOLS):
                m.emissionprob_[i,j] = 0.0
                if j>mu-w/2 and j<=(mu+w/2):
                    m.emissionprob_[i,j] = 1/float(w)
        #print m.emissionprob_
        #if ntest == 10:
            #quit()
        
        for i in range(ntest):
            sum = 0.0
            for j in range(NSYMBOLS):
                sum += m.emissionprob_[i,j]
            
        #m.emissionprob_[2,120] = 0.001
        
        m.check()
        print fs + ' [setup] ' + PASS
            
        st, em = m.sample(nsim_samples)
        print '----------- state sequence & emissions -----------------------'
        print st
        print em
        assert len(st) == len(em), 'Emissions dont match states from sample()'
        
        print '\n\nTest valid sample outputs:'
        for i,s in enumerate(st):
            #print 'checking: ' , i, s, em[i]
            if m.emissionprob_[s,em[i]] < epsilon:
                m._error('invalid emission detected')
        print 'got valid emissions'
        
        print '\nForward Algorithm:'

        print 'state estimate: '
        print '       forwardS()   (regular math)'
        print m.forwardS(em)
        print '       forwardSL()  (log math)'
        print '         (v-matrix)'
        print m.forwardSL(em)[0]
        
        print '\nBackward Algorithm:'
        #print m.backwardSL(em)
     
