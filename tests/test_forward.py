import numpy as np
import model01 as m1
import model00 as m0
from hmm_bt import *
from abtclass import *
import matplotlib.pyplot as plt

#
#   Effect of output Ratio on Fwd alg perf. with 20% perturbation
#

#NST = 6    # Small model
NST = 16

NEpochs = 15000  #  

print '\n\n'
print '          testing forward algorithm: test_forward.py'
if NST < 10:
    print '                  SMALL model'
    from simp_ABT import *   # req'd for 6-state
else:
    print '                  LARGE model'
    from peg2_ABT import *  # req'd for 16-state

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
    sequence_name =  'Forward_test_sequence'+str(NST)+'stateR'+str(Ratio)+'.txt'
    seq_data_f = open(sequence_name,'w')
    bb.set('logfileptr',seq_data_f)   #allow BT nodes to access/write to file
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
    
    # Now run FWD Alg for various model perts
        
    # reset these for each Ratio
    logps=[]
    log_avgs = []  # avg log probability 
    rused = []     # the output ratio used

    for model_perturb in [0, 0.1, 0.25, 0.50]:
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


        Y = []    # Observations
        X = []    # True state
        seq_lengths = []   # Length of each sequence
        seq_data_f = open(sequence_name,'r')
        [X,Y,seq_lengths] = read_obs_seqs(seq_data_f)
        seq_data_f.close()

        counter = 0
        logprob = 0
        log_avg = 0
        
        OLD = False
        if OLD:  # original method
            for i in range(len(seq_lengths)):
                sample = Y[counter:counter+seq_lengths[i]]
                logprob += M.score(sample,[seq_lengths[i]])
                counter += seq_lengths[i]
            log_avg = logprob/len(seq_lengths)  # not sure this is right but harmless?
            log_avgs.append(log_avg)
            logps.append(logprob)
        else:
            logprob = M.score(Y,seq_lengths)
            logps.append(logprob)
            log_avg = logprob/len(seq_lengths)
            log_avgs.append(log_avg)
            
        rused.append(Ratio)
        
    l1 = len(log_avgs) + 1
    f = '{}, '*l1
    t= f.format(Ratio, *log_avgs)
    print ' output: '
    print t
    outputs.append(t)
    
print '\n\n\n'
for line in outputs:
    print line
    
    
    



