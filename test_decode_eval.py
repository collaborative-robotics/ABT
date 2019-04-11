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

assertct = 0
 
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
ls3 = []
seqs1 = []
seqs2 = []
seqs3 = []

for i in range(10):   # 10 test sequences
    #minimum of 5 in sequence
    l1 = 5 + int(random.random()*(Lmax-5) + 0.5)
    lengths.append(l1)
    ls3.append(l1)
    #print 'length: ', l1, '|', 
    for i in range(l1):   # generate a random sequence of l1 names
        s = tmod.statenos[random.choice(tmod.names)]
        seqs1.append(s)
        seqs2.append(s)
        seqs3.append(s)
assert len(seqs1) == sum(lengths), 'Somethings wrong with sequence setup'
assertct += 1

####################################################################################
#  First no deletions or insertions!!!! just changes
# Add some errors  to FIRST THREE Seqs
# seqsx[0] has 1 error
seqs2[0] = 1
# seqsx[1] has 2 errors
seqs2[7] = 2
seqs2[8] = 3
# seqsx[2] has 3 errors
seqs2[16] = 1
seqs2[17] = 2
seqs2[18] = 3

#s1 = np.matrix(seqs1)   # needs to be list
s2 = np.array(seqs2).reshape((sum(lengths)))  # needs to by numpy matrix of 1D
#print 'Setup: ',s2.shape

[avgd, maxd, count] = hbt.Veterbi_Eval(s2, seqs1, tmod.names, lengths, tmod.statenos)

# avgd:  average sed per symbol
# maxd:  max sed for any seq
# count:  total sed for all seqs
if(False):
    print 'avgd:   ', '{:6.3f}'.format(avgd)
    print 'maxd:   ', '{:6.3f}'.format(maxd)
    print 'count   ', '{:6d}'.format(count)

test_eps = 0.001
fs = 'test_decode_eval: string change test: assertion failure'
assert abs(avgd - 0.099) < test_eps, fs
assertct += 1
assert abs(maxd - 0.600) < test_eps, fs
assertct += 1
assert abs(count - 6) == 0, fs
assertct += 1

print '\n' 
print '   test_decode_eval.py '
print '\n  Passed all',assertct,' assertions '

#i = 0
#for l in ls3:
    #for j in range(l):
        #print '[',str(i)+','+str(j)+']'+str(seqs1[i+j])+'/'+str(seqs3[i+j]) ,
    #print ''
    #i += j+1


