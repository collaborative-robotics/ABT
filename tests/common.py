#
# stub for testing utilities
import random
import numpy as np

epsilon_probs = 0.00001  # required accuracy for probabilities

#
#  robust assertion that two floats are equal
def assert_feq(a,b,message='assertion failure: floats should be equal', eps=epsilon_probs):
    e = abs(a-b)
    assert e<eps, message    
    return

def all_random_seeds(x):
    random.seed(x)
    np.random.seed(x)
