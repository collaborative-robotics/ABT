#!/usr/bin/python
#
#   Top-level scripted task
#
#
#    23-May    Add looping for multiple runs
#    30-Jul    Final computations for paper

import sys
import os
import datetime
from hmm_bt import *

from abt_constants import *

##   Set up research parameters

CSVOUTPUT = True

############################################
#
#        Basic Job Config
# 

NEWDATA = True

Task = BaumWelch

global NEpochs  

Mil = 1000000

NEpochs = 1000  # number of simulations

# amount HMM parameters should be ofset 
#   from the ABT parameters.  Offset has random sign (+/-)
HMM_delta = 0.05   #  5%  
HMM_delta = 0.00   

#
############################################

##  The ABT file for the task (CHOOSE ONE)
#from peg2_ABT import *   # uses model01.py
from simp_ABT import *


#############################################
#
#      Manage outer loop (a set of runs)
#
Nruns = 10


########## results output files

logdir = 'logs04/'

outputdir = 'out04/'
oname = outputdir +  'hmm_fit_out_'+datetime.datetime.now().strftime("%y-%m-%d-%H-%M")

# HMM analysis output
of = open(oname,'w')    

# log file for progress info
infolog = open('infolog04', 'a')  # append
em = 9999

if CSVOUTPUT:
    fcsv = open('csvlog04','a') 
    print >> fcsv, '-------',datetime.datetime.now().strftime("%y-%m-%d-%H-%M"), 'Nruns: ', Nruns, 'x', NEpochs

#################################################
#
#   Outer Loop
#
for run in range(Nruns):
    print >> infolog, datetime.datetime.now().strftime("%y-%m-%d-%H-%M"), 'task: ', task, ' run ',run+1,'/',Nruns, ' NEpocs: ', NEpochs,'Emax: ', em
    infolog.flush()    # make sure this info visible in file
    os.fsync(infolog.fileno())
    print '\n-------------------------------------------\n   Starting Run ',run+1, 'of', Nruns, '\n\n'
    # open the log file
    id = str(int(100*(Ratio))) # encode the ratio (delta mu/sigma) into filename
    lfname = logdir+'statelog'+id+'.txt'
    logf = open(lfname,'w')   
 
    #####    make a string report describing the setup
    #
    # 
    rep = []
    rep.append('-------------------------- BT to HMM ---------------------------------------------')
    rep.append('NSYMBOLS: {:d}   NEpochs: {:d} '.format(NSYMBOLS,NEpochs))
    rep.append('sigma: {:.2f}    Symbol delta: {:d}   Ratio:  {:.2f}'.format(sig, int(di), float(di)/float(sig)))
    rep.append('----------------------------------------------------------------------------------')
    rep.append(' ')

    
    #############################################
    #
    #    Set up models

           
    #############################################
    #
    #    Build the ABT and its blackboard
    #

    [ABT, bb] = ABTtree()  # defined in xxxxxxABT.py file

    #############################################
    #
    #    Generate Simulated Data
    #
    if(NEWDATA):
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
        
        
    #############################################
    #
    #    Read simulated sequence data
    #

    [X,Y,Ls] = read_obs_seqs(lfname)
    
    # remove the old log file
    #os.system('rm '+lfname)

    #############################################
    #
    #    HMM setup
    #

    M = HMM_setup(Pi,A,sig,names)

    #############################################
    #
    #   Perturb the HMM's parameters (optional)
    #
    if(HMM_delta > 0.0001):
        HMM_perturb( M, HMM_delta )

    if(task == BaumWelch):
        #############################################
        #
        #   Identify HMM params with Baum-Welch
        #
        print "starting HMM fit with ", len(Y), ' observations.'

        M.fit(Y,Ls)
        # print the output file header
        for rline in rep:
            print >>of, rline

        outputAmat(A,"Original A Matrix", names, of)
        outputAmat(M.transmat_,"New A Matrix", names, of)


        ##  compare the two A matrices
        #     (compute error metrics)
        [e,e2,em,N2,im,jm,anoms,erasures] = Adiff(A,M.transmat_, names)

        print >> of, 'EAavg    A-matrix error: {:.8f} ({:d} non zero elements)'.format(e2,N2)
        print >> of, 'EAinfty  A-matrix error: {:.3f} (at {:d} to {:d})'.format(em,im,jm)
        if len(anoms) == 0:
            anoms = 'None'
        print >> of, 'Anomalies: ', anoms
        if len(erasures) == 0:
            anoms = 'None'
        print >> of, 'Erasures : ', erasures
        
    if CSVOUTPUT:
        print >>fcsv, '{:3d} {:.3f}, {:3d}, {:.3f}, {:2d}, {:2d}, {:.3f}, {:.3f}'.format(task, Ratio, int(di), float(di)/float(sig),run+1,Nruns,e2,em)

#  End of loop of runs

of.close()
os.system('cp {:s} {:s}'.format(oname,outputdir+'lastoutput'))

 
#
#    HMM state tracking analysis
# 

