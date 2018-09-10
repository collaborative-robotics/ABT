#!/usr/bin/python
#
#   Top-level scripted task   TEST VERSION   31-Aug-18
#
#   21-Aug  see spreadsheet:
# https://docs.google.com/spreadsheets/d/1Ky3YH7SmxLFGL0PH2aNlbJbTtUTGU-UjAokIZUBkl9M/edit#gid=0
#

#   Baum Welch tests

import sys
import os
import uuid
import datetime
from hmm_bt import *
from abt_constants import *

#MODEL = SMALL 
MODEL = BIG

##
#     Uncomment to supress Deprecation Warnings from hmm_lean / scikit
#            (untested as yet becasue I commented out the warning in scikit)
#import warnings
#with warnings.catch_warnings():
    #warnings.filterwarnings('ignore', category=DeprecationWarning)

##   Set up research parameters


ownname = sys.argv[0]
 
 
############################################
#
#        Basic Job Config
#

NEWDATA = True  # flag to generate data once

task = BaumWelch   # Viterbi / Forward
 

#
#    Change non-zero A-matrix elements to RANDOM [0.0-1.0)
#

#
############################################

##  The ABT file for the task (CHOOSE ONE)

if MODEL== BIG:
    from peg2_ABT import * # big  14+2 state  # uses model01.py
if MODEL==SMALL:
    from simp_ABT import *  # small 4+2 state # uses model02.py

#############################################
#
#      Manage outer loop (a set of runs)
#
########## define metadata and output data files

metadata_name = 'hmm_bw_metadata.txt'

datafile_name = 'data_'+str(uuid.uuid4())+'.csv'  # a unique filename

sequence_name = 'seq_'+str(uuid.uuid4())
# HMM analysis output
of = open(oname,'w')
 
em = 9999

nsims = 0
e2T = 0.0
emT = 0.0

Nruns = 10  #testing
sig = 2.000
Ratio = 1.0  #testing
HMM_delta = 0.2  #testing
NEpochs = 20000    # testing

di = int(Ratio*sig)   # change in output obs mean per state

if CSVOUTPUT:
    fdata = open(datafile_name,'w')
    print >> fdata, '-------',datetime.datetime.now().strftime("%y-%m-%d-%H:%M"), 'Nruns: ', Nruns, 'x', NEpochs, 'HMM_delta: ', HMM_delta, ' #states: ',len(names)
    #task, Ratio, int(di), float(di)/float(sig),run+1,Nruns,e2,em)
    print >> fdata, 'tsk  Ratio   di   Sigma  run#     e2     emax '

#################################################
#
#   Outer Loop
#
for run in range(Nruns):

    print '\n-------------------------------------------\n   Starting Run ',run+1, 'of', Nruns, '\n\n'
    # open the log file
    id = str(int(100*(Ratio)))+'iter'+str(run)  # encode the ratio (delta mu/sigma) into filename
    lfname = logdir+script_name+'_statelog.txt'


    #####    make a string report describing the setup
    #
    #
    rep = []
    rep.append('-------------------------- BT to HMM ---------------------------------------------')
    stringtime = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
    rep.append(stringtime)
    rep.append('NSYMBOLS: {:d}   NEpochs: {:d} N-States: {:d} '.format(NSYMBOLS,NEpochs,len(names)))
    rep.append('HMM_delta: {:.3f}'.format(HMM_delta))
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

    #HMM_ABT_to_random(M)   # randomize probabilites
    #print 'Applied Random Matrix Perturbation'
    HMM_perturb(M, HMM_delta)
    print 'Applied Matrix Perturbation: ' + str(HMM_delta)
    A_row_test(M.transmat_, sys.stdout)
    B = M.transmat_.copy()  # store perturbed


    # special test code
    #  compare the two A matrices
    #     (compute error metrics)
    testeps = 0.00001
    [e,e2,em,N2,im,jm,anoms,erasures] = Adiff(A,M.transmat_, names)

    print >> of, 'EAavg    A-matrix error: {:.8f} ({:d} non zero elements)'.format(e2,N2)
    print >> of, 'EAinfty  A-matrix error: {:.3f} (at {:d} to {:d})'.format(em,im,jm)
    assert em > 0.0 , 'Perturbation caused no difference in A matrices'
    assert e2 > 0.0 , 'Perturbation caused no difference in A matrices'
    print 'Model Size: ',len(names)
    if len(names) < 8:
        outS_index = 4
    else:
        outS_index = 14
    outF_index = outS_index+1
    assert M.transmat_[outS_index,outS_index] - 1.0 < testeps, 'A 1.0 element was modified'
    assert M.transmat_[outF_index,outF_index] - 1.0 < testeps, 'A 1.0 element was modified'
    print 'Passed A-matrix Assertions'
    #end of special test code



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
        outputAmat(B,"Perturbed A Matrix", names, of)
        outputAmat(M.transmat_,"New A Matrix (pertb + HMM fit)", names, of)


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
        print >>fdata, '{:2d}, {:.3f}, {:3d}, {:.3f}, {:2d}, {:2d}, {:.3f}, {:.3f}'.format(task, Ratio, int(di), float(sig),run+1,Nruns,e2,em)

    nsims += 1
    emT += em
    e2T += e2
    # update an information log on this run
    print >> infolog, datetime.datetime.now().strftime("%y-%m-%d-%H-%M"), 'task: ', task, ' run ',run+1,'/',Nruns, ' NEpochs: ', NEpochs,'Emax: ', em
    infolog.flush()    # make sure this info visible in file
    os.fsync(infolog.fileno())

#  End of loop of runs

if CSVOUTPUT:
    print >>fdata, '{:3d} {:s} {:.3f}, {:.3f}'.format(task, 'Average e2, em: ',e2T/nsims,emT/nsims)
    fdata.close()

of.close()
os.system('cp {:s} {:s}'.format(oname,outputdir+'lastoutput'))


