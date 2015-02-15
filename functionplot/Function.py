#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

from __future__ import division
import numpy as np
from sympy import diff, solve, simplify
from PointOfInterest import PointOfInterest as POI
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
        expr = expr.replace('log2(', 'np.log2(')
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
        if 'log(' in expr or 'ln(' in expr or 'loge(' in expr or \
                'log2' in expr:
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
        try:
            x = solve(expr, 'x')
            for i in x:
                try:
                    xc = float(i)
                    self.poi.append(POI(xc, 0, 2))
                    debug('Added x intercept at ('+str(xc)+',0)')
                # TypeError is thrown for complex solutions during casting
                # to float. We only want real solutions.
                except TypeError:
                    debug(str(i)+' is probably a complex solution for "'+\
                            str(expr)+'". Skipping.')
        except NotImplementedError:
            debug('NotImplementedError for solving "'+str(expr)+\
                    '". x intercepts not calculated')
        #
        # y intercept
        #
        y = expr.subs('x', 0)
        try:
            yc = float(y)
            self.poi.append(POI(0, yc, 3))
            debug('Added y intercept at (0,'+str(yc)+')')
        except TypeError:
            debug(str(y)+' is probably a complex y intercept for "'+\
                    str(expr)+'". Not adding y intercept.')
        #
        # min/max
        #
        f1 = diff(expr, 'x')
        try:
            x = solve(f1, 'x')
            for i in x:
                y = expr.subs('x', i)
                try:
                    xc = float(i)
                    xy = float(y)
                    self.poi.append(POI(xc, xy, 4))
                    debug('Added local min/max at ('+str(xc)+','+str(yc)+')')
                # TypeError is thrown for complex solutions during casting
                # to float. We only want real solutions.
                except TypeError:
                    debug(str(i)+' is probably a complex solution for '+\
                            '1st derivative of "'+\
                            str(expr)+'". Skipping.')
        except NotImplementedError:
            debug('NotImplementedError for solving 1st derivative of "'+\
                    str(expr)+'" = "'+str(f1)+\
                    '". Min/max points not calculated.')

        # throws error with periodic functions
        except AttributeError:
            debug('AttributeError for evaluating: '+str(expr)+\
                '. Function is probably periodic. '+\
                ' Min/max values not calculated')

        #
        # inflection points
        #
        f2 = diff(f1, 'x')
        try:
            x = solve(f2, 'x')
            for i in x:
                y = expr.subs('x', i)
                try:
                    xc = float(i)
                    xy = float(y)
                    self.poi.append(POI(xc, xy, 5))
                    debug('Added inflection point at ('+str(xc)+','+\
                            str(yc)+')')
                # TypeError is thrown for complex solutions during casting
                # to float. We only want real solutions.
                except TypeError:
                    debug(str(i)+' is probably a complex solution for '+\
                            '2nd derivative of "'+\
                            str(expr)+'". Skipping.')
        except NotImplementedError:
            debug('NotImplementedError for solving 2nd derivative of "'+\
                    str(expr)+'" = "'+str(f1)+\
                    '". Inflection points not calculated.')

        # throws error with periodic functions
        except AttributeError:
            debug('AttributeError for evaluating 2nd derivative of "'+\
                    str(expr)+'". Function is probably periodic. '+\
                    'Inflection values not calculated')


    def calc_poi2(self):
        expr = self.simp_expr
        np_expr = self.np_expr
        
        self.poi = []
        #
        # x intercepts
        #
        try:
            x = solve(expr, 'x')
            for i in x:
                try:
                    xc = float(i)
                    self.poi.append(POI(xc, 0, 2))
                # TypeError is thrown for complex solutions during casting
                # to float. We only want real solutions.
                except TypeError:
                    debug(str(i)+' is probably a complex solution for '+\
                            expr+'. Skipping.')
        except NotImplementedError:
            debug('NotImplementedError for solving '+self.expr+\
                    '. x intercepts not calculated')
        #
        # y intercept
        #
        #FIXME: I think the next is superfluous. There is only one y intercept
        x = 0
        try:
            y = eval(np_expr)
            try:
                xc = float(x)
                yc = float(y)
                self.poi.append(POI(xc, yc, 3))
                # TypeError is thrown for complex solutions during casting
                # to float. We only want real solutions.
            except TypeError:
                debug(str(x)+' and/or '+str(y)+\
                        ' are probably complex solutions for '+\
                        expr+'. Skipping')
        except ZeroDivisionError:
            debug('ZeroDivisionError for evaluating '+self.expr+\
                    '. y intercept not calculated.')
        #
        # min/max
        #
        f1 = diff(expr, 'x')
        try:
            x = np.array(solve(f1, 'x'), dtype=float)
            x2 = solve(f1, 'x')
            try:
                y = eval(np_expr)
                for i in range(0,len(x)):
                    try:
                        xc = float(x[i])
                        yc = float(y[i])
                        self.poi.append(POI(xc, yc, 4))
                    # TypeError is thrown for complex solutions during casting
                    # to float. We only want real solutions.
                    except TypeError:
                        debug('('+str(x[i])+','+str(y[i])+')'\
                                ' is probably a complex solution for '+\
                                expr+'. Min/max not calculated.')
            # throws error with periodic functions
            except AttributeError:
                debug('AttributeError for evaluating: '+self.np_expr+\
                    '. Function is probably periodic. '+\
                    ' Min/max values not calculated')
        except NotImplementedError:
            debug('NotImplementedError for soliving 1st derivative of '+\
                    self.expr+'. Min/max values not calculated')
        #
        # inflection points
        #
        f2 = diff(f1, 'x')

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

