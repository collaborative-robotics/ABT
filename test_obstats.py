#!/usr/bin/python
#
#   Test observation stats 
#    generated

import sys

import numpy as np
import matplotlib.pyplot as plt
from hmm_bt import *

from model00 import *
from abt_constants import * 

nargs = len(sys.argv) - 1

#print 'Nargs: ', nargs
#print 'Argv:  ', sys.argv
#quit()

if nargs == 1:
    lfname = logdir+sys.argv[1]
else:
# read in data file 
    lfname = logdir+'statelog.txt'
    
logf = open(lfname,'r')

state_selection = 'l2'

X = []   # state names 
Y = []   # observations
Ls =[]   # length of the epochs/runouts

seq = [] # current state seq
os  = [] # current obs seq

Ahat = np.zeros((N,N))  # N def in model0x

for line in logf:
   #print '>>>',line
   line = line.strip()
   if line == '---': 
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

outputAmat(Ahat,"raw Ahat",names,sys.stdout)

#  divide to create frequentist prob estimates
for i in range(N-2):  # rows (but NOT OutS and OutF cause they don't transition out)
    rsum = np.sum(Ahat[i,:])
    print 'A,sum', Ahat[i,:], rsum
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
    
    
print 'Statistics for all state outputs in {:d} observations, {:d} epochs.'.format(len(X),len(Ls))
for j in range(N):
    mu = s1[j]/n[j]
    sigma = np.sqrt(n[j]*s2[j] - s1[j]*s1[j]) / n[j]
    error = mu - outputs[names[j]]
    print  '{:3d}, {: <6}, {:.1f}, {:.2f}      {:.2f}'.format(1+j, names[j], mu,sigma,error)
    
outputAmat(A,   "Initial   A Matrix",names, sys.stdout)
outputAmat(Ahat,"Empirical A Matrix",names, sys.stdout)

if(False):
    # print histogram of specified state observations
    state = names[statenos[state_selection]-1]
    hist = np.zeros(NSYMBOLS)

    n2 = 0
    for i in range(len(X)):
        s = X[i]
        n2 += 1
        #print n,s,Y[i]
        if s == state:
            hist[Y[i][0]] += 1  # count the output 
        
    print 'Studied {:d} symbols for state {:s}'.format(n2,state)
    for i in range(len(hist)):
        if hist[i] > 0.001:
            print i, hist[i]
        
    
    