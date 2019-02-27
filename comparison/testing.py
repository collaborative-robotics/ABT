import numpy as np
import nltk
from abt_constants import *
import hmm_log as blake
from HMM import *
import math as m
from sklearn.preprocessing import normalize

np.random.seed(1000)

class data_gen:
    def __init__(self,a,b, pi):
        assert np.array_equal(pi.shape[0],a.shape[0])
        assert np.array_equal(a.shape[0],a.shape[1])
        assert np.array_equal(b.shape[0], a.shape[0])
        # print(np.sum(a,axis = 1).shape, np.ones(a.shape[0]).shape)
        # assert np.array_equal(np.sum(a,axis = 1), np.ones(a.shape[0]))
        # assert np.array_equal(np.sum(a,axis = 0),np.ones(a.shape[0]))
        # assert np.array_equal(np.sum(b,axis = 0),np.ones(b.shape[1]))
        self.transmat = a
        self.emission = b
        assert np.sum(pi) == 1 and pi[-1] == 0
        self.pi = pi

    def generate_data(self, lr = False):
        state = np.random.choice(np.arange(self.pi.shape[0]), p = self.pi)
        st =[]
        obs = []
        st.append(state)
        if lr ==  False:
            while state != self.transmat.shape[0] - 1:
                # print(self.emission.shape[1], self.emission[state,:].shape)
                observation = np.random.choice(np.arange(self.emission.shape[1]), p = self.emission[state,:])
                obs.append(observation)
                state = np.random.choice(np.arange(self.transmat.shape[0]), p  = self.transmat[state,:])
                st.append(state)
                # print(state, self.transmat.shape[0] - 1)
            obs.append(np.random.choice(np.arange(self.emission.shape[1]), p = self.emission[state,:]))
            return st, obs
        if lr ==  True:
            # print("HIt")
            # exit()
            while state != self.transmat.shape[0] - 1 and state != self.transmat.shape[0] - 2:
                # print(self.emission.shape[1], self.emission[state,:].shape)
                observation = np.random.choice(np.arange(self.emission.shape[1]), p = self.emission[state,:])
                obs.append(observation)
                state = np.random.choice(np.arange(self.transmat.shape[0]), p  = self.transmat[state,:])
                st.append(state)
                # print(state, self.transmat.shape[0] - 1)
            obs.append(np.random.choice(np.arange(self.emission.shape[1]), p = self.emission[state,:]))
            return st, obs

    def runout(self, runouts, model = "vidur", flag =  False):
        if model == "vidur":
            obs = []
            sts = []
            l = []
            for i in range(runouts):
                st, ob = self.generate_data(flag)
                obs.append(ob)
                sts.append(st)
                l.append(len(ob))
            return obs,l

        if model == "NLTK":
            obs = []
            for i in range(runouts):
                st, ob = self.generate_data()
                o = []
                for j in range(len(st)):
                    o.append((ob[j],st[j]))
                obs.append(o)
            return obs
        if model == "blake":
            obs = []
            l = []
            for i in range(runouts):
                st,ob = self.generate_data()
                obs.extend(ob)
                l.append(len(ob))
            return obs, l
        else:
            print("Better Luck next time")
            exit()

def HMM(A,B,pi,lib = "vidur"):
    states = list(range(A.shape[0]))
    corpus = list(range(B.shape[1]))
    if lib == "vidur":
        model = hmm(A.shape[0], b.shape[1])
        model.custom(pi,A,B)
        return model
    if lib == "blake":
        model = blake.hmm(A.shape[0])
        model.custom(pi,A,B)
        return model
    if lib == "NLTK":
        transitionc = {}
        for i,condition in enumerate(states):
            dic = {}
            for j,state in enumerate(states):
                dic[state] = A[i][j]
            transitionc[condition] = ( nltk.probability.DictionaryProbDist(dic))
        transitionc = nltk.probability.DictionaryConditionalProbDist(transitionc);

        emissionc = {}
        for i,condition in enumerate(corpus):
            dic = {}
            for j,state in enumerate(states):
                dic[state] = B[j][i]
            emissionc[condition] = ( nltk.probability.DictionaryProbDist(dic))

        initialc = {}
        for i,condition in enumerate(states):
            initialc[condition] = pi[i]
        print(initialc)
        initialc = nltk.probability.DictionaryProbDist(initialc)
        emissionc = nltk.probability.DictionaryConditionalProbDist(transitionc);
        model = nltk.tag.hmm.HiddenMarkovModelTagger(list(corpus),states,transitionc,emissionc,initialc)
        # trainer = nltk.tag.hmm.HiddenMarkovModelTrainer()
        return model
        # trainer.train_unsupervised(unlabeled_sequences=obs_nltk , model = model, max_iterations = 1)
        # print(initialc, emissionc, transitionc)
    else:
        print("Try again next time")
        exit()

