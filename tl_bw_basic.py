#!/usr/bin/python
#
#   Fresh BW tests - try to show convergence to right model

# Special top-level to test convergence of BW Algorithm
#

import sys
import os
import subprocess
import uuid
import datetime
from hmm_bt import *
from abt_constants import *
import abtclass as abtc


###############################################
#
##    Setup BW convergence Tests
#
#   (all config in abt_constants.py <---  task_BWConv.py



##
#    Supress Deprecation Warnings from hmm_lean / scikit
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

##   Set up research parameters mostly in abt_constants.py

# amount HMM parameters should be ofset
#   from the ABT parameters.  Offset has random sign (+/-)

if len(sys.argv) != 3:
    print 'Please use two command line arguments as follows:'
    print ' > tl_bw_hmm    X.XXX comment'
    print '  to indicate the HMM perturbation value (0.0--1.0)'
    print '  and a comment (use single quotes for multiple words) to describe the run'
    print 'You entered: '
    print sys.argv
    quit()
    
HMM_delta = float(sys.argv[1])
comment = str(sys.argv[2])

#################################################
#     Normally 0.0 < HMM_delta < 0.500
###   As a flag, if HMM_delta > random_flag it is a signal 
#        that HMM initial A matrix should be set to RANDOM
HMM_RANDOM_INIT = False
if HMM_delta > random_flag:
    HMM_RANDOM_INIT = True


#
########     Generate HMM model parameters
#

N=6
names = []
for i in range(N):
    names.append('s'+str(i+1))  #  's1', 's2', etc

 
# INITIAL State Transition Probabilities
#  make A one bigger to make index human

Case = 2

if Case == 1:
    #
    #    Case 1:  fully random 
    #
    A = np.zeros((N+1,N+1))

    [rn,cn] = A.shape
    for r in range(1,rn):   # ignore 0th row    
        rsum = 0.0
        for c in range(1,cn):
            A[r][c] = random.random()
            rsum += A[r][c]
        for c in range(1,cn):  # normalize the rows
            A[r][c] /= rsum
            
    A = A[1:N+1,1:N+1]  # get zero offset index (instead of math/fortran style)
    A_row_test(A, sys.stdout)

elif Case == 2:
    #
    #   Case 2: Simple L-to-R
    #
    A = np.zeros((N,N))
    # simple-left-to-right
    for i in range(N):
        if i<(N-1):
            A[i,i] = 0.25
            A[i,i+1] = 0.75
        else:
            A[i,i] = 1.0
    A_row_test(A, sys.stdout)
       
else:
    print 'Invalid model Case defined (must be 1 or 2)'
    quit()
 
#print 'Model size: ', A.shape
#quit()
 
#  these output values are place-holders, replaced later
outputs = {}
i = 0
for n in names:
    outputs[n] = 2*i
    i += 1

## Model class takes care of this now
#Pi = np.zeros(N)
#Pi[0] = 1.0      # always start at state 1
 
#  This is probably not nesc:   names.index('l3') == 2
#statenos = {'l1':1, 'l2': 2, 'l3':3, 'l4':4,  'OutS':5, 'OutF':6}
statenos = {}
for n in names:
    statenos[n] = names.index(n)

di = 2  # placeholder

###  Regenerate output means:
i = FIRSTSYMBOL
#di = Ratio*sig  # = nxsigma !!  now in abt_constants
for n in outputs.keys():
    outputs[n] = i
    i += di
    
modelT = abtc.model(len(names))  # make a new model
modelT.A = A.copy()
#modelT.PS = PS
modelT.outputs = outputs
modelT.statenos = statenos
modelT.names = names
modelT.sigma = sig

#A_row_test(modelT.A, sys.stdout)

M = HMM_setup(modelT)

#print M.sample(3*N)   #  enough to always get stuck in last state

#  Generate data set for model fitting
#
Nrunouts = 15000
data = []
lens = []
smax = N-1

if Case == 2:
    Nsamples = 3*N
    # generate observation data from HMM
    for i in range(Nrunouts):
        X , states = M.sample(Nsamples)
        lencnt = 0
        for i,x in enumerate(X):  
            if states[i] < smax:     # ignore data when stuck in final state
                data.append(int(x))
                lencnt +=1
            else:
                data.append(int(x))  # except don't ignore 1 time in final state
                lencnt +=1
                lens.append(lencnt)
                break
        #print X,states
                
elif Case == 1:
    Nsamples = 3*N
    # generate observation data from HMM
    for i in range(Nrunouts):
        X , states = M.sample(Nsamples)
        for i,x in enumerate(X):
            data.append(int(x))
        lens.append(3*N)
        #print X, states
             
data = np.array(data).reshape(-1,1)  # needed for hmmlearn
lens = np.array(lens)

#print "simulation outputs:"
#print data
#print 'sequence lengths: ',lens
print 'Total Lengths: ', np.sum(lens),len(data)

assert np.sum(lens) == len(data), 'data doesnt match lengths (can be just a RARE event)'

M2 = M.fit(data,lens)

Adiff_Report(A,M.transmat_,modelT.names,of=sys.stdout)

#print '\n\n Model B matrix'
#print np.where(M.emissionprob_ > 0.01)
#print 'Max emissionprob: ', np.max(M.emissionprob_)
