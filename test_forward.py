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
#   Effect of output Ratio on Fwd alg perf. with 20% perturbation
#

#NST = 6    # Small model
NST = 16

print '\n\n'
print '          testing forward algorithm: test_forward.py'
if NST < 10:
    print '                  SMALL model'
else:
    print '                  LARGE model'


for Ratio in RatioList:
    print '\n\n'
    print '          testing forward algorithm with output Ratio: ', Ratio
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
    
    
    model_perturb = 0.5
    test_eps = 0.000001
    
    
    Ar = np.copy(M.transmat_)
    HMM_model_sizes_check(M)
    HMM_perturb(M, model_perturb, model)



    [e,e2,em,N2,im,jm,anoms,erasures] = Adiff(Ar,M.transmat_, model.names)


    ##  some assertions to make sure pertubations are being done right
    #   (if they aren't there's not point in doing the sim)
    if model_perturb > 0.0:
        assert em > 0.0 , 'Perturbation caused no difference in A matrices'
        assert e2 > 0.0 , 'Perturbation caused no difference in A matrices'
    print 'em: {:.2f}'.format(em)
    print 'e2: {:.2f}'.format(e2)
    if model.n < 8:
        outS_index = 4
    else:
        outS_index = 14
    outF_index = outS_index+1
    assert M.transmat_[outS_index,outS_index] - 1.0 < test_eps, 'A 1.0 element was modified'
    assert M.transmat_[outF_index,outF_index] - 1.0 < test_eps, 'A 1.0 element was modified'
    print 'Passed A-matrix Assertions'



    # for i in range(M.emissionprob_.shape[0]):
    #     plt.bar(np.arange(NSYMBOLS),M.emissionprob_[i])
    # plt.show()
    # exit(0)
    [ABT, bb, leaves] = ABTtree(model)


    sequence_name =  'Forward_test_sequence.txt'
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

    Y = []    # Observations
    X = []    # True state
    Ls = []   # Length of each sequence
    seq_data_f = open(sequence_name,'r')
    [X,Y,Ls] = read_obs_seqs(seq_data_f)
    seq_data_f.close()

    counter = 0
    logprob = 0
    log_avg = 0
    for i in range(len(Ls)):
        sample = Y[counter:counter+Ls[i]]
        logprob += M.score(sample,[Ls[i]])
        counter += Ls[i]
    log_avg = logprob/len(Ls)
    log_avgs.append(log_avg)
    rused.append(Ratio)
    
print '\n\nModel perturb: ', model_perturb
print 'Symbol mean ratios: ', rused
print 'Log Probs:          ', log_avgs

pr1 = log_avgs[rused.index(5.0)]
pr2 = log_avgs[rused.index(0.25)]

