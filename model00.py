#!/usr/bin/python
# 
## hmm model params
import numpy as np


NSYMBOLS = 150 # number of VQ symbols for observations

NEpochs = 100  # number of simulations

T = True
F = False

logdir = 'logs/'
names = ['l1','l2','l3','l4', 'OutS', 'OutF']

N = len(names)
print 'N = ',N

# prob success for each node
# note dummy value for PS[0] for math consistency
PS = [0, 0.65, 0.75, .8, 0.9, 1.0,1.0]


# INITIAL State Transition Probabilities
#  make A one bigger to make index human
A = np.zeros((N+1,N+1))
A[1,2] = PS[1]
A[1,3] = 1.0-PS[1]
A[2,3] = PS[2]
A[2,6] = 1.0-PS[2]
A[3,4] = PS[3]
A[3,5] = 1.0-PS[3]
A[4,5] = PS[4]
A[4,6] = 1.0-PS[4]
A[5,5] = 1.0
A[6,6] = 1.0

A = A[1:N+1,1:N+1]  # get zero offset index
print 'Size: A:', A.size
######################
sig = 2.0 
#
outputs = {'l1':2, 'l2': 5, 'l3':8, 'l4': 8,  'OutS':10, 'OutF':20}

Pi = np.zeros(N)
Pi[0] = 1.0      # always start at state 1
 
statenos = {'l1':1, 'l2': 2, 'l3':3, 'l4':4,  'OutS':5, 'OutF':6}

###  Regenerate output means:
i = 20
di = 3*sig  # = nxsigma !!
for n in outputs.keys():
    outputs[n] = i
    i += di
    
    
    