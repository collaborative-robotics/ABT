from Log_class import *
import numpy as np
# import numpy as np
import numbers
from random import *
import matplotlib.pyplot as plt
#import editdistance as ed   #pip install editdistance
##from tqdm import tqdm
import os
import sys
NSYMBOLS = 40
num = 0
import time
class hmm():
    ########################################
    #Assumes 2D observations
    ########################################
    def __init__(self,states, nsymbols):
    # assert A.shape[0] == A.shape[1] && A.ndim == 2
    # assert b.shape[0] == A,shape[0]
    # self.A = np.log()
    # self.b =
        self.Nstate = states
        self.nsymbols = nsymbols

        # self.Pi = np.broadcast_to(np.array(logP(np.inf)),states)

        self.Pi = np.zeros((states,1))
        self.Pi.setflags(write = 1)
        # self.Pi[0] = logP(1)
        self.Pi[0] = 1
        # self._transmat = np.broadcast_to(np.concatenate((np.array(logP(1)).reshape(1),np.repeat(np.array(logP(0)),states - 1))),(self.Nstate,self.Nstate))

        self._transmat = np.diag(np.ones(self.Nstate))
        # np.concatenate(np.array(logP(1)),np.repeat(np.array(logP(0)),states - 1),axis = 0)
        # np.array(logP(1)),np.repeat(np.array(logP(0)),states - 1)

        # self._emission = np.broadcast_to(np.array(logP(3)),(self.Nstate,self.nsymbols))

        self._emission = np.zeros((self.Nstate,self.nsymbols))
        self._emission.flags['WRITEABLE'] = True
        # print(self._transmat.shape)

