#!/usr/bin/python
#

#  Test for HMM setup and perturbs


import numpy as np
import matplotlib.pyplot as plt

#sudo pip install scikit-learn  # dep for hmmlearn
#pip install -U --user hmmlearn
from hmmlearn import hmm
#####################################################

#####################################################
from hmm_bt import *
 


###############################################
# compare two A-matrices
#

def Adiff(A1,A2,names):
    e = 0
    em = -99999.9
    e2 = 0   # avge error of NON ZERO elements
    N = A1.shape[0]
    #print 'Adiff: A shape: ', A1.shape
    N2 = 0   # count the non-zero Aij entries 
            #  should be 2(l+2) of course
    anoms = []
    erasures = []
    for i in range(N):
        for j in range(N):
            e1 = (A1[i,j]-A2[i,j])**2
            #print 'error: ', e1,i,j
            #print 'A1[ij] ',A1[i,j], '  A2[ij] ',A2[i,j], (A1[i,j]-A2[i,j])
            if(e1 > em):
                em = np.sqrt(e1)
                imax = i
                jmax = j
                #print "storing emax: ", em, i,j
            if(A1[i,j] > 0.000001):
                e2 += e1
                N2 += 1
            e += e1
            if(A1[i,j]==0.0 and A2[i,j]>0.0):
                anoms.append([i,j])
            if(A1[i,j]>0.0 and A2[i,j] < 0.0000001):
                erasures.append([names[i],names[j]])
    e  = np.sqrt(e/(N*N))  # div total number of Aij elements
    e2 = np.sqrt(e2/N2)  # RMS error of NON zero Aij
    em = np.sqrt(em)     # Max error
    #print 'imax, jmax; ', imax, jmax
    return [e,e2,em,N2,imax,jmax,anoms,erasures]

#####################################################

#####################################################
#from model00 import *


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
of = open('HMM_test_rep.txt', 'w')

M = HMM_setup(Pi, A, sig, names)

outputAmat(A,"Initial A Matrix",names,of)
HMM_perturb(M, 0.01)
outputAmat(M.transmat_, "Perturbed A Matrix", names, of)

A_row_check(M.transmat_, of)
A_row_test(M.transmat_, of)



of.close()
