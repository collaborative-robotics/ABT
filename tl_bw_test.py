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
import subprocess
import uuid
import datetime
from hmm_bt import *
from abt_constants import *

#MODEL = SMALL 
MODEL = BIG

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


 
############################################
#
#        Basic Job Config
#

NEWDATA = True  # flag to generate data once

task = BaumWelch   # Viterbi / Forward

script_name = 'bw_hmm'


# amount HMM parameters should be ofset
#   from the ABT parameters.  Offset has random sign (+/-)

if len(sys.argv) != 1:
    print 'TEST VERSION:'
    print 'Edit your params on line 53.\n  You entered:'
    print sys.argv
    quit()
    
comment = 'xxxxxx TESTING xxxxx'


##################################################################
#
#              Major Run Parameters
#
Nruns = 3  #testing
sig = 2.001
Ratio = 3.00  #testing
HMM_delta = 0.244  #testing
NEpochs = 20000    # testing
##################################################################


#################################################
#     Normally 0.0 < HMM_delta < 0.500
###   As a flag, if HMM_delta > 5.0 it is a signal 
#        that HMM initial A matrix should be set to RANDOM
HMM_RANDOM_INIT = False
if HMM_delta > 4.95:
    HMM_RANDOM_INIT = True


print 'Nruns v1: ',Nruns
#
print 'Nruns v2: ',Nruns

#############################################
#
#      Manage outer loop (a set of runs)
#


#######################################################################
#
# define output files for metadata and output data
#
#

ownname = sys.argv[0]
 
git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'])[:10]  # first 10 chars to ID software version

datadir = 'test/'
seqdir  = 'test/'

urunid = str(uuid.uuid4())  # a unique hash code for this run 

#if these don't exist, create them 
for ndir in [datadir, seqdir]:
    if not (os.path.exists(os.path.dirname(ndir))):
        os.mkdir(ndir)


metadata_name = 'test_metadata.txt'
# Metadata file format:  each line: (comma sep)
#
#  0) date and time stamp
#  1) name of data file
#  2) ownname  (name of the top level file)
#  3) git hash (1st 10 chars of current git hash)
#  4) number of HMM / BT states
#  5) text field (comment)
#
datafile_name = datadir+'data_'+urunid+'.csv'  # a unique filename
# Datafile format:  comma sep
#
#  0)  Task code (2=Baum Welch)
#  1)  Ratio  (codeword mean spacing / sigma)
#  2)  di     (codeword spacing)
#  3)  HMM_delta    amt HMM params changed
#  4)  Sigma
#  5)  run#
#  6)  e2 (RMS error)
#  7)  emax (max error)

sequence_name =  seqdir+'seq_'+urunid+'.txt'   # name of sim sequence file
#
#  sequence file format
#
#  1) true state name
#  2) observation codeword value
#  

fmeta = open(metadata_name, 'a')  #  append metadata to a big log
fdata = open(datafile_name, 'w')  #  unique filename for csv output 
# open sequence_name   in NEWDATA section below  

nsims = 0
e2T = 0.0
emT = 0.0

print 'Nruns v3: ',Nruns

print '-----'
print 'Model Size: ', model.n

##  output the metadata
line = '{:s} | {:s} | {:s} | {:s} | {:d} | {:s}'.format(datetime.datetime.now().strftime("%y-%m-%d-%H:%M"), datafile_name, ownname, git_hash, model.n,  comment)
print >> fmeta , line

###
###  Generate output means:
i = FIRSTSYMBOL
di = Ratio*sig  # = nxsigma !!  now in abt_constants
for n in model.outputs.keys():
    model.outputs[n] = i
    i += di
