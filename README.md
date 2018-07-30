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
There is a Gaussian probability density applied to each state with mean `mu` and standard deviation `sigma`.

## Setup:

To build a model you have to create three files (bad!)

 1. `modelxx.py`.   This file contains/initializes
 
    a. The names of your ABT leafs,
    
    b. The initial probability of success for each leaf
    
    c. The mean and variance for the emission symbol distribution for each state

 2. `[ProjName].py`.   This file sets up the ABT with 
 
    a. the new leaf class `aug_leaf()` (from abtclass.py)
    
    b. the (current ProjName = `peg2.py`) e.g. peg in hole task. 
    
    c. or- a simple test project:   `simp_ABT.py`

 3. `toplevelxx.py`.   This file seqences the computational steps, typically:
 
    a. model setup
    
    b. simulated data generation
    
    c. HMM initialization
    
    d. HMM model fitting
    
    e. reporting
    
## Other Files

 * `hmm_bt.py`
 
    Utilities for A-matrices, and special magic for setting up an HMM_setup
    
 * `abtclass.py`

    The new "leaf" class which Augments the BT to work with Success/Fail probabilities, and stochastic observations from each leaf. 
    
