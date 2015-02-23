#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

from __future__ import division
import numpy as np
from sympy import diff, limit, simplify, latex
from sympy.functions import Abs
from PointOfInterest import PointOfInterest as POI
from helpers import pod, fsolve, rfc
from logging import debug
import re

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
            debug('This looks like a constant function: '+self.np_expr)
            self.constant = True
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
        # implied multiplication
        expr = re.sub('([0-9])([a-z\(])', '\\1*\\2', expr)
        expr = re.sub('([a-z\)])([0-9])', '\\1*\\2', expr)
        expr = re.sub('(pi)([a-z\(])', '\\1*\\2', expr)
        expr = re.sub('([a-z\)])(pi)', '\\1*\\2', expr)
        expr = re.sub('(\))([a-z]\()', '\\1*\\2', expr)
        expr = re.sub('(x)([a-z]\()', '\\1*\\2', expr)
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
        expr = expr.replace('log(', 'np.log(')
        # square root
        expr = expr.replace('sqrt(', 'np.sqrt(')
        # absolute value. For numpy, turn the sympy Abs function to np.abs
        expr = expr.replace('Abs(', 'np.abs(')
        # pi and e
        expr = expr.replace('pi', 'np.pi')
        expr = expr.replace('e', 'np.e')
        # powers
        expr = expr.replace('^', '**')
        return expr
    
    def _simplify_expr(self, expr):
        # sympy.functions.Abs is imported as Abs so we're using it that way
        # with sympy
        expr = expr.replace('abs(', 'Abs(')
        # sympy only supports natural logarithms and log(x) = ln(x). For log
        # base 10, we'll do the convertion manually:
        # log10(x) = ln(x)/ln(10) = ln(x)/2.302585093 = 0.4342944819*ln(x)
        # The number of decimal points is restricted to 4, otherwise
        # calculations could take a really long time. 4 is good enough in any
        # case. Example for f(x) = log(x)-1:
        # - 3 decimals: 152ms
        # - 4 decimals: 228ms
        # - 5 decimals: 301ms
        # - 6 decimals: 561ms
        # - 7 decimals: 3.89s
        expr = expr.replace('log(', '0.4343*ln(')
        simp_expr = simplify(expr)
        debug('"'+expr+'" has been simplified to "'+str(simp_expr)+'"')
        return simp_expr


    def _get_mathtex_expr(self, expr):
        # expr is a simplified sympy expression. Creates a LaTeX string from
        # the expression using sympy latex printing.
        e = latex(expr)
        e = e.replace('0.4343 \\log{', '\\log10{')
        e = e.replace('log{', 'ln{')
        e = e.replace('log10', 'log')
        e = e.replace('\\lvert', '|')
        e = e.replace('\\rvert', '|')
        e = '$'+e+'$'
        return e

    def calc_poi(self):
        expr = self.simp_expr
        
        self.poi = []
        #
        # y intercept
        #
        debug('Looking for the y intercept for: '+str(expr))
        y = expr.subs('x', 0)
        yc = rfc(y)
        if yc is not None:
            self.poi.append(POI(0, yc, 3))
            debug('Added y intercept at (0,'+str(yc)+')')
        if not self.constant:
            #
            # x intercepts
            #
            debug('Looking for x intercepts for: '+str(expr))
            x = fsolve(expr)
            for xc in x:
                self.poi.append(POI(xc, 0, 2))
                debug('Added x intercept at ('+str(xc)+',0)')

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
                    debug('Added inflection point at ('+\
                            str(xc)+','+str(yc)+')')
            #
            # discontinuity points (vertical asymptotes)
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
            # horizontal asymptotes
            #
            #FIXME: implement this
            # if the limit(x->+oo)=a, or limit(x->-oo)=a, then y=a is a
            # horizontal asymptote.
            # sympy: limit(expr, x, oo)
            debug('Looking for horizontal asymptotes for: '+str(expr))
            try:
                lr = limit(expr, 'x', 'oo')
                ll = limit(expr, 'x', '-oo')
                if 'oo' not in str(lr):
                    debug('Found a horizontal asymptote at y='+str(lr)+\
                            ' as x->+oo.')
                    self.poi.append(POI(0, lr, 7))
                if 'oo' not in str(ll):
                    if ll == lr:
                        debug('Same horizontal asymptote as x->-oo.')
                    else:
                        debug('Found a horizontal asymptote at y='+str(ll)+\
                                ' as x->-oo')
                        self.poi.append(POI(0, ll, 7))
            except NotImplementedError:
                debug('NotImplementedError for finding limit of "'+\
                        str(expr)+'"')

    def __init__(self, expr, xylimits):
        # the number of points to calculate within the graph using the
        # function
        self.resolution = 1000
        self.visible = True
        self.constant = False
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
            self.mathtex_expr = self._get_mathtex_expr(self.simp_expr)
            self.calc_poi()

