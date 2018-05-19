### ABT (Augmented Behavior Trees)

## Goals: 
 * simulate an ABT having stochastic output distribution for each leaf
 * Use hmmlearn library to estimate stochastic ABT parameters from output data
 * Support authoring of ABTs

## Setup:

To build a model you have to create three files (bad!)

 1. modelxx.py   This file contains/initializes
    a. The names of your ABT leafs,
    b. The initial probability of success for each leaf
    c. The mean output symbol value for each state

 2. abt_xxx.py   This file sets up the ABT using 
    a. abt_leaf() (from abtclass.py)

 3. toplevelxx.py   This file seqences the computational steps, typically:
    a. model setup
    b. simulated data generation
    c. HMM initialization
    d. HMM model fitting
    e. reporting
    
