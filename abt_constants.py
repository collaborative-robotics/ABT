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
Ratio = 0.25    # spread of symbols relative to obs SD
di = int(Ratio*sig)   # change in output obs mean per state

K = 1000
M = 1000*1000

NEpochs = 20*K

####  How many analysis runs to do
Nruns = 10
