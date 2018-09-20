#!/usr/bin/python
# 
#     test decoder error measures
#
#

import os as os

# b3 class modified by BH, local version in current dir
import b3 as b3          # behavior trees
#import random as random
import math as m
import numpy as np
import random as random
from abt_constants import *
#from abt_class import *
import abtclass as abt
import hmm_bt as hbt

 
 
#Build a model
tmod = abt.model(5) # with 5 states

tmod.names = ['a','b','c','d','e']
tmod.statenos = {'a':1, 'b': 2, 'c':3, 'd':4,  'e':5}


##  Generate some state seqs with and without errors
#
#
random.seed(430298219)  # we want same seqs every time so we can assert for right answers                        
Lmax = 10
lengths = []
seqs1 = []
seqs2 = []
for i in range(10):   # 10 test sequences
    l1 = 5 + int(random.random()*(Lmax-5) + 0.5)
    lengths.append(l1)
    for i in range(l1):   # generate a random sequence of l1 names
        s = random.choice(tmod.names)
        seqs1.append(s)
        seqs2.append(s)

assert len(seqs1) == sum(lengths), 'Somethings wrong with sequence setup'

print 'Generated Sequences: '
print 'Lengths: ', lengths
print 'Seq1:    ', seqs1

# Add some errors  to FIRST THREE Seqs
# seqsx[0] has 1 error
seqs2[0] = 'a'
# seqsx[1] has 2 errors
seqs2[7] = 'b'
seqs2[8] = 'c'
# seqsx[2] has 3 errors
seqs2[16] = 'a'
seqs2[17] = 'b'
seqs2[18] = 'c'

print 'Seq2:    ', seqs2

#s1 = np.matrix(seqs1)   # needs to be list
s2 = np.matrix(seqs2)  # needs to by numpy matrix
[totald, cost, count] = hbt.Veterbi_Eval(s2, seqs1, tmod.names, lengths, tmod.statenos)


print 'totald: ', totald
print 'cost:   ', cost
print 'count   ', count

################################################################
## Evaluation of Veterbi
#def Veterbi_Eval(p,x,names,l,statenos):
    #'''
    #p = state sequence estimates (concatenated state seqs)
    #x = true state sequences
    #names = list of state names (Nx1)
    #l = lengths of each state sequence
    #statenos = 
    #'''



