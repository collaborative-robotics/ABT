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


if len(sys.argv) < 2:
    print ' usage:   fwd_alg_graph.py   FILENAME'
    quit()
else:
    inputfilename = str(sys.argv[1])
    print 'Input file: ', inputfilename

if '16' in inputfilename:
    NST = 16
else:
    NST = 6
    
#################################################
#
#   Basic graph params
plotH = 800
plotV = 900

 

Xticklabs = []
RatioL = []
pert0 = []
pert1 = []
pert25 = []
pert50 = []
 
nrow = 0
allrows = []

perts = [0, 0.1, 0.25, 0.50]

headrow = False
with open(inputfilename,'r') as f:
        d1 = csv.reader(f,delimiter=',',quotechar='"')
        for row in d1:
            print '---------------------------------'
            print row
            if not headrow:
                print row
                allrows.append(row)
                #print row
                nrow += 1
                             
                Xticklabs.append(row[0])
                RatioL.append(float(row[0]))
                pert0.append(float(row[1]))
                pert1.append(float(row[2]))
                pert25.append(float(row[3]))
                pert50.append(float(row[4]))
            headrow = False
N = len(pert0)

p0 = np.array(pert0)
p1 = np.array(pert1)
p25 = np.array(pert25)
p50 = np.array(pert50)

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
stTitle  = 'Forward LogP vs. Output Ratio ('+str(NST)+'-state model)'
listXticks = Xticklabs
ymax = 0
ymin = -40


#########################################################
#
#  LogP Final vs Output Ratio 0.1 2.5
#

#figno = 1
#modelstring = comment[0]
#d1 = []
#d2 = []

#print 'going through ', len(Ratios), 'data'
#for i in range(len(Ratios)):
    #d = logPs[i]
    #if approx(pert[i],0.2):
        #d1.append(d)
    #elif approx(pert[i],0.5):
        #d2.append(d)
#box_data = [d1, d2]
#ymax = 0
#ymin = -2000

#stXlabel = 'Model Perturbation'
#stYlabel = 'Final LogP'
#stTitle  = 'BW Final LogP vs. Model Perturbation (all ratios)' 
#listXticks = ['0.2','0.5']


#########################################################
#
#    Improvement vs perturbation
#
 
#
#  Plot 1
fig1 = plt.figure(figno)
#figno += 1


#bp = plt.boxplot(data, notch=True,vert=True ,patch_artist=True)
#bp = plt.boxplot(box_data, notch=True,vert=True ,patch_artist=True)

bp = plt.plot(RatioL, pert0, RatioL, pert1, RatioL, pert25, RatioL, pert50, marker='s')

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

if NST == 6:
    plt.annotate('pert = 0.0', (3.2, -6.6))
    plt.annotate('pert = 0.1', (3.2, -7.1))
    plt.annotate('pert = 0.25', (3.2, -7.5))
    plt.annotate('pert = 0.50', (3.2, -9))
else:
    plt.annotate('pert = 0.0', (3.2, -28))
    plt.annotate('pert = 0.1', (3.2, -34))
    plt.annotate('pert = 0.25', (3.2, -36))
    plt.annotate('pert = 0.50', (3.2, -38.5))

plt.grid(color='lightgray', which='both')

plt.show(block=False)
figure_output(plt, 'Forward_Alg_LogP_vs_output_ratio', '', str(NST))

            
