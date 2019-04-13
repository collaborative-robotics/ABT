#!/usr/bin/python
#
#   Utilities for BT-HMM_
#

import numpy as np
from random import *
import matplotlib.pyplot as plt
import editdistance as ed       #sudo pip install editdistance
from tqdm import tqdm
import os
import sys

#sudo pip install scikit-learn  # dep for hmmlearn
#pip install -U --user hmmlearn
from hmmlearn import hmm
import random as random

from abt_constants import *
import abtclass as abtc

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

#def A_non_zero(A):
    #'''
    #make sure trans matrix has no 0.0 elements
    #'''
    #eps = 1.0E-5        # min value
    ##print 'A-matrix row test'
    #for i in range(A.shape[0]):
        #for j in range(A.shape[1]):
            #if(A[i,j] < eps):
                #A[i,j] = eps
        #sum = 0.0
        #for j in range(A.shape[1]):
            #sum += A[i,j]
        #for j in range(A.shape[1]):
            #A[i,j] /= sum


def HMM_setup(model, toler=0.01, maxiter=20):     #  New: setup model.B:  discrete emission probs.
    #print 'Size: A: ', A.shape
    l = model.A.shape[0]
    #print 'len(Pi): ', len(Pi), l
    #M = hmm.GaussianHMM(n_components=l, covariance_type='diag', n_iter=maxiter, tol=toler, init_params='')
    #M.typestring = 'GaussianHMM'
    #   fit all params:  params='ste'
    #   fit only A matrix:  params='t'

    M = hmm.MultinomialHMM(n_components=l, n_iter=maxiter, params='t', init_params='',verbose=True)
    M.typestring = 'MultinomialHMM'

    #M.n_features = 1
    M.startprob_ = model.Pi
    M.transmat_ = model.A
    #############################  Gaussian emissions
    #  set emissionprob below
    #  .means and .covars are for GaussianHMM()
    #tmpmeans = []
    #for i in range(len(names)):
        #tmpmeans.append( [ outputs[names[i]] ] )
    #M.means_ = np.array(tmpmeans)
    #M.means_ = 0.5*np.ones(l).reshape([l,1])  # is this a bug??? what about \delta\mu * i???
    #m = np.zeros(model.n)
    #for i,n in enumerate(model.names):
        #m[i] = model.outputs[n]
    #m.shape = [l,1]
    #M.means_ = m
    #print 'means shape: ', M.means_.shape
    #tmpcovars = model.sigma * np.ones((l))
    #tmpcovars.shape = [l,1]
    #M.covars_ = np.array(tmpcovars)
    #########################
    sig = 2.0  # HACK!!!
    #############################   Multinomial emissions
    #   setup discrete model.B for MultinomialHMM()
    for i,n in enumerate(model.names):
        tmp_leaf = abtc.aug_leaf(0.500)  # dummy leaf to use SetObsDensity() method
        tmp_leaf.set_Obs_Density(model.outputs[n], sig)
        #print 'mean: ', model.outputs[n]
        for j in range(NSYMBOLS):
            model.B[i,j] = tmp_leaf.Obs[j]    # guarantees same P's as ABT(!)
    M.emissionprob_ = np.array(model.B.copy())  # docs unclear on this name!!!!
    return M


def HMM_model_sizes_check(M):
    #print 'Model size check:'
    #print 'Transmatrix: ',M.transmat_.shape
    #print 'Outputs:     ',M.means_.shape
    #print 'done...'
    #quit()
    l = M.transmat_.shape[0]
    fs = 'Your HMM has inconsistent model sizes and will not run: quitting'
    assert M.transmat_.shape == (l,l), fs
    #assert M.means_.shape == (l,1), fs


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


#
# initialize A-matrix to all NxN elements random
#  (subject to Sum(row) == 1)
#
def HMM_fully_random(model):
    A_rand = model.A.copy()
    [rn,cn] = A_rand.shape
    for r in range(rn):
        rsum = 0.0
        for c in range(cn):
            A_rand[r][c] = random.random()
            rsum += A_rand[r][c]
        for c in range(cn):  # normalize the rows
            A_rand[r][c] /= rsum

    # randomize means of the output observations
    B = np.zeros(model.n)
    for i,n in enumerate(model.names):
        B[i] = int( 0.5 + FIRSTSYMBOL + (NSYMBOLS-FIRSTSYMBOL)*random.random() )
    B.shape = [rn,1]   # match req. of hmmlearn
    return A_rand, B

# apply a delta (random +-) to the elements of A
#   subject to sum of row = 1.]
#
#    NEW: if d > 5  initialize A matrix to RANDOM values
#

