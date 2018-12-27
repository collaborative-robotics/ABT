<<<<<<< HEAD
import numpy as np
from numbers import Number

class hf():
    def __init__(self,x = 1):
        if isinstance(x,hf):
            self = x
            return

        if x == 0 or x == -np.inf:
            self.m = np.inf
=======

import numpy as np
from numbers import Number

class logP():
    def __init__(self,x = 1):
        if isinstance(x,logP):
            self = x
            return
        if x == np.inf:
            self.m = np.inf
            self.e = np.inf
            return
        if x == 0:
            self.m = 0
>>>>>>> UWmaster2
            self.e = 0
        else :
            self.e = np.int64(np.log10(x))
            self.m = np.float64(x*float(10)**-self.e)

    def __str__(self):
        return "{0:f} x 10^{1:d}".format(self.m,self.e)

    def __add__(self,x):
<<<<<<< HEAD
        if not isinstance(x,(Number,hf)):
            raise ValueError("Not a valid datatype")
        if isinstance(x, Number):
            x = hf(x)
        if self.m == np.inf:
            return x
        if x.m == np.inf:
            return self
        m = self.m + x.m*float(10)**(x.e-self.e)
        res = hf()
=======
        if not isinstance(x,(Number,logP)):
            raise ValueError("Not a valid datatype")
        if isinstance(x, Number):
            x = logP(x)
        if self.m == np.inf or x.m == np.inf:
            return logP(np.inf)
        m = self.m + x.m*float(10)**(x.e-self.e)
        res = logP()
>>>>>>> UWmaster2
        res.m = m
        res.e = self.e
        return res

    def __sub__(self,x):
<<<<<<< HEAD
        if not isinstance(x,(Number,hf)):
            raise ValueError("Not a valid datatype")
        if isinstance(x, Number):
            x = hf(x)
=======
        if not isinstance(x,(Number,logP)):
            raise ValueError("Not a valid datatype")
        if isinstance(x, Number):
            x = logP(x)
>>>>>>> UWmaster2
        if self.m == np.inf:
            return x
        if x.m == np.inf:
            return self
        m = self.m - x.m*float(10)**(x.e-self.e)
<<<<<<< HEAD
        res = hf()
=======
        res = logP()
>>>>>>> UWmaster2
        res.m = m
        res.e = self.e
        return res

    def __mul__(self,x):
<<<<<<< HEAD
        if not isinstance(x,(Number,hf)):
            raise ValueError("Not a valid datatype")
        if isinstance(x, Number):
            x = hf(x)
=======
        if not isinstance(x,(Number,logP)):
            raise ValueError("Not a valid datatype")
        if isinstance(x, Number):
            x = logP(x)
>>>>>>> UWmaster2
        if x.m == -np.inf:
            return x
        m = x.m * self.m
        e = self.e + x.e
<<<<<<< HEAD
        res = hf()
=======
        res = logP()
>>>>>>> UWmaster2
        res.m = m
        res.e = e
        return res

    def __div__(self,x):
<<<<<<< HEAD
        if not isinstance(x,(Number,hf)):
            raise ValueError("Not a valid datatype")
        if isinstance(x, Number):
            x = hf(x)
        if x.m == -np.inf:
            return x
        m = self.m / x.m
        e = self.e - x.e
        res = hf()
=======
        if not isinstance(x,(Number,logP)):
            raise ValueError("Not a valid datatype")
        if isinstance(x, Number):
            x = logP(x)
        if x.m == np.inf or x.test_val == 0:
            # print ("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@hit")
            # exit()
            return logP(np.inf)
        m = self.m / x.m
        e = self.e - x.e
        res = logP()
>>>>>>> UWmaster2
        res.m = m
        res.e = e
        return res

<<<<<<< HEAD
=======
    def test_val(self):
        return (self.m * 10.00**self.e)

    def id(self):
        return 'scale'

def array(x):
    assert isinstance(x,(list,np.ndarray))
    x = np.array(x)
    # index = x.shape(:-1)
    # last  = x.shape(-1)
    new_x = np.empty(x.shape, dtype = 'O')
    for i in np.ndindex(x.shape):
        new_x[i] = logP(x[i])
    return new_x
    # else:

>>>>>>> UWmaster2
# def matmul(a,b):
#     assert a.shape[1] == b.shape[0]
#     for i in range(a.shape[0]%8):


#
<<<<<<< HEAD
# a = np.broadcast_to(np.array(hf(5)),(2,2))
# b = np.broadcast_to(np.array(hf(6)),(2,2))
=======
# a = np.broadcast_to(np.array(logP(5)),(2,2))
# b = np.broadcast_to(np.array(logP(6)),(2,2))
>>>>>>> UWmaster2
# print(np.dot(a,b))
# print(a[0][0])
