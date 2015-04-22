#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

from __future__ import division
import numpy as np
from sympy import simplify, pi
from sympy.functions import Abs
from Function import Function
from PointOfInterest import PointOfInterest as POI
from helpers import fsolve, rfc, remove_outliers, euclidean, BreakLoop
from logging import debug

class FunctionGraph:

    def zoom_default(self):
        self.auto = True
        self.update_graph_points()

    def zoom_x_in(self):
        self.auto = False
        self._zoom(zoom_out=False, zoom_x=True, zoom_y=False)
    
    def zoom_x_out(self):
        self.auto = False
        self._zoom(zoom_out=True, zoom_x=True, zoom_y=False)

    def zoom_y_in(self):
        self.auto = False
        self._zoom(zoom_out=False, zoom_x=False, zoom_y=True)

    def zoom_y_out(self):
        self.auto = False
        self._zoom(zoom_out=True, zoom_x=False, zoom_y=True)

    def zoom_in(self):
        self.auto = False
        self._zoom(zoom_out=False)

    def zoom_out(self):
        self.auto = False
        self._zoom(zoom_out=True)

    def _zoom(self, zoom_out=False, zoom_x=True, zoom_y=True,
            multiplier=1):
        if zoom_out:
            sf = self.scale_factor*multiplier
        else:
            sf = 1.0/(self.scale_factor*multiplier)
        if zoom_x:
            x_center = (self.x_max + self.x_min)/2
            x_range = self.x_max - self.x_min
            new_x_range = x_range*sf
            self.x_min = x_center - new_x_range/2
            self.x_max = x_center + new_x_range/2
        if zoom_y:
            y_center = (self.y_max + self.y_min)/2
            y_range = self.y_max - self.y_min
            new_y_range = y_range*sf
            self.y_min = y_center - new_y_range/2
            self.y_max = y_center + new_y_range/2
        if self.logscale:
            if self.x_min < 0:
                self.x_min = 0
            if self.y_min < 0:
                self.y_min = 0
        self.update_graph_points()

    def update_graph_points(self):
        for f in self.functions:
            if f.visible:
                f.update_graph_points([self.x_min, self.x_max,
                    self.y_min, self.y_max])

    def add_function(self, expr):
        debug('Adding function: '+expr)
        xylimits = [self.x_min, self.x_max, self.y_min, self.y_max]
        f = Function(expr, xylimits, self.logscale)
        if f.valid:
            self.functions.append(f)
            self.calc_intersections()
            self.update_xylimits()
            return True
        else:
            return False

    def update_xylimits(self):
        if self.auto:
            vertical_asymptotes = False
            horizontal_asymptotes = False
            debug('Calculating xylimits.')
            xl = []
            yl = []
            points = []
            # add function specific POIs
            for f in self.functions:
                if f.visible:
                    for p in f.poi:
                        if self.point_type_enabled[p.point_type]:
                            # don't add vertical or horizontal
                            # asymptotes here
                            if p.point_type < 6 or p.point_type > 7:
                                point = [p.x, p.y]
                                if point not in points:
                                    points.append([p.x, p.y])
            # add graph POIs (function intersections)
            for p in self.poi:
                if p.function[0].visible and p.function[1].visible \
                    and self.point_type_enabled[p.point_type]:
                    point = [p.x, p.y]
                    if point not in points:
                        points.append([p.x, p.y])
            # add default POIs (origin (0,0) etc)
            for p in self.poi_defaults:
                if self.point_type_enabled[p.point_type]:
                    point = [p.x, p.y]
                    if point not in points:
                        points.append([p.x, p.y])
            # asymptotes
            # we need a trick to put asymptotes far away, but also
            # show them on the x axis. So, if there are any
            # asymptotes, we increase the size of the respective
            # axis 2 times.
            for f in self.functions:
                if f.visible:
                    for p in f.poi:
                        # vertical asymptotes
                        if p.point_type == 6:
                            if self.point_type_enabled[p.point_type]:
                                vertical_asymptotes = True
                                point = [p.x, 0]
                                if point not in points:
                                    points.append([p.x, 0])
                        # horizontal asymptotes
                        elif p.point_type == 7:
                            if self.point_type_enabled[p.point_type]:
                                horizontal_asymptotes = True
                                point = [0, p.y]
                                if point not in points:
                                    points.append([p.x, 0])
            # gather everything together
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
            # asymptotes. Increase the axis size in case any are
            # found
            if vertical_asymptotes:
                y_min = y_min - y_range
                y_max = y_max + y_range
            if horizontal_asymptotes:
                x_min = x_min - x_range
                x_max = x_max + x_range
            # take care of edge cases, where all poi in an axis have
            # the same coordinate.
            if x_min == x_max:
                x_min = x_min-1
                x_max = x_min+1
            if y_min == y_max:
                y_min = y_min-1
                y_max = y_min+1
            # find the max period of all functions involved and check
            # if at least 2 periods are shown
            periods = []
            for f in self.functions:
                if f.periodic:
                    periods.append(f.period)
            if len(periods) > 0:
                max_period = float(max(periods))
                x_range = x_max - x_min
                x_middle = (x_max - x_min)/2
                if x_range < 2*max_period:
                    x_min = float(x_middle - 1.2*max_period)
                    x_max = float(x_middle + 1.2*max_period)
            debug('Setting X limits to '+\
                    str(x_min)+' and '+str(x_max))
            debug('Setting Y limits to '+\
                    str(y_min)+' and '+str(y_max))
            self.x_min = x_min
            self.x_max = x_max
            self.y_min = y_min
            self.y_max = y_max
            # zoom out twice, gives better output
            self._zoom(zoom_out=True, zoom_x=True, zoom_y=True, multiplier=2)
        if self.logscale:
            if self.x_min < 0:
                self.x_min = 0
                self.x_max = 100*self.x_max
            if self.y_min < 0:
                self.y_min = 0
                self.y_max = 100*self.y_max

    def grouped_poi(self, points):
        # max distance for grouped points is graph diagonal size /100
        dmax = euclidean(POI(self.x_min,self.y_min),
                POI(self.x_max,self.y_max))/100
        # temp list of grouped points. Every group is a sublist
        c=[]
        for i in points:
            c.append([i])
        done = False
        while not done:
            try:
                l = len(c)
                for i in xrange(0,l-1):
                    for j in xrange(1,l):
                        if i != j:
                            for m in c[i]:
                                for n in c[j]:
                                    if euclidean(m,n) < dmax:
                                        for k in c[j]:
                                            c[i].append(k)
                                        c.pop(j)
                                        raise BreakLoop
                done = True
            except BreakLoop:
                pass
        # final list of grouped points. For groups, return a single
        # point with coordinates the mean values of the coordinates
        # of the points that are grouped
        grouped = []
        for i in c:
            l = len(i)
            if l == 1:
                grouped.append(i[0])
            else:
                x_sum = 0
                y_sum = 0
                for j in i:
                    x_sum+=j.x
                    y_sum+=j.y
                x = x_sum/l
                y = y_sum/l
                grouped.append(POI(x,y,9,size=l))
        return grouped

    def calc_intersections(self):
        # we're using plist as a helper list for checking if
        # a point is already in
        plist = []
        self.poi = []
        l = len(self.functions)
        for i in xrange(0, l-1):
            f = self.functions[i]
            for j in xrange(i+1, l):
                g = self.functions[j]
                debug('Looking for intersections between "'+f.expr+\
                        '" and "'+g.expr+'".')
                #FIXME: maybe I can do away with simplify here?
                d = str(f.simp_expr)+'-('+str(g.simp_expr)+')'
                try:
                    ds = simplify(d)
                    x = fsolve(ds)
                    if x is None:
                        x = []
                    for i in x:
                        y = f.simp_expr.subs('x', i)
                        xc = rfc(i)
                        yc = rfc(y)
                        if xc is not None and yc is not None:
                            pc = [xc, yc]
                            p = POI(xc, yc, 1, function=[f,g])
                            if pc not in plist:
                                plist.append(pc)
                                self.poi.append(p)
                                debug('New intersection point: ('+\
                                        str(xc)+','+str(yc)+')')
                except ValueError:
                    debug('ValueError exception. Probably a '+\
                            'bug in sympy.')

    def clear(self):
        self.x_min = -1.2
        self.x_max = 1.2
        self.y_min = -1.2
        self.y_max = 1.2
        self.logscale = False
        self.auto = True

    def new(self):
        self.visible = True
        self.show_legend = True
        self.legend_location = 1 # upper right
        self.show_poi = True
        
        self.outliers = False
        self.grouped = True
        
        self.functions = []
        self.poi = []
        self.poi_defaults = []
        self.poi_defaults.append(POI(0, 0, 0))
        self.poi_defaults.append(POI(0, 1, 0))
        self.poi_defaults.append(POI(0, -1, 0))
        self.poi_defaults.append(POI(1, 0, 0))
        self.poi_defaults.append(POI(-1, 0, 0))
        self.clear()


    def __init__(self):
        self.scale_factor = 1.2
        # we have 8 types of POIs
        self.point_type_enabled = [
                True, # 0: standard axis points
                True, # 1: function intersections
                True, # 2: x intercepts
                True, # 3: y intercept
                True, # 4: local min/max
                True, # 5: inflection points
                True, # 6: vertical asymptotes
                True, # 7: horizontal asymptotes
                True, # 8: slope is 45 or -45 degrees
                True  # 9: grouped POIs
                ]
        self.new()
