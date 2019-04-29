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
#NST = 16



if NST < 10:
    print '                  SMALL model'
    from simp_ABT import *   # req'd for 6-state
else:
    print '                  LARGE model'
    from peg2_ABT import *  # req'd for 16-state


for Ratio in RatioList:

    if NST == 16:
        model = m1.modelo01
    elif NST == 6:
        model = m0.modelo00
    
        
    model.setup_means(FIRSTSYMBOL,Ratio, sig)
    M = HMM_setup(model)

    #print '   HMM emission probabilities:'
    #for i in range(len(model.names)):
        #print i, M.emissionprob_[i]
        
    # for now pick states 2,3. consecutive(!) (exist in both models!)
    
    pr = HMM_Project(M,2,3)
    pr_all = HMM_ProjectAll(M)
    
    #print 'Ratio: ', Ratio, 'Pr(2,3) ', pr, ' All states: ', pr_all
    
    line = '{:d} & {:5.2f} & {:.2e} & {:.2e} \\ \hline'.format(NST, Ratio, pr, pr_all)
    print line
