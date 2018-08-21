#!/usr/bin/python
#
#   Top-level scripted task
#
#   21-Aug  see spreadsheet: 
# https://docs.google.com/spreadsheets/d/1Ky3YH7SmxLFGL0PH2aNlbJbTtUTGU-UjAokIZUBkl9M/edit#gid=0
#

#   Baum Welch tests

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

NEWDATA = True  # flag to generate data once

task = BaumWelch   # Viterbi / Forward 

script_name = 'bw_hmm_b'

global NEpochs  

Mil = 1000000

NEpochs = 5000  # number of simulations

# amount HMM parameters should be ofset 
#   from the ABT parameters.  Offset has random sign (+/-)
HMM_delta = 0.10   # 10%   

#
############################################

##  The ABT file for the task (CHOOSE ONE)

from peg2_ABT import * # big  14+2 state  # uses model01.py
#from simp_ABT import *  # small 4+2 state # uses model00.py

#############################################
#
#      Manage outer loop (a set of runs)
#
Nruns = 10

########## results output files

logdir = 'logs_'+script_name+'/'

outputdir = 'out_'+script_name+'/'
oname = outputdir +  'hmm_fit_out_'+datetime.datetime.now().strftime("%y-%m-%d-%H-%M")

# HMM analysis output
of = open(oname,'w')    

# log file for progress info
infolog = open('infolog'+script_name, 'a')  # append
em = 9999

if CSVOUTPUT:
    fcsv = open('csvlog'+script_name,'a') 
    print >> fcsv, '-------',datetime.datetime.now().strftime("%y-%m-%d-%H-%M"), 'Nruns: ', Nruns, 'x', NEpochs
    #task, Ratio, int(di), float(di)/float(sig),run+1,Nruns,e2,em)
    print >> fcsv, 'tsk Ratio     di   Sigma  run#       e2  emax '

#################################################
#
#   Outer Loop
#
for run in range(Nruns):
    print >> infolog, datetime.datetime.now().strftime("%y-%m-%d-%H-%M"), 'task: ', task, ' run ',run+1,'/',Nruns, ' NEpochs: ', NEpochs,'Emax: ', em
    infolog.flush()    # make sure this info visible in file
    os.fsync(infolog.fileno())
    
    print '\n-------------------------------------------\n   Starting Run ',run+1, 'of', Nruns, '\n\n'
    # open the log file
    id = str(int(100*(Ratio)))+'iter'+str(run)  # encode the ratio (delta mu/sigma) into filename
    lfname = logdir+'statelog.txt'
        
 
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
    #    Generate Simulated Data only on first round
    #
    if(NEWDATA):
        seq_data_f = open(lfname,'w')
        bb.set('logfileptr',seq_data_f)   #allow BT nodes to access file
        osu = names[-2]  # state names
        ofa = names[-1]
            
        for i in range(NEpochs):
            result = ABT.tick("ABT Simulation", bb)
            if (result == b3.SUCCESS):
                seq_data_f.write('{:s}, {:.0f}\n'.format(osu,outputs[osu]))  # not random obs!
            else:
                seq_data_f.write('{:s}, {:.0f}\n'.format(ofa,outputs[ofa]))
            seq_data_f.write('---\n')
            
        seq_data_f.close()
        seq_data_f = open(lfname,'r') # save file and reset pointer

        print 'Finished simulating ',NEpochs,'  epochs'
        
    NEWDATA = False
    #############################################
    #
    #    Read simulated sequence data
    #

    seq_data_f = open(lfname,'r')
    [X,Y,Ls] = read_obs_seqs(seq_data_f)
    seq_data_f.close()
    
    assert len(Y) > 0, 'Empty observation sequence data'
    
    # remove the old log file
    #os.system('rm '+lfname)

    #############################################
    #
    #    HMM setup
    #
    Ac = A.copy()
    M = HMM_setup(Pi,Ac,sig,names)

    #############################################
    #
    #   Perturb the HMM's parameters (optional)
    #
    #outputAmat(M.transmat_,'Model A matrix',names,sys.stdout)      

    A_row_test(M.transmat_, sys.stdout)
    
    if(HMM_delta > 0.0001):
        HMM_perturb( M, HMM_delta )

    A_row_test(M.transmat_, sys.stdout) 
    
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
        print >>fcsv, '{:3d} {:.3f}, {:3d}, {:.3f}, {:2d}, {:2d}, {:.3f}, {:.3f}'.format(task, Ratio, int(di), float(sig),run+1,Nruns,e2,em)

#  End of loop of runs

of.close()
os.system('cp {:s} {:s}'.format(oname,outputdir+'lastoutput'))

 
#
#    HMM state tracking analysis
# 

