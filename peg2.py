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
 
####################################################################################
##
#                         Demo of ABT for Peg-In-Hole Task
# 
#
demo_bt = b3.BehaviorTree()

LeafDebug = False
SolverDebug = False

NSYMBOLS = 150 # number of VQ symbols for observations

NEpochs = 1000  # number of simulations

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
            print 'aug_leaf: Warning may gen negative observations'
            #quit()
        for j in range(NSYMBOLS):
            self.Obs[j] = gaussian(j+0.5,mu,sig)
            #print "j/Obs:",j,self.Obs[j]
        print self.Name, 'obs:', mu, sig
        
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


sig = 2.0
outputs = {'l1':2, 'l2a1': 5, 'l2b1':8, 'l2a2': 8,  'l2b2':11, 'l345':14, 'l6a1':17, 'l6b1':20, 'l6a2':23, 'l6b2':26, 'l789':29, 'l10a1':33, 'l10b1':36, 'l10c1':28, 'OutS':30, 'OutF':30}

##  Regenerate output means:
i = 0
di = 8
for n in outputs.keys():
    outputs[n] = i
    i += di
    
    
#print outputs
#quit()
 

########  Step 1  Position Left Grasper over block
    
l1 = aug_leaf(1.0) 
l1.set_Obs_Density(outputs['l1'], sig)
l1.Name = 'l1'

########  Step 2 Insert and Grasp block

# try 1    
l2a1 = aug_leaf(0.9)
l2a1.Name = 'l2a1'
l2a1.set_Obs_Density(outputs['l2a1'],sig)     # emit "2"

l2b1 = aug_leaf(0.95)
l2b1.Name = 'l2b1'
l2b1.set_Obs_Density(outputs['l2b1'],sig)     # emit "4"

l21 = b3.Sequence([l2a1,l2b1]) 

# try 2
l2a2 = aug_leaf(0.9)
l2a2.Name = 'l2a2'
l2a2.set_Obs_Density(outputs['l2a2'],sig)     # emit "12"

l2b2 = aug_leaf(0.95)
l2b2.Name = 'l2b2'
l2b2.set_Obs_Density(outputs['l2b2'],sig)     # emit "12"

l22 = b3.Sequence([l2a2,l2b2]) 

l2 = b3.Priority([l21,l22])


##########  Steps 3-5  Lift clear / reorient / move

l345 = aug_leaf(1.0)
l345.Name = 'l345'
l345.set_Obs_Density(outputs['l345'],sig)

##########  Step 6 Insert Right grasper / grasp

# try 1
l6a1 = aug_leaf(0.6)
l6a1.Name = 'l6a1'
l6a1.set_Obs_Density(outputs['l6a1'],sig)

l6b1 = aug_leaf(0.75)
l6b1.Name = 'l6b1'
l6b1.set_Obs_Density(outputs['l6b1'],sig)

# try 2
l6a2 = aug_leaf(0.6)
l6a2.Name = 'l6a2'
l6a2.set_Obs_Density(outputs['l6a2'],sig)

l6b2 = aug_leaf(0.75)
l6b2.Name = 'l6b2'
l6b2.set_Obs_Density(outputs['l6b2'],sig)

l61 = b3.Sequence([l6a1,l6b1])
l62 = b3.Sequence([l6a2,l6b2])
l6  = b3.Priority([l61,l62]) 
l6.Name = "leaf 6"

########  Steps 7-9   Release Left / Reorient / Position

l789 = aug_leaf(1.0)
l789.Name = 'l789'
l789.set_Obs_Density(outputs['l789'],sig)

########  Step 10     Place on peg / Release / Clear 
     
l10a1 = aug_leaf(0.9)
l10a1.Name = 'l10a1'
l10a1.set_Obs_Density(outputs['l10a1'],sig)

l10b1 = aug_leaf(0.95)
l10b1.Name = 'l10b1'
l10b1.set_Obs_Density(outputs['l10b1'],sig)
    
l10c1 = aug_leaf(0.8)
l10c1.Name = 'l10c1'
l10c1.set_Obs_Density(outputs['l10c1'],sig)

l10 = b3.Sequence([l10a1,l10b1,l10c1])
l10.Name = 'Position/Release'

###    Debugging


#quit()

N1 = b3.Sequence([l1, l2, l345, l6, l789, l10])
N1.Name = 'Sequencer Node'
N1.BHdebug = T
bb = b3.Blackboard()

# open the log file
logf = open(logdir+'statelog.txt','w')
bb.set('logfileptr',logf)

demo_bt.root = N1

for i in range(NEpochs):
    demo_bt.tick("First test tree for ABTs", bb)
    logf.write('---\n')
    
logf.close()

    
    