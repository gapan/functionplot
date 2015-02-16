#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

from __future__ import division
import numpy as np
from sympy import diff, simplify
from PointOfInterest import PointOfInterest as POI
from helpers import pod, fsolve, rfc
from logging import debug

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
        try:
            y[y>y_max] = np.inf
            y[y<y_min] = np.inf
        # if f(x)=a, make sure that y is an array with the same size as x and
        # with a constant value.
        except TypeError:
            debug('Probably a constant function: '+self.np_expr)
            l = len(x)
            yarr = np.ndarray([l,])
            yarr[yarr!=y]=y
            y = yarr
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
        # turn greek (unicode) notation to english
        expr = expr.replace('\xce\xb7\xce\xbc(', 'sin(')
        expr = expr.replace('\xcf\x83\xcf\x85\xce\xbd(', 'cos(')
        expr = expr.replace('\xce\xb5\xcf\x86(', 'tan(')
        expr = expr.replace('\xcf\x83\xcf\x86(', 'cot(')
        expr = expr.replace('\xcf\x83\xcf\x84\xce\xb5\xce\xbc(', 'csc(')
        expr = expr.replace('\xcf\x84\xce\xb5\xce\xbc(', 'sec(')
        expr = expr.replace('\xcf\x87', 'x')
        expr = expr.replace('\xcf\x80', 'pi')
        # FIXME: provide for implied multiplication symbol
        # examples: 2x -> 2*x, x(x+1) -> x*(x+1) etc
        return expr

    def _get_np_expr(self, expr):
        # add "np." prefix to trig functions
        expr = expr.replace('sin(', 'np.sin(')
        expr = expr.replace('cos(', 'np.cos(')
        expr = expr.replace('tan(', 'np.tan(')
        expr = expr.replace('cot(', '1/np.tan(') # no cot in numpy
        expr = expr.replace('sec(', '1/np.cos(') # no sec or csc either
        expr = expr.replace('csc(', '1/np.sin(')
        # correct log functions
        expr = expr.replace('log(', 'np.log10(')
        expr = expr.replace('loge(', 'np.log(')
        expr = expr.replace('ln(', 'np.log(')
        # square root
        expr = expr.replace('sqrt(', 'np.sqrt(')
        # absolute value
        expr = expr.replace('abs(', 'np.abs(')
        # pi and e
        expr = expr.replace('pi', 'np.pi')
        expr = expr.replace('e', 'np.e')
        # powers
        expr = expr.replace('^', '**')
        return expr
    
    def _simplify_expr(self, expr):
        # don't simplify if it a log function is included
        if False:
        #if 'log(' in expr or 'ln(' in expr or 'loge(' in expr or \
        #        'log2' in expr:
            debug('"'+expr+'" is a log function. Not simplifying.')
            return expr
        else:
            simp_expr = simplify(expr)
            debug('"'+expr+'" has been simplified to "'+str(simp_expr)+'"')
            return simp_expr


    # FIXME: actually implement this
    # sympy printing to LaTeX can probably do it
    def _get_mathtex_expr(self, expr):
        return expr

    def calc_poi(self):
        expr = self.simp_expr
        
        self.poi = []
        #
        # x intercepts
        #
        debug('Looking for x intercepts for: '+str(expr))
        x = fsolve(expr)
        for xc in x:
            self.poi.append(POI(xc, 0, 2))
            debug('Added x intercept at ('+str(xc)+',0)')
        #
        # y intercept
        #
        debug('Looking for the y intercept for: '+str(expr))
        y = expr.subs('x', 0)
        yc = rfc(y)
        if yc is not None:
            self.poi.append(POI(0, yc, 3))
            debug('Added y intercept at (0,'+str(yc)+')')
        #
        # min/max
        #
        debug('Looking for local min/max for: '+str(expr))
        f1 = diff(expr, 'x')
        x = fsolve(f1)
        for xc in x:
            y = expr.subs('x', xc)
            yc = rfc(y)
            if yc is not None:
                self.poi.append(POI(xc, yc, 4))
                debug('Added local min/max at ('+str(xc)+','+str(yc)+')')
        #
        # inflection points
        #
        debug('Looking for inflection points for: '+str(expr))
        f2 = diff(f1, 'x')
        x = fsolve(f2)
        for xc in x:
            y = expr.subs('x', xc)
            yc = rfc(y)
            if yc is not None:
                self.poi.append(POI(xc, yc, 5))
                debug('Added inflection point at ('+str(xc)+','+str(yc)+')')
        #
        # discontinuity points (vertival asymptotes)
        #
        debug('Looking for discontinuity points for: '+str(expr))
        dp = pod(expr, 'x')
        for i in dp:
            y = expr.subs('x', i)
            xc = rfc(i)
            #yc = float(y) # this returns inf.
            # we'll just put discontinuity points on the x axis
            if xc is not None:
                yc = 0
                self.poi.append(POI(xc, yc, 6))
                debug('Added discontinuity point at ('+str(xc)+','+\
                        str(yc)+')')
        #
        # asymptotes
        #
        #FIXME: implement this

    def __init__(self, expr, xylimits):
        # the number of points to calculate within the graph using the
        # function
        self.resolution = 1000
        self.visible = True
        self.valid = True
        self.expr = self._get_expr(expr)
       
        # simplifying helps with functions like y=x^2/x which is
        # actually just y=x. Doesn't hurt in any case.
        # Also throws an error in case there are syntax problems
        try:
            self.simp_expr = self._simplify_expr(self.expr)
            # expression as used by numpy
            self.np_expr = self._get_np_expr(str(self.simp_expr))
            self.valid = self.update_graph_points(xylimits)
        except:
            self.valid = False
        self.poi = []

        if self.valid:
            # FIXME: mathtex expr should be in LaTeX format
            self.mathtex_expr = self._get_mathtex_expr(self.expr)
            self.calc_poi()

