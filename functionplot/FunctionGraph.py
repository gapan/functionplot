#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

from __future__ import division
from Function import Function
import numpy as np

class FunctionGraph:

    # for now this defaults to setting limits to -1.2 to 1.2
    # it will eventually autoadjust to functions
    def zoom_default(self):
        self.clear()
        # FIXME: set these in the calculated values
        #self.x_min, self.x_max, self.y_min, self.y_max
        self.update_graph_points()

    def zoom_x_in(self):
        self._zoom_x(zoom_out=False)
        self.update_graph_points()
    
    def zoom_x_out(self):
        self._zoom_x(zoom_out=True)
        self.update_graph_points()

    def zoom_y_in(self):
        self._zoom_y(zoom_out=False)
        self.update_graph_points()

    def zoom_y_out(self):
        self._zoom_y(zoom_out=True)
        self.update_graph_points()

    def zoom_in(self):
        self._zoom(zoom_out=False)
        self.update_graph_points()

    def zoom_out(self):
        self._zoom(zoom_out=True)
        self.update_graph_points()

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

    def update_graph_points(self):
        for f in self.functions:
            if f.visible:
                f.update_graph_points([self.x_min, self.x_max,
                    self.y_min, self.y_max])

    def add_function(self, expr):
        xylimits = [self.x_min, self.x_max, self.y_min, self.y_max]
        f = Function(expr, xylimits)
        if f.valid:
            self.functions.append(f)
            return True
        else:
            return False
        self.update_poi()

    def update_poi(self):
        self.poi = []
        for f in self.functions:
            if f.visible:
                for p in f.poi:
                    self.poi.append(p)

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
        self.functions = []
        self.poi = []
        self.clear()
       
        if False:
        #if True:
            xylimits = [self.x_min, self.x_max, self.y_min, self.y_max]
            f = Function('2*sin(pi*x)', xylimits)
            self.functions.append(f)
            f = Function('x^2+x^3-3*x^2', xylimits)
            self.functions.append(f)
            f = Function('sin(pi*x)', xylimits)
            self.functions.append(f)
            f = Function('x**2', xylimits)
            self.functions.append(f)
            f = Function('-x**2+2', xylimits)
            self.functions.append(f)
            f = Function('-x**3', xylimits)
            self.functions.append(f)
            f = Function('x+1', xylimits)
            self.functions.append(f)
            f = Function('-x-2', xylimits)
            self.functions.append(f)