#################################################
#
#   Outer Loop
#
for run in range(Nruns):

    print '\n-------------------------------------------\n   Starting Run ',run+1, 'of', Nruns, '\n\n'
 
    #####    make a string report describing the setup
    #
    #
    rep = []
    rep.append('-------------------------- BT to HMM ---------------------------------------------')
    stringtime = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
    rep.append(stringtime)
    rep.append('NSYMBOLS: {:d}   NEpochs: {:d} N-States: {:d} '.format(NSYMBOLS,NEpochs,len(model.names)))
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

    [ABT, bb] = ABTtree(model)  # defined in xxxxxxABT.py file

    #############################################
    #
    #    Generate Simulated Data only on first round
    #
    if(NEWDATA):
        seq_data_f = open(sequence_name,'w')
        bb.set('logfileptr',seq_data_f)   #allow BT nodes to access file
        osu = model.names[-2]  # state names
        ofa = model.names[-1]

        for i in range(NEpochs):
            result = ABT.tick("ABT Simulation", bb)
            if (result == b3.SUCCESS):
                seq_data_f.write('{:s}, {:.0f}\n'.format(osu,model.outputs[osu]))  # not random obs!
            else:
                seq_data_f.write('{:s}, {:.0f}\n'.format(ofa,model.outputs[ofa]))
            seq_data_f.write('---\n')

        seq_data_f.close()

        print 'Finished simulating ',NEpochs,'  epochs'

    NEWDATA = False
    #############################################
    #
    #    Read simulated sequence data
    #

    Y = []
    X = []
    Ls = []
    seq_data_f = open(sequence_name,'r')
    [X,Y,Ls] = read_obs_seqs(seq_data_f)
    seq_data_f.close()

    assert len(Y) > 0, 'Empty observation sequence data'


    #############################################
    #
    #    HMM setup
    #
    Ac = A.copy()  # isolate orig A matrix from HMM
    Ar = A.copy()  # reference original copy
    M = HMM_setup(Pi,Ac,sig,model.names)

    #############################################
    #
    #   Perturb the HMM's parameters (optional)
    #
    #outputAmat(M.transmat_,'Model A matrix',model.names,sys.stdout)

    A_row_test(M.transmat_, sys.stdout)   # Make sure A-Matrix Valid

    
    testeps = 0.00001
    if(not HMM_RANDOM_INIT and HMM_delta > testeps):
        #HMM_ABT_to_random(M)   # randomize probabilites
        #print 'Applied Random Matrix Perturbation'
        HMM_perturb(M, HMM_delta)
        print 'Applied Matrix Perturbation: ' + str(HMM_delta)
        

    if (HMM_RANDOM_INIT):
        A_rand = A.copy() 
        [rn,cn] = A_rand.shape
        for r in range(rn):      # normalize the rows
            rsum = 0.0
            for c in range(cn):
                A_rand[r][c] = random.random()
                rsum += A_rand[r][c]
            for c in range(cn):
                A_rand[r][c] /= rsum
        M.transmat_ = A_rand
        print 'Applied FULLY RANDOM Matrix Perturbation: '
        outputAmat(M.transmat_, 'RANDOM a-mat', model.names)
    
    
    A_row_test(M.transmat_, sys.stdout)   # Make sure A-Matrix Valid

    # special test code
    #  compare the two A matrices
    #     (compute error metrics)
    testeps = 0.00001
    if HMM_delta > testeps: 
        [e,e2,em,N2,im,jm,anoms,erasures] = Adiff(Ar,M.transmat_, model.names)

        
        ##  some assertions to make sure pertubations are being done right
        #   (if they aren't there's not point in doing the sim)
        assert em > 0.0 , 'Perturbation caused no difference in A matrices'
        assert e2 > 0.0 , 'Perturbation caused no difference in A matrices'
        #print 'em: {:.2f}'.format(em)
        #print 'e2: {:.2f}'.format(e2)
        if model.n < 8:
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
        #for rline in rep:
            #print >>of, rline

        #outputAmat(A,"Original A Matrix", model.names, of)
        #outputAmat(B,"Perturbed A Matrix", model.names, of)
        #outputAmat(M.transmat_,"New A Matrix (pertb + HMM fit)", model.names, of)


        ##  compare the two A matrices
        #     (compute error metrics)
        [e,e2,em,N2,im,jm,anoms,erasures] = Adiff(A,M.transmat_, model.names)

        #print >> of, 'EAavg    A-matrix error: {:.8f} ({:d} non zero elements)'.format(e2,N2)
        #print >> of, 'EAinfty  A-matrix error: {:.3f} (at {:d} to {:d})'.format(em,im,jm)

        if len(anoms) == 0:
            anoms = 'None'
        #print >> of, 'Anomalies: ', anoms
        if len(erasures) == 0:
            anoms = 'None'
        #print >> of, 'Erasures : ', erasures

        print >>fdata, '{:2d}, {:.3f}, {:3d}, {:.3f}, {:.3f}, {:2d}, {:.3f}, {:.3f}'.format(task, Ratio, int(di), HMM_delta, float(sig), run+1, e2,em)

    nsims += 1
    emT += em
    e2T += e2

#  End of loop of runs

#print >>fdata, '{:3d} {:s} {:.3f}, {:.3f}'.format(task, 'Average e2, em: ',e2T/nsims,emT/nsims)
fdata.close()
fmeta.close()



