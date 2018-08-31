#!/usr/bin/python
#

#  Test for HMM setup and perturbs

import sys
import numpy as np
import matplotlib.pyplot as plt

#sudo pip install scikit-learn  # dep for hmmlearn
#pip install -U --user hmmlearn
from hmmlearn import hmm
#####################################################

#####################################################
from hmm_bt import *   # bring in the HMM_perturb() function 
 
 

logdir = 'logs/'
names = ['l1','l2','l3','l4', 'OutS', 'OutF']

N = len(names)
 
# PS = prob of success for each node
# note dummy value for PS[0] for math consistency
PS = [0, 0.65, 0.75, .8, 0.9, 1.0,1.0]
if len(PS) != N+1:
    print 'Incorrect PS length'
    quit()

# INITIAL State Transition Probabilities
#  make A one bigger to make index human
A = np.zeros((N+1,N+1))
A[1,2] = PS[1]
A[1,6] = 1.0-PS[1]
A[2,3] = PS[2]
A[2,6] = 1.0-PS[2]
A[3,4] = 1.0-PS[3]
A[3,5] = PS[3]
A[4,5] = PS[4]
A[4,6] = 1.0-PS[4]
A[5,5] = 1.0
A[6,6] = 1.0

A = A[1:N+1,1:N+1]  # get zero offset index

# A1 is a second A matrix to test for the special case of A[ij] == 1.0
# INITIAL State Transition Probabilities
#  make A one bigger to make index humannode
# note dummy value for PS[0] for math consistency
PS = [0, 1.0, 0.75, .8, 0.9, 1.0,1.0]
if len(PS) != N+1:
    print 'Incorrect PS length'
    quit()
A1 = np.zeros((N+1,N+1))
A1[1,2] = PS[1]
A1[1,6] = 1.0-PS[1]
A1[2,3] = PS[2]
A1[2,6] = 1.0-PS[2]
A1[3,4] = 1.0-PS[3]
A1[3,5] = PS[3]
A1[4,5] = PS[4]
A1[4,6] = 1.0-PS[4]
A1[5,5] = 1.0
A1[6,6] = 1.0

A1 = A1[1:N+1,1:N+1]  # get zero offset index
 
######################
sig = 2.0 

Ratio = 3.0
#
#  these values are place-holders, replaced later
outputs = {'l1':2, 'l2': 5, 'l3':8, 'l4': 8,  'OutS':10, 'OutF':20}

Pi = np.zeros(N)
Pi[0] = 1.0      # always start at state 1
 
#  This is probably not nesc:   names.index('l3') == 2
statenos = {'l1':1, 'l2': 2, 'l3':3, 'l4':4,  'OutS':5, 'OutF':6}

###  Regenerate output means:
i = 20
di = Ratio*sig  # = nxsigma !!
for n in outputs.keys():
    outputs[n] = i
    i += di
    
    
    
#####################################################
of = open('HMM_test_rep.txt', 'w') # clobber old report

B = A.copy()
M = HMM_setup(Pi, B, sig, names)

outputAmat(M.transmat_,"Initial A Matrix",names,of)
print 'Perturbing by 0.25 -----'
HMM_perturb(M, 0.25)  
outputAmat(M.transmat_, "Perturbed A Matrix", names, of)

A_row_check(M.transmat_, of)
A_row_test(M.transmat_, of)

print '-------------------------- resulting distance metrics -------------------'

x = Adiff(M.transmat_, A ,names)
#    return [e,e2,em,N2,imax,jmax,anoms,erasures]

print 'EAinfty = ',x[2]    # em
print 'EAavg   = ',x[1]    # e2

assert x[2] > 0.0 , 'Perturbation caused no difference in A matrices'
assert x[1] > 0.0 , 'Perturbation caused no difference in A matrices'


print '-------------------------- test distance metrics -------------------'
print ' each element += 0.2  both errors should = 0.2'

# reset the two matrices A and B to identical
B = A.copy()
[r1, c1] = B.shape
#r1 -= 2    # don't perturb for Os and Of states
for r in range(r1):
    for c in range(c1):
        if B[r][c] > 0:  # apply NON RANDOM perturb
            B[r][c] += 0.2  #  test for metrics

x = Adiff(A, B ,names)
#    return [e,e2,em,N2,imax,jmax,anoms,erasures]

#outputAmat(A,'A', names, sys.stdout)
#outputAmat(B,'B', names, sys.stdout)
fs = 'Problem with distance metrics Adiff(A,B,names)'
print 'EAinfty = ',x[2]    # em
testeps = 0.00001
assert x[2] - 0.2 < testeps, fs
print 'EAavg   = ',x[1]    # e2
assert x[1] - 0.2 < testeps, fs

##  Test special A matrix with 1.0 element in it


print '\n\nTesting A matrix with a 1.0 element'
M1 = HMM_setup(Pi, A1, sig, names)
B = A1.copy()
#outputAmat(A,"Initial A Matrix",names,of)
print 'Perturbing by 0.25'
HMM_perturb(M1, 0.25)  
#outputAmat(M.transmat_, "Perturbed A Matrix", names, of)
 
A_row_test(M1.transmat_, of)
          
print '\n\n HMM_perturb(M, d) PASSES all tests\n\n'
of.close()
