#!/usr/bin/python

#
#    "global" constants needed by all
#

# Task01    SMALL   BaumWelch
# Task02    SMALL   Viterbi
# Task03    BIG     BaumWelch
# Task04    BIG     Viterbi


NSYMBOLS = 250
FIRSTSYMBOL = 25

SMALL = 1   # flags to switch models 
BIG   = 2
LARGE = BIG


MODEL = BIG   # may need to clear this for test_xxx.py

random_flag = 0.500  # if a 'perturbation' is  > this, it means totally random
                     #  state transition matrix with no zero elements

RatioList = [5.0, 0.0, 0.25, 1.0, 2.5]  # output spacing ratios (di/sigma)
 
T = True
F = False

Forward   = 0
Viterbi   = 1
BaumWelch = 2
BWTest    = 3

######################
sig = 2.0

K = 1000
M = 1000*1000

NEpochs = 20*K

####  How many analysis runs to do
Nruns = 15

task = BaumWelch 