# hmm(10,10)
    def Forawrd(self, observation, length):
        log_prob = np.empty(lengths.shape[0])
        for i in range(obsevation.shape[0]):
            # print(length[i])
            foward_lattice = np.empty((self.Nstate,length[i]))
            foward_lattice[:,0] = self.Pi * self._emission[:,observation[i][0]]
            for j in range(1,length[i]-2):
                foward_lattice[:,j] = np.sum(foward_lattice[:,j-1].reshape(1,self.Nstate) * self._transmat, axis = 0) * self._emission[:,observation[i][j]]
            log_prob[i] = np.sum(foward_lattice[:,length(i)])
        return log_prob

    def POlambda(self, Y):
        al = self.Forward_one(Y,len(Y))
        T = len(Y)-1
        a = 0
        for j in range(self.Nstate):
            b = al[j,T]
            a = a + b
        return a

    def Backward(self, observation, length) :
        backward_lattice = np.empty((self.Nstate,length))
        backward_lattice[:,length-1] = 1
        # print((np.sum((self._emission[:,[observation[1+1]]] * self._transmat), axis = 1)).shape)
        for i in range(length-2,-1,-1):
            backward_lattice[:,i] = np.sum((self._emission[:,[observation[i+1]]].T * self._transmat * backward_lattice[:,i+1].T), axis = 1)# * backward_lattice[:,i+1]
        return backward_lattice

    def Viterbi(self, observation, length):
        state_sequence = np.empty((observation.shape[0],np.max(length)))
        for i in range(observation.shape[0]):
            prob_sequence = np.zeros((self.Nstate,np.max(length)))
            veter_lattice = np.zeros((self.Nstate,length[i]))
            veter_lattice[:,0] = (self.Pi * self._emission[:,[observation[i][0]]]).T
            prob_sequence[:,0] = 0
            for j in range(1,length[i]):
                d = veter_lattice[:,[j-1]] * self._transmat
                veter_lattice[:,j] = np.amax(d,axis = 0) * self._emission[:,[observation[i][j]]].T
                prob_sequence[:,j] = np.argmax(d,axis = 0)
            endprob  = np.max(veter_lattice[:,-1])
            endarg = np.argmax(veter_lattice[:,-1])
            state_sequence[i][length[i]-1] = endarg
            for k in range(length[i]-2,-1,-1):
                state_sequence[i][k] = prob_sequence[int(state_sequence[i][k+1])][k+1]
        return state_sequence

    def Forward_one(self,observation,length):
        foward_lattice = np.zeros((self.Nstate,length))
        foward_lattice[:,0] = (self.Pi * self._emission[:,[observation[0]]]).T
        for j in range(0,length-1):
            foward_lattice[:,j+1] = np.sum(foward_lattice[:,[j]]* self._transmat, axis = 0) * self._emission[:,[observation[j+1]]].T
        return foward_lattice


    def BaumWelch(self,observation,length):
        denoms = np.zeros(1,self.Nstate)
        nums = np.zeros((self.Nstate,self.Nstate))
        denoms2 = np.zeros(self.Nstate)
        bnums = np.zeros((self.Nstate,self.nsymbols))
        for i in range(observation.shape[0]):
            foward_lattice = self.Forward_one(observation[i],length[i])
            backward_lattice = self.Backward(observation[i],length[i])
            # Numerator
            xi = np.zeros((length[i],self.Nstate,self.Nstate)) #TODO: Correction
            for j in range(0,length[i]-1):

                xi[j] = foward_lattice[:,[j]] * self._transmat * self._emission[:,[observation[i][j+1]]].T * backward_lattice[:,[j+1]].T
                xi[j] /= np.sum(xi[j])
            # xi /= np.sum(xi)
            # xi2 = xi;
            # xi2[length[i]-1] = 0
            nums = nums + np.sum(xi[:-2],axis = 0)
            denom = np.sum(np.sum(xi[:-2],axis = 2),axis = 0)
            denoms += denom
            #Update
            # print("::::",denom.shape)
            # print("::::",(np.sum(xi,axis = 0)).shape)
            # self._transmat = np.sum(xi,axis = 0) / denom#.reshape(self.Nstate,1)
            #_emission update
            gamma2 = np.sum(xi,axis = 1)
            denom2 = np.sum(np.sum(xi,axis = 1),axis = 0)
            denoms2 += denom2
            # print(":::::::::",gamma2.shape,denom2.shape)
            # b = np.tile(np.array(logP(0)),(nstate,nsymbols))
            b = np.zeros((self.Nstate,self.nsymbols))
            # print((b[:,[observation[i][j]]] + gamma2[[j]].T).shape)
            # print((b[:,observation[i][j]] + gamma2[[j]]).shape)
            for j in range(length[i]):
                b[:,observation[i][j]] = np.squeeze(b[:,[observation[i][j]]].T + gamma2[[j]].T)
            # print(denom2.shape,b.shape)
            # b /= denom2.reshape(self.Nstate,1)
            bnums += b
        self._transmat = nums/denoms
        self._emission = bnums/denoms2.reshape(denoms.shape[0],1)

    def baum_welch_step(self,observation,length):
        global num
        alpha = self.Forward_one(observation, length)
        beta =self.Backward(observation, length)
        num_a = np.zeros((self.Nstate,self.Nstate))
        den_a = np.zeros((self.Nstate,1))
        num_b = np.zeros(self._emission.shape)
        # print(self._emission.shape)
        den_b = np.zeros((self.Nstate,1))
        for i in range(len(observation)-1):
            # print("Point: ",i)
            # print(alpha[-1,i],beta[-1,i+1],self._emission[-1,[observation[i+1]]])#,self._transmat[-1,-1])
            num_a += alpha[:,[i]] * self._transmat * self._emission[:,[observation[i+1]]].T * beta[:,[i+1]].T
            num_b[:,observation[i]] = np.squeeze(num_b[:,[observation[i]]] + alpha[:,[i]] * beta[:,[i]])
        den_a = np.sum((alpha * beta)[:,:-1], axis = 1).reshape(self.Nstate,1)
        den_b = np.sum((alpha * beta)[:,:-1], axis = 1).reshape(self.Nstate,1)
        return num_a, num_b, den_a, den_b

    def fit(self,observations,lengths):
        num_a = np.zeros((self.Nstate,self.Nstate))
        den_a = np.zeros((self.Nstate,1))
        num_b = np.zeros(self._emission.shape)
        den_b = np.zeros((self.Nstate,1))
        list = []
        for i in range(len(lengths)):

            observation = observations[i]
            # print(observation)
            length = lengths[i]
            # prob = self.POlambda(observation)
            na,nb,da,db = self.baum_welch_step(observation,length)
            list.append(na[0,0])
            num_a += na#/prob
            num_b += nb#/prob
            den_a += da#/prob
            den_b += db#/prob
        print(num_a)
        print("2: ", num_b)
        # exit()
        self._transmat = num_a/den_a
        self._emission = num_b/den_b

    def sample(self,T):
        states = []
        emissions = []
        # initial starting state
        state, p = self.pick_from_vec(self.Pi)
        states.append(state)
        #print 'initial state: ',state
        # main loop
        for i in range(T-1):
            # generate emission
            em, p = self.pick_from_vec(self._emission[state,:])
            emissions.append(em)
            # find next state
            state, p = self.pick_from_vec(self._transmat[state,:])
            #print 'next state: ', state
            states.append(state)

        # generate a final emission
        em, p = self.pick_from_vec(self._emission[state,:])
        emissions.append(em)
        return (states, emissions)

