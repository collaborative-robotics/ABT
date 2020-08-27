#!/usr/bin/python
# 
#      Random # tester
#
#

import os as os

# b3 class modified by BH, local version in current dir
import b3 as b3          # behavior trees
#import random as random
import math as m
import numpy as np


import unittest
import mock

from tests.common import *
#from common import *


import numpy as np
import abt_constants
from abtclass import *
from hmm_bt import *
 


class Test_random(unittest.TestCase):


    def test_random(self):

        rigoroustest = 10000000
        quicktest    = 50000
        
        NEpochs = quicktest
        
        Nbins = 20

        print 'Testing np.random.uniform with',NEpochs, ' trials ... '

        delta = 1.0 / float(Nbins)

        hist = np.zeros(Nbins)

        for i in range(NEpochs):
            x = np.random.uniform(0,1.0)
            n = int(Nbins*x )
            hist[n] += 1

        i = 0
        sum = 0
        mind = 9999999999
        maxd = -1

        for n in hist:
            print i, n
            sum += n
            if n > maxd:
                maxd = n
            if n < mind:
                mind = n
        print 'Sum: ', sum
        print 'Min: ', mind
        print 'Max: ', maxd
        var_pct = 100.0 * (maxd-mind)/(NEpochs/Nbins)
        print '% variation: ', var_pct, '%'
        
        if NEpochs == rigoroustest:
            assert (var_pct < 1.0), 'more than expected non-uniformity'
        else: 
            assert (var_pct < 10.0), 'more than expected non-uniformity'

            
        

if __name__ == '__main__':
    unittest.main()

