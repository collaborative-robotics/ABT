#!/usr/bin/python
#
#   Utilities for BT-HMM_
#

import numpy as np
import matplotlib.pyplot as plt
import editdistance as ed
from tqdm import tqdm
import os
import sys

#sudo pip install scikit-learn  # dep for hmmlearn
#pip install -U --user hmmlearn
from hmmlearn import hmm
import random as random

def outputAmat(A,title,names,of=sys.stdout):
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
#   subject to sum of row = 1.]
def HMM_perturb(M, d):
      # A matrix
    A = M.transmat_
    #np.save("M_trans",M.transmat_)
    #np.save("Means",M.means_)
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
    logf.close()
    return [X,Y,Ls]

#print 'Shapes: '
#print 'Y', Y.shape
#print Y
#print 'Ls', Ls.shape
#print Ls

#quit()


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
    anoms = [] #identification
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
###############################################################
# Evaluation of Veterbi
def Veterbi_Eval(p,x,names,l,statenos):
    x = np.array(x)
    counter = 0
    b = np.zeros((len(l),len(names)))
    predict = np.empty((len(l),len(names)), dtype = object)
    x_sorted = np.empty((len(l),len(names)), dtype = object)
    e = np.empty((p.shape[0],1), dtype = object)
    for i in range(len(l)):
        for j in range(l[i]):
            b[i][j] = p[counter] # sorted prediction according to the state number (Number of itertions * number of states)
            predict[i][j] = names[p[counter]] # sorted predicted data with names
            x_sorted[i][j] = x[counter] # Orignal Sorted Simulation
            e[counter] = names[p[counter]] # Predicted Names list
            counter+=1
    for i in range(len(e)):
        e[i] = statenos[np.ndarray.item(e[i])]
        x[i] = statenos[x[i]]
    totald = ed.eval(np.array2string(e),np.array2string(x))
    cost = np.empty(len(l))
    count = 0
    for i in tqdm(range(len(l))):
        cost[i] = ed.eval(np.array2string(predict[i]),np.array2string(x_sorted[i])) # Cost per data string
        if cost[i]==0:
            count+=1
    return [totald, cost, count]

##############################################
#Forward Pass
##############################################
def Foward_eval(obs,l,M):
    # counter = 0
    # os.system('clear')
    # print "######################################",obs.shape
    # obs_sequence = 0
    # while counter < len(l):
    #     obs_slice = obs[counter:(l[obs_sequence]-1)]
    #     foward = np.zeros((M.transmat_.shape[0],l[obs_sequence]))
    #     for s in range(M.transmat_.shape[0]):
    #         forward[s][0] = M.startprob_[s] * obs_slice[0,s]
    #     for t in range (1,len(obs.slice)):
    #         for s in range (M.transmat_.shape[0]):
    #             for last_step in range(M.transmat_.shape[0]):
    #                 foward[s,t] += foward[t-1,last_step]*M.transmat_[last_step,s]*obs_slice[t,s]
    counter = 0
    logprob = 0
    log_avg = 0
    for i in range(len(l)):
        sample = obs[counter:counter+l[i]]
        logprob += M.score(sample,[l[i]])
        counter += l[i]
    log_avg = logprob/len(l)
    return log_avg
######################################################
#Plotter
######################################################
def Plotter(master,y):
    #Foward_eval
    ffig, fax = plt.subplots(1,1)
    for run in range(master.shape[1]):
        labeler = "Run Number "+ str(run)
        fax.plot(y,master[0,run,:,0],label = labeler)
        fax.set(ylabel='Average Log Probability',xlabel='HMM Delta',title = 'Forward')
        fax.grid()
    vfig, vax = plt.subplots(1,1)
    vfig2, vax2 = plt.subplots(1,1)
    for run in range(master.shape[1]):
        labeler = "Run Number "+ str(run)
        vax.plot(y,master[1,run,:,0], label  = labeler)
        vax.set(ylabel='Total Edit Distance',xlabel='HMM Delta',title = 'Viterbi')
        vax.grid()
    for run in range(master.shape[1]):
        labeler = "Run Number "+ str(run)
        vax2.plot(y,master[1,run,:,2], label  = labeler)
        vax2.set(ylabel='Number of Exact Matches',xlabel='HMM Delta',title = 'Viterbi')
        vax2.grid()
    bfig, bax = plt.subplots(1,1)
    bfig2,bax2 = plt.subplots(1,1)
    bfig3,bax3 = plt.subplots(1,1)
    for run in range(master.shape[1]):
        labeler = "Run Number "+ str(run)
        bax.plot(y,master[2,run,:,0], label = labeler)
        bax.set(ylabel='Eaverage Distance',xlabel='HMM Delta',title = 'BaumWelch')
        bax.grid()
    for run in range(master.shape[1]):
        labeler = "Run Number "+ str(run)
        bax2.plot(y,master[2,run,:,1], label = labeler)
        bax2.set(ylabel='EAinfty',xlabel='HMM Delta',title = 'BaumWelch')
        bax2.grid()
    for run in range(master.shape[1]):
        labeler = "Run Number "+ str(run)
        bax3.plot(y,master[2,run,:,2], label = labeler)
        bax3.set(ylabel='EMax',xlabel='HMM Delta',title = 'BaumWelch')
        bax3.grid()
    plt.legend(handles=[fax,vax,bax ])
    ffig.savefig("forward.png")
    vfig.savefig("Veterbi.png")
    vfig2.savefig("Veterbi2.png")
    bfig.savefig("BaumWelch.png")
    bfig2.savefig("BaumWelch2.png")
    bfig3.savefig("BaumWelch3.png")
#print "shapes:"
#print "outputs", len(outputs)
#print "means_", (M.means_.shape)
#print "covars", (tmpcovars.shape)
#print "trans",  (M.transmat_.shape)