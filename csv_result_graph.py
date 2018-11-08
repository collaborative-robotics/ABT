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

#Forward   = 0  # define task codes
#Viterbi   = 1
#BaumWelch = 2



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
 
 
 
def data_vis(data, Ratios):
    print 'Data to be plotted: '
    for i,v in enumerate(data):
        print Ratios[i], ' | ', v
        print ''
    print '\n\n'

cmd_line_Ratio = -1     # flag value
if len(sys.argv) == 2:  # we have an arg
    cmd_line_Ratio = float(sys.argv[1])

# first open up the metadata.

data_prefix = ''  # normally
#data_prefix = '/home/blake/Dropbox/UWEE/ABT/'   # testing

metadata_name = data_prefix+'metadata.txt'
#metadata_name = 'metadata.txt'
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
print 'Select one or more files to plot:         ('+metadata_name+')'
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

#print 'Menu:'
#print menu
#quit()
files = []
modelsize = menu[sti][4]  # user must stay with same model size
print 'Setting prev mod size:', modelsize
for i in range(sti,eni+1):
    files.append(data_prefix+menu[i][1].strip())   #filename
    if menu[i][4] != modelsize:
        print 'you have selected multiple model sizes - not a fair comparison'
        quit()
        
#

Task = []
RatioL = []
pert  = []
Eavg  = []
Emax  = []
IterCount = []
nrow = 0
allrows = []

# Read in data from all the files
firsttask = -999
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
            stEavg  = row[6]    #  these may depend on task
            stEmax  = row[7]    #  make sure two entries every task

            if firsttask < 0.0:
                firsttask = int(sttask)
            elif int(sttask) != firsttask:
                print 'You are mixing multiple tasks for plotting.'
                print '   reselect data rows with same task'
                quit()
            Task.append(int(sttask))
            RatioL.append(float(stRatioL))
            IterCount.append(int(stdi))
            pert.append(float(stpert))
            Eavg.append(float(stEavg))
            Emax.append(float(stEmax))

# New names for convergence tol and iteration count
ConvTol = RatioL

print 'read in', files
#print len(pert), ' perturbations'
#print pert 
#quit()

ymax = 1.0  #error plotting range 0.0--ymax

#####################################################
#
##   Collect data values for each "X" value
#
nprows = 0
taskID = 0
data = []
datamin = []   #min error for each set
dataminx = []   #min x val for each set


rs = set(RatioL)   # default is set of all ratios found
print 'Ratios: ', sorted(rs)
ratiostring = 'all ratios'
if cmd_line_Ratio >= 0.0:   # this means we are going to select a specific ratio
    rs = set([cmd_line_Ratio])
    print 'Selecting Ratios: ', sorted(rs)  # might be multiple rs later
    ratiostring = 'Ratio = {:5.2f}'.format(cmd_line_Ratio)
    
nan_count = 0
usedrows = []     # for debugging basically
epsilon = 0.0001


#
#   Note: when plotting BW convergence, "Ratio" field is really tolerance
ic_v_tol = []  #iteration counts for each run for each tolerance and selected Ratios

for r in sorted(rs): #iterate over the Ratios
    l = []
    ic = []
    emin = 99999999999999.0
    for [j, v] in enumerate(Eavg):
        if not np.isnan(v): 
            if abs(r-RatioL[j])<epsilon: # cheezy grep
                usedrows.append(allrows[j])
                l.append(v)
                if v < emin:
                    emin = v
                ic.append(IterCount[j])
                nprows += 1
        else:
            nan_count += 1
    # l is a list of all Eavg values for a each Ratio
    data.append(l)   # get a list of lists: [ ... [Eavg samples for given ratio ] ....]
    # plot min error instead!
    datamin.append(emin)   # only one point per "ratio"
    dataminx.append(r)
    ic_v_tol.append(ic)   # add data collected for this tolerance ("Ratio")

