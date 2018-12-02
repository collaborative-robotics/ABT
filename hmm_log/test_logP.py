#!/usr/bin/python
#
#  tests for logP() package
#

import numpy as np
import numbers 
from logP import *

print '\n\n  Testing logP() class and related ...\n\n'

#####################################
# test basic log functions
e = np.exp(1)

y = ELv([e, e*e, 0, np.sqrt(e)])

assert isinstance(y[0], float), 'ELv returns wrong type'
#print y
fs = ' elog() test FAIL'
assert abs(y[0] - 1.0) < epsilon, fs
assert abs(y[1] - 2.0) < epsilon, fs
assert np.isnan(y[2]), fs
assert abs(y[3] - 0.5) < epsilon, fs
assert abs(ELv(e*e)-2.0) < epsilon, fs
print ' elog() tests    PASSED'

# eexp()
fs = ' eexp() test  FAIL'
assert  abs(EEv(1)-e) < epsilon, fs
y = EEv([2, 0, LZ, -1])
#print y
assert abs(y[0]-e*e) < epsilon, fs
assert abs(y[1]-1.0) < epsilon, fs
assert abs(y[2]-0.0) < epsilon, fs
assert abs(y[3]-1/e) < epsilon, fs

assert abs(EEv(1) - e) < epsilon, fs

y = EEv([[e, 0],[LZ, 1]])
assert abs(y[1,1]-e) < epsilon, fs
print ' eexp() tests    PASSED'

###################################
# test logP classes and operator overlays
x = logP(0.25)
y = logP(0.25)

# make sure stuff returns right types
#print 'x: ', type(x)
assert isinstance(x, logP), 'logP() returns wrong type'
assert x.lp == np.log(0.25), 'logP() returns wrong value'

##############################
#
#  logP __add__()

z = x + y
assert isinstance(z,logP), 'logP() __add__ returns wrong type'

logsum = np.log(0.25 + 0.25)

fs = 'logP() __add__'
assert abs(z.lp-logsum) < epsilon, fs+FAIL
assert abs((x+y).lp-logsum) < epsilon, fs+FAIL
print fs+PASS

##############################
#
#  logP __mull__()
x = logP(0.25)
y = logP(0.25)
z = x * y
assert isinstance(z,logP), 'logP() __mul__ returns wrong type'
logprod = np.log(0.25*0.25)

fs = 'logP() __mul__ '
assert abs(z.lp-logprod) < epsilon, fs+FAIL
assert abs((x*y).lp-logprod) < epsilon, fs+FAIL
z = x * logP(0)
assert np.isnan(z.lp), fs+FAIL
print fs+PASS

#############################
#
#  logP += A*B
#

x = logP(0.25)
y = logP(0.25)
t = logP(0.25)
t += x*y
fs = 'logP() combined add and times'
assert isinstance(t, logP),fs+FAIL
assert np.exp(t.lp)== 0.25*0.25+0.25 ,fs+FAIL
print fs+PASS


print 'logP classes          PASS'
    
####################################################
#  logP for vectors 
#
x = logPv([e, e*e, e*e*e])
y = logPv([e*e, e, 1/e])

fs = 'logPv returns wrong type'
assert isinstance(x[0], logP), fs
assert isinstance(y[2], logP), fs 

fs = 'logPv() instantiation    FAIL'
assert abs(y[0].lp -  2.0) < epsilon, fs
assert abs(y[1].lp -  1.0) < epsilon, fs
assert abs(y[2].lp - -1.0) < epsilon, fs


print 'logPv() Setitem tests'

q =logPv([e*e, e, 1/e]) 
q[1] = logP(0.5)



# let's exponentiate sums and check them
z = x+y
assert isinstance(z, logPv), ' logPv addition produces wrong type'
m = []
for l in z.v:
    m.append(EE(l.lp))
m = np.array(m)



#print 'm;',m
fs = 'logPv() addition tests '
#print 'compare: ', m[0], (e+e*e)
assert abs(m[0] - (e+e*e)) < epsilon, fs + 'FAIL'
assert abs(m[1] - (e+e*e)) < epsilon, fs + 'FAIL'
assert abs(m[2] - (e*e*e + 1/e)) < epsilon, fs + 'FAIL'

