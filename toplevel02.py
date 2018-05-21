#!/usr/bin/python
#
#   Top-level scripted task
#

#   Big BT for #
import sys
import os
import datetime
from hmm_bt import *

from abt_constants import *

##   Set up research parameters

global NEpochs  

NEpochs = 10000  # number of simulations

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
[X,Y,Ls] = read_obs_seqs(logdir+'statelog.txt')

#############################################
#
#    HMM model identification
#

M = HMM_setup(Pi,A,sig,names)

print "starting HMM fit with ", len(Y), ' observations.'

M.fit(Y,Ls)

########## results output file

outputdir = 'out/'
oname = 'hmm_fit_out_'+datetime.datetime.now().strftime("%y-%m-%d-%H-%M")

of = open(outputdir+oname,'w')

# print the output file header
for rline in rep:
    print >>of, rline

outputAmat(A,"Original A Matrix", names, of)
outputAmat(M.transmat_,"New A Matrix", names, of)


## TEST A-diff

#B = np.zeros(A.shape)
#n=16
#for i in range(n):
    #for j in range(n):
        #B[i,j]=A[i,j]
#B[5,3]= 0.1
#[e,e2,em,N2,im,jm,anoms,erasures] = Adiff(A,B,names)
#print 'top: im, jm: ', im,jm


##  compare the two A matrices
#     (compute error metrics)
[e,e2,em,N2,im,jm,anoms,erasures] = Adiff(A,M.transmat_, names)


print >> of, 'RMS  A-matrix error: {:.3f}'.format(e)
print >> of, 'RMS  A-matrix error: {:.8f} ({:d} non zero elements)'.format(e2,N2)
print >> of, 'Max  A-matrix error: {:.3f} (at {:d} to {:d})'.format(em,im,jm)
if len(anoms) == 0:
    anoms = 'None'
print >> of, 'Anomalies: ', anoms
if len(erasures) == 0:
    anoms = 'None'
print >> of, 'Erasures : ', erasures



of.close()
os.system('cp {:s} {:s}'.format(outputdir+oname,outputdir+'lastoutput'))

 
#
#    HMM state tracking analysis
# 