dperts= []
perts = set(pert)
print 'Perturbations (HMM_deltas):', sorted(perts)
for p in sorted(perts):
    l = []
    for [j,v] in enumerate(Eavg):   #Y axis values
        if not np.isnan(v): 
            if abs(p-pert[j])<epsilon:   # cheezy grep
                if RatioL[j] in rs:      # selected ratio(s)
                    l.append(v)
                    
    dperts.append(l)  # get a list of lists: [ ... [Eavg samples for given perturbation ] ....]
    
dct = 0
#for l in data:
    #dct += len(l)
    
#
# collect convergence iteration count for each test (if BW_testing)
#
    
print 'plotting ', nprows,' rows ' , len(usedrows)
print nan_count, ' NaN values for Eavg, out of ', dct
print ''

#for r in usedrows:
    #print r


# make boxplots for Eavg

plotH = 800
plotV = 900

modelstring = str(modelsize) + '-state Model'



#####################################################################################
#
#        Forward/backward Results plots
#
if(firsttask == Forward):
    print ' Forward data plots not yet implemented'
    quit()


#####################################################################################
#
#        Viterbi decoder Results plots
#
if(firsttask == Viterbi):
    ##########
    #
    
    #print 'Viterbi Plot: size of data: '
    #for i, line in enumerate(data):
        #print sorted(list(rs))[i], line

    if cmd_line_Ratio < 0.0:   # i.e. we want to study all ratios  
        #  Plot 1: Error vs. Ratio
        figno = 1
        fig1 = plt.figure(figno)
        figno += 1
        bp = plt.boxplot(data, notch=True,vert=True ,patch_artist=True)
        
        #standardize graph size
        #figptr = plt.gcf()
        figptr = fig1
        DPI = figptr.get_dpi()    
        figptr.set_size_inches(plotH/float(DPI),plotV/float(DPI))
        
        for b in bp['boxes']:
            b.set_facecolor('Moccasin')

        # set up some labels for the X-axis (Ratios)
        tstrs = [0.00]
        for r in sorted(rs):
            tstrs.append(str(r))
        plt.xticks(range(len(rs)+1), tstrs)

        plt.xlabel('Ratio (di/sig)')
        #plt.xlabel('HMM perturbation (dimensionless)')
        plt.ylabel('String Edit Distance per symbol')
        ymax  = 1.1  # every state wrong = 1.0
        plt.ylim(0.0, ymax)
        plt.title('Viterbi Tracking Error vs. Ratio, '+modelstring)

        
        plt.show(block=False)
        
        figure_output(plt, 'Vit_vs_R', modelstring, ratiostring)

        
   ##########
    #
    #  Plot 2: decoder SED vs. Perturbation
    #
    figno = 2
    fig2 = plt.figure(figno)
    bp2 = plt.boxplot(dperts, notch=True,vert=True ,patch_artist=True)

    #standardize graph size
    figptr = fig2
    DPI = figptr.get_dpi()    
    figptr.set_size_inches(plotH/float(DPI),plotV/float(DPI))

    for b in bp2['boxes']:
        b.set_facecolor('Moccasin')

    plt.xlabel('HMM Perturbation')
    plt.ylabel('String Edit Distance per symbol')
    ymax = 1.1
    plt.ylim(0.0, ymax)
    plt.title('Viterbi decoder Edit Distance vs Perturbation, '+modelstring+', '+ratiostring)

    tstrs = ['0.0']
    for p in sorted(perts):
        pstr = str(p)
        if p > random_flag:
            pstr = 'random' 
        tstrs.append(pstr)
    plt.xticks(range(len(perts)+1), tstrs)

    plt.show(block=False)
    figure_output(plt, 'Vit_vs_P', modelstring, ratiostring)