print fs + '         PASS'

###############################################3
#   maxlv() test 
#
v = logPv([0.001, 0.01, 0.5, 4, 0.0])
i, l = v.maxlv()

fs = 'logPv() maxlv()  '
assert i==3, fs + FAIL
print l, l.lp
assert l.lp == np.log(4), fs + FAIL
print fs + PASS


##########################################
#  logPv  __mul__ tests 
#
fs = 'logPv() vector * vector multiply'

x = logPv([e, e*e, e*e*e])
y = logPv([e*e, e, 1/e])

t = x*y
print t, type(t)
assert t.v[0].lp == 3.0, fs + FAIL
assert t.v[1].lp == 3.0, fs + FAIL
assert t.v[2].lp == 2.0, fs + FAIL



print '\nlogPv() Tests  ' + PASS

#######################################
#
#   test logPm  - matrix version
#
    #  logP for matrices 
x = logPm([
    [e, e*e, e*e*e],
    [e, e*e, e*e*e],
    [e, e*e, e*e*e]  ])
y = logPm([
    [e*e, e, 1/e],
    [e*e, e, 1/e],
    [e*e, e, 1/e]  ])

fs = 'logPm returns wrong type'
assert np.shape(x.m) == (3,3), fs
#print x[0,0], type(x.m[0,0])
assert isinstance(x.m[0,0], numbers.Number), fs
assert isinstance(y, logPm), fs
assert isinstance(y[2,1], logP), fs

#print '---'
#print x
#print y
#print '----'

fs = 'logPm() instantiation'
assert abs(y[1,0].lp - 2.0)  < epsilon, fs + FAIL
assert abs(y[2,1].lp - 1.0)  < epsilon, fs + FAIL
assert abs(y[1,2].lp - -1.0) < epsilon

print fs + PASS


    
print 'Setitem tests'

q =logPm([
    [e*e, e, 1/e],
    [e*e, e, 1/e],
    [e*e, e, 1/e]  ]) 
q[1,2] = logP(5)

fs = 'logPm setitem() test: '
assert q[1,2].lp == np.log(5), fs+FAIL
print fs+PASS

print 'Starting matrix addition tests ...'
z = x + y
assert isinstance(z,logPm), ' logPm() __add__ returns wrong type'


#m = EEv(z)  # let's exponentiate sums and check them
m = logPm(0.5*np.ones((3,3)))
for i in [0,1,2]:
    for j in [0,1,2]:
        m.m[i,j] = logP(EE(z.m[i,j]))


fs = 'EEv(z) matrix argument:  '
assert np.shape(m.m) == (3,3), fs + 'FAIL'

print fs + '             PASS'

#print 'm;',m
fs = 'logPm  __add__() '
#print m[0,0].lp, logP(e+e*e).lp
assert abs(m[0,0].lp - np.log(e+e*e)) < epsilon, fs + 'FAIL'
assert abs(m[0,1].lp - np.log(e+e*e)) < epsilon, fs + 'FAIL'
assert abs(m[0,2].lp - np.log(e*e*e + 1/e)) < epsilon, fs + 'FAIL'
print fs + '         PASS'


print '   logPm() matrix tests passed'
###################################################################
#
#  math combining vector, matrix, getitem, etc.
#

fs = 'logPx mixed math tests'

s = logP(0.5)
v = logPv([1.0, 0.5, 0.25, e])
m = logPm([[1.0, 0.5, 0.25, e],
            [1.0, 0.5, 0.25, e],
            [1.0, 0.5, 0.25, e]])

n = logPv(np.ones(4))

t = logP(0) + logP(0)
assert np.isnan(t.lp), fs+FAIL
t = s + v[1]
assert np.exp(t.lp) == 1.0, fs+FAIL
t = v[0] + m[1,1]
assert np.exp(t.lp) == 1.5, fs+FAIL
t = s + n[2]
assert np.exp(t.lp) == 1.5, fs+FAIL
t = logP(0) + n[2]
assert np.exp(t.lp) == 1.0, fs+FAIL
t = logP(0) * n[2]
assert np.isnan(t.lp), fs+FAIL


print fs+PASS


print '\n\n           logPx() --  ALL TESTS PASS \n\n'

    
