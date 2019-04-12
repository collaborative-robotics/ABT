import numpy as np
import model01 as m1
import model00 as m0
from peg2_ABT import *
from hmm_bt import *
from abtclass import *
import matplotlib.pyplot as plt

log_avgs = []  # avg log probability 
rused = []     # the output ratio used

#
#   Testing Baum Welch Model ID
#

tol = 0.01   # HMM convergence tol (Delta P)
pert = 0.2   # HMM Param perturbation amount

NST = 6    # Small model
#NST = 16    # Big Model

if NST ==6:
    datafile = 'data_6state.txt'
elif NST == 16:
    datafile = 'data_16state.txt'
else:
    print 'Cant find a suitable dataset file'
    quit()


print '\n\n'
print '          testing BW algorithm: test_baum_welch.py'


if NST < 10:
    print '                  SMALL model'
else:
    print '                  LARGE model'


#for Ratio in RatioList:
for Ratio in [2.5, 0.1]:
    print '\n\n'
    print '          testing BW algorithm with output Ratio: ', Ratio
    print '                                    perturbation: ', pert
    if NST == 16:
        model = m1.modelo01
    elif NST == 6:
        model = m0.modelo00
        
    model.setup_means(FIRSTSYMBOL,Ratio, sig)
    M = HMM_setup(model)
    
    #print ' HMM review: '
    #print 'A'
    #print M.transmat_
    #print 'B'
    #print M.emissionprob_
    #print'\n\n'
    
    model_perturb = 0.2
    test_eps = 0.000001
    
    Ar = np.copy(M.transmat_)   # store the original HMM A matrix
    HMM_model_sizes_check(M)    # just a check for corruption 
    HMM_perturb(M, model_perturb, model)  # change HMM A-Matrix a bit

    # measure how much the A-matrix has changed and characterize changes
    [e,e2,em,N2,im,jm,anoms,erasures] = Adiff(Ar,M.transmat_, model.names)

    #  This is NOT the perturbation test, but just
    ##  some assertions to make sure pertubations are being done right
    #   (if they aren't there's not point in doing the BW test)
    if model_perturb > 0.0:
        assert em > 0.0 , 'Perturbation caused no difference in A matrices'
        assert e2 > 0.0 , 'Perturbation caused no difference in A matrices'
    print 'em: {:.2f}'.format(em)
    print 'e2: {:.2f}'.format(e2)
    # locate output states  HACK
    if model.n < 8:
        outS_index = 4
    else:
        outS_index = 14
    outF_index = outS_index+1
    assert M.transmat_[outS_index,outS_index] - 1.0 < test_eps, 'A 1.0 element was modified'
    assert M.transmat_[outF_index,outF_index] - 1.0 < test_eps, 'A 1.0 element was modified'


    #############################################
    #
    #    Read simulated sequence data
    #

    Y = []    # Observations
    X = []    # True state 
    Ls = []   # Length of each sequence
    seq_data_f = open(datafile,'r')
    [X,Y,Ls] = read_obs_seqs(seq_data_f)
    seq_data_f.close()

    assert len(Y) > 0, 'Empty observation sequence data'
    assert Ls.sum() == len(Y), 'Error in data set sequence lengths'
    assert Ls.sum() == len(X), 'Error in data set sequence lengths'

    #############################################
    #
    #    HMM setup
    #
    A = model.A.copy()
    Ac = A.copy()  # isolate orig A matrix from HMM
    Ar = A.copy()  # reference original copy
    M = HMM_setup(model, tol, 20)   # 20 is a very big iteration count(!)
    
    #############################################
    #
    #   Perturb the HMM's parameters (optional)
    #
    #outputAmat(M.transmat_,'Model A matrix',model.names,sys.stdout)

    HMM_perturb(M, pert, model)
    A_row_test(M.transmat_, sys.stdout)   # Make sure A-Matrix Valid

    
    ############################################
    #
    #    do BW fit
    #
    M.fit(Y,Ls)
    print 'Completed HMM fit(): Converged: ', M.monitor_.converged
    print M.monitor_
             
    
