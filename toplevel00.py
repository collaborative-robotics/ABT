#!/usr/bin/python
#
#   Top-level scripted task
#

import datetime
from hmm_bt import *

##   Set up research parameters

global NSYMBOLS  
global NEpochs 

NSYMBOLS = 150 # number of VQ symbols for observations

NEpochs = 100  # number of simulations

##  The ABT file for the task (in this case FLS block Xfer)
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

logdir = 'logs/'
[X,Y,Ls] = read_obs_seq(logdir+'statelog.txt')

#############################################
#
#    HMM model identification
#

M = HMMsetup(Pi,A,names)

print "starting HMM fit with ", len(Y), ' observations.'

M.fit(Y,Ls)

########## results output file

outputdir = 'out/'
oname = 'hmm_fit_out_'+datetime.datetime.now().strftime("%y-%m-%d-%H-%M")

of = open(outputdir+oname,'w')

# print the output file header
for rline in rep:
    print >>of, rline

outputAmat(A,"Original A Matrix", of)
outputAmat(M.transmat_,"New A Matrix", of)

#np.set_printoptions(precision=3,suppress=True)
 
#
#    HMM state tracking analysis
# 

