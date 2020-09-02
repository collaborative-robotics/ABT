#!/usr/bin/python
# 
#      Generate test results for forward alg tracking 
#        and ABT against HMM with different perturbations
#
#

import os
import sys

import random as random
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

# specific imports for this test: 
import model01 as m1
import model00 as m0
import matplotlib.pyplot as plt

KEEP_DATA = False  # delete data files after test

NST = 6    # Small model
#NST = 16

#  Too few epochs and asserts will fail "reasonableness" tests
#  Too many and test will be slow.   2000 seems a good balance
NEpochs_test = 2000  #  
tested_perts = [0, 0.1, 0.25, 0.50]
if NST < 10:
    print '                  SMALL model'
    from simp_ABT import *   # req'd for 6-state
else:
    print '                  LARGE model'
    from peg2_ABT import *  # req'd for 16-state

class Test_Forward_Algorithm(unittest.TestCase):

    def test_FA_01(self):
        tc.all_random_seeds(430298219)  # we want same seqs every time so we can assert for right answers                        
        results_logP = {}
        files_used = []
        #
        #   Effect of output Ratio on Fwd alg perf. with 20% perturbation
        #

        outputs = []  # hold outputs for printing at end
        for Ratio in RatioList:
            
            ##
            #
            #   Do a simulation file for each Ratio
            #
            if NST == 16:
                model = m1.modelo01
            elif NST == 6:
                model = m0.modelo00
                    
            model.setup_means(FIRSTSYMBOL,Ratio, sig)
            [ABT, bb, leaves] = ABTtree(model)
            pref = 'tests/data_for_tests/'
            sequence_name =  pref+'Forward_test_sequence'+str(NST)+'stateR'+str(Ratio)+'.txt'
            if not os.path.isfile(sequence_name):
                print'No existing data file. starting simulation to generate data'
                seq_data_f = open(sequence_name,'w')
                bb.set('logfileptr',seq_data_f)   #allow BT nodes to access/write to file
                osu = model.names[-2]  # state names
                ofa = model.names[-1]

                for i in range(NEpochs_test):
                    result = ABT.tick("ABT Simulation", bb)
                    if (result == b3.SUCCESS):
                        seq_data_f.write('{:s}, {:.0f}\n'.format(osu,model.outputs[osu]))  # not random obs!
                    else:
                        seq_data_f.write('{:s}, {:.0f}\n'.format(ofa,model.outputs[ofa]))
                    seq_data_f.write('---\n')
                seq_data_f.close()
                print 'Finished simulating ',NEpochs_test,'  epochs.  Ratio: ', Ratio
            else:
                print 'Using existing data sequence: '+sequence_name
            files_used.append(sequence_name)
            
            # Now run FWD Alg for various model perts
                
            # reset these for each Ratio
            logps=[]
            log_avgs = []  # avg log probability 
            rused = []     # the output ratio used

            for model_perturb in tested_perts:
                print '\n\n'
                print '          (',NST,' states)'
                print '          testing forward algorithm with output Ratio: ', Ratio
                print '                         pert = ', model_perturb
                
                M = HMM_setup(model)
                
                test_eps = 0.000001
                
                Ar = np.copy(M.transmat_)
                HMM_model_sizes_check(M)
                HMM_perturb(M, model_perturb, model)


                [e,e2,em,N2,im,jm,anoms,erasures] = Adiff(Ar,M.transmat_, model.names)


                Y = []    # Observations
                X = []    # True state
                seq_lengths = []   # Length of each sequence
                seq_data_f = open(sequence_name,'r')
                [X,Y,seq_lengths] = read_obs_seqs(seq_data_f)
                seq_data_f.close()

                #counter = 0
                logprob = 0
                log_avg = 0
                
                logprob = M.score(Y,seq_lengths)
                logps.append(logprob)
                log_avg = logprob/len(seq_lengths)
                log_avgs.append(log_avg)
                
                rused.append(Ratio)
                
            l1 = len(log_avgs) + 1
            f = '{:6.1f},          '*l1 # one logavg for each perturb
            t= f.format(Ratio, *log_avgs)
            print ' output: '
            print t
            outputs.append(t)
            results_logP[Ratio] = log_avgs
            
        outputs.append('Simulated {:} Epochs.'.format(NEpochs_test))
        
        print '\n\n\n'
        tmpstr = '         Ratio          '
        for p in tested_perts:
            tmpstr += ' {:4.2f}            '.format(p)
        print 'Log Probabilities\n                  HMM  perturbation '
        print tmpstr
        for line in outputs:
            print '     '+line
        
     # some random asserts based on working state Aug 2020
        #    by random chance these may fail occasionally
        #    These are expected values but do not necessarily PROVE correct fwd alg.
        fs = 'forward algorithm results not as expected'
        if NST == 6:  # values for small model
            assert results_logP[0.0][0] > -6.0, fs
            assert results_logP[0.0][3] > -8.0, fs
            assert results_logP[1.0][0] > -11.0, fs
            assert results_logP[1.0][3] > -9.0, fs
            assert results_logP[2.5][2] > -8.0, fs
        if NST == 16:  # values for small model
            assert results_logP[0.0][0] > -23.0, fs
            assert results_logP[0.0][3] > -28.0, fs
            assert results_logP[1.0][0] > -28.0, fs
            assert results_logP[1.0][3] > -32.0, fs
            assert results_logP[2.5][2] > -32.0, fs
        print 'passed reasonableness assertions'
        
        if not KEEP_DATA:
            for fn in files_used:
                os.remove(fn)
            
        
if __name__ == '__main__':
    unittest.main()





