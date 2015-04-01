#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

# pod function borrowed from the sympy project bug tracker.
# It will be available in a future sympy release. See:
# http://goo.gl/7HdtGJ

from __future__ import division
from sympy import Wild, solve, simplify, log, exp, evalf, re, im
from logging import debug
import numpy as np
import multiprocessing as mp
import Queue
import random

def pod(expr, sym):
    """
    Find the points of Discontinuity of a real univariate function

    Example
    =========

    >>> from sympy.calculus.discontinuity import pod
    >>> from sympy import exp, log, Symbol
    >>> x = Symbol('x', real=True)
    >>> pod(log((x-2)**2) + x**2, x)
    [2]
    >>> pod(exp(1/(x-2)**2), x)
    [2]

    """
    #  For now this a hacky implementation.

    # not trying for trig function because they have infinitely
    # many solutions, and this can turn out to be problematic
    # for example solve(tan(x), x) returns only 0 for now
    if expr.is_polynomial():
        return []
    pods = []
    try:
        pods = pods + solve(simplify(1/expr), sym)
    except NotImplementedError:
        return []
    p = Wild("p")
    q = Wild("q")
    r = Wild("r")

    # check the condition for log
    expr_dict = expr.match(r*log(p) + q)
    if not expr_dict[r].is_zero:
        pods += solve(expr_dict[p], sym)
        pods += pod(expr_dict[p], sym)
        pods += pod(expr_dict[r], sym)

    # check the condition for exp
    expr = expr.rewrite(exp)
    expr_dict = expr.match(r*exp(p) + q)
    if not expr_dict[r].is_zero:
        pods += solve(simplify(1/expr_dict[p]), sym)
        pods += pod(expr_dict[p], sym)
        pods += pod(expr_dict[r], sym)

    return list(set(pods)) # remove duplicates

def mpsolve(q, expr):
    try:
        x = solve(expr, 'x')
        q.put(x)
    except NotImplementedError:
        debug('NotImplementedError for solving "'+str(expr)+'"')
        q.put(None)
    except TypeError:
        debug('TypeError exception. This was not supposed to '+\
                'happen. Probably a bug in sympy.')
        q.put(None)

def fsolve(expr):
    xl = []
    try:
        q = mp.Queue()
        p = mp.Process(target=mpsolve, args=(q, expr,))
        p.start()
        # timeout solving after 5 seconds
        x = q.get(True, 5)
        p.join()
        if x is None:
            xl = None
        else:
            for i in x:
                xc = rfc(i)
                if xc is not None:
                    xl.append(xc)
                    debug('Found solution: '+str(xc))
    except Queue.Empty:
        debug('Solving timed out.')
        xl = None
    finally:
        p.terminate()
    return xl

def rfc(x):
    '''
    rfc - Real From Complex
    This tries to detect if a complex number as given by sympy is
    actually a real number. If it is, then it returns the real part
    as a float.
    '''
    try:
        xc = round(float(x), 15)
    # TypeError is thrown for complex solutions during casting
    # to float. We only want real solutions.
    except TypeError:
        # But, there are times that a real solution is calculated
        # as a complex solution, with a really small imaginary part,
        # for example: 2.45009658902771 - 1.32348898008484e-23*I
        # so in cases where the imaginary part is really small,
        # keep only the real part as a solution
        xe = x.evalf()
        debug('Checking if this is a complex number: '+str(xe))
        real = re(xe)
        img = im(xe)
        try:
            if abs(img) < 0.00000000000000001*abs(real):
                debug(str(real)+' is actually a real.')
                xc = round(float(real),15)
            else:
                debug('Yes, it is probably a complex.')
                xc = None
        # another TypeError is raised if we have a function with
        # abs()
        # this is a hack but appears to work
        # FIXME: I don't think this is needed for abs() anymore.
        except TypeError:
            try:
                xc = eval(str(xe))
                debug('Looks like a solution for an abs() '+\
                        'function: '+str(xc))
            except NameError:
                debug('Cannot really tell. I give up.')
                xc = None
    return xc

def percentile(plist, perc):
    '''
    returns the perc (range 0-100) percentile of plist
    '''
    x = sorted(plist)
    n = len(x)
    pos = (n+1)*perc/100
    k = int(np.floor(pos))
    a = pos-k
    p = x[k-1]+a*(x[k]-x[k-1])
    return p

def remove_outliers(plist):
    '''
    This function takes a list (of floats/ints) and returns the list,
    having replaced any outliers with the median value of the list.
    '''
    q1 = percentile(plist, 25)
    q3 = percentile(plist, 75)
    iqr = q3 - q1
    # This looks like a nice value. Decrease to make it easier for
    # a value to become an outlier, increase to make it harder.
    k = 9
    # this is the median
    m = percentile(plist, 50)
    # these are the limits we don't allow values to go under/over
    min_lim = q1 - k*iqr
    max_lim = q3 + k*iqr
    if min_lim < max_lim:
        debug('Any values<'+str(min_lim)+' or >'+\
                str(max_lim)+' are outliers.')
        for i in xrange(0,len(plist)):
            if plist[i] < min_lim or plist[i] > max_lim:
                debug('Found outlier: '+str(plist[i]))
                # if outliers are detected, replace their values with
                # the median. That way it's easier to just set the
                # axis limits to the min/max of the remaining values.
                plist[i] = m
    return plist

