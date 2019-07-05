import numpy as np
import model01 as m1
import model00 as m0
from hmm_bt import *
from abtclass import *
import matplotlib.pyplot as plt

logps=[]
log_avgs = []  # avg log probability 
rused = []     # the output ratio used

#
#   Effect of output Ratio on Fwd alg perf. with 20% perturbation
#
 
print '\n\n'
print '          testing "projection" metric for HMM transparency: test_projection.py'


NST = 6    # Small model
NST = 16



if NST < 10:
    print '                  SMALL model'
    from simp_ABT import *   # req'd for 6-state
else:
    print '                  LARGE model'
    from peg2_ABT import *  # req'd for 16-state



print '\n(compare states 2,3)\nN states & Ratio & KLD  & JSD & JSAll\\\\ \\hline'


print'\n\nN & Ratio & $KLD$ & $JSD$ & $JSD_{ALL}$'
for Ratio in RatioList:

    if NST == 16:
        model = m1.modelo01
    elif NST == 6:
        model = m0.modelo00
    
        
    model.setup_means(FIRSTSYMBOL,Ratio, 2.0)
    #
    
    M = HMM_setup(model)

    #  Make sure no obs probs are exaclty 0.0  use pmin instead 
    for i,n in enumerate(model.names):
        tmp_leaf = abtc.aug_leaf(0.500)  # dummy leaf to use SetObsDensity() method
        tmp_leaf.set_Obs_Density(model.outputs[n], sig)
        for j in range(NSYMBOLS):
            model.B[i,j] = tmp_leaf.Obs[j]    # guarantees same P's as ABT(!)
    M.emissionprob_ = np.array(model.B.copy())  # docs unclear on this name!!!!
    
    
    #print '   HMM emission probabilities:'
    #for i in range(len(model.names)):
        #print i, M.emissionprob_[i]
        
    # for now pick states 2,3. consecutive(!) (exist in both models!)
    
    pr = HMM_Project(M,2,3)
    pr_all = HMM_ProjectAll(M)
    kld = KL_diverge(M,2,3)
    jsd = JS_diverge(M,2,3)
    jsa = JS_ALL(M)
    
    line = '{:d} & {:.2f} &  {:.2f} & {:.2f} & {:.2f} \\\\ \hline'.format(NST, Ratio,  kld,jsd, jsa)
    print line
    
print 'log2(N) =', np.log2(NST)
