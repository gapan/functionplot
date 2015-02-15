#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

# pod function borrowed from the sympy project. It will be available in a
# future sympy release:
# https://github.com/hargup/sympy/blob/e8d07985635bc4d7ee42c22534073ac9433231c3/sympy/calculus/discontinuity.py

from sympy import Wild, solve, simplify, log, exp, evalf, re, im
from logging import debug

def pod(expr, sym):
    # pod: Points of discontinuty, (will replace with a better name)
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
    pods = pods + solve(simplify(1/expr), sym)
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


def fsolve(expr):
    xl = []
    try:
        x = solve(expr, 'x')
        for i in x:
            xc = real_from_complex(i)
            if xc is not None:
                xl.append(xc)
                debug('Found solution: '+str(xc))
    except NotImplementedError:
        debug('NotImplementedError for solving "'+str(expr)+'"')
    return xl

def real_from_complex(x):
    '''
    This tries to detect if a complex number as given by sympy is actually
    a real number. If it is, then it returns the real part as a float.
    '''
    try:
        xc = float(x)
    # TypeError is thrown for complex solutions during casting
    # to float. We only want real solutions.
    except TypeError:
        # But, there are times that a real solution is calculated
        # as a complex solution, with a really small imaginary part,
        # for example: 2.45009658902771 - 1.32348898008484e-23*I
        # so in cases where the imaginary part is really small,
        # keep only the real part as a solution
        debug('Checking if this is a complex number: '+str(x.evalf()))
        real = re(x.evalf())
        img = im(x.evalf())
        if abs(img) < 0.00000000000000001:
            debug(str(real)+' is actually a real.')
            xc = float(real)
        else:
            debug(str(x.evalf())+' is probably a complex.')
            xc = None
    return xc
    
