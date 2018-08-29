#!/usr/bin/python
#
#   Utilities for BT-HMM_
#

import numpy as np
import matplotlib.pyplot as plt
import sys

#sudo pip install scikit-learn  # dep for hmmlearn
#pip install -U --user hmmlearn
from hmmlearn import hmm
import random as random

def outputAmat(A,title,names,of):        
    print >> of, title   # eg, "Original  A matrix:"
    for i in range(A.shape[0]):
        print >> of, '{0: <7}'.format(names[i]),
        for j in range(A.shape[1]):
            print >> of, '{:.5f} '.format(A[i,j]),
        print >> of, '\n'

def A_row_check(A,of):
    print >> of, "A-matrix row check"  
    eps = 1.0E-6        # accuracy 
    for i in range(A.shape[0]):
        r = 0
        for j in range(A.shape[1]):
            if A[i,j] < 0.0:
                r += 10000000
            r += A[i,j]
        print >> of, i,r
        if abs(r-1.0) > eps:
            print >> of, 'Problem: row ',i,' of A-matrix sum is != 1.0 -or- row contains a P<0  sum = ', r
 
def A_row_test(A,of):
    eps = 1.0E-6        # accuracy 
    #print 'A-matrix row test'
    for i in range(A.shape[0]):
        r = 0
        for j in range(A.shape[1]):
            assert A[i,j] >= 0.0, ' A matrix Prob value < 0.0!'
            assert A[i,j] <= 1.0, ' A matrix Prob value > 1!'
            r += A[i,j]
        #print  'assertion:', i,r
        assert abs(r-1.0) < eps, 'Assert Problem: a row sum of A-matrix is != 1.0, sum = '+str(r)
        
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
    M.means_ = 0.5*np.ones(l).reshape([l,1])  # is this a bug??? what about \delta\mu * i???
    #print 'means shape: ', M.means_.shape
    tmpcovars = sig * np.ones((l))
    tmpcovars.shape = [l,1]
    M.covars_ = np.array(tmpcovars)
    return M




#  Replace ABT transition probabilities with 
# random values (only the non-zero elements tho).

def HMM_ABT_to_random(M):
    # A matrix  
    A = M.transmat_
    [r1, c1] = A.shape
    r1 -= 2    # don't perturb for output states:  Os and Of
    for r in range(r1):
        flag = -1
        for c in range(c1):
            # second non-zero element of row
            #print 'looking at element: ',r,c
            #print 'flag = ', flag
            if flag > 0  and A[r][c] > 0: 
                A[r][c] = 1.0 - flag
                #print 'setting second element to', 1.0 - flag
            # first non-zero element of row
            elif A[r][c] > 0:
                if abs(A[r][c] - 1.0) < 0.000001: # don't mess with 1.0 transitions
                    continue
                A[r][c] = random.random() # Uniform(0.0-1.0)
                flag = A[r][c]      # store value (for use above)
    M.transmat_ = A  # maybe unnecessary??
    

    
# apply a delta (random +-) to the elements of A
#   subject to sum of row = 1.
def HMM_perturb(M, d):
    # A matrix  
    A = M.transmat_
    [r1, c1] = A.shape
    r1 -= 2    # don't perturb for Os and Of states
    for r in range(r1):
        flag = -1
        for c in range(c1):
            # second non-zero element of row
            #print 'looking at element: ',r,c
            #print 'flag = ', flag
            if flag > 0  and A[r][c] > 0: 
                A[r][c] = 1.0 - flag
                #print 'setting second element to', 1.0 - flag
            # first non-zero element of row
            elif A[r][c] > 0:
                if abs(A[r][c] - 1.0) < 0.000001: # don't mess with 1.0 transitions
                    continue
                A[r][c] *= 1.0 + randsign() * d
                if A[r][c] > 0.99:
                    A[r][c] = 0.99  # don't allow going to 1.0 or above
                flag = A[r][c]      # store value (for use above)
                
    M.transmat_ = A    # maybe unnecessary??
    
    # B matrix means
    #B = M.means_
    #for i in range(len(B)):
        #B[i] = B[i] * (1.0 +  randsign() * d)
    #M.means_ = B
    
def randsign():
    a = random.random()
    if a > 0.500:
        return 1
    else:
        return -1
    
# read in observation sequences data file
def read_obs_seqs(logf):
    #logf = open(fn,'r')

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
    #logf.close()
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
    e2 = 0   # avg error of NON ZERO elements
    N = A1.shape[0]
    #print 'Adiff: A shape: ', A1.shape
    N2 = 0   # count the non-zero Aij entries 
            #  should be 2(l+2) of course
    anoms = []
    erasures = []
    for i in range(N-2): # skip last two rows which are 1.000
        for j in range(N): 
            e1 = (A1[i,j]-A2[i,j])**2
            #print 'error: ', e1,i,j
            #print 'A1[ij] ',A1[i,j], '  A2[ij] ',A2[i,j], (A1[i,j]-A2[i,j])
            if(e1 > em):
                em = e1
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

######################################################
#
#   Print an A matrix comparison/diff report
#

def Adiff_Report(A1,A2,names,of=sys.stdout):
    [e,e2,em,N2,im,jm,anoms,erasures] = Adiff(A1, A2, names)


    print >> of, 'RMS  A-matrix error: {:.3f}'.format(e)
    print >> of, 'RMS  A-matrix error: {:.8f} ({:d} non zero elements)'.format(e2,N2)
    print >> of, 'Max  A-matrix error: {:.3f} (at {:d} to {:d})'.format(em,im,jm)
    if len(anoms) == 0:
        anoms = 'None'
    print >> of, 'Anomalies: ', anoms
    if len(erasures) == 0:
        anoms = 'None'
    print >> of, 'Erasures : ', erasures 



