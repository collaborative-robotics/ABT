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
 
testeps = 0.00001  # epsilon for comparing floats

SMALL = 1
BIG   = 2
MODEL = BIG

logdir = 'logs/'


######################
sig = 2.0 

Ratio = 3.0


if MODEL == SMALL:

    names = ['l1','l2','l3','l4', 'OutS', 'OutF']

    N = len(names)
     
    # PS = prob of success for each node
    # note dummy value for PS[0] for math consistency
    PS = [0, 0.65, 0.75, .8, 0.5000, 1.0,1.0]
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
    PS = [0, 1.0, 0.75, .8, 0.5000, 1.0,1.0]
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
     
    #
    #  these values are place-holders, replaced later
    outputs = {'l1':2, 'l2': 5, 'l3':8, 'l4': 8,  'OutS':10, 'OutF':20}

    #  This is probably not nesc:   names.index('l3') == 2
    statenos = {'l1':1, 'l2': 2, 'l3':3, 'l4':4,  'OutS':5, 'OutF':6}


if MODEL == BIG:    

    names = ['l1','l2a1','l2b1','l2a2','l2b2', 'l345', 'l6a1', 'l6b1', 'l6a2', 'l6b2', 'l789', 'l10a1', 'l10b1', 'l10c1', 'OutS', 'OutF']

    N = len(names)
    # prob success for each node
    # note dummy value for PS[0] for math consistency
    PS = [0.0, 1.0, 0.9, 0.8, 0.9, 0.9, 1.0, 0.9, 0.8, 0.9, 0.9, 1.0,0.9,0.75, 0.5, 1.0, 1.0]
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

    ###  model for 1.0 testing (note A already has 1.0 element)
    A1 = A.copy()
    #
    outputs = {'l1':2, 'l2a1': 5, 'l2b1':8, 'l2a2': 8,  'l2b2':11, 'l345':14, 'l6a1':17, 'l6b1':20, 'l6a2':23, 'l6b2':26, 'l789':29, 'l10a1':33, 'l10b1':36, 'l10c1':28, 'OutS':30, 'OutF':30}

    statenos = {'l1':1, 'l2a1': 2, 'l2b1':3, 'l2a2':4,  'l2b2':5, 'l345':6, 'l6a1':7, 'l6b1':8, 'l6a2':9, 'l6b2':10, 'l789':11, 'l10a1':12, 'l10b1':13, 'l10c1':14, 'OutS':15, 'OutF':16}
    

Pi = np.zeros(len(names))
Pi[0] = 1.0      # always start at state 1
     
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
print '\n\n ------------------------------  ',len(names),' state model perturbation tests -----------------------'
print >>of, '\n\n ------------------------------  ',len(names),' state model perturbation tests -----------------------'
print 'See more detail at: > more HMM_test_rep.txt'
print 'Perturbing by 0.25'
#########################################################################
HMM_perturb(M, 0.25)  
#########################################################################
outputAmat(M.transmat_, "Perturbed A Matrix", names, of)

A_row_check(M.transmat_, of)
A_row_test(M.transmat_, of)

print '-------------------------- resulting distance metrics -------------------'

x = Adiff(M.transmat_, A ,names)
#    return [e,e2,em,N2,imax,jmax,anoms,erasures]

print 'EAmax   = ',x[2]    # em
print 'EAavg   = ',x[1]    # e2

assert x[2] > 0.0 , 'Perturbation caused no difference in A matrices'
assert x[1] > 0.0 , 'Perturbation caused no difference in A matrices'
print 'Model Size: ',len(names)
if len(names) < 8:
    outS_index = 4
else:
    outS_index = 14
outF_index = outS_index+1
assert M.transmat_[outS_index,outS_index] - 1.0 < testeps, 'A 1.0 element was modified'
assert M.transmat_[outF_index,outF_index] - 1.0 < testeps, 'A 1.0 element was modified'


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

assert x[2] - 0.2 < testeps, fs
print 'EAavg   = ',x[1]    # e2
assert x[1] - 0.2 < testeps, fs

##  Test special A matrix with 1.0 element in it


print '\n\n'
print '-------------------------- Testing A-matrix 1.00 elements  -------------------'

M1 = HMM_setup(Pi, A1, sig, names)
B = A1.copy()
#outputAmat(A,"Initial A Matrix",names,of)
print 'Perturbing by 0.25'
HMM_perturb(M1, 0.25)  
#outputAmat(M.transmat_, "Perturbed A Matrix", names, of)
 
A_row_test(M1.transmat_, of)
          
print '\n\n HMM_perturb(M, d) PASSES all tests\n\n'
of.close()
