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
import sys as sys

from abt_constants import *

##   Set up research parameters

CSVOUTPUT = True
METAOUTPUT = True

MODEL = SMALL 
#MODEL = BIG

############################################
#
#        Basic Job Config
#

NEWDATA = True  # flag to generate data once

task = BaumWelch   # Viterbi / Forward


#assert len(sys.argv) == 2, 'Need a command line argument (HMM_delta)'
#script_name = 'bw_hmm_big'+ str(sys.argv[1])

script_name = 'bw_hmm_big_meta'

if METAOUTPUT:
    fmeta = open('meta_output.csv','w')


# amount HMM parameters should be ofset
#   from the ABT parameters.  Offset has random sign (+/-)
#HMM_delta = 0.00   # no perturb


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
    print >> fcsv, '-------',datetime.datetime.now().strftime("%y-%m-%d-%H-%M"), 'Nruns: ', Nruns, 'x', NEpochs, ' #states: ',len(names)
    #task, Ratio, int(di), float(di)/float(sig),run+1,Nruns,e2,em)
    print >> fcsv, 'tsk Hdelt Ratio   di   Sigma  run#  e2  emax '

nsims = 0
e2T = 0.0
emT = 0.0


bigratiotest = [0.25, 0.5, 1, 5.0, 0.25, 0.5, 1, 5.0, 0.25, 0.5, 1, 5.0]

smallratiotest = [0.25, 5.0]

#####    make a string report describing the setup
#
#
rep = []
rep.append('-------------------------- BT to HMM ---------------------------------------------')
rep.append(datetime.datetime.now().strftime("%y-%m-%d-%H:%M"))
rep.append('NSYMBOLS: {:d}   NEpochs: {:d} N-States: {:d} '.format(NSYMBOLS,NEpochs,len(names)))
rep.append('sigma: {:.2f}    Symbol delta: {:d}   Ratio:  {:.2f}'.format(sig, int(di), float(di)/float(sig)))
rep.append('----------------------------------------------------------------------------------')
rep.append(' ')

if METAOUTPUT:
    for line in rep:
        print >>fmeta, line
    print >>fmeta, 'tsk,Ratio, H_del, di, sig, r, Nr, e_avg, e_max'
        #task, Ratio, HMM_delta, int(di), float(sig),run+1,Nruns,e2,em

#################################################
#
#   Outer Loop
loopsize = len(bigratiotest)*4*Nruns
loopcount = 0
for Ratio in bigratiotest:
    ################################################
    #
    #   amount initial HMM params are changed from exact
    #
    for HMM_delta in [0.50, 0.20, 0.10, 0.00]:
        print 'Starting run with Ratio = ', Ratio, 'Hmm_delta = ', HMM_delta, ' loop: ',loopcount,'/',loopsize
        ########################
        # 
        #  run loop 
        #
        for run in range(Nruns):
            loopcount += 1
            print '\n-------------------------------------------\n   Starting Run ',run+1, 'of', Nruns, '\n\n'
            # open the log file
            id = str(int(100*(Ratio)))+'iter'+str(run)  # encode the ratio (delta mu/sigma) into filename
            lfname = logdir+script_name+'_statelog.txt'


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

                print 'Finished simulating ',NEpochs,'  epochs'

            NEWDATA = False
            #############################################
            #
            #    Read simulated sequence data
            #
            X = []
            Y = []
            Ls = []
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
                print >>fcsv, '{:2d}, {:.3f}, {:3d}, {:.3f}, {:2d}, {:2d}, {:.3f}, {:.3f}'.format(task, Ratio, int(di), float(sig),run+1,Nruns,e2,em)

            if METAOUTPUT:
                print >>fmeta, '{:2d}, {:.3f}, {:.3f}, {:3d}, {:.3f}, {:2d}, {:2d}, {:.3f}, {:.3f}'.format(task, Ratio, HMM_delta, int(di), float(sig),run+1,Nruns,e2,em)
                fmeta.flush()             # make sure this writes to HDD now
                os.fsync(fmeta.fileno())  #

            nsims += 1
            emT += em
            e2T += e2
            # update an information log on this run
            print >> infolog, datetime.datetime.now().strftime("%y-%m-%d-%H-%M"), 'task: ', task, ' run ',run+1,'/',Nruns, ' NEpochs: ', NEpochs,'Emax: ', em
            infolog.flush()    # make sure this info visible in file
            os.fsync(infolog.fileno())

    #  End of loop of runs

    if CSVOUTPUT:
        print >>fcsv, '{:3d} {:s} {:.3f}, {:.3f}'.format(task, 'Average e2, em: ',e2T/nsims,emT/nsims)
        
        
fmeta.close()
fcsv.close()
of.close()
os.system('cp {:s} {:s}'.format(oname,outputdir+'lastoutput'))


