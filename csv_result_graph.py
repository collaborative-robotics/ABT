#!/usr/bin/env python
import numpy as np       # operations on numerical arrays
import csv               # file I/O
import math as m
import operator          # for sorting list of class instances
import numpy as np
from scipy import stats
import datetime as dt
from   dateutil import parser

import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator

#

Ratio = []
pert  = []
Eavg  = []
Emax  = []

nrow = 0

with open('tmp.csv','rb') as f:
    d1 = csv.reader(f,delimiter=',',quotechar='"')

    for row in d1:
        nrow += 1
        sttask  = row[0]
        stRatio = row[1]
        stpert  = row[2]
        stdi    = row[3]
        stsig   = row[4]
        strn    = row[5]
        stnr    = row[6]
        stEavg  = row[7]
        stEmax  = row[8]

        Ratio.append(float(stRatio))
        pert.append(float(stpert))
        Eavg.append(float(stEavg))
        Emax.append(float(stEmax))


print 'Read in ', nrow,' rows'
print 'len(Ratio): ', len(Ratio)
print ''
fig, ax1 = plt.subplots(figsize=(14,6))
#plt.subplots_adjust(left=.25)
rect = fig.patch
rect.set_facecolor('white')
ax1.xaxis.grid(True,linestyle='-', which='major', color='lightgrey',alpha=0.5)


ymax = 0.4   #error plotting range 0.0--ymax

data = []
rs = set(Ratio)
print 'Ratios: ', sorted(rs)
epsilon = 0.0001
for r in rs:
    l = []
    for [j, v] in enumerate(Eavg):
        if abs(r-Ratio[j])<epsilon:
            l.append(v)
    data.append(l)

dperts= []
perts = set(pert)
for p in perts:
    l = []
    for [j,v] in enumerate(Eavg):
        if abs(p-pert[j])<epsilon:
            l.append(v)
    dperts.append(l)

#print data

# make boxplots for Eavg

##########
#
#  Plot 1: Error vs. Ratio
bp = plt.boxplot(data, notch=True,vert=True ,patch_artist=True)
for b in bp['boxes']:
    b.set_facecolor('lightblue')


plt.xlabel('Ratio (di/sig)')
plt.ylabel('Error')
plt.ylim(0.0, ymax)
plt.title('Avg Error vs. Ratio')

tstrs = [0.00]
for r in sorted(rs):
    tstrs.append(str(r))
plt.xticks(range(len(rs)+1), tstrs)

plt.show()

##########
#
#  Plot 2: Error vs. Ratio
#

bp2 = plt.boxplot(dperts, notch=True,vert=True ,patch_artist=True)
for b in bp['boxes']:
    b.set_facecolor('lightblue')


plt.xlabel('HMM A-matrix Perturbation')
plt.ylabel('Error')
plt.ylim(0.0, ymax)
plt.title('Avg Error vs. Perturbation')

tstrs = [0.00]
for p in sorted(perts):
    tstrs.append(str(p))
plt.xticks(range(len(perts)+1), tstrs)

plt.show()
