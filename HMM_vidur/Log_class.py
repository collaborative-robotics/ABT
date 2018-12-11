import numpy as np
from numbers import Number

class hf():
    def __init__(self,x = 1):
        if isinstance(x,hf):
            self = x
            return

        if x == 0 or x == -np.inf:
            self.m = np.inf
            self.e = 0
        else :
            self.e = np.int64(np.log10(x))
            self.m = np.float64(x*float(10)**-self.e)

    def __str__(self):
        return "{0:f} x 10^{1:d}".format(self.m,self.e)

    def __add__(self,x):
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
        res.m = m
        res.e = self.e
        return res

    def __sub__(self,x):
        if not isinstance(x,(Number,hf)):
            raise ValueError("Not a valid datatype")
        if isinstance(x, Number):
            x = hf(x)
        if self.m == np.inf:
            return x
        if x.m == np.inf:
            return self
        m = self.m - x.m*float(10)**(x.e-self.e)
        res = hf()
        res.m = m
        res.e = self.e
        return res

    def __mul__(self,x):
        if not isinstance(x,(Number,hf)):
            raise ValueError("Not a valid datatype")
        if isinstance(x, Number):
            x = hf(x)
        if x.m == -np.inf:
            return x
        m = x.m * self.m
        e = self.e + x.e
        res = hf()
        res.m = m
        res.e = e
        return res

    def __div__(self,x):
        if not isinstance(x,(Number,hf)):
            raise ValueError("Not a valid datatype")
        if isinstance(x, Number):
            x = hf(x)
        if x.m == -np.inf:
            return x
        m = self.m / x.m
        e = self.e - x.e
        res = hf()
        res.m = m
        res.e = e
        return res

# def matmul(a,b):
#     assert a.shape[1] == b.shape[0]
#     for i in range(a.shape[0]%8):


#
# a = np.broadcast_to(np.array(hf(5)),(2,2))
# b = np.broadcast_to(np.array(hf(6)),(2,2))
# print(np.dot(a,b))
# print(a[0][0])
