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


# some examples from IKBT

#tanSolver = tan_solve()
#tanSolver.BHdebug = SolverDebug
#tanSolver.Name = "Tangent Solver"

#tanSol = b3.Sequence([tanID, tanSolver])
#tanSol.Name = "TanID+Solv"
#tanSol.BHdebug =  LeafDebug


#algID = algebra_id()
#algID.Name = "Algebra ID"
#algID.BHdebug = LeafDebug

#algSolver = algebra_solve()
#algSolver.Name = "Algebra Solver"
##algSolver.BHdebug = LeafDebug

#algSol = b3.Sequence([algID, algSolver])
#algSol.Name = "Algebra ID and Solve"
#algSol.BHdebug = SolverDebug
 
#           ONE BT TO RULE THEM ALL!
#   Higher level BT nodes here
##

#sc_tan = b3.Sequence([b3.OrNode([tanSol, scSol]), rk])
#worktools = b3.Priority([algSol, sc_tan, Simu_Eqn_Sol, sacSol, x2z2_Solver])
#subtree = b3.RepeatUntilSuccess(b3.Sequence([asgn, worktools]), 6)
#solveRoutine = b3.Sequence([sub_trans, subtree,  updateL, compDetect])

#topnode = b3.RepeatUntilSuccess(solveRoutine, 7) #max 10 loops

#ikbt.root = topnode 

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
        # Transition Probabilties for this leaf
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
                return j
        return j
    
    def tick(self,tick):
        a = random.uniform(0,1.0)
        #print "random: ",a , "   Ps: ", self.pS
        print "------------------------------------> obs: ", self.gen_obs()
        if a<self.pS:
            return b3.SUCCESS 
        else:
            return b3.FAILURE 
print"\n\n"

########  Step 1  Position Left Grasper over block
    
leaf1 = aug_leaf(1.0) 
leaf1.set_Obs_Density(5,1)


########  Step 2 Insert and Grasp block
    
leaf2a = aug_leaf(0.9)
leaf2a.set_Obs_Density(12,1)

leaf2c = aug_leaf(0.95)
leaf2c.set_Obs_Density(12,1)


leaf2b = b3.Sequence([leaf2a,leaf2c])
leaf2 = b3.RepeatUntilSuccess(leaf2b,2) 


##########  Steps 3-5  Lift clear / reorient / move

leaf3to5 = aug_leaf(1.0)
leaf3to5.set_Obs_Density(5,1)

##########  Step 6 Insert Right grasper / grasp

leaf6a = aug_leaf(0.6)
leaf6a.set_Obs_Density(18,1)

leaf6c = aug_leaf(0.75)
leaf6c.set_Obs_Density(18,1)

leaf6b = b3.Sequence([leaf6a,leaf6c])
leaf6 = b3.RepeatUntilSuccess(leaf6b,2)

leaf6.Name = "Leaf 6"

########  Steps 7-9   Release Left / Reorient / Position

leaf7to9 = aug_leaf(1.0)
leaf7to9.set_Obs_Density(5,1)

########  Step 10     Place on peg / Release / Clear 
     
leaf10a = aug_leaf(0.9)
leaf10a.set_Obs_Density(22,1)

leaf10c = aug_leaf(0.95)
leaf10c.set_Obs_Density(22,1)
    
leaf10d = aug_leaf(0.8)
leaf10d.set_Obs_Density(22,1)
leaf10b = b3.Sequence([leaf10a,leaf10c])
leaf10 = b3.RepeatUntilSuccess(leaf10b,2) 

###    Debugging
leaf6.BHdebug = T


N1 = b3.Sequence([leaf1, leaf2, leaf3to5, leaf6, leaf7to9, leaf10])
N1.Name = 'Sequencer Node'
N1.BHdebug = T
bb = b3.Blackboard()

demo_bt.root = N1

demo_bt.tick("First test tree for ABTs", bb)

    
    