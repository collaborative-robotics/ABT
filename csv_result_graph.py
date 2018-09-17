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

cmd_line_Ratio = -1     # flag value
if len(sys.argv) == 2:  # we have an arg
    cmd_line_Ratio = float(sys.argv[1])

# first open up the metadata.

metadata_name = 'hmm_bw_metadata.txt'
metadata_name = 'metadata.txt'
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
print '-------------------------------------------------'
print 'Select one or more files to plot:'
menu = runs[-MenuSize:]
for [i,r] in enumerate(menu):  # last 10 runs for ref 
    date = r[0]
    nstates = r[4]
    comment = r[5]
    print '{:3d} | {:15s} |{:3d}| {:s}'.format(i,date,int(nstates), comment.strip())
print '-------------------------------------------------'


st = raw_input('Select start: ')
en = raw_input('Select   end: ')

sti = int(st)
eni = int(en)

files = []
modelsize = menu[sti][4]  # user must stay with same model size
print 'Setting prev mod size:', modelsize
for i in range(sti,eni+1):
    files.append(menu[i][1].strip())   #filename
    if menu[i][4] != modelsize:
        print 'you have selected multiple model sizes - not a fair comparison'
        quit()
        
     
#

RatioL = []
pert  = []
Eavg  = []
Emax  = []

nrow = 0
allrows = []

# Read in data from all the files
for file in files:
    with open(file,'rb') as f:
        d1 = csv.reader(f,delimiter=',',quotechar='"')
        for row in d1:
            allrows.append(row)
            #print row
            nrow += 1
            sttask  = row[0]
            stRatioL = row[1]
            stdi    = row[2]   
            stpert  = row[3]    # same as HMM_delta
            stsig   = row[4]
            strn    = row[5]
            stEavg  = row[6]
            stEmax  = row[7]

            RatioL.append(float(stRatioL))
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
nprows = 0
data = []
rs = set(RatioL)
print 'Ratios: ', sorted(rs)
ratiostring = 'all ratios'
if cmd_line_Ratio >= 0.0:   # this means we are going to select
    rs = set([cmd_line_Ratio])
    print 'Selecting Ratios: ', sorted(rs)  # might be multiple rs later
    ratiostring = 'Ratio = {:5.2f}'.format(cmd_line_Ratio)
    
usedrows = []
epsilon = 0.0001
for r in sorted(rs):
    l = []
    for [j, v] in enumerate(Eavg):
        if abs(r-RatioL[j])<epsilon: # cheezy grep
            usedrows.append(allrows[j])
            l.append(v)
            nprows += 1
    data.append(l)   # get a list of lists: [ ... [Eavg samples for given ratio ] ....]

dperts= []
perts = set(pert)
print 'Perturbations (HMM_deltas):', sorted(perts)
for p in sorted(perts):
    l = []
    for [j,v] in enumerate(Eavg):
        if abs(p-pert[j])<epsilon:   # cheezy grep
            if RatioL[j] in rs:      # selected ratio(s)
                l.append(v)
    dperts.append(l)  # get a list of lists: [ ... [Eavg samples for given perturbation ] ....]


print 'plotting ', nprows,' rows ' , len(usedrows)
print ''

for r in usedrows:
    print r


# make boxplots for Eavg

plotH = 800
plotV = 900

modelstring = str(modelsize) + '-state Model'

if(cmd_line_Ratio < 0.0):  # only plot this if no Command line param (Ratio)
    ##########
    #
    #  Plot 1: Error vs. Ratio
    fig1 = plt.figure(1)
    bp = plt.boxplot(data, notch=True,vert=True ,patch_artist=True)
    
    #standardize graph size
    #figptr = plt.gcf()
    figptr = fig1
    DPI = figptr.get_dpi()    
    figptr.set_size_inches(plotH/float(DPI),plotV/float(DPI))
    
    for b in bp['boxes']:
        b.set_facecolor('lightblue')


    plt.xlabel('Ratio (di/sig)')
    plt.ylabel('RMS Error')
    plt.ylim(0.0, ymax)
    plt.title('Avg Error vs. Ratio, '+modelstring)

    tstrs = [0.00]
    for r in sorted(rs):
        tstrs.append(str(r))
    plt.xticks(range(len(rs)+1), tstrs)

    plt.show(block=False)
        
    print 'Enter a filename for this plot: (.png will be added)'
    pfname = raw_input('string:')    
    plt.savefig(pfname)

##########
#
#  Plot 2: Error vs. Perturbation
#

fig2 = plt.figure(2)
bp2 = plt.boxplot(dperts, notch=True,vert=True ,patch_artist=True)

#standardize graph size
figptr = fig2
DPI = figptr.get_dpi()    
figptr.set_size_inches(plotH/float(DPI),plotV/float(DPI))

for b in bp2['boxes']:
    b.set_facecolor('lightblue')

plt.xlabel('HMM A-matrix Perturbation')
plt.ylabel('RMS Error')
plt.ylim(0.0, ymax)
plt.title('Avg Error vs. Perturbation, '+modelstring+', '+ratiostring)

tstrs = ['0.0']
for p in sorted(perts):
    tstrs.append(str(p))
plt.xticks(range(len(perts)+1), tstrs)

plt.show(block=False)
        
print 'Enter a filename for this plot: (.png will be added)'
pfname = raw_input('string:')

plt.savefig(pfname+'.png')

#plt.show()
