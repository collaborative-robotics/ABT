#!/usr/bin/python
#
#   Track a BT evolution with corresponding HMM!!
#   match fig BT-01164_Huge.png
#     from BT-Hmm proposal   May 18

import numpy as np
import matplotlib.pyplot as plt

#sudo pip install scikit-learn  # dep for hmmlearn
#pip install -U --user hmmlearn 
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
A[7,8] = 0.90
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
A[15,15] = 1.0
A[16,16] = 1.0

A = A[1:17,1:17]  # get zero offset index


print "Original  A matrix:"
for i in range(16):
    for j in range(16):
        print '{:.3f} '.format(A[i,j]),
    print '\n' 
    
print "A-matrix row check"
for i in range(16):
    r = 0
    for j in range(16):
        r += A[i,j]
    print i, r
    

names = ['l1','l2a1','l2b1','l2a2','l2b2', 'l345', 'l6a1', 'l6b1', 'l6a2', ';6b2', 'l789', 'l10a1', 'l10b1', 'l10c1', 'OutS', 'OutF']

sig = 2.0
outputs = {'l1':2, 'l2a1': 4, 'l2b1':6, 'l2a2':8 ,'l2b2':10, 'l345':12, 'l6a1':14, 'l6b1':16, 'l6a2':18, ';6b2':20, 'l789':22, 'l10a1':24, 'l10b1':26, 'l10c1':28, 'OutS':30, 'OutF':30}
#
Pi = np.zeros(16)
Pi[0] = 1.0      # always start at state 1


M = hmm.GaussianHMM(n_components=16, covariance_type='diag', n_iter=10,init_params='')
#M.n_features = 1
M.startprob_ = Pi
M.transmat_ = A
tmpmeans = []
for i in range(len(names)):
    tmpmeans.append( [ outputs[names[i]] ] )
M.means_ = np.array(tmpmeans)
tmpcovars = sig* np.ones((16))
tmpcovars.shape = [16,1]
M.covars_ = np.array(tmpcovars)


# read in data file



logdir = 'logs/'
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


print "starting HMM fit with ", len(Y), ' sequences.'   
 
quit() 
 
Y=np.array(Y).reshape(-1,1)  # make 2D
Ls = np.array(Ls)
M.fit(Y,Ls)

np.set_printoptions(precision=3,suppress=True)

print "New A matrix:"
for i in range(len(names)):
    for j in range(len(names)):
        print '{:.3f} '.format(M.transmat_[i,j]),
    print '\n' 

quit()

#print "shapes:"
#print "outputs", len(outputs)
#print "means_", (M.means_.shape)
#print "covars", (tmpcovars.shape)
#print "trans",  (M.transmat_.shape)


# Generate sample data
#X, Z = M.sample(50)
#print X.shape, Z.shape 
#print type(X), type(Z)

#for i in range(len(Z)):
    #print names[Z[i]], int(0.5 + X[i,0])
    
    
