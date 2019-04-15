#!/usr/bin/env python
import numpy as np       # operations on numerical arrays
import csv               # file I/O
import math as m
import sys               # for command line args
import operator          # for sorting list of class instances
import numpy as np
from scipy import stats
import datetime as dt
from   dateutil import parser

import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator

from abt_constants import *


def figure_output(plt, task, modelstring, ratiostring='all'):
    print 'Enter a filename for this plot: (.png will be added)'
    rs = ratiostring.replace(' ','')
    rs = rs.replace('=','-')
    rs = rs.replace('.','p')
    ms = modelstring.replace(' ','')
    ms = ms.replace('Ratio','R_')
    ms = ms.replace('-stateModel','')
    fname = 'res_'+task+'_'+ ms +'_'+rs+'.png'
    #fname.replace(' ','')
    print 'proposed file name: (CR to accept)', fname
    pfname = raw_input('new name:')
    if(pfname == ''):
        pfname = fname
    plt.savefig(pfname)
    return


#################################################
#
#   Basic graph params
plotH = 800
plotV = 900

fname = 'bw_converg_16-state.txt'
#fname = 'bw_converg_6-state.txt'

Task = []
RatioL = []
pert  = []
Eavg  = []
Emax  = []
IterCount = []


date = []
c_hash = []
pert = []
ModTyp = []
e2init = []
e2fin  = []
eminit = []
emfin  = []
c_iter = []
comment = []

nrow = 0
allrows = []

with open(fname,'r') as f:
        d1 = csv.reader(f,delimiter='|',quotechar='"')
        for row in d1:
            allrows.append(row)
            #print row
            nrow += 1
            stdate  = row[0]
            sthash  = row[1]
            stpert  = row[2]
            stModTyp   = row[3]    # same as HMM_delta
            ste2init   = row[4]
            ste2fin    = row[5]
            steminit   = row[6]    #  these may depend on task
            stemfin    = row[7]    #  make sure two entries every task
            stiter     = row[8]
            #comment    = row[9]
            
            date.append(stdate)
            c_hash.append(sthash)
            pert.append(float(stpert))
            ModTyp.append(float(stModTyp))
            e2init.append(float(ste2init))
            e2fin.append(float(ste2fin))
            eminit.append(float(steminit))
            emfin.append(float(stemfin))
            c_iter.append(int(stiter))
            comment.append(row[9])
            
#########################################################
#
#  Basic before-after boxplot
#
#figno = 1
#modelstring = comment[0]
#box_data = [e2init, e2fin]
#ymax = 0.3


#########################################################
#
#    Improvement vs perturbation
#

figno = 1
modelstring = '16-state ABT-like model'
d = [] # delta
d1 = []
d2 = []
d3 = []
for i in range(len(e2init)):
    d.append(e2fin[i]-e2init[i])
for i in range(len(d)):
    if pert[i] == 0.1:
        d1.append(d[i])
    if pert[i] == 0.3:
        d2.append(d[i])
    if pert[i] == 0.5:
        d3.append(d[i])
box_data = [d1,d2,d3]
ymax = 0.3

##########
#
#  Plot 1: Error vs. Ratio
fig1 = plt.figure(figno)
#figno += 1


#bp = plt.boxplot(data, notch=True,vert=True ,patch_artist=True)
bp = plt.boxplot(box_data, notch=True,vert=True ,patch_artist=True)

#standardize graph size
#figptr = plt.gcf()
figptr = fig1
DPI = figptr.get_dpi()
figptr.set_size_inches(plotH/float(DPI),plotV/float(DPI))

#for b in bp['boxes']:
    #b.set_facecolor('lightblue')


#plt.xlabel('Initial and Final RMS A-matrix Error')
#plt.ylabel('RMS Error')
#plt.ylim(0.0, ymax)
#plt.title('BW Parameter Estimation: A-matrix Improvement, '+modelstring)

plt.xlabel('Perturbation in RMS A-matrix')
plt.ylabel('Delta RMS Error')
plt.ylim(-ymax, ymax)
plt.title('BW Parameter Estimation: A-matrix Improvement, '+modelstring)
locs, labels = plt.xticks()
plt.xticks(locs, ['0.1','0.3','0.5'])

plt.show(block=False)
figure_output(plt, 'BW_A-Mat-Improvement', modelstring, 'all-perts')

            
