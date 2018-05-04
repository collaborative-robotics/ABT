#!/usr/bin/python
# 


# modified by BH, local version in current dir
import os as os
import b3 as b3          # behavior trees
import random as random
import math as m
import numpy as np
 
####################################################################################
##
#                         Demo of ABT for Peg-In-Hole Task
# 
#
demo_bt = b3.BehaviorTree()

LeafDebug = False
SolverDebug = False

NSYMBOLS = 30 # number of VQ symbols for observations

T = True
F = False

logdir = 'logs/'
       
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
        
    def set_Obs_Density(self, mu, sig):
        if (mu+sig) > NSYMBOLS or ((mu-sig) < 0):
            print "Bad observation init"
            quit()
        for j in range(NSYMBOLS):
            self.Obs[j] = gaussian(j+0.5,mu,sig)
            #print "j/Obs:",j,self.Obs[j]
 
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
        print "------------------------------------> obs: ", observation
        f.write(self.Name+', '+str(observation)+'\n')
        if a<self.pS:
            return b3.SUCCESS 
        else:
            return b3.FAILURE 
print"\n\n"

########  Step 1  Position Left Grasper over block
    
leaf1 = aug_leaf(1.0) 
leaf1.set_Obs_Density(5,1)
leaf1.Name = 'L1'


########  Step 2 Insert and Grasp block
    
leaf2a = aug_leaf(0.9)
leaf2a.set_Obs_Density(12,1)
leaf2a.Name = 'L2a'

leaf2c = aug_leaf(0.95)
leaf2c.set_Obs_Density(12,1)
leaf2c.Name = 'L2c'

leaf2b = b3.Sequence([leaf2a,leaf2c])
leaf2 = b3.RepeatUntilSuccess(leaf2b,2) 


##########  Steps 3-5  Lift clear / reorient / move

leaf3to5 = aug_leaf(1.0)
leaf3to5.set_Obs_Density(5,1)
leaf3to5.Name = 'L345'

##########  Step 6 Insert Right grasper / grasp

leaf6a = aug_leaf(0.6)
leaf6a.set_Obs_Density(18,1)
leaf6a.Name = 'L6a'

leaf6c = aug_leaf(0.75)
leaf6c.set_Obs_Density(18,1)
leaf6c.Name = 'L6c'

leaf6b = b3.Sequence([leaf6a,leaf6c])
leaf6 = b3.RepeatUntilSuccess(leaf6b,2)
leaf6.Name = "Leaf 6"

########  Steps 7-9   Release Left / Reorient / Position

leaf7to9 = aug_leaf(1.0)
leaf7to9.set_Obs_Density(5,1)
leaf7to9.Name = 'L789'

########  Step 10     Place on peg / Release / Clear 
     
leaf10a = aug_leaf(0.9)
leaf10a.set_Obs_Density(22,1)
leaf10a.Name = 'L10a'

leaf10c = aug_leaf(0.95)
leaf10c.set_Obs_Density(22,1)
leaf10c.Name = 'L10c'
    
leaf10d = aug_leaf(0.8)
leaf10d.set_Obs_Density(22,1)
leaf10d.Name = 'L10d'

leaf10b = b3.Sequence([leaf10a,leaf10c,leaf10d])

leaf10 = b3.RepeatUntilSuccess(leaf10b,2) 

###    Debugging
leaf6.BHdebug = T


N1 = b3.Sequence([leaf1, leaf2, leaf3to5, leaf6, leaf7to9, leaf10])
N1.Name = 'Sequencer Node'
N1.BHdebug = T
bb = b3.Blackboard()

# open the log file
logf = open(logdir+'statelog.txt','w')
bb.set('logfileptr',logf)

demo_bt.root = N1

demo_bt.tick("First test tree for ABTs", bb)

    
    