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
from abt_constants import *
from abt_class import *


NEpochs = 10000000
Nbins = 20

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
print '% variation: ', 100.0 * (maxd-mind)/(NEpochs/Nbins), '%'


print '\n\n\n'
print 'Testing gaussian function: '
