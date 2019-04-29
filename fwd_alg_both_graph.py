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


def approx(a,b):
    if abs(a-b) < abs(0.00001*a):
        return True
    return False

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

names = ['fwd_res2_6state.csv', 'fwd_res2_16state.csv']
    
#################################################
#
#   Basic graph params
plotH = 800
plotV = 900

 

Xticklabs = []
RatioL = []
 
nrow = 0
allrows = []

perts = [0, 0.1, 0.25, 0.50]
loop = 0
headrow = False
for ifn in names:
    pert0 = []
    pert1 = []
    pert25 = []
    pert50 = []
    with open(ifn,'r') as f:
            d1 = csv.reader(f,delimiter=',',quotechar='"')
            for row in d1:
                print '---------------------------------'
                print row
                if not headrow:
                    allrows.append(row)
                    #print row
                    nrow += 1
                                
                    Xticklabs.append(row[0])
                    if loop ==0:
                        RatioL.append(float(row[0]))
                    pert0.append(float(row[1]))
                    pert1.append(float(row[2]))
                    pert25.append(float(row[3]))
                    pert50.append(float(row[4]))
                headrow = False
    N = len(pert0)

    if(loop == 0):
        p0 = np.array(pert0)
        p1 = np.array(pert1)
        p25 = np.array(pert25)
        p50 = np.array(pert50)
    if(loop == 1):
        p01 = np.array(pert0)
        p11 = np.array(pert1)
        p251 = np.array(pert25)
        p501 = np.array(pert50)
        
    loop += 1
print pert0
print p0


#########################################################
#
#  Basic lineplot
#
figno = 1
modelstring = 'ABT-like HMM'
                        

ymax = 0.3

stXlabel = 'Output Ratio'
stYlabel = 'Log Probability per sequence'
stTitle  = 'Forward LogP vs. Output Ratio, 6 & 16-state models'
listXticks = Xticklabs
ymax = 0
ymin = -40


#########################################################
#
#    LogP vs perturbation
#
 
#
#  Plot 1
fig1 = plt.figure(figno)
#figno += 1


#bp = plt.boxplot(data, notch=True,vert=True ,patch_artist=True)
#bp = plt.boxplot(box_data, notch=True,vert=True ,patch_artist=True)

bp = plt.plot(RatioL, p0, RatioL, p1, RatioL, p25, RatioL, p50, marker='s')
bp = plt.plot(RatioL, p01, RatioL, p11, RatioL, p251, RatioL, p501, marker='s')

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

#plt.xlabel('Perturbation in RMS A-matrix')
#plt.ylabel('Delta RMS Error')
#plt.ylim(-ymax, ymax)
#plt.title('BW Parameter Estimation: A-matrix Improvement, '+modelstring)
#locs, labels = plt.xticks()
#plt.xticks(locs, ['0.1','0.3','0.5'])


plt.xlabel(stXlabel)
plt.ylabel(stYlabel)
plt.ylim(ymin, ymax)
plt.title(stTitle)
#locs, labels = plt.xticks()
#plt.xticks(locs, listXticks)

plt.annotate('pert = 0.0, pert=0.1', (3.2, -6.6))
#plt.annotate('pert = 0.1', (3.2, -7.1))
plt.annotate('pert = 0.25', (3.2, -8))
plt.annotate('pert = 0.50', (3.2, -9))

plt.annotate('pert = 0.0', (3.2, -28))
plt.annotate('pert = 0.1', (3.2, -29.4))
plt.annotate('pert = 0.25', (3.2, -31.5))
plt.annotate('pert = 0.50', (3.2, -37))

plt.grid(color='lightgray', which='both')

plt.show(block=False)
figure_output(plt, 'Forward_Alg_LogP_vs_output_ratio_BOTHMODELS', '', '')

            
