#
# stub for testing utilities

epsilon_probs = 0.00001  # required accuracy for probabilities

def assert_feq(a,b,message='assertion failure: floats should be equal', eps=epsilon_probs):
    e = abs(a-b)
    assert e<eps, message    
    return

