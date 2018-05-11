#!/usr/bin/python
#
#   Track a BT evolution with corresponding HMM!!
#   match fig BT-01164_Huge.png
#     from BT-Hmm proposal   May 18

import numpy as np
import matplotlib.pyplot as plt
import datetime

#sudo pip install scikit-learn  # dep for hmmlearn
#pip install -U --user hmmlearn
from hmmlearn import hmm

# BT and HMM parameters here
from  model01 import *

########## results output file

outputdir = 'out/'
oname = 'hmm_fit_out_'+datetime.datetime.now().strftime("%y-%m-%d-%H-%M")

of = open(outputdir+oname,'w')

print >> of, "Original  A matrix:"
for i in range(16):
    print >> of, '{0: <7}'.format(names[i]),
    for j in range(16):
        print >> of, '{:.3f} '.format(A[i,j]),
    print >> of, '\n'

print >> of, "A-matrix row check"
for i in range(16):
    r = 0
    for j in range(16):
        r += A[i,j]
    print >> of, i,r
    if r > 1.0:
        print >> of, 'Problem: row ',i,' of A-matrix sum is > 1.0'
        quit()

#quit()

M = hmm.GaussianHMM(n_components=16, covariance_type='diag', n_iter=10, init_params='')
#M.n_features = 1
M.startprob_ = Pi
M.transmat_ = A
tmpmeans = []
for i in range(len(names)):
    tmpmeans.append( [ outputs[names[i]] ] )
M.means_ = np.array(tmpmeans)
tmpcovars = sig * np.ones((16))
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


print "starting HMM fit with ", len(Y), ' observations.'


Y=np.array(Y).reshape(-1,1)  # make 2D
Ls = np.array(Ls)

#print 'Shapes: '
#print 'Y', Y.shape
#print Y
#print 'Ls', Ls.shape
#print Ls

#quit()

M.fit(Y,Ls)

#np.set_printoptions(precision=3,suppress=True)

print >> of, "New A matrix:"
for i in range(len(names)):
    print >> of, '{0: <7}'.format(names[i]),
    for j in range(len(names)):
        print >> of, '{:.3f} '.format(M.transmat_[i,j]),
    print >> of, '\n'


# compute A matrix errors etc

e = 0
em = 0
N = len(names)
anoms = []
erasures = []
for i in range(N):
    for j in range(N):
        e1 = (A[i,j]-M.transmat_[i,j])**2
        if(e1 > em):
            em = e1
        e += e1
        if(A[i,j]==0.0 and M.transmat_[i,j]>0.0):
          anoms.append([i,j])
        if(A[i,j]>0.0 and M.transmat_[i,j] < 0.0000001):
          erasures.append([names[i],names[j]])
e /= np.sqrt(N*N)
em = np.sqrt(em)

print >> of, 'RMS  A-matrix E**2: {:.3f}'.format(e)
print >> of, 'Max     A-matrix E: {:.3f}'.format(em)
if len(anoms) == 0:
    anoms = 'None'
print >> of, 'Anomalies: ', anoms
if len(erasures) == 0:
    anoms = 'None'
print >> of, 'Erasures : ', erasures
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


