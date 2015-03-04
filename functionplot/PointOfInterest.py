#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

class PointOfInterest:

    def __init__(self, x, y, point_type):
        self.x = x
        self.y = y

        # POI types:
        # 0: standard axis points {(0,0), (0,1), (1,0)}
        # 1: function intersections
        # 2: x intercept
        # 3: y intercept
        # 4: local min/max
        # 5: inflection points
        # 6: vertical asymptotes
        # 7: horizontal asymptotes

        self.point_type = point_type

