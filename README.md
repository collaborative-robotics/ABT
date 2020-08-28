### ABT (Augmented Behavior Trees)

## Goals: 
 * simulate an ABT having stochastic output distribution for each leaf.
 * Use hmmlearn library to estimate stochastic ABT parameters from output data.
 * Support authoring of ABTs.

 
## Classes:

The simulation is built on the [b3 library](https://github.com/behavior3/behavior3py),
a python Behavior Tree library.  The new leaf class, `aug_leaf(b3.Action)` inherits the 
b3 Action class and adds transition and emission probabilities.  

Emmisions (observations) from each state are modeled by `NSYMBOLS`  discrete symbols. 
There is a Gaussian probability density applied to each state with mean `mu` and standard deviation `sigma`.  The observations are integer valued.  Default sigma = 2.00

## Setup:

To build a model you have to create three files (bad!)

1. `modelxx.py`.   This file contains/initializes
 
    a. The names of your ABT leafs,
    
    b. The initial probability of success for each leaf
    
    c. The mean and variance for the emission symbol distribution for each state

    d. an object of class model (defined in abtclass.py)
    
    e. all of this is folded into an object of class model() (def in abtclass.py)

2. `[ProjName]_ABT.py`.   This file sets up the ABT with 
 
    a. the new leaf class `aug_leaf()` (from abtclass.py)

    b. the 16-state file peg_ABT.py  e.g. peg in hole task. 
    
    c. or- a simple test project:   `simp_ABT.py` with 4+2 states

    d. Coming soon: automatic generation of HMM from BT file



3. `tl_bw_hmm.py`.   This file seqences the computational steps, typically:
 
    a. model setup
    
    b. simulated data generation
    
    c. HMM initialization
    
    d. HMM model fitting
    
    e. reporting

`tl_bw_hmm.py` has two command line arguments:   the HMM perturbation magnitude (0.0<p<0.5) and a text comment for the data meta file. 
    
##  Output Files

Your results will appear in three files

1. metadata.txt -- one line for each run of tl_xxxxxxx.py. 

Unique filenames are generated using URI's.  Each line contains 
    
  0. date and time stamp
  1. name of data file
  2. ownname  (name of the top level file)
  3. git hash (1st 10 chars of current git hash)
  4. number of HMM / BT states
  5. text field (comment)

2. sequences/   contains the simulated state transition/observation sequences

3. bw_output/   containts datafiles (item 1 of metadata).   Data file line:
   1.  Task code (2=Baum Welch)
   1.  Ratio  (codeword mean spacing / sigma)
   2.  di     (codeword spacing)
   3.  HMM_delta    amt HMM params changed
   4.  Sigma
   5.  run#
   6.  e2 (RMS error)
   7.  emax (max error)


## Other Files

 * `hmm_bt.py`
 
    Utilities for A-matrices, and special magic for setting up an HMM_setup
    
 * `abtclass.py`

    The new "leaf" class which Augments the BT to work with Success/Fail probabilities, and stochastic observations from each leaf. 
    
