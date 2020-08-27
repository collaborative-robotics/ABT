#!/usr/bin/python
# 
#      Template for testing ABT functionality
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
 


class Test_hmm_bt_unit(unittest.TestCase):


    def test_A_row_check(self):
        # build a test matrix
        Atest = np.zeros([10,10])
        for i in range(10):
            Atest[i,i] = 1.0  # initial non zero
        for i in range(10):
            Atest[0,i] = 0.100
        Btest = Atest.copy()
        Btest[0,5] = 0.095    # row does not sum to 1
        outfile = mock.Mock()

        # start testing row_check
        
        assert A_row_check(Atest,outfile), 'Detecting error in valid A matrix'
        assert not A_row_check(Btest,outfile), 'Fail to detect invalid rowsum (<1)' 
        Btest[0,5] = 0.105
        assert not A_row_check(Btest,outfile), 'Fail to detect invalid rowsum (>1)' 

    def test_A_row_test(self):
        # build a test matrix
        Atest = np.zeros([10,10])
        for i in range(10):
            Atest[i,i] = 1.0  # initial non zero
        for i in range(10):
            Atest[0,i] = 0.100
        
        outfile = mock.Mock()
        assert A_row_check(Atest,outfile), 'testing data error: invalid A matrix'
        A_row_test(Atest, outfile)   # should pass
        
    #def test_XXNAME_2(self):

         
        
    #def test_XXNAME_2(self):

         
        
    #def test_XXNAME_2(self):

         
        

if __name__ == '__main__':
    unittest.main()

