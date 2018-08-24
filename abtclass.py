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
 
global NEpochs 

# BT and HMM parameters here
from  model00 import *

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
            self.Obs[j] = 0.0001  # a nominal non-zero value
            
    def __init__(self,probSuccess):
        b3.BaseNode.__init__(self)
        # Transition Probabilities for this leaf
        self.pS = probSuccess
        self.pF = 1.0-self.pS
        #  Observation Densities for this leaf
        self.Obs = np.zeros(NSYMBOLS)
        # give a residual obs prob:
        for j in range(NSYMBOLS):
            self.Obs[j] = 0.0001  # a nominal non-zero value
        
    def set_Obs_Density(self, mu, sig):
        if (mu+sig) > NSYMBOLS or ((mu-sig) < 0):
            print 'aug_leaf: Warning may gen negative observations'
            #quit()
        psum = 0.0
        pmin = 0.0001 # smallest allowed probability
        for j in range(NSYMBOLS):
            self.Obs[j] = gaussian(float(j),float(mu),float(sig))
            #clear the tiny numerical values 
            if self.Obs[j] < pmin:
                self.Obs[j] = 0.0
            psum += self.Obs[j]
            
        #normalize the Observation distrib so it sums to 1.000
        for j in range(NSYMBOLS):
            self.Obs[j] /= psum
        
        
    # initialize Success Prob for leaf    
    def set_Ps(self, P):
        assert P >= 0 and P <= 1.0, 'Invalid Success Probability'
        self.pS = P
        self.pF = 1.0-P
        
    def gen_obs(self):
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
        a = np.random.uniform(0,0.99999)
        f.write(self.Name+', '+str(self.gen_obs())+'\n')  # this output is for the HMM analysis (not testing)
        if a<self.pS:
            return b3.SUCCESS 
        else:
            return b3.FAILURE  
        
        

