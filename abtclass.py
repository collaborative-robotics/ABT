#!/usr/bin/python
# 
#      Augmented BT Class
#
#

import os as os

# b3 class modified by BH, local version in current dir
import b3 as b3          # behavior trees
import random as random
import math as m
import numpy as np

global NSYMBOLS  
NSYMBOLS = 150 # number of VQ symbols for observations

global NEpochs 


# BT and HMM parameters here
from  model00 import *

def gaussian(x, mu, sig):
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
        for j in range(NSYMBOLS):
            self.Obs[j] += gaussian(j+0.5,mu,sig)
            psum += self.Obs[j]
            #print "j/Obs:",j,self.Obs[j]
        #normalize the Observation density so it sums to 1.000
        for j in range(NSYMBOLS):
            self.Obs[j] /= psum
            
        #print self.Name, 'obs:', mu, sig
        
        
    # initialize Success Prob for leaf    
    def set_Ps(self, P):
        self.pS = P
        self.pF = 1.0-P
        
    def gen_obs(self):
        a = random.uniform(0,1.0)
        b = 0.0
        for j in range(NSYMBOLS):
            b += self.Obs[j]
            #print "Obs: b,a", b,a
            if b >= a:
                return j;
        return j
    
    def tick(self,tick):
        f = tick.blackboard.get('logfileptr')
        a = random.uniform(0,1.0)
        f.write(self.Name+', '+str(self.gen_obs())+'\n')
        if a<self.pS:
            return b3.SUCCESS 
        else:
            return b3.FAILURE  
        
        

