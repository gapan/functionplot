#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

import numpy as np
from Function import Function
from sympy import diff, solve

#f = Function('x^4+x^2', [0,1,0,1])
f = Function('x^4+x^3-3*x^2', [0,1,0,1])
f1 = diff(f.expr, 'x')
x = solve(f1, 'x')
print 'sympy', x
print type(x)
x = np.array(x)
print 'sympy to np.array', x
print type(x)
print eval(f.np_expr)
