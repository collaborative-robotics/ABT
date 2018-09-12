#!/usr/bin/python

#
#    "global" constants needed by all
#

NSYMBOLS = 150
FIRSTSYMBOL = 20

SMALL = 1   # flags to switch models 
BIG   = 2

RatioList = [0.25, 1.0, 2.5, 5.0]  # output spacing ratios (di/sigma)

MODEL = SMALL  # can override

T = True
F = False

Forward   = 0
Viterbi   = 1
BaumWelch = 2

######################
sig = 2.0

K = 1000
M = 1000*1000

NEpochs = 20*K

####  How many analysis runs to do
Nruns = 10
