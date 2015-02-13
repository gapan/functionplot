#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

import numpy as np
from PointOfInterest import PointOfInterest as POI

class Function:
    
    def update_graph_points(self, xylimits):
        x_min, x_max, y_min, y_max = xylimits
        x = np.arange(x_min, x_max, float(x_max-x_min)/self.resolution)
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

    # FIXME: actuall implement this
    def _get_mathtex_expr(self, expr):
        return expr


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



