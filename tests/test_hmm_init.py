#!/usr/bin/python
#
#  test HMM_setup(model) function  **in hmm_by.py**
## hmm model params

import unittest
import mock

from tests.common import *
#from common import *


import numpy as np
import abt_constants
from abtclass import *
from hmm_bt import *
 


class Test_hmm_init(unittest.TestCase):


    def test_init1(self):
             
        names = ['l1','l2a1','l2b1','l2a2','l2b2', 'l345', 'l6a1', 'l6b1', 'l6a2', 'l6b2', 'l789', 'l10a1', 'l10b1', 'l10c1', 'OutS', 'OutF']

        N = len(names)
        # prob success for each node
        # note dummy value for PS[0] for math consistency
        PS = [0.0, 1.0, 0.9, 0.8, 0.9, 0.9, 1.0, 0.9, 0.8, 0.9, 0.9, 1.0,0.9,0.75, 0.8, 1.0, 1.0]
        if len(PS) != N+1:
            print 'Incorrect PS length'
            quit()
            
            
        # INITIAL State Transition Probabilities
        #  make A one bigger to make index human
        A = np.zeros((17,17))
        A[1,2] = PS[1]
        A[1,16] = 1.0-PS[1]
        A[2,3] = PS[2]
        A[2,4] = 1.0-PS[2]
        A[3,4] = 1.0-PS[3]
        A[3,6] = PS[3]
        A[4,5] = PS[4]
        A[4,16] = 1.0-PS[4]
        A[5,6] = PS[5]
        A[5,16] = 1.0-PS[5]
        A[6,7] = PS[6]
        A[7,8] = PS[7]
        A[7,9] = 1.0-PS[7]
        A[8,9] = 1.0-PS[8]
        A[8,11] = PS[8]
        A[9,10] = PS[9]
        A[9,16] = 1.0-PS[9]
        A[10,11] = PS[10]
        A[10,16] = 1.0-PS[10]
        A[11,12] = PS[11]
        A[12,13] = PS[12]
        A[12,16] = 1.0-PS[12]
        A[13,14] = PS[13]
        A[13,16] = 1.0-PS[13]
        A[14,15] = PS[14]
        A[14,16] = 1.0-PS[14]
        A[15,15] = PS[15]
        A[16,16] = PS[16]

        A = A[1:17,1:17]  # get zero offset index

        #
        outputs = {'l1':2, 'l2a1': 5, 'l2b1':8, 'l2a2': 8,  'l2b2':11, 'l345':14, 'l6a1':17, 'l6b1':20, 'l6a2':23, 'l6b2':26, 'l789':29, 'l10a1':33, 'l10b1':36, 'l10c1':28, 'OutS':30, 'OutF':30}

        statenos = {'l1':1, 'l2a1': 2, 'l2b1':3, 'l2a2':4,  'l2b2':5, 'l345':6, 'l6a1':7, 'l6b1':8, 'l6a2':9, 'l6b2':10, 'l789':11, 'l10a1':12, 'l10b1':13, 'l10c1':14, 'OutS':15, 'OutF':16}

        di = 2  # placeholder
        #################################################################
        ##  Regenerate output means:  (easier to change below)
        i = FIRSTSYMBOL
        #di = Ratio*sig  # = nxsigma !!  now in abt_constants
        for n in outputs.keys():
            outputs[n] = i
            i += di
            
        modelT = model(len(names))  # make a new model
        modelT.A = A
        modelT.PS = PS
        modelT.outputs = outputs
        modelT.statenos = statenos
        modelT.names = names
        modelT.sigma = sig

        test_eps = 0.00000001   # test epsilon
        nasserts = 0

        M = HMM_setup(modelT)   #   set up the HMM

                
        fs = 'Failed to properly initialize '
        # compare A matrices

        assert M.n_components == modelT.n
        nasserts += 1

        assert A.all() == M.transmat_.all(), fs + 'A matrix'
        nasserts += 1


        ########## B -matrix
        
        if M.typestring == 'MultinomialHMM': 
            #############################   Multinomial emissions
            #   setup discrete model.B for MultinomialHMM()
            #print np.shape(M.emissionprob_)
            assert np.shape(M.emissionprob_)[0] == M.n_components
            assert (M.emissionprob_ != 0).all(), 'An emission Probability (B) == 0'
            assert (M.emissionprob_  > 0).all(), 'An emission Probability (B) < 0'
            assert (M.emissionprob_ < 1.0).all(), 'An emission Probability (B) > 1.0'
            nasserts += 4

            # Sum should be == number of states (eg 1xM.n_components
            assert np.sum(M.emissionprob_) - M.n_components < M.n_components*test_eps,  'Emmision Probabilities Sum != 1.0)'
            nasserts += 1

            for i,n in enumerate(modelT.names):
                tmp_leaf = abtc.aug_leaf(0.500)  # dummy leaf to use SetObsDensity() method
                ##perturb the mean by bdelta before generating the emission probs.
                ## No perturbation for this testing script: test_hmm_init.py
                bdelta = 0.0
                newmean = modelT.outputs[n] + randsign() * bdelta
                ##print 'Setting mean for state ',i, 'from ' , model.outputs[n], ' to ', newmean
                tmp_leaf.set_Obs_Density(newmean, sig)
                ## TEST: do the HMM emissionprob_ 's match this?
                for j in range(NSYMBOLS):
                    assert modelT.B[i,j] == tmp_leaf.Obs[j], 'mismatch of observation output probs (B[i,j])'    # set up correctly?
                    nasserts += 1

            #M.emissionprob_ = np.array(modelT.B.copy())  # docs unclear on this name!!!!   

        elif M.typestring == 'GaussianHMM':
            # compare output means
            for n in names:
                i = statenos[n]
                o = outputs[n]
                #print 'comparing ', n, M.means_[i-1], o
                assert M.covars_[i-1] == modelT.sigma, fs + ' covariance = sigma ' + str(i)
                nasserts += 1
                assert M.means_[i-1] == o, fs + 'Output mean ' + str(i)
                nasserts += 1
        
        else:
            print 'Unknown model typestring'
            quit() 
            
        print 'Testing HMM setup for ', M.typestring
        print 'HMM_setup PASSED all ', nasserts, ' assertions'


if __name__ == '__main__':
    unittest.main()

