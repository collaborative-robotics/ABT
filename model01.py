#!/usr/bin/python
#
## hmm model params

## hmm model params
import numpy as np
from abt_constants import *

names = ['l1','l2a1','l2b1','l2a2','l2b2', 'l345', 'l6a1', 'l6b1', 'l6a2', 'l6b2', 'l789', 'l10a1', 'l10b1', 'l10c1', 'OutS', 'OutF']

N = len(names)
# prob success for each node
# note dummy value for PS[0] for math consistency
PS = [0.0, 1.0, 0.9, 0.8, 0.9, 0.9, 1.0, 0.9, 0.8, 0.9, 0.9, 1.0,0.9,0.75, 0.8, 1.0, 1.0]
if len(PS) != N+1:
    print 'Incorrect PS length'
    quit()

# INITIAL State Transition Probabilities
#  make A one bigger to make index human
A = np.zeros((17,17))
A[1,2] = PS[1]
A[2,3] = PS[2]
A[2,4] = 1.0-PS[2]
A[3,4] = 1.0-PS[3]
A[3,6] = PS[3]
A[4,5] = PS[4]
A[4,16] = 1.0-PS[4]
A[5,6] = PS[5]
A[5,16] = 1.0-PS[5]
A[6,7] = PS[6]
A[7,8] = PS[7]
A[7,9] = 1.0-PS[7]
A[8,9] = 1.0-PS[8]
A[8,11] = PS[8]
A[9,10] = PS[9]
A[9,16] = 1.0-PS[9]
A[10,11] = PS[10]
A[10,16] = 1.0-PS[10]
A[11,12] = PS[11]
A[12,13] = PS[12]
A[12,16] = 1.0-PS[12]
A[13,14] = PS[13]
A[13,16] = 1.0-PS[13]
A[14,15] = PS[14]
A[14,16] = 1.0-PS[14]
A[15,15] = PS[15]
A[16,16] = PS[16]

A = A[1:17,1:17]  # get zero offset index

#
outputs = {'l1':2, 'l2a1': 5, 'l2b1':8, 'l2a2': 8,  'l2b2':11, 'l345':14, 'l6a1':17, 'l6b1':20, 'l6a2':23, 'l6b2':26, 'l789':29, 'l10a1':33, 'l10b1':36, 'l10c1':28, 'OutS':30, 'OutF':30}

statenos = {'l1':1, 'l2a1': 2, 'l2b1':3, 'l2a2':4,  'l2b2':5, 'l345':6, 'l6a1':7, 'l6b1':8, 'l6a2':9, 'l6b2':10, 'l789':11, 'l10a1':12, 'l10b1':13, 'l10c1':14, 'OutS':15, 'OutF':16}

#################################################################
##  Regenerate output means:  (easier to change below)
i = 20
#di = Ratio*sig  #  now set up in abt_constants
for n in names:
    outputs[n] = i
    i += di

#print 'Outputs: (mean of each states observations)'
#print outputs


Pi = np.zeros(16)
Pi[0] = 1.0      # always start at state 1
