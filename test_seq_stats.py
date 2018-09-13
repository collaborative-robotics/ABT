#!/usr/bin/python
#
#   Test observation stats 
#    generated

import sys

import numpy as np
import matplotlib.pyplot as plt
from hmm_bt import *

from abt_constants import *  

MODEL = BIG

testeps = 1.96 / np.sqrt(float(NEpochs))  # will convert to confidence interval
testsigeps = 0.10   # 1% of standard value 2.0

print 'Test epsilon: ', testeps
print 'Test sig epsilon: ', testsigeps

##
#    Supress Deprecation Warnings from hmm_lean / scikit
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

##   Set up research parameters mostly in abt_constants.py

############################################

##  The ABT file for the task (CHOOSE ONE)

if MODEL== BIG:
    from peg2_ABT import * # big  14+2 state  # uses model01.py
    from model01 import *
    model = modelo01
    
if MODEL==SMALL:
    from simp_ABT import *  # small 4+2 state # uses model02.py
    from model00 import *
    model = modelo00

GENDATA = False  #  (determined by # args below)

logdir = ''

nargs = len(sys.argv)

if nargs == 1:
    GENDATA = False  # use standard data
elif nargs == 2:
    if(sys.argv[1] == "GENDATA"):
        GENDATA = True
        Ratio = 3.0        #  set this for the generated data
        lfname = logdir+'TSTstatelog.txt'
    else:
        lfname = str(sys.argv[1])
        Ratio = float(di)/sig

print 'Starting observation stats test on ', lfname
if GENDATA:
    print ' Generating NEW data'

NEpochs = 100000

num_states = model.n
    
logf = open(lfname,'r')


print '\n\n\n                       Sequence Test Report '
print '                                     checking state transition stats from ground truth \n\n'

state_selection = 'l2'

X = []   # state names 
Y = []   # observations
Ls =[]   # length of the epochs/runouts

seq = [] # current state seq
os  = [] # current obs seq

Ahat = np.zeros((model.n,model.n))  # N def in model0x

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
               k = model.names.index(seq[i-1])
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
        
#state = model.names[13]

N = model.n - 2   # don't expect OutF and OutS

# set up sums for each state
s1 = np.zeros(N)
s2 = np.zeros(N)
n  = np.zeros(N)  # counts for each state

for i in range(len(X)): 
    for j in range(N):     # accumulate stats for each state
        #print X[j],model.names[j]
        if X[i] == model.names[j]:
            s1[j] +=  Y[i][0]
            s2[j] += (Y[i][0])**2
            n[j]  += 1
            #print X[j], s1[j], s2[j]

outputAmat(A,   "Model A Matrix",    model.names, sys.stdout)    
outputAmat(Ahat,"Empirical A Matrix",model.names, sys.stdout)

print 'A-matrix estimation errors: '

Adiff_Report(A,Ahat,model.names) 

print 'Studied ',len(X), 'observations,', model.n, 'state model'

#################################################################
#
#   Generate state visit frequencies
#
#
nv = np.zeros(model.n)
for i in range(len(X)):    # go through data once
    s = X[i]  # current true state    
    nv[names.index(s)] += 1 # count the visit 
    
print '\n\nState Visit Frequency Report'
for n in names:
    v = nv[names.index(n)]
    print n, ' visited ', v ,'times out of ', nsims, ' = ', float(v)/float(nsims)
        
    
    
print 'WARNING: No Assertions Yet for this test'


