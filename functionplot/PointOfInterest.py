#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

class PointOfInterest:

    def __init__(self, x, y, point_type):
        #FIXME: not sure if we have to set visible for each point.
        # Probably it could only be set for each point_type
        self.visible = True
        self.x = x
        self.y = y

        # POI types:
        # 0: function 
        # 1: x intercept
        # 2: y intercept
        # 3: local min/max
        self.point_type = point_type

