#!/usr/bin/python
#
#  speed tests for logP() package
#

import numpy as np
import numbers
import sys as sys
import time               # for benchmarking

FAIL = 'FAIL'
PASS = 'PASS'
epsilon = 1.0E-06

from logP import *
from logP_matrix import *

##
#    Important:  use scripts:   set_log_test and set_scale_test prior to this 
#             command.   These scripts choose the desired version of logP() class
#
#    set_log_test: cp logP_log.py logP.py
#        etc/
#
#

logf = open('t.txt','w')


def trep(n, msg, t):
    string = '{:10d} {:20s}{:12.7f}'.format(n,msg,t)
    print >>logf, string
    print string


TN = 5000
print '\n\n  Timing logP() class and related ...\n'
p = logP(0.5)

libname = p.id()  # figure out what type of logP()

print '            Using: ', libname,'\n\n'
print >>logf, 'library: ', libname

start_time = time.clock()
for i in range(TN):
    p = logP(0.5)
t =  time.clock() - start_time
trep(TN,'Instantiations',t)


e = np.exp(1) 
 
if libname=='scale':
    ##################################
    #
    #  test logP_norm()
    #
    
    x = logP(0.5)
    start_time = time.clock()
    for i in range(TN):
        x.norm()
    t= time.clock() - start_time
    trep(TN,' x.norm(0.5): ',t)
    
#############################
#
#  logP __add__()


x = logP(0.25)
y = logP(0.25)
start_time = time.clock()
for i in range(TN):
    z = x + y
t = time.clock()-start_time
trep(TN,' x + y ',t)


#############################
#
#  logP __mult__()

msg =  ' x * y ' 
x = logP(0.25)
y = logP(0.25)
start_time = time.clock()
for i in range(TN):
    z = x * y
trep(TN,msg, time.clock()-start_time)



#############################
#
#  logP __div__()

x = logP(0.25)
y = logP(0.2)
start_time = time.clock()
for i in range(TN):
    z = x / y
t=time.clock()-start_time
trep(TN,' x/y ',t)
##############################
#
#    test_val()
#


x = logP(0.25)
y = logP(0.25)
start_time = time.clock()
for i in range(TN):
    z = x.test_val()
t= time.clock()-start_time
trep(TN,' x.test_val() ', t)


##############################
#
#    add a scalar
#

x = logP(0.25)
y = logP(0.25)
start_time = time.clock()
for i in range(TN):
    z = x + 0.10
t= time.clock()-start_time
trep(TN,' x + 0.10',t)




##############################
#
#    add and times += 

x = logP(0.25)
y = logP(0.25)
start_time = time.clock()
for i in range(TN):
    z += x*y
t= time.clock()-start_time
trep(TN,' z += x*y',t)

###################################################################
#
#     Vectors
#

#############
#Instantiation

start_time = time.clock()
for i in range(TN):
    x = logPv([e, e*e, e*e*e])
    #y = logPv([e*e, e, 0.001])
t= time.clock()-start_time
trep(TN,'3-Vect. Instantiation',t)

#############
# vector addition

x = logPv([e, e*e, e*e*e])
y = logPv([e*e, e, 0.001])
start_time = time.clock()
for i in range(TN):
    z = x+y
t= time.clock()-start_time
trep(TN,'3-Vect. Add',t)

#############
# vector addition

x = logPv([e, e*e, e*e*e])
y = logPv([e*e, e, 0.001])
start_time = time.clock()
for i in range(TN):
    z = x*y
t= time.clock()-start_time
trep(TN,'3-Vect. Mult',t)

quit()   
 
    
    
    
####################################################
#  logP for vectors 
# 

q =logPv([e*e, e, 1/e]) 
q[1] = logP(0.5)


print '\n Test addition of logPv vectors  with '+libname
# let's  sumn two logPv vectors and check them
z = x+y
fs = ' logPv addition produces wrong type'
assert isinstance(z, logPv), fs + FAIL

for i in range(3):
    print ' sum computation: ', x[i],y[i],z[i] 


m = []  # a list of numerical float values
for l in z.v:
    print 'appending ', l, l.test_val()
    m.append(l.test_val())
m = np.array(m)

#print 'm;',m
fs = 'logPv() addition tests '
#print 'compare: ', m[0], (e+e*e)
print 'error: ', abs(m[0] - (e*e+e))
assert abs(m[0] - (e+e*e)) < epsilon, fs + 'FAIL'
print 'error: ', abs(m[1] - (e*e+e))
assert abs(m[1] - (e+e*e)) < epsilon, fs + 'FAIL'
print 'error: ', abs(m[2] - (e*e*e + 1/e))
#assert abs(m[2] - (e*e*e + 0.001)) < epsilon, fs + 'FAIL'

#  logPv add the elements:
x = np.array([[1,2,3,4,5],
              [1,2,3,4,5],
              [1,2,3,4,5],
              [1,2,3,4,5],
              [1,2,3,4,5]   ])
al = logPm(x/10.0)

T = 4
a = logP(0.0) 
print ' adding array elements:'
for j in range(5):
    x = al[T,j]
    print '        ',al[T,j], al[T,j].test_val(), x, x.test_val()
    a = a + x

print a.test_val()
assert a.test_val() == 1.5, fs + libname


print fs + libname+ '         PASS'

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
assert abs(t.v[0].test_val() - e*e*e) < epsilon, fs + FAIL
assert abs(t.v[1].test_val() - e*e*e) < epsilon , fs + FAIL
assert abs(t.v[2].test_val() - e*e) < epsilon, fs + FAIL



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

#print '--------------------------'
#print y
#print y[1,0].test_val(),  e*e
#print '--------------------------'

fs = 'logPm returns wrong type'
assert np.shape(x.m) == (3,3), fs
#print x[0,0], type(x.m[0,0])
assert isinstance(x.m[0,0], numbers.Number), fs
assert isinstance(y, logPm), fs
assert isinstance(y[2,1], logP), fs
 
fs = 'logPm() instantiation'

#print y[1,0],  e*e

assert abs(y[1,0].test_val() - e*e)  < epsilon, fs + FAIL
assert abs(y[2,1].test_val() - e)  < epsilon, fs + FAIL
assert abs(y[1,2].test_val() - 1.0/e) < epsilon, fs + FAIL

print fs + PASS

################################################################   TODO:
#
#     Tests for 3D logPm() instances
#

y3 = logPm(np.array(
        [ [
        [e*e, e, 1/e],
        [e*e, e, 1/e],
        [e*e, e, 1/e] ],
        [
        [e*e, e, 1/e],
        [e*e, e, 1/e],
        [e*e, e, 1/e] ],
        [
        [e*e, e, 1/e],
        [e*e, e, 1/e],
        [e*e, e, 1/e] ],
        [
        [e*e, e, 1/e],
        [e*e, e, 1/e],
        [e*e, e, 1/e] ]  ] )
    )
     
###########    add some assertions here

###########   also test math with 3D matrices  

    
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


print '\n\n           logPx() --  ALL TESTS PASS  with '+ libname+'\n\n'

    
