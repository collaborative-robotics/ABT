import numpy as np
import model01 as m1
import model00 as m0
from peg2_ABT import *
from hmm_bt import *
from abtclass import *
import matplotlib.pyplot as plt
import datetime
import subprocess

log_avgs = []  # avg log probability 
rused = []     # the output ratio used

#
#   Testing Baum Welch Model ID
#

tol = 1.0   # HMM convergence tol (Delta P)
pert = 0.2   # HMM Param perturbation amount

NST = 6    # Small model
#NST = 16    # Big Model

# if these data files don't exist, you can generate them with 
#   test_forward.py w/ KEEPDATA = True and renaming files
test_data_prefix = 'tests/data_for_tests/'
if NST ==6:
    datafile = test_data_prefix + 'BW_test_data_6state.txt'
    testing_model = m0.modelo00

elif NST == 16:
    datafile = test_data_prefix + 'BW_test_data_16state.txt'
    testing_model = m1.modelo01
else:
    print 'Cant figure out a suitable dataset file'
    quit()

print '\n\n'
print '          testing BW algorithm: test_baum_welch.py'

git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'])[:10]  # first 10 chars to ID software version


if NST < 10:
    print '                  SMALL model'
else:
    print '                  LARGE model'


#for Ratio in RatioList:
for Ratio in [2.1]:
    print '\n\n'
    print '          testing BW algorithm with output Ratio: ', Ratio
    print '                                    perturbation: ', pert

        
    testing_model.setup_means(FIRSTSYMBOL,Ratio, sig)
    M = HMM_setup(testing_model)
    
    #print ' HMM review: '
    #print 'A'
    #print M.transmat_
    #print 'B'
    #print M.emissionprob_
    #print M.emissionprob_.shape
    #print'\n\n'
    
    model_perturb = 0.2
    test_eps = 0.000001
    
    Ar = np.copy(M.transmat_)   # store the original HMM A matrix
    HMM_model_sizes_check(M)    # just a check for corruption 
    HMM_perturb(M, model_perturb, testing_model)  # change HMM A-Matrix a bit

    # measure how much the A-matrix has changed and characterize changes
    [e,e2,em,N2,im,jm,anoms,erasures] = Adiff(Ar,M.transmat_, testing_model.names)

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
    A = testing_model.A.copy()
    Ac = A.copy()  # isolate orig A matrix from HMM
    Ar = A.copy()  # reference original copy

    M = HMM_setup(testing_model, tol, 20)   # 20 is a very big iteration count(!)
    M2 = HMM_setup(testing_model, tol, 20)   # Identical Copy

    #############################################
    #
    #   Perturb the HMM's parameters (optional)
    #
    #outputAmat(M.transmat_,'Model A matrix',testing_model.names,sys.stdout)

    HMM_perturb(M, pert, testing_model)
    A_row_test(M.transmat_, sys.stdout)   # Make sure A-Matrix Valid
    HMM_model_sizes_check(M)    # just a check for corruption 

    #############################################
    #
    #  Check sequence data
    #
    A_row_test(M.transmat_, sys.stdout)
    print "starting HMM fit with ", len(Y), ' observations.'
    outputAmat(M.transmat_, 'A-matrix for multinomial BW', testing_model.names)
    M._check_input_symbols(Y)
    print 'Input symbols Passed'   

    ############################################
    #
    #    do BW fit
    #
    print ' starting Baum Welch algorithm on data'
    print ' iteration progress ...'
    M.fit(Y,Ls)
    print 'Completed HMM fit(): Converged: ', M.monitor_.converged
    print M.monitor_
             
        
    ##################################################
    #
    #    Report on changes of A matrix due to BW adaptation
    #

    print '\n\n'
    print 'Ratio = ', Ratio, '   HMM delta / perturbation = ', pert

    print "Initial FIT M2->M: "
    Adiff_Report(M2.transmat_, M.transmat_, testing_model.names,of=sys.stdout)

    [e,e2,em,N2,im,jm,anoms,erasures] = Adiff(M.transmat_,M2.transmat_, testing_model.names)
    
    print 'e2:', e2
    print 'em:', em
    print 'im:', im
    print 'jm:', jm
    print 'anoms: ', anoms
    print 'erasures:', erasures
    
    print 'baum welch algorithm passed -- but performance seems poor tbd...'


