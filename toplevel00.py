#!/usr/bin/python
#
#   Top-level scripted task
#


##   Set up research parameters

global NSYMBOLS  
global NEpochs 

NSYMBOLS = 150 # number of VQ symbols for observations

NEpochs = 100  # number of simulations

##  The ABT file for the task
from peg2 import *


#############################################
#
#    Set up model params


#####    make a string report describing the setup
#
# 
rep = []
rep.append('-------------------------- BT to HMM ---------------------------------------------')
rep.append('NSYMBOLS: {:d}   NEpochs: {:d} '.format(NSYMBOLS,NEpochs))
rep.append('sigma: {:.2f}    Symbol delta: {:d}   Ratio:  {:.2f}'.format(sig, int(di), float(di)/float(sig)))
rep.append('----------------------------------------------------------------------------------')
rep.append(' ')

           
#############################################
#
#    Build the ABT and its blackboard
#

[ABT, bb] = flsblockABT()

#############################################
#
#    Generate Simulated Data
#

###    Debugging
#quit()
# open the log file
logf = open(logdir+'statelog.txt','w')
bb.set('logfileptr',logf)


for i in range(NEpochs):
    ABT.tick("ABT Simulation", bb)
    logf.write('---\n')
    
logf.close()

print 'Finished simulating ',NEpochs,'  epochs'
    
    
#############################################
#
#    HMM model Initialization
#

#############################################
#
#    HMM model identification
#

#############################################
#
#    HMM state tracking analysis
# 

