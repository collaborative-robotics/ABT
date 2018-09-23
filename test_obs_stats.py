#!/usr/bin/python
#
## hmm model params for SIMPLE 4-state BT
import numpy as np
import sys

from abt_constants import *

MODEL = BIG

testeps = 1.96 / np.sqrt(float(NEpochs))  # will convert to confidence interval
testsigeps = 0.10   # mean must be within this many SDs of actual mean.

print 'Test sig epsilon: ', testsigeps, ' standard deviations'

##
#    Supress Deprecation Warnings from hmm_lean / scikit
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

##   Set up research parameters mostly in abt_constants.py

############################################

##  The ABT file for the task (CHOOSE ONE)

if MODEL== BIG:
    from peg2_ABT import * # big  14+2 state  # uses model01.py
    from model01 import *
    model = modelo01
    
if MODEL==SMALL:
    from simp_ABT import *  # small 4+2 state # uses model02.py
    from model00 import *
    model = modelo00


GENDATA = False  #  (determined by # args below)

logdir = ''

# use this filename to know exact observation count.
lfname = logdir + 'REF_test_statelog.txt'
refdataname = lfname

nargs = len(sys.argv)

if nargs == 1:
    print 'Please use a filename on command line'
    print 'Args: ', sys.argv
    print 'Usage: '
    print '> test_obs_stats   [GENDATA|filename]'
    quit()
elif nargs == 2:
    if(sys.argv[1] == "GENDATA"):
        GENDATA = True 
        lfname = logdir+'TSTstatelog.txt'
    else:
        lfname = str(sys.argv[1]) 

print 'Starting observation stats test on ', lfname
if GENDATA:
    print ' Generating NEW data'

Ratio = float(raw_input('Enter the Ratio expected for the data:'))

NEpochs = 100000

num_states = model.n
#NEpochs = 1000

#####    make a string report describing the setup
#
#
rep = []
rep.append('-------------------------- Stat Validation of ABT Sim output ---------------------')
if(GENDATA):
    rep.append('  Generating new test data')
rep.append('NSYMBOLS: {:d}   NEpochs: {:d} Number of states: {:d}'.format(NSYMBOLS,NEpochs,num_states))
rep.append('sigma: {:.2f}    Symbol delta: {:d}   Ratio:  {:.2f}'.format(sig, int(di), float(di)/float(sig)))
rep.append('----------------------------------------------------------------------------------')
rep.append(' ')


#############################################
#
#    Build the ABT and its blackboard
#

model.setup_means(FIRSTSYMBOL, Ratio, sig)

[ABT, bb, leaves] = ABTtree(model)  # see file xxxx_ABT (e.g. Peg2_ABT, simp_ABT)

if(GENDATA):
    print 'Data will appear in '+lfname
    x = 'About to perform %d simulations. <enter> to cont.:' % NEpochs
    raw_input(x)

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

    osu = names[-2]  # state names
    ofa = names[-1]

    for i in range(NEpochs):
        result = ABT.tick("ABT Simulation", bb)
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

dN = {}    # number of observations seen for each state  
dSum = {}  # sum of observations in each state
dS2 = {}   # sum of observation^2 in each state
smu = {}   # mean of each state's observations
ssig = {}  # standard dev of each state's observations

# initial values
for n in names:
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

if lfname == refdataname:
    print '\n\nUsing reference data set: checking accurate length count: ', nsims , ' Observations:',nobs
    assert nsims== NEpochs, 'Failed to get accurate number of simulations'
    print 'Passed: correct simulation count assertion'
    # assertion below not really meaningful - doesn't test anything outside this file
    #assert nobs==1089131, 'Failed to get accurate number of observations'
    #print 'Passed: correct observation count assertion'

else:
    print 'Processed ',nsims,' Epochs, ', nobs, 'Observations.'

print '\nFile analyzed: ', lfname
for rl in rep:
    print rl

##   Test initialization of stat observation means
print 'Testing observation means and SD:'

print 'States:'
print model.names
print 'Intended Obs Means:'
print model.outputs

print '    name        N            sum        sum^2           mu          S.D.'
for [i,n] in enumerate(names):
    smu[n] = dSum[n] / float(dN[n])
    ssig[n] = np.sqrt(dN[n]*dS2[n] - dSum[n]*dSum[n]) / float(dN[n])
    print '%10s  %8d  %12.1f %12.1f %12.1f %12.1f' % ( n, dN[n], dSum[n], dS2[n], smu[n], ssig[n])

    if i < num_states-2: # ignore last two states OutS OutF
        #print 'Sigma estimation error: ', abs(ssig[n]-sig)
    
        assert(abs(ssig[n] - sig) < testsigeps), 'Excessive error in SD'

        mu_err = abs(smu[n]-model.outputs[n])  # check inside 95% confidence interval
        assert mu_err < testsigeps*ssig[n] , 'Excessive error in mean'

print 'Passed: state mean and SD assertions'

