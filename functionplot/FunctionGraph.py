#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

from __future__ import division
import numpy as np
from sympy import simplify
from Function import Function
from PointOfInterest import PointOfInterest as POI
from helpers import fsolve, rfc, remove_outliers
from logging import debug

class FunctionGraph:

    # for now this defaults to setting limits to -1.2 to 1.2
    # it will eventually autoadjust to functions
    def zoom_default(self):
        self.clear()
        self.auto = True
        self.update_graph_points()

    def zoom_x_in(self):
        self.auto = False
        self._zoom_x(zoom_out=False)
        self.update_graph_points()
    
    def zoom_x_out(self):
        self.auto = False
        self._zoom_x(zoom_out=True)
        self.update_graph_points()

    def zoom_y_in(self):
        self.auto = False
        self._zoom_y(zoom_out=False)
        self.update_graph_points()

    def zoom_y_out(self):
        self.auto = False
        self._zoom_y(zoom_out=True)
        self.update_graph_points()

    def zoom_in(self):
        self.auto = False
        self._zoom(zoom_out=False)

    def zoom_out(self):
        self.auto = False
        self._zoom(zoom_out=True)

    def _zoom_x(self, zoom_out=False):
        if zoom_out:
            sf = self.scale_factor
        else:
            sf = 1.0/self.scale_factor
        x_center = (self.x_max + self.x_min)/2
        x_range = self.x_max - self.x_min
        new_x_range = x_range*sf
        self.x_min = x_center - new_x_range/2
        self.x_max = x_center + new_x_range/2
    
    def _zoom_y(self, zoom_out=False):
        if zoom_out:
            sf = self.scale_factor
        else:
            sf = 1.0/self.scale_factor
        y_center = (self.y_max + self.y_min)/2
        y_range = self.y_max - self.y_min
        new_y_range = y_range*sf
        self.y_min = y_center - new_y_range/2
        self.y_max = y_center + new_y_range/2
   
    def _zoom(self, zoom_out=False):
        self._zoom_x(zoom_out)
        self._zoom_y(zoom_out)
        self.update_graph_points()

    def update_graph_points(self):
        for f in self.functions:
            if f.visible:
                f.update_graph_points([self.x_min, self.x_max,
                    self.y_min, self.y_max])

    def add_function(self, expr):
        debug('Adding function: '+expr)
        xylimits = [self.x_min, self.x_max, self.y_min, self.y_max]
        f = Function(expr, xylimits)
        if f.valid:
            self.functions.append(f)
            self.calc_intercepts()
            self.update_xylimits()
            return True
        else:
            return False

    def update_xylimits(self):
        if self.auto:
            debug('Calculating xylimits.')
            xl = []
            yl = []
            points = []
            # add function specific POIs
            for f in self.functions:
                if f.visible:
                    for p in f.poi:
                        # don't add discontinuity points here
                        if p.point_type < 6:
                            point = [p.x, p.y]
                            if point not in points:
                                points.append([p.x, p.y])
            # add graph POIs (function intercepts)
            for p in self.poi:
                point = [p.x, p.y]
                if point not in points:
                    points.append([p.x, p.y])
            # add default POIs (origin (0,0) etc)
            for p in self.poi_defaults:
                point = [p.x, p.y]
                if point not in points:
                    points.append([p.x, p.y])
            for point in points:
                xl.append(point[0])
                yl.append(point[1])
            # remove outliers
            if not self.outliers:
                # we need at least 7 points to detect outliers
                if len(xl) > 6:
                    debug('Trying to find outliers in X axis.')
                    xl = remove_outliers(xl)
                    debug('Trying to find outliers in Y axis.')
                    yl = remove_outliers(yl)
            x_min = min(xl)
            x_max = max(xl)
            x_range = x_max - x_min
            y_min = min(yl)
            y_max = max(yl)
            y_range = y_max - y_min
            # discontinuity points
            # we need a trick to put discontinuity points far away, but also
            # show them on the x axis. So, if there are any discontinuity
            # points, we increase the size of the y axis 2 times.
            discontinuities = False
            for f in self.functions:
                if f.visible:
                    for p in f.poi:
                        if p.point_type == 6:
                            y_min = y_min - y_range
                            y_max = y_max + y_range
                            #point = [p.x, p.y]
                            #if point not in points:
                            #    points.append([p.x, p.y])
            # take care of edge cases, where all poi in an axis have the same
            # coordinate.
            if x_min == x_max:
                x_min = x_min-1
                x_max = x_min+1
            if y_min == y_max:
                y_min = y_min-1
                y_max = y_min+1
            debug('Setting X limits to '+str(x_min)+' and '+str(x_max))
            debug('Setting Y limits to '+str(y_min)+' and '+str(y_max))
            self.x_min = x_min
            self.x_max = x_max
            self.y_min = y_min
            self.y_max = y_max
            # zoom out twice, gives better output
            self._zoom(zoom_out=True)
            self._zoom(zoom_out=True)

    def calc_intercepts(self):
        # we're using plist as a helper list for checking if
        # a point is already in
        plist = []
        self.poi = []
        l = len(self.functions)
        for i in range(0, l-1):
            f = self.functions[i]
            for j in range(i+1, l):
                g = self.functions[j]
                debug('Looking for intercepts between "'+f.expr+\
                        '" and "'+g.expr+'".')
                #FIXME: maybe I can do away with simplify here?
                d = str(f.simp_expr)+'-('+str(g.simp_expr)+')'
                ds = simplify(d)
                x = fsolve(ds)
                for i in x:
                    y = f.simp_expr.subs('x', i)
                    xc = rfc(i)
                    yc = rfc(y)
                    if xc is not None and yc is not None:
                        pc = [xc, yc]
                        p = POI(xc, yc, 1)
                        if pc not in plist:
                            plist.append(pc)
                            self.poi.append(p)
                            debug('New intercept point: ('+\
                                    str(xc)+','+str(yc)+')')

    def clear(self):
        self.x_min = -1.2
        self.x_max = 1.2
        self.y_min = -1.2
        self.y_max = 1.2
        self.axis_type = 'linear'
        self.auto = True


    def __init__(self):
        self.scale_factor = 1.2
        self.visible = True
        self.show_legend = True
        
        self.outliers = False
        
        self.functions = []
        self.poi = []
        self.poi_defaults = []
        self.poi_defaults.append(POI(0, 0, 0))
        self.poi_defaults.append(POI(0, 1, 0))
        self.poi_defaults.append(POI(0, -1, 0))
        self.poi_defaults.append(POI(1, 0, 0))
        self.poi_defaults.append(POI(-1, 0, 0))
        self.clear()
