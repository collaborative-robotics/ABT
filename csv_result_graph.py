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
print Ratio
print ''
fig, ax1 = plt.subplots(figsize=(14,6))
#plt.subplots_adjust(left=.25)
rect = fig.patch
rect.set_facecolor('white')
ax1.xaxis.grid(True,linestyle='-', which='major', color='lightgrey',alpha=0.5)

data = []
rs = set(Ratio)
epsilon = 0.0001
for r in rs:
    l = []
    for [j, v] in enumerate(Eavg):
        if abs(r-Ratio[j])<epsilon:
            l.append(v) 
    data.append(l)
 
#print data
 
# make boxplots for Eavg
bp = plt.boxplot(data, notch=True,vert=True ,patch_artist=True)
for b in bp['boxes']:
    b.set_facecolor('lightblue')


plt.xlabel('Ratio (di/sig)')
plt.ylabel('Error')
plt.title('Avg Error vs. Ratio')

tstrs = []
for r in rs:
    tstrs.append(str(r))
plt.xticks([1, 2], tstrs)

plt.show()

#plt.ylabel('Route')
#plt.xlabel('sec/km')