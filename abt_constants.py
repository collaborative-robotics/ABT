#!/usr/bin/python

#
#    "global" constants needed by all
#

NSYMBOLS = 150

T = True
F = False

Forward   = 1
Viterbi   = 2
BaumWelch = 3

######################
sig = 2.0
Ratio = 1.0     # spread of symbols relative to obs SD

K = 1000
M = 1000*1000

NEpochs = 200

####  How many analysis runs to do
Nruns = 10
