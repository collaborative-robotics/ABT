#!/usr/bin/python
#

#  Test for HMM setup and perturbs


import numpy as np
import matplotlib.pyplot as plt

#sudo pip install scikit-learn  # dep for hmmlearn
#pip install -U --user hmmlearn
from hmmlearn import hmm

from hmm_bt import *


from model00 import *

of = open('HMM_test_rep.txt', 'w')

M = HMM_setup(Pi, A, sig, names)

outputAmat(A,"Initial A Matrix",names,of)
HMM_perturb(M, 0.01)
outputAmat(M.transmat_, "Perturbed A Matrix", names, of)





of.close()
