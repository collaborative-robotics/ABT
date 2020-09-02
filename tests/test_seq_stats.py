#!/usr/bin/python
# 
#      Template for testing ABT functionality
#
#

import os
import sys

#import random as random
import math as m
import numpy as np


import unittest
import mock

import tests.common as tc

import abt_constants
from abtclass import *
from hmm_bt import *
 
# b3 class modified by BH, local version in current dir
import b3 as b3          # behavior trees

MODEL = BIG

max_avg_abs_non_zero = 0.02
max_max_abs_non_zero = 0.03
  
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator

#from abt_constants import *

##  The ABT file for the task (CHOOSE ONE)
tc.all_random_seeds(430298219)  # we want same seqs every time so we can assert for right answers                        

MODEL = SMALL
if MODEL== BIG:
    from peg2_ABT import * # big  14+2 state  # uses model01.py
    from model01 import *
    model = modelo01
if MODEL==SMALL:
    from simp_ABT import *  # small 4+2 state # uses model02.py
    from model00 import *
    model = modelo00

GENDATA = True
Ratio = 4    # doesn't matter so keep it fixed.

PLOTTING = False  # for a graph of discrete Gaussian

testeps = 2.0
testsigeps = 2.0 # sigma must be within this of actual sigma.

print 'Test sig epsilon: ', testsigeps/ac.sig, ' standard deviations'

##
#    Supress Deprecation Warnings from hmm_lean / scikit
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

##   Set up research parameters mostly in abt_constants.py

logdir = 'tests/data_for_tests/'
lfname = logdir + 'Sequence_Stats_test.txt' # file name for output log info


class Test_Seq_Stats(unittest.TestCase):


    def test_SS01(self):


        ##
        #    Supress Deprecation Warnings from hmm_lean / scikit
        import warnings
        warnings.filterwarnings('ignore', category=DeprecationWarning)

        ##   Set up research parameters mostly in abt_constants.py

         

        print 'Starting observation stats test on ', lfname
        if GENDATA:
            print ' Generating NEW data'

            NEpochs = 100000

        num_states = model.n
            
        print 'Initial num states: ', num_states

        logf = open(lfname,'r')



        #
        #   Check that we have the right model for the data (for comparison)
        #


        print '\n\n\n                       Sequence Test Report '
        print '                             (test_seq_stats.py) '
        print '                                     checking state transition stats from ground truth \n\n'

        #state_selection = 'l2'

        X = []   # state names 
        Y = []   # observations
        Ls =[]   # length of the epochs/runouts

        seq = [] # current state seq
        os  = [] # current obs seq

        Ahat = np.zeros((model.n,model.n))  # N def in model0x

        nsims = 0
        for line in logf:
            #print '>>>',line
            line = line.strip()
            if line == '---': 
                nsims += 1
                # store freq of state transitions
                for i in range(len(seq)):
                    if(i>0):  # no transition INTO first state
                        assert seq[i] in model.names, 'Unknown state visited.  Probably wrong MODEL (BIG/SMALL) selection.'
                        j = model.names.index(seq[i])
                        k = model.names.index(seq[i-1])
                        Ahat[k,j] += 1
                Ls.append(len(os)) 
                os  = []
                seq = []
            else:
                [state, obs ] = line.split(',')
                seq.append(state)
                os.append(obs)
                X.append(state)
                Y.append([int(obs)])
                os.append([int(obs)])


        #  divide to create frequentist prob estimates
        for i in range(model.n-2):  # rows (but NOT OutS and OutF cause they don't transition out)
            rsum = np.sum(Ahat[i,:])
            #print 'A,sum', Ahat[i,:], rsum
            for j in range(model.n): # cols
                Ahat[i,j] /= rsum
                
        Ahat[-2,-2] = 1.0   # by convention self-state trans in OutS/F but these never occur
        Ahat[-1,-1] = 1.0
                
        #state = model.names[13]

        N = model.n - 2   # don't expect OutF and OutS

        # set up sums for each state
        s1 = np.zeros(N)
        s2 = np.zeros(N)
        n  = np.zeros(N)  # counts for each state

        for i in range(len(X)): 
            for j in range(N):     # accumulate stats for each state
                #print X[j],model.names[j]
                if X[i] == model.names[j]:
                    s1[j] +=  Y[i][0]
                    s2[j] += (Y[i][0])**2
                    n[j]  += 1
                    #print X[j], s1[j], s2[j]

        outputAmat(A,   "Model A Matrix",    model.names, sys.stdout)    
        outputAmat(Ahat,"Empirical A Matrix",model.names, sys.stdout)

        print 'A-matrix estimation errors: '

        Adiff_Report(A,Ahat,model.names) 

        [e,e2,em,N2,imax,jmax,anoms,erasures] = Adiff(A,Ahat,model.names)
            
        ####################################################################
        #
        #     State Transition Stats assertions
        #

        #max_avg_abs_non_zero = 0.01   # (see top)
        #max_max_abs_non_zero = 0.03

        assert abs(e2) < max_avg_abs_non_zero, 'Too much avg RMS error in non-zero elements: '+str(e2)
        assert abs(em) < max_max_abs_non_zero, 'Too much MAX RMS error in non-zero elements: '+str(em)

        print 'Erasures: ', erasures

        assert erasures != 'None', 'Erasure(s) found'
        assert anoms    != 'None', 'Anomaly(s) found'

            
        print 'Studied ',len(X), 'observations,', model.n, 'state model'

        #################################################################
        #
        #   Generate state visit frequencies report
        #
        #
        nv = np.zeros(model.n)
        for i in range(len(X)):    # go through data once
            s = X[i]  # current true state    
            nv[names.index(s)] += 1 # count the visit 
            
        print '\n\nState Visit Frequency Report'
        for n in names:
            v = nv[names.index(n)]
            #print n, ' visited ', v ,'times out of ', nsims, ' = ', float(v)/float(nsims)
            print '{:>10s}: visited {:6d} times out of {:6d} simulations ({:5.1f}%)'.format(n,int(v),nsims,100.0*float(v)/float(nsims))
                
        print 'Sequence test PASSED'


if __name__ == '__main__':
    unittest.main()

