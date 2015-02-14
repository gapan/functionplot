#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

from __future__ import division
import numpy as np
from sympy import diff, solve
from PointOfInterest import PointOfInterest as POI

class Function:
    
    def update_graph_points(self, xylimits):
        x_min, x_max, y_min, y_max = xylimits
        x = np.arange(x_min, x_max, (x_max-x_min)/self.resolution)
        # if it doesn't evaluate, the expression is wrong
        try:
            y = eval(self.np_expr)
        except:
            return False
        # no need to calculate values that are off the displayed scale
        # this fixes some trouble with asymptotes like in tan(x)
        # FIXME: unfortunately there is more trouble with asymptotes
        y[y>y_max] = np.inf
        y[y<y_min] = np.inf
        self.graph_points = x, y
        return True

    def _get_expr(self, expr):
        # caps to lowercase
        expr = expr.lower()
        # remove all spaces
        expr = expr.replace(' ', '')
        # replace commas with decimals
        expr = expr.replace(',', '.')
        # braces and bracets to parens
        expr = expr.replace('{', '(')
        expr = expr.replace('}', ')')
        expr = expr.replace('[', '(')
        expr = expr.replace(']', ')')
        # turn greek notation to english
        expr = expr.replace('\xce\xb7\xce\xbc(', 'sin(')
        expr = expr.replace('\xcf\x83\xcf\x85\xce\xbd(', 'cos(')
        expr = expr.replace('\xce\xb5\xcf\x86(', 'tan(')
        expr = expr.replace('\xcf\x83\xcf\x86(', 'cot(')
        expr = expr.replace('\xcf\x83\xcf\x84\xce\xb5\xce\xbc(', 'csc(')
        expr = expr.replace('\xcf\x84\xce\xb5\xce\xbc(', 'sec(')
        expr = expr.replace('\xcf\x87', 'x')
        expr = expr.replace('\xcf\x80', 'pi')
        # FIXME: provide for implied multiplication symbol
        return expr

    def _get_np_expr(self, expr):

        # add "np." prefix to trig functions
        expr = expr.replace('sin(', 'np.sin(')
        expr = expr.replace('cos(', 'np.cos(')
        expr = expr.replace('tan(', 'nxp.tan(')
        expr = expr.replace('cot(', '1/np.tan(') # no cot in numpy
        expr = expr.replace('sec(', '1/np.cos(') # no sec or csc either
        expr = expr.replace('csc(', '1/np.sin(')
        # correct log functions
        expr = expr.replace('log(', 'np.log10(')
        expr = expr.replace('ln(', 'np.log(')
        expr = expr.replace('loge(', 'np.log(')
        expr = expr.replace('log2(', 'np.log(')
        # just in case someone misspells sqrt
        expr = expr.replace('sqr(', 'sqrt(')
        expr = expr.replace('sqrt(', 'np.sqrt(')
        # absolute value
        expr = expr.replace('abs(', 'np.abs(')
        # pi and e
        expr = expr.replace('pi', 'np.pi')
        expr = expr.replace('e', 'np.e')
        # powers
        expr = expr.replace('^', '**')
        return expr

    # FIXME: actually implement this
    # sympy printing to LaTeX can probably do it
    def _get_mathtex_expr(self, expr):
        return expr

    def calc_poi(self):
        # POI types:
        # 1: x intercept
        # 2: y intercept
        # 3: local min/max
        self.poi = []
        # x intercepts
        try:
            x = solve(self.expr, 'x')
            for i in x:
                self.poi.append(POI(i, 0, 0))
        except NotImplementedError:
            print 'NotImplementedError for solving',self.expr,
            print 'x intercepts not calculated'
        # y intercept
        x = 0
        try:
            y = eval(self.np_expr)
            print x,y
            self.poi.append(POI(x, y, 1))
        except ZeroDivisionError:
            print 'ZeroDivisionError for evaluating:', self.np_expr,
            print 'y intercept not calculated'
        # min/max
        f1 = diff(self.expr, 'x')
        try:
            x = np.array(solve(f1, 'x'))
            x2 = solve(f1, 'x')
            try:
                y = eval(self.np_expr)
                for i in range(0,len(x)):
                    self.poi.append(POI(x[i], y[i], 3))
            # throws error with periodic functions
            except AttributeError:
                print 'AttributeError for evaluating:',self.np_expr,
                print 'min/max values not calculated'
        except NotImplementedError:
            print 'NotImplementedError for solving 1st deriv. of',self.expr,
            print 'min/max values not calculated'
            

    def __init__(self, expr, xylimits):
        # the number of points to calculate within the graph using the
        # function
        self.resolution = 1000
        
        self.expr = self._get_expr(expr)
        self.visible = True

        # expression as used by numpy
        self.np_expr = self._get_np_expr(self.expr)
        # FIXME: mathtex expr should be in LaTeX format
        self.mathtex_expr = self._get_mathtex_expr(self.expr)

        self.valid = self.update_graph_points(xylimits)
        self.poi = []
        if self.valid:
            self.calc_poi()

    def __call__(self, val):
        print val
        for v in val:
            print v



