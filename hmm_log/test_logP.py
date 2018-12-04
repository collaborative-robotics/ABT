#!/usr/bin/python
#
#  tests for logP() package
#

import numpy as np
import numbers
import sys as sys

FAIL = 'FAIL'
PASS = 'PASS'
epsilon = 1.0E-06

if len(sys.argv) != 2:
    print ''' Usage:
       >python  test_logP.py  [log|scale]
       
    log = use logP_log
    scale = use logP_scale
    '''
    quit()

a = sys.argv[1]
print '\n\n'
if a == 'log':
    from logP_log import *
    print '        Using logP_log.py'
elif a == 'scale':
    from logP_scale import logP
    print '        Using logP_scale.py'
else:
    print 'illegal cmd line option: '+a
    quit()
    
from logP_matrix import *


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
assert abs(x.test_val() - (0.25))< epsilon, 'logP() returns wrong value'
assert abs(x.test_val() - (0.25))< epsilon, 'logP() returns wrong value'



##################################
#
#  test logP_norm()
#
x = logP(0.5)
x.norm()
fs = '   norm test'
assert abs(x.test_val() - 0.5)<epsilon, fs+FAIL
x.norm()
x.norm()
x.norm()
assert abs(x.test_val() - 0.5)<epsilon, fs+FAIL
print fs+PASS
 
##############################
#
#  logP __add__()

x = logP(0.25)
y = logP(0.25)
z = x + y
assert isinstance(z,logP), 'logP() __add__ returns wrong type'

logsum = np.log(0.25 + 0.25)

fs = 'logP() __add__'
assert abs(z.test_val()-0.500) < epsilon, fs+FAIL
assert abs((x+y).test_val()-0.500) < epsilon, fs+FAIL
print fs+PASS

##############################
#
#  logP __mull__()
x = logP(0.25)
y = logP(0.25)
z = x * y
assert isinstance(z,logP), 'logP() __mul__ returns wrong type'
prod = 0.25*0.25
logprod = np.log(prod)

fs = 'logP() __mul__ '
assert abs(z.test_val()-prod) < epsilon, fs+FAIL
assert abs((x*y).test_val()-prod) < epsilon, fs+FAIL
z = x * logP(0)
assert z.test_val() == 0, fs+FAIL
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
assert t.test_val() == 0.25*0.25+0.25 ,fs+FAIL
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
assert abs(y[0].test_val() -  e*e) < epsilon, fs
assert abs(y[1].test_val() - e) < epsilon, fs
assert abs(y[2].test_val() - 1.0/e) < epsilon, fs


print 'logPv() Setitem tests'

q =logPv([e*e, e, 1/e]) 
q[1] = logP(0.5)



# let's exponentiate sums and check them
z = x+y
assert isinstance(z, logPv), ' logPv addition produces wrong type'
m = []
for l in z.v:
    m.append(l.test_val())
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

print fs,i, l, l.test_val() 
assert i==3, fs + FAIL
assert abs(l.test_val() - 4.0)<epsilon, fs + FAIL
print fs + PASS


##########################################
#  logPv  __mul__ tests 
#
fs = 'logPv() vector * vector multiply'

x = logPv([e, e*e, e*e*e])
y = logPv([e*e, e, 1/e])

t = x*y
print t, type(t)
assert t.v[0].test_val() == e*e*e, fs + FAIL
assert t.v[1].test_val() == e**3 , fs + FAIL
assert t.v[2].test_val() == e*e, fs + FAIL



print '\nlogPv() Tests  ' + PASS

#######################################
#
#   test logPm  - matrix version
#
    #  logP for matrices 
x = logPm(np.array([
        [e, e*e, e*e*e],
        [e, e*e, e*e*e],
        [e, e*e, e*e*e]  ]))

y = logPm(np.array([
        [e*e, e, 1/e],
        [e*e, e, 1/e],
        [e*e, e, 1/e]  ]))

print y[1,0], y[1,0].mant, e*e

fs = 'logPm returns wrong type'
assert np.shape(x.m) == (3,3), fs
#print x[0,0], type(x.m[0,0])
assert isinstance(x.m[0,0], numbers.Number), fs
assert isinstance(y, logPm), fs
assert isinstance(y[2,1], logP), fs
 
fs = 'logPm() instantiation'

print y[1,0].test_val(), y[1,0].mant, e*e
assert abs(y[1,0].test_val() - e*e)  < epsilon, fs + FAIL
assert abs(y[2,1].test_val() - e)  < epsilon, fs + FAIL
assert abs(y[1,2].test_val() - 1.0/e) < epsilon, fs + FAIL

print fs + PASS


    
print 'Setitem tests'

q =logPm(np.array(
    [
    [e*e, e, 1/e],
    [e*e, e, 1/e],
    [e*e, e, 1/e]  ]
    )) 
q[1,2] = logP(5)

fs = 'logPm setitem() test: '
assert (q[1,2].test_val() -5)<epsilon, fs+FAIL
print fs+PASS

print 'Starting matrix addition tests ...'
z = x + y
assert isinstance(z,logPm), ' logPm() __add__ returns wrong type'


fs = 'EEv(z) matrix argument:  '
assert np.shape(z.m) == (3,3), fs + 'FAIL'

print fs + '             PASS'

#print 'm;',m
fs = 'logPm  __add__() '

assert abs(z[0,0].test_val() - (e+e*e)) < epsilon, fs + 'FAIL'
assert abs(z[0,1].test_val() - (e+e*e)) < epsilon, fs + 'FAIL'
assert abs(z[0,2].test_val() - (e*e*e + 1/e)) < epsilon, fs + 'FAIL'
print fs + '         PASS'


print '   logPm() matrix tests passed\n'
###################################################################
#
#  math combining vector, matrix, getitem, etc.
#

fs = 'logPx mixed math tests'

s = logP(0.5)
v = logPv([1.0, 0.5, 0.25, e])
m = logPm(np.array(
    [[1.0, 0.5, 0.25, e],
     [1.0, 0.5, 0.25, e],
     [1.0, 0.5, 0.25, e]])
    )

n = logPv(np.ones(4))

t = logP(0) + logP(0)
assert abs(t.test_val()-0)<epsilon, fs+FAIL
t = s + v[1]
assert abs(t.test_val() - 1.0)<epsilon, fs+FAIL
t = v[0] + m[1,1]
assert t.test_val() == 1.5, fs+FAIL
t = s + n[2]
assert t.test_val() == 1.5, fs+FAIL
t = logP(0) + n[2]
assert t.test_val()  == 1.0, fs+FAIL
t = logP(0) * n[2]
assert (t.test_val()-0.0)<epsilon, fs+FAIL


print fs+PASS


print '\n\n           logPx() --  ALL TESTS PASS \n\n'

    