def set_Obs_Density(mu, sig, NSYMBOLS):
    Obs = np.zeros(NSYMBOLS)
    if (mu+sig) > NSYMBOLS or ((mu-sig) < 0):
        print ('aug_leaf: Warning may gen negative/overrange observations')
        print (self.Name, mu, sig)
        #quit()
    psum = 0.0
    pmin = 1.0e-9 # smallest allowed probability (see test_obs_stats.py!!)
    for j in range(NSYMBOLS):
        Obs[j] = gaussian(float(j),float(mu),float(sig))
        #clear the tiny numerical values
        if Obs[j] < pmin:
            Obs[j] = pmin   ###   require B[i,j] >= pmin
        psum += Obs[j]

    #normalize the Observation distrib so it sums to 1.000
    for j in range(NSYMBOLS):
        Obs[j] /= psum
    return Obs

def gaussian(x, mu, sig):
    sig = abs(sig)
    a = 1.0/(sig*(m.sqrt(2*m.pi))) * m.exp(-0.5*((x-mu)/sig)**2)
    #print "A gaussian: ", a
    return a

def HMM_fully_random(A,B):
    A_rand = A
    [rn,cn] = A_rand.shape
    for r in range(rn):
        rsum = 0.0
        for c in range(cn):
            A_rand[r][c] = np.random.random()
            rsum += A_rand[r][c]
        for c in range(cn):  # normalize the rows
            A_rand[r][c] /= rsum

    # randomize means of the output observation
        B = normalize(np.random.random(B.shape), norm = 'l1', axis = 1)


    return A_rand, B


if __name__ == "__main__":
    # a = np.array([[.35, .35 , .3], [.5,.3, .2], [0,0,1]])
    # b = np.array([[.35, .35 , .3], [.5,.3, .2], [0,0,1]])
    # gen = data_gen(a,b,np.array([.2,.8,0]))
    # print(gen.generate_data())
    # ********************* NON- ERGODIC****************************
    PS = [0, 0.5, 0.5, .5, 0.5, 1.0,1.0]
    N = 6
    A = np.zeros((N+1,N+1))
    A[1,2] = PS[1]
    A[1,6] = 1.0-PS[1]
    A[2,3] = PS[2]
    A[2,6] = 1.0-PS[2]
    A[3,4] = 1.0-PS[3]
    A[3,5] = PS[3]
    A[4,5] = PS[4]
    A[4,6] = 1.0-PS[4]
    A[5,5] = 1.0
    A[6,6] = 1.0

    A = A[1:N+1,1:N+1]  # get zero offset index

    i = 25
    nsym  = 250
    Ratio = RatioList[0]
    di = Ratio*sig
    outputs = np.empty(A.shape[0])
    for n in range(outputs.shape[0]):
        outputs[n] = i    # outputs[] = mean output for each state
        i += di
    B = np.zeros((A.shape[0], nsym))
    for i in range(A.shape[0]):
        B[i,:] = set_Obs_Density(outputs[i], sig, nsym)
    gen = data_gen(A,B,np.array([1,0,0,0,0,0]))
    obs_vidur, lena = gen.runout(10000,"vidur",True)
    model_1 = hmm(A.shape[0],B.shape[1])
    rand_A, rand_B = HMM_fully_random(A,B)
    print(rand_B.shape)
    model_1.custom(np.array([[1,0,0,0,0,0]]).T,rand_A,rand_B)
    # exit()
    # for i in range(1):
    #     model_1.fit(np.array(obs_vidur), np.array(lena))
    # print(model_1._transmat)

    ######## NTLk
    obs_nltk = gen.runout(10000,'NLTK',True)
    model_2 = HMM(rand_A,rand_B,np.array([1,0,0,0,0,0]),"NLTK")
    trainer = nltk.tag.hmm.HiddenMarkovModelTrainer()
    # print(obs_nltk)
    trainer.train_unsupervised(unlabeled_sequences=obs_nltk , model = model_2 , max_iterations = 5)

    ############# BLAKE ###################
    # obs_blake, l = gen.runout(1000, 'blake', True)
    # # print(len(obs_blake),len(l))
    # model_3 = HMM(rand_A, rand_B,np.array([1,0,0,0,0,0]),"blake")
    # # print(rand_B.shape)
    # # exit()
    # for i in range(4):
    #     model_3.fitMultiple(obs_blake,l)
    # print(model_3.transmat_)
