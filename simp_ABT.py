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
import abt_constants

global NEpochs

from abtclass import *

# BT and HMM parameters here
from abt_constants import *

from model02 import *

leafs = []

def ABTtree():
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



    ########  Leaf 1

    l1 = aug_leaf(0.75)  # placeholder Ps value of 0.75
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

    node_12 = b3.Sequence([l1,l2])
    node_12.Name = 'Node 12'

    node_34 = b3.Priority([l3,l4])
    node_34.Name = 'Node 2'



    ######  Top level sequence node
    node_root = b3.Sequence([node_12,node_34])
    node_root.Name = 'top level'
    node_root.BHdebug = F

    # make fake leafs for OutS and OutF

    OS = aug_leaf(1.0)
    OS.Name = 'OutS'
    leafs.append(OS)

    OF = aug_leaf(1.0)
    OF.Name = 'OutF'
    leafs.append(OF)

    demo_bt.root = node_root

    bb = b3.Blackboard()

    ##############################################################ABTtree()####################################
    ##  Set leaf params
    demo_bt.HMM_create()

    # set up leaf probabilities
    for l in leafs:
        # output observeation mu, sigma
        l.set_Obs_Density(outputs[l.Name],sig)
        # set up the Ps
        l.set_Ps(PS[statenos[l.Name]])
        #print ''

    return [demo_bt, bb]
ABTtree()
