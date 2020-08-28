#!/usr/bin/python
#
#   Test hmm_bt etc. via Top-level scripted task
 
import unittest
import mock

from tests.common import *
#from common import *


import numpy as np
import abt_constants as ac 
from abtclass import *
from hmm_bt import *
 
#   imports for this test
import subprocess
import uuid
import datetime
 
import sys as sys
import os as os

# b3 class modified by BH, local version in current dir
import b3 as b3          # behavior trees
#import random as random
import math as m

import warnings


#
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
            

class Test_bw_alg_tl(unittest.TestCase):


    def test_bw_alg_tl(self):
        print('Test env: path: ', sys.path[0:2])
        print('NSYMBOLS: ', NSYMBOLS)
        print('NEpochs: ', NEpochs)
        print('sig: ', ac.sig)
        print('Nruns: ', ac.Nruns)
        print('Model size:', model.n)
        
        Nruns = ac.Nruns
        Nruns = 2   # 5 is too long
        ###############################################
        #
        ##    Setup BW convergence Tests
        #
        #   (all config in abt_constants.py <---  task_BWConv.py



        ##
        #    Supress Deprecation Warnings from hmm_lean / scikit
        warnings.filterwarnings('ignore', category=DeprecationWarning)

        ##   Set up research parameters mostly in abt_constants.py

        ############################################
        #
        #        Basic Job Config
        #

        NEWDATA = True  # flag to generate data once

        ##  these now set in abt_constants
        #task = BaumWelch   # Viterbi / Forward
        ##task = Viterbi 


        # amount HMM parameters should be ofset
        #   from the ABT parameters.  Offset has random sign (+/-)

        #if len(sys.argv) != 3:
            #print 'Please use two command line arguments as follows:'
            #print ' > tl_bw_hmm    X.XXX comment'
            #print '  to indicate the HMM perturbation value (0.0--1.0)'
            #print '  and a comment (use single quotes for multiple words) to describe the run'
            #print 'You entered: '
            #print sys.argv
            #quit()
            
        #HMM_delta = float(sys.argv[1])
        #comment = str(sys.argv[2])
        HMM_delta = 0.1
        comment = 'unit testing'


        #################################################
        #     Normally 0.0 < HMM_delta < 0.500
        ###   As a flag, if HMM_delta > random_flag it is a signal 
        #        that HMM initial A matrix should be set to RANDOM
        HMM_RANDOM_INIT = False
        if HMM_delta > random_flag:
            HMM_RANDOM_INIT = True


            
        # check a few things about the model
        model.check()

        #############################################
        #
        #      Manage outer loop (a set of runs)
        #

        assert task == BaumWelch or task == BWTest, ' incorrect task specified for test'

        #######################################################################
        #
        # define output files for metadata and output data
        #
        #

        ownname = sys.argv[0]
        
        git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'])[:10]  # first 10 chars to ID software version

       
        if task == BaumWelch or task == BWTest:
            datadir = 'bw_output/'

        seqdir  = 'sequences/'

        urunid = str(uuid.uuid4())  # a unique hash code for this run 

        #if these don't exist, create them 
        for ndir in [datadir, seqdir]:
            if not (os.path.exists(os.path.dirname(ndir))):
                os.mkdir(ndir)

        metadata_name = 'metadata.txt'
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
        #  0)  Task code (1=Viterbi, 2=Baum Welch)
        #  1)  Ratio  (codeword mean spacing / sigma)
        #  2)  di     (codeword spacing)
        #  3)  HMM_delta    amt HMM params changed
        #  4)  Sigma
        #  5)  run#
        #------------------------------------------------------------------------
        #       Baum-Welch              Viterbi                Forward
        #------------------------------------------------------------------------
        #  6)  e2 (RMS error)     | avg str edit dist  |
        #  7)  emax (max error)   |                    |
        #------------------------------------------------------------------------

        sequence_name =  seqdir+'seq_'+urunid+'.txt'   # name of sim sequence file
        #
        #  sequence file format
        #
        #  1) true state name
        #  2) observation codeword value
        #  

        testname = 'vit_test'+urunid+'.csv'

        #ftest = open(testname, 'w') # testing
        fmeta = open(metadata_name, 'a')  #  append metadata to a big log
        fdata = open(datafile_name, 'w')  #  unique filename for csv output   

        print '-----'
        print 'Model Size: ', model.n

        ##  output the metadata
        line = '{:s} | {:s} | {:s} | {:s} | {:d} | {:s}'.format(datetime.datetime.now().strftime("%y-%m-%d-%H:%M"), datafile_name, ownname, git_hash, model.n,  comment)
        print >> fmeta , line

        #################################################
        #
        #   Outer Loop
        #
        if(NEWDATA==False and HMM_delta < testeps):   # no point in repeating the same computation!
            Nruns = 1

        Ratio = 2.5    
        #for Ratio in RatioList:
        for tol in [1.0]:       # not clear why we had this loop at all
            
            di = int(Ratio*sig)   # change in output obs mean per state
            ###  Regenerate output means:model.setup_means(FIRSTSYMBOL,Ratio, sig)
            model.setup_means(FIRSTSYMBOL, Ratio, sig)
            
            NEWDATA = True   
            for run in range(Nruns):

                print '\n-------------------------------------------\n Ratio = ',Ratio, ':  Starting Run ',run+1, 'of', Nruns, '\n\n'
                # open the log file
                id = str(int(100*(Ratio)))+'iter'+str(run)  # encode the ratio (delta mu/sigma) into filename
            
                #####    make a string report describing the setup
                #
                #
                rep = []
                rep.append('-------------------------- BT to HMM ---------------------------------------------')
                stringtime = datetime.datetime.now().strftime("%y-%m-%d-%H-%M")
                rep.append(stringtime)
                rep.append('NSYMBOLS: {:d}   NEpochs: {:d} N-States: {:d} '.format(NSYMBOLS,NEpochs,len(model.names)))
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

                [ABT, bb, leaves] = ABTtree(model)  # defined in xxxxxxABT.py file
                # make sure (damn sure!) ABT probs are same as HMM stats
                #     (HMM will be perturbed later, should be consistent NOW)
                for l in leaves:
                    # output observation mu, sigma
                    l.set_Obs_Density(model.outputs[l.Name],sig)
                    # set up the Ps (prob of success)
                    l.set_Ps(model.PS[model.statenos[l.Name]])
                    
                    
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

                Y = []    # Observations
                X = []    # True state 
                Ls = []   # Length of each sequence
                seq_data_f = open(sequence_name,'r')
                [X,Y,Ls] = read_obs_seqs(seq_data_f)
                seq_data_f.close()

                assert len(Y) > 0, 'Empty observation sequence data'
        

                #############################################
                #
                #    HMM setup
                #
                A = model.A.copy()
                Ac = A.copy()  # isolate orig A matrix from HMM
                Ar = A.copy()  # reference original copy
                M = HMM_setup(model, tol, 5)   # 20 is a very big iteration count(!)

                #############################################
                #
                #   Perturb the HMM's parameters (optional)
                #
                #outputAmat(M.transmat_,'Model A matrix',model.names,sys.stdout)

                A_row_test(M.transmat_, sys.stdout)   # Make sure A-Matrix Valid (assertions)

                
                testeps = 0.00001
                if(not HMM_RANDOM_INIT and HMM_delta > testeps):
                    #HMM_ABT_to_random(M)   # randomize probabilites
                    #print 'Applied Random Matrix Perturbation'
                    HMM_perturb(M, HMM_delta,model)
                    print 'Applied HMM Perturbation: ' + str(HMM_delta)
                    

                if (HMM_RANDOM_INIT):
                    M.transmat_, M.means_ = HMM_fully_random(model)
                    print 'Applied FULLY RANDOM Matrix Perturbation: '
                    outputAmat(M.transmat_, 'RANDOM a-mat', model.names)
                    print 'Applied FULLY RANDOM B-matrix Perturbation'
            
                    
                ###   make sure everything is cool with the HMM we will use below:
                A_row_test(M.transmat_, sys.stdout)
                HMM_model_sizes_check(M)    # contains assertions
                M._check()   # a built in param checker(!) from hmmlearn
                print 'Passed HMM param tests'
                    
                ##################################################
                #
                #       Forward Algorithm
                #
                #if(task == Forward):
                    #print 'This test is only for Baum Welch Convergence Testing - quitting.'
                    #quit()
                    
                ###################################################
                ##
                ##       Veterbi Algorithm
                ##
                #if(task == Viterbi):
                    #print 'This test is only for Baum Welch Convergence Testing - quitting.'
                    #quit()

                
                if(task == BaumWelch or task == BWTest):
                    #############################################
                    #
                    #   Identify HMM params with Baum-Welch
                    #
                    print "starting HMM fit with ", len(Y), ' observations.'

                    M.fit(Y,Ls)
                    if(BWTest):
                        print 'Completed HMM fit(): Converged: ', M.monitor_.converged
                        print M.monitor_
                    
                    # some basic checks
                    fs = 'Suspicious baum-welch results: try re-running in case of rare events.'
                    if model.n == 6:
                        assert M.monitor_.history[-1] < 100000.0, fs  # seems like good sanity value for N=6
                    assert M.monitor_.converged, fs
                    
                    # print the output file header
                    #for rline in rep:
                        #print >>of, rline

                    #outputAmat(A,"Original A Matrix", model.names, of)
                    #outputAmat(B,"Perturbed A Matrix", model.names, of)
                    #outputAmat(M.transmat_,"New A Matrix (pertb + HMM fit)", model.names, of)


                    ##  compare the two A matrices
                    #     (compute error metrics)
                    [e,e2,em,N2,im,jm,anoms,erasures] = Adiff(Ar,M.transmat_, model.names)
                    print 'ERR======'
                    print e, e2, em, N2, im, jm
                    assert em < 0.20, fs
                    print '   ======'
                    if len(anoms) == 0:
                        anoms = 'None'
                    #print >> of, 'Anomalies: ', anoms
                    if len(erasures) == 0:
                        anoms = 'None'
                    #print >> of, 'Erasures : ', erasures
                    if task == BWTest:                 
                        print >>fdata, '{:2d}, {:.6f}, {:3d}, {:.3f}, {:.3f}, {:2d}, {:.3f}, {:.3f}'.format(task, tol, M.monitor_.iter, HMM_delta, float(sig), run+1, e2,em)
                    else: 
                        print >>fdata, '{:2d}, {:.3f}, {:3d}, {:.3f}, {:.3f}, {:2d}, {:.3f}, {:.3f}'.format(task, Ratio, int(di), HMM_delta, float(sig), run+1, e2,em)
        

            #  End of loop of runs

        #ftest.close()
        fdata.close()
        fmeta.close()

        print '\n\n                         Model Run Completed   \n\n'


            
        

if __name__ == '__main__':
    unittest.main()



