#!/usr/bin/python
#
#   Utilities for BT-HMM_
#

import numpy as np
import numbers
from random import *
import matplotlib.pyplot as plt
#import editdistance as ed   #pip install editdistance
##from tqdm import tqdm
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
        for i in range(len(Y)):
            for j in range(self.N):
                v[i,j] = np.exp(alpha.m[i,j])
        return v, alpha
            
            
    #  Backward Algorithm
    #
    def backwardSL(self, Y):
        T = len(Y)
        #print Y
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
    #   Viterbi Algorithm
    #     (Rabiner '89 eqns 32a-35)
    
    def Viterbi(self,Obs):
        logA =  logPm(self.transmat_)
        logB =  logPm(self.emissionprob_)
        
        #Initialization             (32a,b)
        T = len(Obs)
        delta = logPm(np.ones((T,self.N)))
        for j in range(self.N):
            delta[0,j] = logP(self.Pi[j]) * logB[j,Obs[0]]
        chi = np.zeros((T,self.N)).astype(int)    # note: NOT a logPx()
            
        #Recursion                   (33)  
        d = logPv(np.zeros(self.N))
        for t in range(1,T):    #emission loop
            for j in range(self.N):   # state loop time t
                for i in range(self.N):   # state loop time t-1
                    d[i] = delta[t-1,i]*logA[i,j]
                #print 'd: ',d
                argmax, lpmax = d.maxlv()
                delta[t,j] = lpmax * logB[j,Obs[t]] 
                chi[t,j] = argmax
                    
        #Termination      
       
        tmp = logPv(np.ones(self.N))
        for i,lpv in enumerate(tmp):
            tmp[i] = delta[T-1,i] 
        qam, pstar = tmp.maxlv()  # most likely terminal state
        qstar = [0]*T
        qstar[T-1] = qam
        
        # State Seq. backtracking        (35)
        for i in range(0,T-2):
            t = T-2-i
            qstar[t] = chi[t+1,qstar[t+1]]
        self.VitVis(Obs,qstar,delta,chi)
        return qstar
     
    # visualize viterbi backtracking for debugging
    def VitVis(self,Obs,qstar,delta,chi):
        lines = []
        for j in range(self.N):
            lj = ''
            for t in range(len(Obs)):
                c = ' '
                if not np.isnan(delta[t,j].lp):
                    c = '.'  # non-zero prob for state j
                if j == qstar[t]:
                    c = '*'  # optimal selection
                    if np.isnan(delta[t,j].lp):
                        c = 'X'  # this shouldn't be 
                lj += c
            lines.append(lj)
        
        print 'State evolution:'
        for j in range(self.N):
            print j, '  ['+lines[j]+']'
        print '\n\n'
        
        
        
    # 
    #  Baum Welch Algorithm
    #
    def fit(self,Obs):
        alpha = self.forwardSL()
        beta  = self.backwardSL()
        T = len(Obs)
        N = self.N
        xi = logPm(np.zeros((T,N,N)))       #    (37)
        for i in range(N):
            for j in range(N):
                s1 += alpha[t-1,i]*self.transma_[i,j]*self.emissionprob_[j,t]*beta[t,j]
        for t in range(1,T):
            for i in range(N):
                for j in range(N):                
                    xi[t,i,j] = alpha[t-1,i]*self.transma_[i,j]*self.emissionprob_[j,t]*beta[t,j]
        gam = logPm(np.zeros((T,N)))     #       (38)
        for t in range(T):
            for j in range(N):
                gam[t,j] +=xi[t,i,j]
        
        gam_v = logPv(np.zeros((N)))      #       (39a)
        for i in range(N):
            for t in range(T-2):
                gam_v[i] += gam[t,i] 

        xi_m = logPm(np.zeros((N,N)))     #       (39b)
        for i in range(N):
            for j in range(N):
                for t in range(T-2):
                    xi_m[i,j] += xi[t,i,j]
                    
        a_hat = logPm(np.zeros((N,N)))   #       (40b)
        for i in range(N):
            for j in range(N):
                a_hat[i,j] = xi_m[i,j]/gam_v[i]
                
        b_hat = logPm(np.zeros((N,NSYMBOLS)))  #   (40c)
        for k in range(NSYMBOLS):
            for j in range(N):
                sum = logP( 0.0 )
                num = logP( 0.0 )
                for t in range(T):
                    if Obs[t] == k:
                        num+=gam[t,j]
                    sum += gam[t,j]
                b_hat[j,k] = num/sum
                
        print '-------------  Ahat  --------------'
        print a_hat
    
                
        
            
    
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
    
    def sample(self,T): 
        states = []
        emissions = []
        # initial starting state
        state, p = self.pick_from_vec(self.Pi)
        states.append(state)
        print 'initial state: ',state
        # main loop
        for i in range(T-1):
            # generate emission
            em, p = self.pick_from_vec(self.emissionprob_[state,:])
            emissions.append(em)
            # find next state
            state, p = self.pick_from_vec(self.transmat_[state,:])
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
#     TESTS of hmm_log class
#

if __name__ == '__main__':
         
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
    
    nsim_samples = 15
    nsim_rollouts = 1
    
    for r in range(10):
        A10[r,r] = pv[r]
        if(r+1 < 10):
            A10[r,r+1] = 1.0-A10[r,r]
                    
    for ntest in [5]:
        fs =  '\n\ntesting hmm with ' + str(ntest) + ' states'
        print fs
        m = hmm(ntest)
        if ntest == 5:
            m.transmat_ = A5
        else:
            m.transmat_ = A10
        
        w = 6
        for i in range(m.N):
            mu = 0.5*w*(i+1)
            for j in range(NSYMBOLS):
                m.emissionprob_[i,j] = 0.0
                if j>mu-w/2 and j<=(mu+w/2):
                    m.emissionprob_[i,j] = 1/float(w)
        #print m.emissionprob_
        #if ntest == 10:
            #quit()
                 
        m.check()
        print fs + ' [setup] ' + PASS
        
        ##############################################################
        #
        #    Simulate the HMM
        #
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
        print m.backwardSL(em)
     
        print '\n\n Test Viterbi Algorithm:'
        print 'st:',st
        print 'em:',em
        #print m.emissionprob_
        stseq =  [0, 0, 1, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4]
        em = [6, 3, 6, 6, 8, 12, 14, 10, 15, 14, 14, 15, 12, 13, 16]
        
        est_correct = [0,0,1,1,2,3,3,3,3,3,3,3,3,4,4]
        
        assert len(em) == len(est_correct), 'test setup problem'
        qs = m.Viterbi(em)
        fs = 'Vitermi state estimation tests'
        for i,q in enumerate(qs):
            assert q==est_correct[i], fs+FAIL
        print fs+PASS
            
        #
        #   Let's try the Baum Welch!
        #
        m.fit(em)
            
