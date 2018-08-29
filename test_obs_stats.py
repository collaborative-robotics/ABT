#!/usr/bin/python
# 
## hmm model params for SIMPLE 4-state BT
import numpy as np
import sys



from abt_constants import *

# Select the ABT file here
#from simp_ABT import *    # basic 4-state HMM 
from peg2_ABT import *         # elaborate 16-state HMM
#

GENDATA = False  #  (determined by # args below)

logdir = 'logs/'
lfname = logdir+'TSTstatelog.txt'
nargs = len(sys.argv)
if nargs == 1:
    GENDATA = True
elif nargs == 2:
    lfname = str(sys.argv[1])
    
NEpochs = 1000000
#NEpochs = 1000

#####    make a string report describing the setup
#
# 
rep = []
rep.append('-------------------------- Stat Validation of ABT Sim output ---------------------')
if(GENDATA):
    rep.append('  Generating new test data')
rep.append('NSYMBOLS: {:d}   NEpochs: {:d} '.format(NSYMBOLS,NEpochs))
rep.append('sigma: {:.2f}    Symbol delta: {:d}   Ratio:  {:.2f}'.format(sig, int(di), float(di)/float(sig)))
rep.append('----------------------------------------------------------------------------------')
rep.append(' ')

           
#############################################
#
#    Build the ABT and its blackboard
#

[ABT, bb] = ABTtree()

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

dN = {}
dSum = {}
dS2 = {}

smu = {}
ssig = {}

for n in names: 
    print 'looking for state: ', n
    dN[n] = 0
    dSum[n] = float(0)
    dS2[n] = float(0)
    
nsims = 1
for line in logf:
    if line == '---\n':
        nsims += 1
    else:
        [st, sy] = line.split(',')
        #print 'state, symbol: ',st, '|',sy
        dN[st] += 1
        x = float(sy)
        dSum[st] += x
        dS2[st] += x*x



print '\nFile analyzed: ', lfname 
for rl in rep:
    print rl
print '    name        N            sum           sum^2     mu         S.D.'
for n in names:
    smu[n] = dSum[n] / float(dN[n])
    ssig[n] = np.sqrt(dN[n]*dS2[n] - dSum[n]*dSum[n]) / float(dN[n])
    
    print '%10s  %8d  %12.1f %12.1f %12.1f %12.1f' % ( n, dN[n], dSum[n], dS2[n], smu[n], ssig[n])
    