##########################################################################
#
#   Utility functions
#
    def vec_normalize(self, v):
        sum = np.sum(v)
        return v/sum

    def pick_from_vec(self,vector):
        if STRICT:
            vector = self.vec_normalize(vector)
            self.row_check(vector,len(vector))

        r = random()
        P = 0.0
        for i in range(len(vector)):
            P += vector[i]
            if r<=P:
                return (i, vector[i])
        self._error('invalid prob vector')

    def check(self):
        print ('model check:')
        sh = np.shape(self._transmat)
        if (sh[0] != self.Nstate or sh[1] != self.Nstate):
            self.error(' _transmat wrong size')
        sh = np.shape(self._emission)
        if (sh[0] != self.Nstate or sh[1] != NSYMBOLS):
            self.error(' _emission wrong size')
        for r in range(self.Nstate):
            self.row_check(self._transmat[r],self.Nstate)
        sum = 0.0
        print ('got here')
        print(self._emission.dtype)
        print(self._transmat.dtype)
        # exit()
        for st in range(self.Nstate):
            self.row_check(self._emission[st,:],NSYMBOLS)
        print("Staring probability check: ")
        self.row_check(self.Pi,self.Nstate)


    def row_check(self,row,m):
        valid = True
        #print 'row_check:', row
        sum = 0.0
        for c in range(m):
            t = row[c]
            if t > 1.0 or  t < 0.0 :
                print ('illegal probability found')
                valid = False
            sum += t
        if abs(sum-1.0) > epsilon:
            valid = False
        if not valid:
            print (row)
            print ('Sum: ', sum)
            self._error('a vector failed row check: sum != 1.0')
        return True


    def _error(self,msg):
        print ('hmm class (hmm_bh): ' + msg)
        quit()

    def probability_check(self,Obs):
        a = self.Forward_one(Obs,len(Obs))
        return np.sum(a[:,-1])

#################################################################################################
#################################################################################################
#################################################################################################
#
#     TESTS of hmm_log class
#

