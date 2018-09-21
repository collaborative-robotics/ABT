#!/usr/bin/python
#
#   Test observation stats 
#    generated

import sys

import numpy as np
import matplotlib.pyplot as plt
from   hmm_bt import *
from   abt_constants import *  

MODEL = BIG

max_avg_abs_non_zero = 0.01
max_max_abs_non_zero = 0.03
 

##
#    Supress Deprecation Warnings from hmm_lean / scikit
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

##   Set up research parameters mostly in abt_constants.py

############################################

##  The ABT file for the task (CHOOSE ONE)
 

if MODEL==BIG:
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
    print 'Please use a filename on command line'
    print 'Args: ', sys.argv
    print 'Usage: '
    print '> test_seq_stats   [GENDATA|filename]'
    quit()
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
    
print 'Initial num states: ', num_states

logf = open(lfname,'r')



#
#   Check that we have the right model for the data (for comparison)
#


print '\n\n\n                       Sequence Test Report '
print '                                     checking state transition stats from ground truth \n\n'

#state_selection = 'l2'

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
               assert seq[i] in model.names, 'Unknown state visited.  Probably wrong MODEL (BIG/SMALL) selection.'
               j = model.names.index(seq[i])
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

[e,e2,em,N2,imax,jmax,anoms,erasures] = Adiff(A,Ahat,model.names)
    
####################################################################
#
#     State Transition Stats assertions
#


max_avg_abs_non_zero = 0.01
max_max_abs_non_zero = 0.03

assert abs(e2) < max_avg_abs_non_zero, 'Too much avg RMS error in non-zero elements'
assert abs(em) < max_max_abs_non_zero, 'Too much MAX RMS error in non-zero elements'

print 'Erasures: ', erasures

assert erasures != 'None', 'Erasure(s) found'
assert anoms    != 'None', 'Anomaly(s) found'

    
print 'Studied ',len(X), 'observations,', model.n, 'state model'

#################################################################
#
#   Generate state visit frequencies report
#
#
nv = np.zeros(model.n)
for i in range(len(X)):    # go through data once
    s = X[i]  # current true state    
    nv[names.index(s)] += 1 # count the visit 
    
print '\n\nState Visit Frequency Report'
for n in names:
    v = nv[names.index(n)]
    #print n, ' visited ', v ,'times out of ', nsims, ' = ', float(v)/float(nsims)
    print '{:>10s}: visited {:6d} times out of {:6d} simulations ({:5.1f}%)'.format(n,int(v),nsims,100.0*float(v)/float(nsims))
        
print 'Sequence test PASSED'
