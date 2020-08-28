#!/usr/bin/python
# 
#      Template for testing ABT functionality
#
#

import os
import sys

# b3 class modified by BH, local version in current dir
import b3 as b3          # behavior trees
#import random as random
import math as m
import numpy as np


import unittest
import mock

import tests.common as tc
import numpy as np
import abt_constants
from abtclass import *
from hmm_bt import *
 

##!/usr/bin/python
##
### hmm model params for SIMPLE 4-state BT
#import numpy as np
#import sys

import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator

#from abt_constants import *

##  The ABT file for the task (CHOOSE ONE)

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

logdir = 'tests/detailed_reports/'
lfname = logdir + 'Observation_Stats_test.txt' # file name for output log info



class Test_Observ_Stats(unittest.TestCase):


    def test_ObStat01(self):

        ############################################


        refdataname = lfname

        # from old command line usage
        #nargs = len(sys.argv)
        #if nargs == 1:
            #print 'Please use a filename on command line'
            #print 'Args: ', sys.argv
            #print 'Usage: '
            #print '> test_obs_stats   [GENDATA|filename]'
            #quit()
        #elif nargs == 2:
            #if(sys.argv[1] == "GENDATA"):
                #GENDATA = True 
                #lfname = logdir+'TSTstatelog.txt'
            #else:
                #lfname = str(sys.argv[1]) 
 
        GENDATA = True

        print 'Starting observation stats test on ', lfname 

        NEpochs = 100000

        num_states = model.n
 
        #####    make a string report describing the setup
        #
        #
        rep = []
        rep.append('-------------------------- Stat Validation of ABT Sim output ---------------------')
        if(GENDATA):
            print ' Generating NEW data'
            rep.append('  Generating new test data')
        rep.append('NSYMBOLS: {:d}   NEpochs: {:d} Number of states: {:d}'.format(NSYMBOLS,NEpochs,num_states))
        rep.append('sigma: {:.2f}    Ratio:  {:.2f}'.format(ac.sig, Ratio))
        rep.append('----------------------------------------------------------------------------------')
        rep.append(' ')

        #################################################
        #
        #    Test gaussian(x, mu, sig)
        mu = 50
        sig = 2.0
        data = []
        ##  Test our "gaussian" function
        a = mu - 5*sig
        b = mu + 5*sig
        N = 250
        x = []
        for i in range(0,N):
            #x = a + (b-a)*float(i)/100.00
            xv = (a + (b-a)*float(i)/100.00)
            data.append(gaussian(xv, mu, sig))
            x.append(xv)
            
        psum = 0.0
        pmin = 0.0000001 # smallest allowed probability
        #pmin = 0.0
        for i,xv in enumerate(x): 
            #clear the tiny numerical values
            if data[i] < pmin:
                data[i] = pmin   ###   require B[i,j] >= pmin
            psum += data[i]

        #normalize the Observation distrib so it sums to 1.000
        for i in range(N):
            data[i] /= psum 

        mu_hat = 0.0
        for i,d in enumerate(data):
            mu_hat += i*d
            
        stat_eps = 0.01

        print 'Gaussian function test: '
        print 'Mean, mean error: ', mu, mu - mu_hat
        tc.assert_feq(mu, mu_hat, 'Excessive mean error in gaussian()', stat_eps)
        ex2 = 0
        for i in range(N):
            xv = x[i]
            d = data[i]
            ex2 += (xv*xv*d)
        sig_hat = np.sqrt(ex2-mu_hat*mu_hat) 

        print 'Sig, sig error:   ', sig, sig-sig_hat
        tc.assert_feq(sig,sig_hat, 'Excessive SD error in gaussian()',stat_eps)

        #################################################
        #   2nd test of 
        #         gaussian(x, mu, sig)
        #        to understand effect of quantization
        #
        print '\n         Gaussian Quantization Test \n'
        mu = 65
        sig = 2.0
        x = []
        data = [] 
        N = 250       # same as application
        for i in range(0,N):
            #x = a + (b-a)*float(i)/100.00
            xv = float(i)
            data.append(gaussian(xv, mu, ac.sig))
            x.append(xv)
            
        psum = 0.0
        pmin = 0.0000001 # smallest allowed probability
        #pmin = 0.0
        pmin = 1.0E-8
        print 'Prob. Floor (pmin): ', pmin
        for i,xv in enumerate(x): 
            #clear the tiny numerical values
            if data[i] < pmin:
                data[i] = pmin   ###   require B[i,j] >= pmin
            psum += data[i]

        #normalize the Observation distrib so it sums to 1.000
        for i in range(N):
            data[i] /= psum 

        mu_hat = 0.0
        for i,d in enumerate(data):
            mu_hat += i*d
            
        stat_eps = 0.01

        print '2nd Gaussian function test: '
        print 'Mean, mean error: ', mu, mu - mu_hat
        tc.assert_feq(mu,mu_hat, 'Excessive mean error in gaussian()', stat_eps)

        ex2 = 0
        for i in range(N):
            xv = x[i]
            d = data[i]
            ex2 += (xv*xv*d)
        sig_hat = np.sqrt(ex2-mu_hat*mu_hat) 

        print 'Sig, sig error:   ', sig, sig-sig_hat
        tc.assert_feq(sig,sig_hat, 'Excessive SD error in gaussian()',stat_eps)


    def test_ObStat02(self):
        #############################################
        #
        #    Build the ABT and its blackboard
        #

        ##   Test initialization of stat observation means
        print 'Testing observation means and SD:'

        print 'States:'
        print model.names
        print 'Intended Obs Means:'
        print model.outputs
        model.setup_means(FIRSTSYMBOL, Ratio, ac.sig)

        if(GENDATA):

            [ABT, bb, leaves] = ABTtree(model)  # see file xxxx_ABT (e.g. Peg2_ABT, simp_ABT)

            print 'Data will appear in '+lfname
            # remove interactive user input
            #x = 'About to perform %d simulations. <enter> to cont.:' % NEpochs
            #raw_input(x)

            #############################################
            #
            #    Generate Simulated Data
            #
            print '\n\n computing and storing simulation data for ', NEpochs, ' simulations.\n\n'
            ###    Debugging
            #quit()
            
            # open the log file
            logf = open(lfname,'w')
            bb.set('logfileptr',logf)

            osu = model.names[-2]  # state names
            ofa = model.names[-1]

            for i in range(NEpochs):
                result = ABT.tick("ABT Simulation", bb)  # tree is composed of aug_leaf nodes
                # Generate the output observation corresponding to tree exit value
                if (result == b3.SUCCESS):
                    logf.write('{:s}, {:.0f}\n'.format(osu,outputs[osu]))  # not random obs!
                else:
                    logf.write('{:s}, {:.0f}\n'.format(ofa,outputs[ofa]))
                logf.write('---\n')

            logf.close()

            print 'Finished simulating ',NEpochs,'  epochs'

        ############################################
        #
        #  Read in the simulated sequence and compute its stats.
        #
        #

        logf = open(lfname,'r')
        print 'Opening ', lfname
        
        dN = {}    # number of observations seen for each state  
        dSum = {}  # sum of observations in each state
        dS2 = {}   # sum of observation^2 in each state
        smu = {}   # mean of each state's observations
        ssig = {}  # standard dev of each state's observations

        # initial values
        for n in model.names:
            #print 'looking for state: ', n
            dN[n] = 0
            dSum[n] = float(0)
            dS2[n] = float(0)

        nsims = 0
        nobs = 0
        for line in logf:
            if line == '---\n':
                nsims += 1
            else:  # accumulate observation data for each true state
                [st, sy] = line.split(',')
                #print 'state, symbol: ',st, '|',sy
                dN[st] += 1
                x = float(sy)
                dSum[st] += x
                dS2[st] += x*x
                nobs += 1

        #if lfname == refdataname:
            #print '\n\nUsing reference data set: checking accurate length count: ', nsims , ' Observations:',nobs
            #assert nsims== NEpochs, 'Failed to get accurate number of simulations'
            #print 'Passed: correct simulation count assertion'
        #else:
        #print 'Processed ',nsims,' Epochs, ', nobs, 'Observations.'

        #print '\nFile analyzed: ', lfname
        #for rl in rep:
            #print rl

        ##   Test initialization of stat observation means
        print 'Testing observation means and SD:'

        print 'States:'
        print model.names
        print 'Intended Obs Means:'
        print model.outputs

        print 'Sigma estimation tolerance: ', testsigeps
        print '    name        N            sum        sum^2           mu          S.D.'
        for [i,n] in enumerate(model.names):
            smu[n] = dSum[n] / float(dN[n])
            ssig[n] = np.sqrt(dN[n]*dS2[n] - dSum[n]*dSum[n]) / float(dN[n])
            print '%10s  %8d  %12.1f %12.1f %12.1f %12.1f' % ( n, dN[n], dSum[n], dS2[n], smu[n], ssig[n])

            if i < model.n - 2: # ignore last two states OutS OutF
                print 'Sigma estimation error: ', abs(ssig[n]-sig)
            
                tc.assert_feq(ssig[n], ac.sig, 'Excessive error in SD estimate', testsigeps)
                mu_err = abs(smu[n]-model.outputs[n])  # check inside 95% confidence interval
                print 'Mean error: ', mu_err
                #assert mu_err < testeps , 'Excessive error in mean'
                tc.assert_feq(mu_err, 0.0, 'Excessive error in mean estimate', testeps)

        print '\n\n            Passed: state emission mean and SD assertions'


        n = 'l2'  #  study a state 

        logf = open(lfname,'r')

        tf = open('t.csv','w')

        em = []
        for line in logf:
            if line == '---\n':
                nsims += 1
            else:  # accumulate observation data for each true state
                [st, sy] = line.split(',')
                if st == n:
                    em.append(float(sy))
        print 'Computed mean/sd: ', np.mean(em), np.std(em)


        if PLOTTING:            
                    
                        
            print '\n\n Please close the current plot to continue with tests\n\n'

            plt.figure(12)    # histogram of ALL run paces

            n, bins, patches = plt.hist(em, 100, normed=0, facecolor='blue', alpha=0.5)
            plt.xlabel('emission')
            plt.xlim([20,60])
            plt.xticks(range(20,60))
            plt.title('Emission Frequency, State l2')
            plt.show()

        logf.close()
