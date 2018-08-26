#!/usr/bin/python
#
#
#   Revised to match fig BT-01164_Huge.png
#     from BT-Hmm proposal   May 18


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
from  model01 import *


def ABTtree():
####################################################################################
##
#                    ABT for Peg-In-Hole Task
#
#
#   Returns an ABT for the task to be modeled
#
    demo_bt = b3.BehaviorTree()

    LeafDebug   = False
    SolverDebug = False

    #print outputs
    #quit()

    leafs = []


    ########  Step 1  Position Left Grasper over block

    l1 = aug_leaf(1.0)
    l1.Name = 'l1'
    leafs.append(l1)

    ########  Step 2 Insert and Grasp block

    # try 1
    l2a1 = aug_leaf(0.9)
    l2a1.Name = 'l2a1'
    leafs.append(l2a1)

    l2b1 = aug_leaf(0.95)
    l2b1.Name = 'l2b1'
    leafs.append(l2b1)

    node_21 = b3.Sequence([l2a1,l2b1])
    node_21.Name = 'Node 21'

    # try 2
    l2a2 = aug_leaf(0.9)
    l2a2.Name = 'l2a2'
    leafs.append(l2a2)

    l2b2 = aug_leaf(0.95)
    l2b2.Name = 'l2b2'
    leafs.append(l2b2)

    node_22 = b3.Sequence([l2a2,l2b2])
    node_22.Name = 'Node 22'

    node_2 = b3.Priority([node_21,node_22])
    node_2.Name = 'Node 2'


    ##########  Steps 3-5  Lift clear / reorient / move

    l345 = aug_leaf(1.0)
    l345.Name = 'l345'
    leafs.append(l345)

    ##########  Step 6 Insert Right grasper / grasp

    # try 1
    l6a1 = aug_leaf(0.6)
    l6a1.Name = 'l6a1'
    leafs.append(l6a1)

    l6b1 = aug_leaf(0.75)
    l6b1.Name = 'l6b1'
    leafs.append(l6b1)

    # try 2
    l6a2 = aug_leaf(0.6)
    l6a2.Name = 'l6a2'
    leafs.append(l6a2)

    l6b2 = aug_leaf(0.75)
    l6b2.Name = 'l6b2'
    leafs.append(l6b2)

    node_61 = b3.Sequence([l6a1,l6b1])
    node_62 = b3.Sequence([l6a2,l6b2])
    node_6  = b3.Priority([node_61,node_62])
    node_6.Name = "node 6"

    ########  Steps 7-9   Release Left / Reorient / Position

    l789 = aug_leaf(1.0)
    l789.Name = 'l789'
    leafs.append(l789)

    ########  Step 10     Place on peg / Release / Clear

    l10a1 = aug_leaf(0.9)
    l10a1.Name = 'l10a1'
    leafs.append(l10a1)

    l10b1 = aug_leaf(0.95)
    l10b1.Name = 'l10b1'
    leafs.append(l10b1)

    l10c1 = aug_leaf(0.8)
    l10c1.Name = 'l10c1'
    leafs.append(l10c1)

    node_10 = b3.Sequence([l10a1,l10b1,l10c1])
    node_10.Name = 'Node 10: Position/Release'

    ######  Top level sequence node
    N1 = b3.Sequence([l1, node_2, l345, node_6, l789, node_10])
    N1.Name = 'Sequencer Node'
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
    demo_bt.HMM_create()

    # set up leaf probabilities
    for l in leafs:
        # output observeation mu, sigma
        #print 'Setting Pobs for {:s} to ({:.2f},{:.2f})'.format(l.Name,outputs[l.Name],sig)
        l.set_Obs_Density(outputs[l.Name],sig)
        # set up the Ps
        #print 'setting PS for:', l.Name, PS[statenos[l.Name]]
        l.set_Ps(PS[statenos[l.Name]])
        #print ''

    return [demo_bt, bb]
