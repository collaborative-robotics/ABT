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

# BT and HMM parameters here
#from  model00 import *

        
def outputAmat(A,title,names,of):        
    print >> of, title   # eg, "Original  A matrix:"
    for i in range(A.shape[0]):
        print >> of, '{0: <7}'.format(names[i]),
        for j in range(A.shape[1]):
            print >> of, '{:.3f} '.format(A[i,j]),
        print >> of, '\n'

def A_row_check(A,of):
    print >> of, "A-matrix row check"
    for i in range(A.shape[0]):
        r = 0
        for j in range(A.shape[1]):
            r += A[i,j]
        print >> of, i,r
        if r > 1.0:
            print >> of, 'Problem: row ',i,' of A-matrix sum is > 1.0'
            quit()

#quit()

def HMM_setup(Pi, A, sig, names):
    #print 'Size: A: ', A.shape
    l = A.shape[0]
    #print 'len(Pi): ', len(Pi), l
    M = hmm.GaussianHMM(n_components=l, covariance_type='diag', n_iter=10, init_params='')
    #M.n_features = 1
    M.startprob_ = Pi
    M.transmat_ = A
    #tmpmeans = []
    #for i in range(len(names)):
        #tmpmeans.append( [ outputs[names[i]] ] )
    #M.means_ = np.array(tmpmeans)
    M.means_ = 0.5*np.ones(l).reshape([l,1])
    print 'means shape: ', M.means_.shape
    tmpcovars = sig * np.ones((l))
    tmpcovars.shape = [l,1]
    M.covars_ = np.array(tmpcovars)
    return M


# read in observation sequences data file
def read_obs_seqs(fn):
    logf = open(fn,'r')

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
    Y=np.array(Y).reshape(-1,1)  # make 2D
    Ls = np.array(Ls)
    return [X,Y,Ls]

#print 'Shapes: '
#print 'Y', Y.shape
#print Y
#print 'Ls', Ls.shape
#print Ls

#quit()



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


