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

# first open up the metadata.


metadata_name = 'hmm_bw_metadata.txt'
# Metadata file format:  each line: (comma sep)
#
# 1) date and time stamp
# 2) name of data file
# 3) ownname  (name of the top level file)
# 4) git hash (1st 10 chars of current git hash)
# 5) number of HMM / BT states
# 6) text field (comment)


fmeta = open(metadata_name, 'r')
runs = []
for line in fmeta:
    runfacts = line.split('|')
    runs.append(runfacts)

MenuSize = 30
print 'Select one or more files to plot:'
menu = runs[-MenuSize:]
for [i,r] in enumerate(menu):  # last 10 runs for ref 
    date = r[0]
    nstates = r[4]
    comment = r[5]
    print '{:d}  {:15s} {:s}'.format(i,date,nstates,comment)


st = raw_input('Select start: ')
en = raw_input('Select   end: ')

sti = int(st)
eni = int(en)

files = []
for i in range(sti,eni+1):
    print 'I found ', menu[i][0] # date
    files.append(menu[i][1].strip())   #filename
     
#

Ratio = []
pert  = []
Eavg  = []
Emax  = []

nrow = 0


for file in files:
    with open(file,'rb') as f:
        d1 = csv.reader(f,delimiter=',',quotechar='"')
        for row in d1:
            print row
            nrow += 1
            sttask  = row[0]
            stRatio = row[1]
            stdi    = row[2]   
            stpert  = row[3]    # same as HMM_delta
            stsig   = row[4]
            strn    = row[5]
            stEavg  = row[6]
            stEmax  = row[7]

            Ratio.append(float(stRatio))
            pert.append(float(stpert))
            Eavg.append(float(stEavg))
            Emax.append(float(stEmax))


print 'Read in ', nrow,' rows' 
print ''
fig, ax1 = plt.subplots(figsize=(14,6))
#plt.subplots_adjust(left=.25)
rect = fig.patch
rect.set_facecolor('white')
ax1.xaxis.grid(True,linestyle='-', which='major', color='lightgrey',alpha=0.5)


ymax = 1.0  #error plotting range 0.0--ymax

#####################################################
#
##   Collect error values for each "X" value
#
data = []
rs = set(Ratio)
print 'Ratios: ', sorted(rs)
epsilon = 0.0001
for r in sorted(rs):
    l = []
    for [j, v] in enumerate(Eavg):
        if abs(r-Ratio[j])<epsilon: # cheezy grep
            l.append(v)
    data.append(l)   # get a list of lists: [ ... [Eavg samples for given ratio ] ....]

dperts= []
perts = set(pert)
print 'Perturbations (HMM_deltas):', sorted(perts)
for p in sorted(perts):
    l = []
    for [j,v] in enumerate(Eavg):
        if abs(p-pert[j])<epsilon:   # cheezy grep
            l.append(v)
    dperts.append(l)  # get a list of lists: [ ... [Eavg samples for given perturbation ] ....]


# make boxplots for Eavg



##########
#
#  Plot 1: Error vs. Ratio
bp = plt.boxplot(data, notch=True,vert=True ,patch_artist=True)
for b in bp['boxes']:
    b.set_facecolor('lightblue')


plt.xlabel('Ratio (di/sig)')
plt.ylabel('RMS Error')
plt.ylim(0.0, ymax)
plt.title('Avg Error vs. Ratio')

tstrs = [0.00]
for r in sorted(rs):
    tstrs.append(str(r))
plt.xticks(range(len(rs)+1), tstrs)

plt.show()

##########
#
#  Plot 2: Error vs. Perturbation
#

bp2 = plt.boxplot(dperts, notch=True,vert=True ,patch_artist=True)
for b in bp['boxes']:
    b.set_facecolor('lightblue')

plt.xlabel('HMM A-matrix Perturbation')
plt.ylabel('RMS Error')
plt.ylim(0.0, ymax)
plt.title('Avg Error vs. Perturbation')

tstrs = ['0.0']
for p in sorted(perts):
    tstrs.append(str(p))
plt.xticks(range(len(perts)+1), tstrs)

plt.show()