def HMM_perturb(M, d, model=abtc.model(1)):
    ''' M = an hmmlearn HMM object
        d = perturbation (0 < d < 1.0)
        model = model parameters
        '''
    assert len(model.names) > 1, 'HMM_perturb() [in hmm_bt.py] must be called with a model (2nd argument)'
    A = M.transmat_
    #np.save("M_trans",M.transmat_)
    #np.save("Means",M.means_)
    [r1, c1] = A.shape
    r1 -= 2    # don't perturb for Os and Of states
    for r in range(r1):  # go through the rows
        flag = -1
        rowcnt = 0   # how many non-zero elements in this row?
        for c in range(c1):
            if A[r][c] > 0.0000001:
                rowcnt += 1
        ##assert rowcnt > 1, 'only 1 non-zero element should not occur ('+str(rowcnt)+') - quitting'
        if rowcnt == 2:    # ABT type models and SLR models
            for c in range(c1):
                # second non-zero element of row
                #print 'looking at element: ',r,c
                #print 'flag = ', flag
                if flag > 0  and A[r][c] > 0:
                    A[r][c] = 1.0 - flag
                    #print 'setting second element to', 1.0 - flag
                # first non-zero element of row
                elif A[r][c] > 0.0000001:
                    if abs(A[r][c] - 1.0) < 0.000001: # don't mess with 1.0 transitions
                        continue
                    change =  randsign() * d
                    #print 'Applying change 1.0 + ',change
                    pbef = A[r][c]
                    A[r][c] *= (1.0 + change)
                    paft =  A[r][c]
                    #print 'Actual Change: ', (paft-pbef)/pbef
                    if A[r][c] >  0.9999:
                        A[r][c] = 0.9999  # don't allow going to 1.0 or above
                    if A[r][c] < 0.0000001:  # don't allow negative
                        A[r][c] = 0.0000001
                    flag = A[r][c]      # store value (for use above)
        elif rowcnt == 3:     #ABT + duration type models
            flag = 0
            for c in range(c1):
                 if c > r: # only above diagonal (don't change A[r,r]
                     if flag > 0 and A[r][c] > 0:
                        # we've found the second transition to one of two next states
                        A[r][c] = (1.0-A[r][r]) - flag  # keep sum == 1.0
                     elif A[r][c] > 0.0000001:
                        if abs(A[r][c] - 1.0) < 0.000001: # don't mess with 1.0 transitions
                            continue
                        # we've found the first transition to one of two next states
                        change =  randsign() * d
                        #print 'Applying change 1.0 + ',change
                        pbef = A[r][c]
                        A[r][c] *= (1.0 + change)
                        paft =  A[r][c]
                        #print 'Actual Change: ', (paft-pbef)/pbef
                        if A[r][c] >  0.9999:
                            A[r][c] = 0.9999  # don't allow going to 1.0 or above
                        if A[r][c] < 0.0000001:  # don't allow negative
                            A[r][c] = 0.0000001
                        flag = A[r][c]      # store value (for use above)

        else:
             #print 'I dont know how to perturb ', rowcnt, ' non-zero values in a row'
             #quit()
             pass    # if there is a 1.0 transition (100% success or fail) just leave it alone

    # Perturb B matrix means.  Each mean must be perturbed by same amount, not by a 1+delta as above
    #    because before, some states had bigger probability errors than others.
    sigma = 2.0    #  HACK
    bdelta = 2 * d * sigma    # factor of 2 just feels better(!)
    #
    #  New coding for Multinomial - explicit probs over the symbol integers
    #   (some kind of "shift"??)  or just regenerate.
    #
    if M.typestring == 'GaussianHMM':
        B = M.means_
        for i,b in enumerate(B):
            #B[i] = int(0.5 + b * (1.0 +  randsign() * d))
            B[i] += randsign() * bdelta
        M.means_ = B
    elif M.typestring == 'MultinomialHMM':
        #########################
        sig = 2.0  # HACK!!!
        #############################   Multinomial emissions
        #   setup discrete model.B for MultinomialHMM()
        for i,n in enumerate(model.names):
            tmp_leaf = abtc.aug_leaf(0.500)  # dummy leaf to use SetObsDensity() method
            #perturb the mean by bdelta before generating the emission probs.
            newmean = model.outputs[n] + randsign() * bdelta
            #print 'Setting mean for state ',i, 'from ' , model.outputs[n], ' to ', newmean
            tmp_leaf.set_Obs_Density(newmean, sig)
            for j in range(NSYMBOLS):
                model.B[i,j] = tmp_leaf.Obs[j]    # guarantees same P's as ABT(!)
        M.emissionprob_ = np.array(model.B.copy())  # docs unclear on this name!!!!
    else:
        print 'Unknown model typestring'
        quit()
    return

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

######################################################
#
#   Print an A matrix comparison/diff report
#

