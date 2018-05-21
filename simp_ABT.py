#!/usr/bin/python
# 
#
#  A simple BT for testing
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

from abtclass import *
# BT and HMM parameters here
#from  model01 import *
from model00 import *


def simple4leafABT():
####################################################################################
##
#                    ABT for a little 4-leaf BT
# 
#
#   Returns an ABT for the task to be modeled
#
    demo_bt = b3.BehaviorTree()

    LeafDebug   = False
    SolverDebug = False

    if not os.path.isdir(logdir):  # if this doesn't exist, create it.
        os.mkdir(logdir) 
        

    #print outputs
    #quit()
    
    leafs = []
    

    ########  Leaf 1
        
    l1 = aug_leaf(0.75) 
    l1.Name = 'l1'
    leafs.append(l1)

    ########  Leaf 2 
        
    l2 = aug_leaf(0.75) 
    l2.Name = 'l2'
    leafs.append(l2)
    
    ########  Leaf 3 
        
    l3 = aug_leaf(0.75) 
    l3.Name = 'l3'
    leafs.append(l3)
    
    ########  Leaf 4 
        
    l4 = aug_leaf(0.75) 
    l4.Name = 'l4'
    leafs.append(l4)
 
    ########     Second Level 
    
    l12 = b3.Sequence([l1,l2]) 
    l12.Name = 'Node 12' 

    l34 = b3.Priority([l3,l4])
    l34.Name = 'Node 2'

 

    ######  Top level sequence node
    N1 = b3.Sequence([l12,l34])
    N1.Name = 'top level'
    N1.BHdebug = F
    
    # make fake leafs for OutS and OutF
    
    OS = aug_leaf(1.0)
    OS.Name = 'OutS'
    leafs.append(OS)
    
    OF = aug_leaf(1.0)
    OF.Name = 'OutF'
    leafs.append(OF)
    
    demo_bt.root = N1

    bb = b3.Blackboard()

    ##################################################################################################
    ##  Set leaf params 

    
    # set up leaf probabilities
    for l in leafs:
        # output observeation mu, sigma
        print 'Setting Pobs for {:s} to ({:.2f},{:.2f})'.format(l.Name,outputs[l.Name],sig)
        l.set_Obs_Density(outputs[l.Name],sig)
        # set up the Ps
        print 'setting PS for:', l.Name, PS[statenos[l.Name]]
        l.set_Ps(PS[statenos[l.Name]])
        print ''

    return [demo_bt, bb]


    