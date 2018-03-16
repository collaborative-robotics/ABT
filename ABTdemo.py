#!/usr/bin/python
# 


# modified by BH, local version in current dir
import os as os
import b3 as b3          # behavior trees
import random as random
import math as m
 
####################################################################################
##
#                                   Set up the BT Leaves
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

NSYMBOLS = 10 # number of VQ symbols for observations

T = True
F = False

logdir = 'logs/'
       
if not os.path.isdir(logdir):  # if this doesn't exist, create it.
    os.mkdir(logdir) 
    

def gaussian(x, mu, sig):
    a = 1.0/(sig*(m.sqrt(2*m.pi))) * m.exp(-0.5*((x-mu)/sig)**2)
    print "A gaussian: ", a
    return a

class aug_leaf(b3.Action): 
    def __init__(self,probSuccess):
        b3.BaseNode.__init__(self)
        # Transition Probabilties for this leaf
        self.pS = probSuccess
        self.pF = 1.0-self.pS
        #  Observation Densities for this leaf
        self.Obs = [ 0 for x in range(NSYMBOLS)] # initialize list
        
    def set_Obs_Density(self, mu, sig):
        if (mu+sig) > NSYMBOLS or ((mu-sig) < 0):
            print "Bad observation init"
            quit()
        for j in range(NSYMBOLS):
            self.Obs[j] = (1/NSYMBOLS)*gaussian(j,mu,sig)
            print "j/Obs:",j,self.Obs[j]
 
    def gen_obs(self):
        a = random.uniform(0,1.0)
        b = 0.0
        for j in range(NSYMBOLS):
            b += self.Obs[j]
            if b >= a:
                return j
    
    def tick(self,tick):
        a = random.uniform(0,1.0)
        print "random: ",a , "   Ps: ", self.pS
        print "------------------------------------> obs: ",self.gen_obs()
        if a<self.pS:
            return b3.SUCCESS 
        else:
            return b3.FAILURE
    
print "-- -- --  Gaussian Test: mu = 3, sig = 1"
sum = 0.0
for i in range(NSYMBOLS):
    tmp = gaussian(i,3,1)
    sum += tmp
    print tmp

print "Sum: ", sum

print"\n\n"
    
leaf1 = aug_leaf(0.9)
print "Test:  leaf 1 ID:"
print leaf1.id

leaf1.set_Obs_Density(3,2)

leaf2 = aug_leaf(0.95)
leaf2.set_Obs_Density(7,2)

leaf3 = aug_leaf(0.9)
leaf3.set_Obs_Density(3,2)

leaf1.Name = "Leaf 1"
leaf2.Name = "Leaf 2"
leaf3.Name = "L3"
        
leaf1.BHdebug = T
leaf2.BHdebug = T
leaf3.BHdebug = T

N1 = b3.Sequence([leaf1, leaf2, leaf3])
N1.Name = 'Sequencer Node'
N1.BHdebug = T
bb = b3.Blackboard()

demo_bt.root = N1

demo_bt.tick("First test tree for ABTs", bb)

    
    