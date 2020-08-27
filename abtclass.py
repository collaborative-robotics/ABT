#!/usr/bin/python
#
#      Augmented BT Class
#
#

import os as os

# b3 class modified by BH, local version in current dir
import b3 as b3          # behavior trees
#import random as random
import math as m
import numpy as np
from abt_constants import *
 

checkepsilon = 1.0e-9

class model():
    def __init__(self, Nstates):
        self.n = Nstates
        self.A = np.zeros([Nstates,Nstates])
        self.PS = np.zeros(Nstates)     # prob of success
        self.B = np.zeros( (Nstates, NSYMBOLS) )   # discrete symbol emission probs. 
        self.names = []
        self.Pi = np.zeros(Nstates)
        self.Pi[0] = 1.0  # always start at first state
        self.statenos = {}   # indeces corresponding to state names
        self.sigma = 2.0     # standard deviation of observation symbols
        self.outputs = {}    # mean value for each state name (dict) 

    def setup_means(self,first, Ratio, sig):
        ''' *means* here means mean value of output symbol for each state 
        ''' 
        assert len(self.names) > 0, 'Names have to be set up first'
        assert len(self.names) == self.n, 'Wrong number of states'
        i = first
        di = Ratio*sig  # 
        for n in self.names:
            self.outputs[n] = i    # outputs[] = mean output for each state
            i += di
            
    # validate model setup
    def check(self):
        assert len(self.names) == self.n, 'Wrong number of states'
        #print self.A   # helps when debugging failures below
        for i in range(self.n-2):   # go through the leaf-states
            assert abs(sum(self.A[i,:]) - 1.0000) < checkepsilon, 'Rows of A-matrix must sum to 1.0: row: '+str(i)
            for j in range(self.n):   # all transitions
                assert abs (self.A[i,j] - 1.00) > checkepsilon, 'Success probs must be < 1.0: A['+str(i)+','+str(j)+']=' + str(self.A[i,j])
        i = self.n - 2
        assert abs(self.A[i,i] - 1.00)        < checkepsilon, 'State Os must have 1.0 self state prob'
        assert abs(sum(self.A[i,:]) - 1.00)   < checkepsilon, 'Row N-2 must sum to 1.0000'
        assert abs(self.A[i+1,i+1] - 1.00)    < checkepsilon, 'State Of must have 1.0 self state prob'
        assert abs(sum(self.A[i+1,:]) - 1.00) < checkepsilon, 'Row N-1 must sum to 1.0000'
        print 'abtclass.py: abt/hmm model parameters passed self.check() assertions'

def gaussian(x, mu, sig):
    sig = abs(sig)
    a = 1.0/(sig*(m.sqrt(2*m.pi))) * m.exp(-0.5*((x-mu)/sig)**2)
    #print "A gaussian: ", a
    return a

class aug_leaf(b3.Action):
    def __init__(self):
        b3.BaseNode.__init__(self)
        # Transition Probabilities for this leaf
        self.pS = 0.9  #default value
        self.pF = 1.0-self.pS
        #  Observation Densities for this leaf
        self.Obs = np.zeros(NSYMBOLS)
        # give a residual obs prob:
        for j in range(NSYMBOLS):
            self.Obs[j] = checkepsilon*2  # a nominal non-zero value

    def __init__(self,probSuccess):
        b3.BaseNode.__init__(self)
        # Transition Probabilities for this leaf
        self.pS = probSuccess
        self.pF = 1.0-self.pS
        #  Observation Densities for this leaf
        self.Obs = np.zeros(NSYMBOLS)
        # give a residual obs prob:
        for j in range(NSYMBOLS):
            self.Obs[j] = 2*checkepsilon  # a nominal non-zero value

    def set_Obs_Density(self, mu, sig):
        if (mu+sig) > NSYMBOLS or ((mu-sig) < 0):
            print 'aug_leaf: Warning may gen negative/overrange observations'
            print self.Name, mu, sig
            #quit()
        psum = 0.0
        pmin = checkepsilon # smallest allowed probability (see test_obs_stats.py!!)
        for j in range(NSYMBOLS):
            self.Obs[j] = gaussian(float(j),float(mu),float(sig))
            #clear the tiny numerical values
            if self.Obs[j] < pmin:
                self.Obs[j] = pmin   ###   require B[i,j] >= pmin
            psum += self.Obs[j]

        #normalize the Observation distrib so it sums to 1.000
        for j in range(NSYMBOLS):
            self.Obs[j] /= psum
            
    # initialize Success Prob for leaf    
    def set_Ps(self, P):
        assert P >= 0 and P <= 1.0, 'Invalid Success Probability'
        self.pS = P
        self.pF = 1.0-P

    def gen_obs(self):  # populate the observation probs over discrete observations for this leaf
        a = np.random.uniform(0,0.999)
        b = 0.0
        for j in range(NSYMBOLS): # accumulate discrete probs over the symbols
            b += self.Obs[j]
            ##print "Obs: b,a", b,a
            #if self.Name == 'l6b2':
                #print 'a,b,j: ', a,b,j
            if b >= a:
                #if self.Name == 'l6b2' and j > 100:
                    #print self.Name, 'gen_obs: a,b,j:', a,b,j
                return j;   # j is the symbol number / observation
        #print 'gen_obs: a,b,j:', a,b,j
        return j

    def tick(self,tick):
        f = tick.blackboard.get('logfileptr')   # this output is for the HMM analysis (not testing)
        f.write(self.Name+', '+str(self.gen_obs())+'\n')  # this output is for the HMM analysis (not testing)
        a = np.random.uniform(0,0.99999)
        if a<self.pS:
            return b3.SUCCESS
        else:
            return b3.FAILURE

    def HMM_build(self,matrix):
        matrix[self.description,self.suc] = self.pS
        matrix[self.description,self.fail] = self.pF
        return matrix
