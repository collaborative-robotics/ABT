#!/usr/bin/python
# 
#     test decoder error measures
#
# 
import os
import sys

#import random as random
import math as m
import numpy as np


import unittest
import mock

import tests.common as tc

import abt_constants
from abtclass import *
import hmm_bt as hbt   # this test did it right(!)

# b3 class modified by BH, local version in current dir
import b3 as b3          # behavior trees

import random


class Test_DecodeEval(unittest.TestCase):


    def test_DE01(self):

        assertct = 0
        
        #Build a model
        tmod = model(5) # with 5 states

        tmod.names = ['a','b','c','d','e']
        tmod.statenos = {'a':1, 'b': 2, 'c':3, 'd':4,  'e':5}


        ##  Generate some state seqs with and without errors
        #
        #
        random.seed(430298219)  # we want same seqs every time so we can assert for right answers                        
        Lmax = 10
        Nseqs = 10
        lengths = []
        ls3 = []
        seqs1 = []
        seqs2 = []
        seqs3 = []

        for i in range(Nseqs):   # 10 test sequences
            #minimum of 5 in sequence
            
            l1 =  Lmax/2 + int(random.random()*(Lmax/2) + 0.5)
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
        s2 = np.array(seqs2).reshape((sum(lengths)))  # needs to be numpy matrix of 1D
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
        tc.assert_feq(avgd, 0.099, fs, test_eps)
        assertct += 1
        tc.assert_feq(maxd,0.600,fs,test_eps)
        assertct += 1
        assert count  == 6, fs
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



        

if __name__ == '__main__':
    unittest.main()