def Adiff_Report(A1,A2,names,of=sys.stdout):
    [e,e2,em,N2,im,jm,anoms,erasures] = Adiff(A1, A2, names)

    N = len(names)
    print >> of, 'RMS A-matrix error: {:.3f}'.format(e)
    print >> of, 'RMS A-matrix error: {:.8f} (only the {:d}/{:d} non zero elements)'.format(e2,N2,N*N)
    print >> of, 'Max abs A-matrix error: {:.3f} (at {:d} to {:d})'.format(em,im,jm)
    if len(anoms) == 0:
        anoms = 'None'
    print >> of, 'Anomalies: ', anoms
    if len(erasures) == 0:
        erasures = 'None'
    print >> of, 'Erasures : ', erasures

def Adiff(A1,A2,names):    # from 8/28
    e = 0
    em = -9.9999E100
    imax = np.nan
    jmax = np.nan
    e2 = 0   # avg error of NON ZERO elements
    N = A1.shape[0]
    assert A1.shape == A2.shape, 'Adiff: A-matrix size mismatch!'
    assert not np.isnan(A1).all(), 'A-matrix contains nan'
    assert not np.isnan(A2).all(), 'A-matrix contains nan'
    #print 'Adiff: A shape: ', A1.shape
    #print "A1: "
    #print A1
    #print "A2: "
    #print A2

    N2 = 0   # count the non-zero Aij entries
            #  should be 2(l+2) for ABT-based matrices
    anoms = [] #identification
    erasures = []
    for i in range(N):
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
            if(A1[i,j]==0.0 and A2[i,j]>0.0):    # for regular but not random perturbations
                anoms.append([i,j])
            if(A1[i,j]>0.0 and A2[i,j] < 0.0000001):
                erasures.append([names[i],names[j]])
    e  = np.sqrt(e/(N*N))  # div total number of Aij elements
    e2 = np.sqrt(e2/N2)  # RMS error of NON zero A[1]ij
    em = np.sqrt(em)     # Max error
    #print 'imax, jmax; ', imax, jmax
    return [e,e2,em,N2,imax,jmax,anoms,erasures]


###############################################
# compare two A-matrices  (NEW)
#

#def Adiff(A1,A2,names):
    #e = 0
    #e_abs_total = 0.0
    #em = -99999.9
    #e2 = 0   # avg error of NON ZERO elementstoler=0.01, maxiter=20
    #N = A1.shape[0]
    ##print 'Adiff: A shape: ', A1.shape
    #N2 = 0   # count the non-zero Aij entries
            ##  should be 2(l+2) of course
    #anoms = [] #identification
    #erasures = []
    #for i in range(N-2): # skip last two rows which are 1.000
        #for j in range(N):
            #e1 = (A1[i,j]-A2[i,j])**2
            #ea  = abs(A1[i,j]-A2[i,j])
            ##print 'error: ', e1,i,j
            ##print 'A1[ij] ',A1[i,j], '  A2[ij] ',A2[i,j], (A1[i,j]-A2[i,j])
            #if(ea > em):   # should be absolute error not e^2
                #em = ea
                #imax = i+1   # change from array index to state numbers
                #jmax = j+1
                ##print "storing emax: ", em, i,j
            #if(A1[i,j] > 0.000001):
                #e2 += ea              # accumulate error for non-zero Aij
                #N2 += 1
            #e_abs_total += ea
            #if(A1[i,j]==0.0 and A2[i,j]>0.0):  # NOTE: implies direction btwn A1 and A2
                #anoms.append([i,j])
            #if(A1[i,j]>0.0 and A2[i,j] < 0.0000001):
                #erasures.append([names[i],names[j]])
    #e  = (e_abs_total/(N*N))  # div total number of Aij elements
    #e2 = (e2/N2)  # RMS error of NON zero Aij
    ##print 'imax, jmax; ', imax, jmax
    #return [e,e2,em,N2,imax,jmax,anoms,erasures]


###############################################################
# Evaluation of Viterbi
#
#   Blake's new start
#
def Veterbi_Eval(p,x,names,l,statenos):
    '''
    p = state sequence estimates (concatenated state seqs, np.array() of numbers)
    x = true state sequences (list of numbers)
    names = list of state names (Nx1)
    l = lengths of each state sequence in 'x'
    statenos =
    '''
    nseqs = len(l)
    maxd = -999999
    count = 0
    totald = 0
    states_visited = set(x)
    assert len(names) == len(states_visited), 'Viterbi Evaluation: wrong states/state-names'
    p1 = list(p)
    offset = 0
    for i in range(len(l)):  # iterate over sequences
        st1 = ''
        st2 = ''
        for j in range(l[i]):  # iterate over symbols in seq i
            st1 += str(p[offset+j])
            st2 += str(x[offset+j])
        d1 = ed.eval(st1,st2)
        d =  d1 / float(len(st2))  # Str edit distance / length of true seq.
        if d > maxd:
            maxd = d
        totald += d
        count += d1
        offset+=j+1
    avgd = totald / float(nseqs)
    return [avgd, maxd, count]
    # avgd:  average sed per symbol
    # maxd:  max sed for any seq
    # count:  total sed for all seqs


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
