#!/usr/bin/python
#
#   Test observation stats 
#    generated

import sys

import numpy as np
import matplotlib.pyplot as plt
from hmm_bt import *

from abt_constants import * 


from abt_constants import *

MODEL = BIG

testeps = 400 / float(NEpochs)   # should be sqrt()^-1 I guess
print 'Test epsilon: ', testeps

# Select the ABT file here
if MODEL==SMALL:
    from simp_ABT import *    # basic 4-state HMM 
elif MODEL==BIG:
    from peg2_ABT import *         # elaborate 16-state HMM
#

GENDATA = False  #  (determined by # args below)

logdir = 'logs/'

# use this filename to know exact observation count.
lfname = logdir + 'REF_test_statelog.txt'
refdataname = lfname

nargs = len(sys.argv)

if nargs == 1:
    GENDATA = False  # use standard data 
elif nargs == 2:
    if(sys.argv[1] == "GENDATA"):
        GENDATA = True
        lfname = logdir+'TSTstatelog.txt'
    else:
        lfname = str(sys.argv[1])

print 'Starting state sequence stats test on ', lfname
if GENDATA:
    print ' Generating NEW data'

    
logf = open(lfname,'r')


print '\n\n\n                       Sequence Test Report '
print '                                     checking state transition stats from ground truth \n\n'

state_selection = 'l2'

X = []   # state names 
Y = []   # observations
Ls =[]   # length of the epochs/runouts

seq = [] # current state seq
os  = [] # current obs seq

Ahat = np.zeros((N,N))  # N def in model0x

nsims = 0
for line in logf:
   #print '>>>',line
   line = line.strip()
   if line == '---': 
       nsims += 1
       # store freq of state transitions
       for i in range(len(seq)):
           if(i>0):  # no transition INTO first state
               j = names.index(seq[i])
               k = names.index(seq[i-1])
               Ahat[k,j] += 1
       Ls.append(len(os)) 
       os  = []
       seq = []
   else:
       [state, obs ] = line.split(',')
       seq.append(state)
       os.append(obs)
       X.append(state)
       Y.append([int(obs)])
       os.append([int(obs)])


#  divide to create frequentist prob estimates
for i in range(N-2):  # rows (but NOT OutS and OutF cause they don't transition out)
    rsum = np.sum(Ahat[i,:])
    #print 'A,sum', Ahat[i,:], rsum
    for j in range(N): # cols
        Ahat[i,j] /= rsum
        
#state = names[13]

N = len(names) - 2   # don't expect OutF and OutS

# set up sums for each state
s1 = np.zeros(N)
s2 = np.zeros(N)
n  = np.zeros(N)  # counts for each state

for i in range(len(X)): 
    for j in range(N):     # accumulate stats for each state
        #print X[j],names[j]
        if X[i] == names[j]:
            s1[j] +=  Y[i][0]
            s2[j] += (Y[i][0])**2
            n[j]  += 1
            #print X[j], s1[j], s2[j]

outputAmat(A,   "Model A Matrix",    names, sys.stdout)    
outputAmat(Ahat,"Empirical A Matrix",names, sys.stdout)

print 'A-matrix estimation errors: '

Adiff_Report(A,Ahat,names) 

print 'Studied ',len(X), 'observations,', len(names), 'state model'

#################################################################
#
#   Generate state visit frequencies
#
#
nv = np.zeros(len(names))
for i in range(len(X)):    # go through data once
    s = X[i]  # current true state    
    nv[names.index(s)] += 1 # count the visit 
    
print '\n\nState Visit Frequency Report'
for n in names:
    v = nv[names.index(n)]
    print n, ' visited ', v ,'times out of ', nsims, ' = ', float(v)/float(nsims)
        
    
    
print 'WARNING: No Assertions Yet for this test'


