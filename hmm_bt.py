#!/usr/bin/python
#
#   Track a BT evolution with corresponding HMM!!
#   match fig BT-01164_Huge.png
#     from BT-Hmm proposal   May 18

import numpy as np
import matplotlib.pyplot as plt

from hmmlearn import hmm

# INITIAL State Transition Probabilities
#  make A one bigger to make index human
A = np.zeros((17,17))
A[1,2] = 1.0
A[2,3] = 0.90
A[2,4] = 0.10
A[3,4] = 0.05
A[3,6] = 0.95
A[4,5] = 0.90
A[4,16] = 0.10
A[5,6] = 0.95
A[5,16] = 0.05
A[6,7] = 1
A[7,8] = 0.090
A[7,10] = 0.10
A[8,9] = 0.05
A[8,11] = 0.95
A[9,10] = 0.90
A[9,16] = 0.10
A[10,11] = 0.95
A[10,16] = 0.05
A[11,12] = 1
A[12,13] = 0.90
A[12,16] = 0.10
A[13,14] = 0.95
A[13,16] = 0.05
A[14,15] = 0.80
A[14,16] = 0.20

A = A[1:17,1:17]  # get zero offset index

names = ['l1','l2a1','l2b1','l2a2','l2b2', 'l345', 'l6a1', 'l6b1', 'l6a2', ';6b2', 'l789', 'l10a1', 'l10b1', 'l10c1']

#
Pi = np.zeros(16)
Pi[0] = 1.0      # always start at state 1


M = hmm.GaussianHMM(n_components=16, covariance_type='diag', n_iter=10)
M.n_features = 1

