#!/usr/bin/python
#
#   Test observation stats 
#    generated

import numpy as np
import matplotlib.pyplot as plt
 
from model01 import *
 
# read in data file 
logf = open(logdir+'statelog.txt','r')

X = []   # state names 
Y = []   # observations
Ls =[]   # lengths 

seq = [] # current state seq
os  = [] # current obs seq

for line in logf:
   #print '>>>',line
   line = line.strip()
   if line == '---': 
       Ls.append(len(os)) 
       os  = []
   else:
       [state, obs ] = line.split(',')
       X.append(state)
       Y.append([int(obs)])
       os.append([int(obs)])

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
    
    
print 'Statistics for all state outputs in {:d} observations.'.format(len(X))
for j in range(N):
    mu = s1[j]/n[j]
    sigma = np.sqrt(n[j]*s2[j] - s1[j]*s1[j]) / n[j]
    error = mu - outputs[names[j]]
    print  '{:3d}, {: <6}, {:.1f}, {:.2f}      {:.2f}'.format(1+j, names[j], mu,sigma,error)
    

# print histogram of specified state observations
state = names[statenos['l10c1']-1]
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
    print i, hist[i]
    
    
    