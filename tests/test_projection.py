# b3 class modified by BH, local version in current dir
#import random as random
import numpy as np
#from abt_class import *

import unittest
import mock

from tests.common import *
#from common import *

import abt_constants
from abtclass import *
from hmm_bt import *
 
##   specific to this test
import model01 as m1
import model00 as m0
import matplotlib.pyplot as plt

NST = 6    # Small model
#NST = 16
 

if NST < 10:
    print '                  SMALL model'
    from simp_ABT import *   # req'd for 6-state
else:
    print '                  LARGE model'
    from peg2_ABT import *  # req'd for 16-state


class Test_projection(unittest.TestCase):


    def test_projection(self):
        #
        #  This test is sort of analytical/exploratory. Thus there are no assertions
        #    however it should not error out.
        #
        

        logps=[]
        log_avgs = []  # avg log probability 
        rused = []     # the output ratio used

        #
        #   Effect of output Ratio on Fwd alg perf. with 20% perturbation
        #
        
        print '\n\n'
        print '          testing "projection" metric for HMM transparency: test_projection.py'


        # choose two state to compare
        if NST == 16:
            s1 = 10
            s2 = 11
        elif NST == 6:
            s1 = 4
            s2 = 5

        print '\n(compare states {:d},{:d})\nN states & Ratio & KLD  & JSD & JSAll\\\\ \\hline'.format(s1,s2)


        print'\n\nN & Ratio & $KLD$ & $JSD$ & $JSD_{ALL}$'
        
        for Ratio in RatioList:

            if NST == 16:
                model = m1.modelo01
            elif NST == 6:
                model = m0.modelo00
                
            model.setup_means(FIRSTSYMBOL,Ratio, 2.0)
            #
            
            M = HMM_setup(model)

            #  Make sure no obs probs are exactly 0.0  use pmin instead 
            for i,n in enumerate(model.names):
                tmp_leaf = abtc.aug_leaf(0.500)  # dummy leaf to use SetObsDensity() method
                tmp_leaf.set_Obs_Density(model.outputs[n], sig)
                for j in range(NSYMBOLS):
                    model.B[i,j] = tmp_leaf.Obs[j]    # guarantees same P's as ABT(!)
            M.emissionprob_ = np.array(model.B.copy())  # docs unclear on this name!!!!
            
            
            #print '   HMM emission probabilities:'
            #for i in range(len(model.names)):
                #print i, M.emissionprob_[i]
                
            # for now pick states s1,s2. consecutive(!) (exist in both models!)
            
            pr = HMM_Project(M,s1,s2)
            pr_all = HMM_ProjectAll(M)
            kld = KL_diverge(M,s1,s2)
            jsd = JS_diverge(M,s1,s2)
            jsa = JS_ALL(M)
            
            line = '{:d} & {:.2f} &  {:.2f} & {:.2f} & {:.2f} \\\\ \hline'.format(NST, Ratio,  kld,jsd, jsa)
            print line
            
        print 'Single compare: ', s1,s2
        print 'log2(N) =', np.log2(NST)



if __name__ == '__main__':
    unittest.main()


