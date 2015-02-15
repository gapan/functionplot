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
        # 0: stantard axis points {(0,0), (0,1), (1,0)}
        # 1: function intercepts
        # 2: x intercept
        # 3: y intercept
        # 4: local min/max
        self.point_type = point_type