if __name__ == '__main__':

    STRICT = True
    epsilon = 1.0E-4
    FAIL = '          FAIL'
    PASS = '          PASS'
    ###################################
    # hmm class tests
    start = time.time()
    # test pic_from_vect(v)
    m = hmm(10,10)
    vector = [0,0,0,.333,.333,.333, 0,0,0]  # note sum = 0.9990000
    #optional if not STRICT:
    #vector = m.vec_normalize(vector)
    fs = 'test pic_from_vec'
    for i in range(10000):  # this really tests sum=1.000000
        x,p = m.pick_from_vec(vector)
        assert (x >1 and  x <= 5), fs+FAIL
    print (fs+PASS)


    ######################################
    #
    #  test model setups for hmm
    #
    w = 6
    A5 = np.array([[.5,.5,0,0,0],[0,.6,.4,0,0],[0,0,.75,.25,0],[0,0,0,0.8,0.2],[0,0,0,0,1.0]])
    pv = [0.5, 0.5, 0.7, 0.65, 0.8, 0.5, 0.3,0.6,0.7, 1.0]

    A10 = np.zeros((10,10))

    nsim_samples = 20
    nsim_rollouts = 100

    for r in range(10):
        A10[r,r] = pv[r]
        if(r+1 < 10):
            A10[r,r+1] = 1.0-A10[r,r]

    for ntest in [5]:
        fs =  '\n\ntesting hmm with ' + str(ntest) + ' states'
        print (fs)
        m = hmm(ntest,NSYMBOLS)
        if ntest == 5:
            m._transmat = A5.copy()
        else:
            m._transmat = A10.copy()
        # print (m._transmat)
        # exit()
        #   set up emission probabilities with width of 'w' symbols

        for i in range(m.Nstate):
            mu = 0.5*w*(i+1)
            for j in range(m.nsymbols):
                m._emission[i,j] = 0.0
                if j>mu-w/2 and j<=(mu+w/2):
                    m._emission[i,j] = 1/float(w)
        #print m._emission
        #if ntest == 10:
            #quit()
        # print(m._emission,m._transmat,m.Pi)
        # exit()
        m.check()
        print (fs + ' [setup] ' + PASS)

        ##############################################################
        #
        #    Simulate the HMM
        #
        st, em = m.sample(nsim_samples)
        print ('----------- state sequence & emissions -----------------------')
        print (st)
        print (em)
        assert len(st) == len(em), 'Emissions dont match states from sample()'

        print ('\n\nTest valid sample outputs:')
        for i,s in enumerate(st):
            #print 'checking: ' , i, s, em[i]
            if m._emission[s,em[i]] < epsilon:
                m._error('invalid emission detected')
        # print(m._emission.sum())
        # print(m._transmat)
        # exit()
        print ('got valid emissions')

        print ('\nForward Algorithm:')

        #print 'state estimate: '
        #print '       forwardS()   (regular math)'
        #print m.forwardS(em)
        #print '       forwardSL()  (log math)'
        #print '         (v-matrix)'

        TINY_EPSILON = 1.0E-20

        print ('\n     Test    Forward Algorithm:')
        fs = '   forward algorithm, forwardSL(em) '
        stseq =  [0, 0, 1, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4]
        em = [6, 3, 6, 6, 8, 12, 14, 10, 15, 14, 14, 15, 12, 13, 16]
        alpha =  m.Forward_one(np.array(em),len(em))
        print(alpha.T)
        # exit()
        # print ('------------alpha-------------')
        # print (alpha)
        # exit()

        #print alpha[14,4].test_val()
        #assert abs(alpha[14,4].test_val()-9.35945852879e-13) < TINY_EPSILON, fs+FAIL
        #assert abs(alpha[ 2,0].test_val()-0.000578703703704) < epsilon, fs+FAIL
        print (fs+PASS)


        print ('\n     Test    Backward Algorithm:')
        stseq =  [0, 0, 1, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4]
        em = [6, 3, 6, 6, 8, 12, 14, 10, 15, 14, 14, 15, 12, 13, 16]

        beta_test =  m.Backward(em,len(em))
        fs = '    backwards algorithm backwardSL(em) '
        print (beta_test.T)
        # exit()
        #assert abs(beta_test[13,3].test_val()-0.1666666666667)<epsilon, fs+FAIL
        #assert abs(beta_test[ 3,0].test_val()-9.57396964103e-11) < TINY_EPSILON , fs+FAIL
        #print fs+PASS

        print ('\n\n Test Viterbi Algorithm:')
        print ('st:',st)
        print ('em:',em)
        #print m._emission
        stseq =  [0, 0, 1, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4,4,4]
        #  NOTE: for BW testing w/ non stationary model, last state must be
        #        occupied more than once!
        em = [6, 3, 6, 6, 8, 12, 14, 10, 15, 14, 14, 15, 12, 13, 16,16,16]

        est_correct = [0,0,1,1,2,3,3,3,3,3,3,3,3,4,4,4,4]
        fs = 'test setup problem - data length mismatch'
        assert len(em) == len(stseq), fs
        assert len(em) == len(est_correct), fs
        # print("Trans":)
        qs = m.Viterbi(np.array(em, ndmin = 2),np.array(len(em), ndmin = 1))
        fs = 'Vitermi state estimation tests'
        # print(qs.shape)
        # exit()
        for i,q in enumerate(np.nditer(qs[0])):
            # print (q,est_correct[i])
            assert q==est_correct[i], fs+FAIL
        print (fs+PASS)
        end = time.time()
        print(end-start)

        #
        #   Let's try the Baum Welch!
        #
        print  ('\n\n   Test Baum Welch fit() method')
        # p0 = m.POlambda(em) #TODO
        # m.fit(np.array(em, ndmin = 2),np.array(len(em), ndmin = 1))
        #p1 = m.POlambda(em)
        ##r = raw_input('<cr>')
        # m.fit([em],[len(em)])
        # print(m._transmat)
        # print(m._emission)
        # exit()
        #p2 = m.POlambda(em)
        ##r = raw_input('<cr>')
        #m.fit(em)
        #p3 = m.POlambda(em)

        print ("    Change in PO-lambda: ")
        # print (p0) #TODO
        #print p1
        #print p2
        #print p3

        print ('\n\n        -- --  --   Multiple Runout HMM.fit()  -- -- -- \n\n\n')


        ###################################################################
        #
        #    Generate the data
        #

        Obs = []
        Sts = []   # true state sequences
        Ls  = []
        Obsll = []
        nrunout = 1000
        for rn in range(nrunout):
            #    Simulate the HMM
            # print("HIT")
            st, em = m.sample(nsim_samples)
            Obs.extend(em)
            Obsll.append(em)  # as list of lists
            Sts.extend(st)
            Ls.append(len(st))
        import pickle
        with open('Obs', 'rb') as fp:
            Obs = pickle.load(fp)
        with open('Obsll','rb') as fp2:
            Obsll = pickle.load(fp2)
        # print((np.array(Obsll)).shape)
        # print(Ls)
        Obsll = np.array(Obsll)
        print(Obsll.shape)
        a = m._transmat
        b = m._emission
        print ('Initial Prob: ', m.probability_check(Obsll[1]))
        for i in range(10):
            m.fit(Obsll,Ls)
        print(np.array_equal(a,m._transmat),np.array_equal(b,m._emission))
        # print(m._transmat.sum(axis = 1))
        # print(m._emission)
        # print(m._transmat)
        print ('Final Prob:   ', m.probability_check(Obsll[1]))

        print (' \n\n               Completed  Test Runs  of hmm_log package   \n\n')
