from Log_class import *
import numpy as np

class hmm():

    def __init__(self,states, nsymbols):
    # assert A.shape[0] == A.shape[1] && A.ndim == 2
    # assert b.shape[0] == A,shape[0]
    # self.A = np.log()
    # self.b =
        self.Nstate = states
        self.nsymbols = nsymbols
        self.Pi = np.broadcast_to(np.array(hf(np.inf)),states)
        self.Pi.setflags(write = 1)
        self.Pi[0] = hf(1)
        self._transmat = np.broadcast_to(np.concatenate((np.array(hf(1)).reshape(1),np.repeat(np.array(hf(np.inf)),states - 1))),(self.Nstate,self.Nstate))
        # np.concatenate(np.array(hf(1)),np.repeat(np.array(hf(0)),states - 1),axis = 0)
        # np.array(hf(1)),np.repeat(np.array(hf(0)),states - 1)
        self._emission = np.broadcast_to(np.array(hf(3)),(self.Nstate,self.nsymbols))
        print(self._transmat.shape)

# hmm(10,10)
    def Forawrd(self, observation, length):
        log_prob = np.empty(lengths.shape[0])
        for i in range(obsevation.shape[0]):
            print(length[i])
            foward_lattice = np.empty((self.Nstate,length[i]))
            foward_lattice[:,0] = self.Pi * self._emission[:,observation[i][0]]
            for j in range(1,length[i]-2):
                foward_lattice[:,j] = np.sum(foward_lattice[:,j-1].reshape(1,self.Nstate) * self._transmat, axis = 0) * self._emission[:,observation[i][j]]

            log_prob[i] = np.sum(foward_lattice[:,length(i)])

    def Backward(self, observation, length) :
        backward_lattice = np.empty((self.Nstate,length))
        backward_lattice[:,length-1] = 1
        for i in range(length-2,-1):
            backwar_lattice[:,i] = np.sum(np.dot(self._transmat,self._emission[:,observation[i]]), axis = 1) * backwar_lattice[:.i+1]
        return backward_lattice

    def Veterbi(self, observation, length):
        state_sequence = np.empty((observation.shape[0],np.max(length)))
        for i in range(observation.shape[0]):
            prob_sequence = np.empty((self.Nstate,np.max(length)))
            veter_lattice = np.empty((self.Nstate,length[i]))
            veter_lattice[:,0] = self.Pi*self._emission[:,observation[0]]
            prob_sequence[;,0] = 0
            for j in range(1,observation.shape[0]):
                veter_lattice[:,j] = np.amax(veter_lattice[:,j-1].reshape(1,self.Nstate) * self._transmat,axis = 0) * self._emission[:,observation[j]]
                prob_sequence[:,j] = np.argmax(veter_lattice[:,j-1].reshape(1,self.Nstate) * self._emission)
            endprob  = np.max(veter_lattice[:,obsevation.shape[0]])
            endarg = np.argmax(veter_lattice[:,obsevation.shape[0]])
            state_sequence[i][length[i]-1] = endarg
            for k in range(length[i]-2,0):
                state_sequence[i][k] = prob_sequence[k+1][state_sequence[i][k+1]]
        return sequence

    def Forward_one(self,observation,length):
        print(length[i])
        foward_lattice = np.empty((self.Nstate,length[i]))
        foward_lattice[:,0] = self.Pi * self._emission[:,observation[0]]
        for j in range(1,length[i]-2):
            foward_lattice[:,j] = np.sum(foward_lattice[:,j-1].reshape(1,self.Nstate) * self._transmat, axis = 0) * self._emission[:,observation[j]]

        # log_prob[i] = np.sum(foward_lattice[:,length(i)])
        return foward_lattice

    def BaumWelch(self,observation,length):
        for i in range(observation.shape[0]):
            foward_lattice = self.Forward_one(observation[i],length[i])
            backward_lattice = self.Backward(observation[i],length[i])
            # Numerator
            xi = np.empty((length[i],self.Nstate,self.Nstate)) #TODO: Correction
            for j in range(0,length[i]-1):
                xi[j] = foward_lattice[:,j].reshape(self.Nstate,1) * self._transmat * self._emission[:,observation[i][j+1]].reshape(1,self.Nstate) *   backward_lattice[:,j+1].reshape(1,self.Nstate)
            xi /= np.sum(eta)
            xi[length[i]-1] = 0
            denom = np.sum(np.sum(xi,axis = 2),axis = 0)
            #Update
            self._transmat = np.sum(xi,axis = 0) / denom.reshape(self.Nstate,1)
            #_emission update
            gammma2 = np.sum(xi,axis = 1)
            denom2 = np.sum(np.sum(xi,axis = 1),axis = 0)
            b = np.tile(np.array(hf(0)),(nstate,nsymbols))
            for j in range(length[i]):
                b[:,observation[j]] += gamma2[j]
            b /= denom2.reshape(1,self.Nstate)

            
