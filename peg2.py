#!/usr/bin/python
# 
#
#   Revised to match fig BT-01164_Huge.png
#     from BT-Hmm proposal   May 18



# modified by BH, local version in current dir
import os as os
import b3 as b3          # behavior trees
import random as random
import math as m
import numpy as np
 
# BT and HMM parameters here
from  model01 import *

####################################################################################
##
#                         Demo of ABT for Peg-In-Hole Task
# 
#
demo_bt = b3.BehaviorTree()

LeafDebug = False
SolverDebug = False
       
if not os.path.isdir(logdir):  # if this doesn't exist, create it.
    os.mkdir(logdir) 
    

def gaussian(x, mu, sig):
    a = 1.0/(sig*(m.sqrt(2*m.pi))) * m.exp(-0.5*((x-mu)/sig)**2)
    #print "A gaussian: ", a
    return a

class aug_leaf(b3.Action): 
    def __init__(self,probSuccess):
        b3.BaseNode.__init__(self)
        # Transition Probabilities for this leaf
        self.pS = probSuccess
        self.pF = 1.0-self.pS
        #  Observation Densities for this leaf
        self.Obs = np.zeros(NSYMBOLS)
        
    def set_Ps(self, P):
        self.pS = P
        self.pF = 1.0-P
        
    def set_Obs_Density(self, mu, sig):
        if (mu+3*sig) > NSYMBOLS or ((mu-3*sig) < 0):
            print 'aug_leaf: Warning may gen negative observations'
            #quit()
        for j in range(NSYMBOLS):
            self.Obs[j] = gaussian(j,mu,sig)
            #print "j/Obs:",j,self.Obs[j]
        #print self.Name, 'obs:', mu, sig
        
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
        #print "random: ",a , "   Ps: ", self.pS
        observation = self.gen_obs()
        #print "------------------------------------> obs: ", observation
        f.write(self.Name+', '+str(observation)+'\n')
        if a<self.pS:
            return b3.SUCCESS 
        else:
            return b3.FAILURE 
print"\n\n"


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

l21 = b3.Sequence([l2a1,l2b1]) 

# try 2
l2a2 = aug_leaf(0.9)
l2a2.Name = 'l2a2' 
leafs.append(l2a2)

l2b2 = aug_leaf(0.95)
l2b2.Name = 'l2b2' 
leafs.append(l2b2)

l22 = b3.Sequence([l2a2,l2b2])
l22.Name = 'Node 2' 

l2 = b3.Priority([l21,l22])


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

l61 = b3.Sequence([l6a1,l6b1])
l62 = b3.Sequence([l6a2,l6b2])
l6  = b3.Priority([l61,l62]) 
l6.Name = "node 6"

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

l10 = b3.Sequence([l10a1,l10b1,l10c1])
l10.Name = 'Node 10: Position/Release'

######  Top level sequence node
N1 = b3.Sequence([l1, l2, l345, l6, l789, l10])
N1.Name = 'Sequencer Node'
N1.BHdebug = F
bb = b3.Blackboard()

##################################################################################################
##  Set leaf params 

    
# set up leaf probabilities
for l in leafs:
    # output observeation mu, sigma
    l.set_Obs_Density(outputs[l.Name],sig)
    # set up the Ps
    #print 'setting probs for:', l.Name, statenos[l.Name]
    l.set_Ps(PS[statenos[l.Name]])


###    Debugging


#quit()
# open the log file
logf = open(logdir+'statelog.txt','w')
bb.set('logfileptr',logf)

demo_bt.root = N1

for i in range(NEpochs):
    demo_bt.tick("First test tree for ABTs", bb)
    logf.write('---\n')
    
logf.close()

print 'Finished simulating ',NEpochs,'  epochs'
    
    