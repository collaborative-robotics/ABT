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

if len(sys.argv) != 4:
    print 'Please use three command line arguments as follows:'
    print ' > tl_bw_hmm   c d comment'
    print '   c -> indicate the model Case'
    print '   d -> perturbation Delta (0-0.5)'
    print '  and a comment (use single quotes for multiple words) to describe the run'
    print '''
    
Case codes (param c):
    RAND = 1
    RAND_PLUS_ZEROS = 2
    SLR = 3
    ABT_LIKE = 4
    ABT_DUR  = 5
'''
    print sys.argv
    quit()
    
#HMM_delta = float(sys.argv[1])
Case = int(sys.argv[1])
HMM_delta = float(sys.argv[2])
comment = str(sys.argv[3])

git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'])[:10]  # first 10 chars to ID software version
 
Nrunouts = 100
sig = 2.0
Ratio = 2.5

#
########     Generate HMM model parameters
#

N=16
names = []
for i in range(N):
    names.append('s'+str(i+1))  #  's1', 's2', etc

 
# INITIAL State Transition Probabilities
#  make A one bigger to make index human
RAND = 1
RAND_PLUS_ZEROS = 2
SLR = 3
ABT_LIKE = 4
ABT_DUR  = 5

#Case = RAND_PLUS_ZEROS
if Case == RAND:
    type_comment =  'Randomized A-matrix'
if Case == RAND_PLUS_ZEROS:
    type_comment =  'Randomized A-matrix with about 20% zeros'
if Case == SLR:
    type_comment =  'Simple Left-to-Right HMM'
if Case == ABT_LIKE:
    type_comment =  'ABT-like HMM structure'
if Case == ABT_DUR:
    type_comment =  'ABT HMM structure + SELF STATE TRANS.'
    
print '\n\n'+type_comment
print 'Ratio = ', Ratio, '   HMM delta / perturbation = ', HMM_delta

if Case == RAND or Case == RAND_PLUS_ZEROS:
    #
    #    Case 1:  fully random 
    #
    zerofrac = 0.20   #  zero out 20% of entries
    A = np.zeros((N+1,N+1))
    rsum = np.zeros(N+1)
    [rn,cn] = A.shape
    for r in range(1,rn):   # ignore 0th row
        for c in range(1,cn):
            A[r][c] = random.random()
            if Case == RAND_PLUS_ZEROS:
                if random.random() < zerofrac:
                    A[r][c] = 0.0
            rsum[r] += A[r][c]
    
            
    for r in range(1,rn):
        for c in range(1,cn):  # normalize the rows
            A[r][c] /= rsum[r]
            
    A = A[1:N+1,1:N+1]  # get zero offset index (instead of math/fortran style)
    A_row_test(A, sys.stdout)


elif Case == SLR:
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
       
elif Case == ABT_LIKE or Case == ABT_DUR:
    #
    #   Like an ABT
    #
    A = np.zeros((N,N))
    # simple-left-to-right
    for r in range(N):
        if r<(N-2):
            A[r,r] = 0.0
            p = 0.5 + 0.25 * random.random()
            A[r,r+1] = p
        else:
            A[r,r] = 1.0   # output states Os Of
            
    for r in range(N-2):
        q = 1.0 - A[r,r+1]
        j = r + 2 + int(random.random()*(N-r-3)+ 0.5)   # pick a random col > diagonal+1
        A[r,j] = q
        
    # normalize?
    if Case == ABT_DUR:
        #
        #    Add in  a self-state transition to ABT
        #
        for r in range(N-2):
            A[r,r] = 0.2
            A[r,r+1] -= 0.2
        
    A_row_test(A, sys.stdout)    # just a good idea
       
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

di = sig*Ratio  # placeholder

#######################################
### generate output means:
i = FIRSTSYMBOL
#di = Ratio*sig  # = nxsigma !!  now in abt_constants
for n in outputs.keys():
    outputs[n] = i
    i += di
    
    
#######################################################
#
#    Make ABT model 
#
modelT = abtc.model(len(names))  # make a new model
modelT.A = A.copy()
#modelT.PS = PS
modelT.outputs = outputs
modelT.statenos = statenos
modelT.names = names
modelT.sigma = sig
modelT.typestring = "MultinomialHMM"

#A_row_test(modelT.A, sys.stdout)

#########################################################
#
#    Build the HMM
#

M = HMM_setup(modelT)

#print M.sample(3*N)   #  enough to always get stuck in last state

#####################################################################
#
#  Generate data set for model fitting
#
data = []
lens = []
smax = N-2   #  real states vs terminal states (Os & Of)

if Case == SLR or Case==ABT_LIKE or Case == ABT_DUR:
    Nsamples = 3*N
    Nsamples = 500
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
        #x = raw_input ('Enter: ')
        
elif Case == RAND or Case == RAND_PLUS_ZEROS:
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


#####################################################################
#
#   Perturb HMM params so that it is not starting at same point as dataset
#

#HMM_perturb(M, HMM_delta, modelT)
if(Case == RAND or Case == RAND_PLUS_ZEROS):
    A2, B2 = HMM_fully_random(modelT) 


    model02 = abtc.model(len(names))  # make a new model
    model02.A = A2.copy()
    #model02.PS = PS
    model02.outputs = modelT.outputs
    model02.statenos = modelT.statenos
    model02.names = modelT.names
    model02.sigma = sig
    model02.typestring = "MultinomialHMM"


    M2 = HMM_setup(model02)


        
elif Case == SLR or Case == ABT_LIKE or Case == ABT_DUR:
    HMM_perturb(M, HMM_delta, modelT)
    
    
    model02 = abtc.model(len(names))  # make a new model
    model02.A = M.transmat_.copy()
    #model02.PS = PS
    model02.outputs = modelT.outputs
    model02.statenos = modelT.statenos
    model02.names = modelT.names
    model02.sigma = sig
    model02.typestring = "MultinomialHMM"


    M2 = HMM_setup(model02)


#################################################3
#
#   Some validations on new perturbed model
#
M2._check()
HMM_model_sizes_check(M2)

print '\n\n'
print "Initial A-matrix perturbation: "
Adiff_Report(A,M2.transmat_,modelT.names,of=sys.stdout)

# store diffs due to perturbation
[e,e2orig,emorig,N2,im,jm,anomsorig,erasuresorig] = Adiff(A,M2.transmat_, modelT.names)

 
##################################################
#
#    Apply Baum Welch to perturbed model
#
M2.fit(data,lens)
 
##################################################
#
#    Report on changed of A matrix due to BW adaptation
#

print '\n\n'+type_comment
print 'Ratio = ', Ratio, '   HMM delta / perturbation = ', HMM_delta

print "Initial FIT M2->M: "
Adiff_Report(M2.transmat_,A, modelT.names,of=sys.stdout)

[e,e2,em,N2,im,jm,anoms,erasures] = Adiff(A,M2.transmat_, modelT.names)

logfname = 'tl_bw_basic_data.txt'
fdata = open(logfname, 'a')

print "\n\nlogging to " + logfname 
print ' date / sw commit / HMM_delta / A-Matrix type / e2orig / e2 / emaxorig / em / iters / comment'

line = '{:s} | {:s} | {:4.2f} | {:d} | {:f} | {:f} |{:f} | {:f} | {:d} | {:s}'.format(datetime.datetime.now().strftime("%y-%m-%d-%H:%M"), git_hash, HMM_delta, Case, e2orig, e2, emorig,  em, M2.monitor_.iter, comment)

print >> fdata, line

fdata.close() 

