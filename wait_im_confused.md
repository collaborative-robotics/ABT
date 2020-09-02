# Wait!  I'm confused by the several BT packages here!
First it is recommended that you read two papers:

1. [Simulation Results on Selector Adaptation in Behavior Trees](https://arxiv.org/pdf/1606.09219)
1. ["Hidden Markov Models derived from Behavior Trees"](https://arxiv.org/pdf/1907.10029.pdf).
    
for context, terminology, notation, and examples. 

## OK, let's start with a little chronology:


1. In 2013, [Marzinotto et al., 2014](http://www.csc.kth.se/~miccol/Michele_Colledanchise/Publications_files/2013_ICRA_mcko.pdf), a great group out of KTH in Sweden, got to work on BTs.
    
2. They released a [javascript package](https://github.com/behavior3/behavior3js) and a [python version](https://github.com/behavior3/behavior3py) shortly after. See `https://github.com/behavior3`.
    
3. Blake Hannaford modified the python version (behavior3py) so that BT selector nodes could learn from experience: *Adaptive BTs*, as documented  in the report: 
    [Simulation Results on Selector Adaptation in Behavior Trees](https://arxiv.org/pdf/1606.09219). These 
    mods are in the branch `abt_dev`
    
4. BH worked on a new class of BTs, *Augmented BTs*, in which each node emits observations drawn from     a probability distribution, and has a defined probability of success on each tick.  These were 
    analytically linked to Hidden Markov Models in the report ["Hidden Markov Models derived from Behavior Trees"](https://arxiv.org/pdf/1907.10029.pdf).
    
 5. In the future, someone could *combine* the classes so that a single derived set of classes supports Adaptive BTs and Augmented BTs.


## Classes:

### *Adaptive BTs* 

The purpose of Adaptive BTs is to learn from experience.  For example, if the third
child of a Selector node with 5 children has the highest probability of success (as learned over multiple tics) then it should be tried first by the selector node instead of
 after the first two nodes fail.
 
 Adaptive BTs  are built on the `behavior3py` module with minor modifications[1].   The key functionality of adaptive BTs is the selector (Priority) node which chooses the most successful child first (as opposed to a fixed order).  This is the `SmrtSel00(), SmrtSel01(), etc.` classes (featuring varieties of the smart selection algorithm). `SmrtSelxx()` are located in the [adaptive-b3 project](https://github.com/collaborative-robotics/adaptive-b3) `main` branch.

### *Augmented BTs* 
The purpose of adaptive BTs is to
1. Study the relationship between Behavior Trees and HMMs
2. Track evolution of a BT in spite of noisy measurements. 
3. Model behavioral systems with stochastic behavior and noisy measurements.

Augmented BTs refer to BTs in which each leaf (`class aug_leaf()') inherits the `behavior3py.Action()` class and adds

```python
self.Ps   # the probability the node will return `b3.SUCCESS' (a fixed param)
self.Pf = 1.0-self.Ps
self.Obs = np.zeros(NSYMBOLS)   # probability to emit each observation symbol in that state.
```

Sadly, instead of a proper import structure, `b3` is hard-copied into the ABT repository.   If 
the `abt_dev` branch of `behavior3py` [1] is updated, recopy the entire `b3` directory from it into `ABT/` .

Augmeted BTs are analytically equivalent to HMMs (e.g. there is exactly one HMM for each ABT).  HMM algorithms are applied to outputs from executed ABTs in various "top level" test software.


## Notes
[1] [b3 library](https://github.com/collaborative-robotics/behavior3py) (a fork of [behavior3py](https://github.com/behavior3/behavior3py), as modified in the `abt_dev` [branch](https://github.com/collaborative-robotics/behavior3py/tree/abt_dev)   