#####################################################################################
#
#        Baum Welch Model Identification Results plots
#
if(firsttask == BaumWelch):
    figno = 1  
    #data_vis(data,sorted(rs))
    #quit()
    if(cmd_line_Ratio < 0.0):  # only plot this if no Command line param (Ratio)
        ##########
        #
        #  Plot 1: Error vs. Ratio
        fig1 = plt.figure(figno)
        figno += 1
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
        plt.title('BW Parameter Estimation: Avg Error vs. Ratio, '+modelstring)

        tstrs = [0.00]
        for r in sorted(rs):
            tstrs.append(str(r))
        plt.xticks(range(len(rs)+1), tstrs)

        plt.show(block=False)
            
        figure_output(plt, 'BW_vs_R', modelstring, ratiostring)

    ##########
    #
    #  Plot 2: Error vs. Perturbation
    #

    fig2 = plt.figure(figno)
    bp2 = plt.boxplot(dperts, notch=True,vert=True ,patch_artist=True)

    #standardize graph size
    figptr = fig2
    DPI = figptr.get_dpi()    
    figptr.set_size_inches(plotH/float(DPI),plotV/float(DPI))

    for b in bp2['boxes']:
        b.set_facecolor('lightblue')

    plt.xlabel('HMM Perturbation')
    plt.ylabel('RMS Error')
    plt.ylim(0.0, ymax)
    plt.title('Avg BW Error vs. Perturbation, '+modelstring+', '+ratiostring)

 
    tstrs = ['0.0']
    for p in sorted(perts):
        pstr = str(p)
        if p > random_flag:
            pstr = 'random' 
        tstrs.append(pstr)
    plt.xticks(range(len(perts)+1), tstrs)
    
    plt.show(block=False)
        
    figure_output(plt, 'BW_vs_P', modelstring, ratiostring)
    
#####################################################################################
#
#        Baum Welch ModelConvergence testing plots
#
if(firsttask == BWTest):
    figno = 1  
    #data_vis(data,sorted(rs))
    #quit()
    ##########
    #
    #  Plot 1: Error vs. Ratio
    fig1 = plt.figure(figno)
    #figno += 1
    
    
    #bp = plt.boxplot(data, notch=True,vert=True ,patch_artist=True)
    bp = plt.scatter(dataminx, datamin)
    
    #standardize graph size
    #figptr = plt.gcf()
    figptr = fig1
    DPI = figptr.get_dpi()    
    figptr.set_size_inches(plotH/float(DPI),plotV/float(DPI))
    
    #for b in bp['boxes']:
        #b.set_facecolor('lightblue')


    plt.xlabel('Convergence Tolerance')
    plt.ylabel('BEST RMS Error')
    plt.ylim(0.0, ymax)
    plt.title('BW Parameter Estimation: BEST Error vs. Tolerance, '+modelstring)
    tols = rs.copy()    # just to keep naming right -- data file entry differes only in Ratio
    tstrs = ['0.0']
    for t in sorted(tols):
        tstrs.append(str(t))
    #plt.xticks(range(len(tols)+1), tstrs)

    plt.show(block=False)
        
    figure_output(plt, 'BW_vs_tol', modelstring, ratiostring)    

    ############################################
     
    #data_vis(data,sorted(rs))
    #quit()
    ##########
    #
    ##  Plot  Iter Count vs Perturbation
    #fig1 = plt.figure(figno)
    #figno += 1
    figno = 2
    fig2 = plt.figure(figno)
    bp = plt.boxplot(ic_v_tol, notch=True,vert=True ,patch_artist=True)
    
    #standardize graph size
    #figptr = plt.gcf()
    figptr = fig2
    DPI = figptr.get_dpi()    
    figptr.set_size_inches(plotH/float(DPI),plotV/float(DPI))
    
    for b in bp['boxes']:
        b.set_facecolor('lightblue')

    plt.xlabel('BW Converg tolerance')
    plt.ylabel('Number of iterations to converge')
    ymax = 15  # iteration count
    plt.ylim(0.0, ymax)
    plt.title('BW Parameter Estimation: Iterations vs. tolerance, '+modelstring)
    tols = rs.copy()    # just to keep naming right -- data file entry differes only in Ratio
    tstrs = ['0.0']
    for t in sorted(tols):
        tstrs.append(str(t))
    plt.xticks(range(len(tols)+1), tstrs)

    plt.show(block=False)
        
    figure_output(plt, 'Iter_vs_tol', modelstring, ratiostring)    

