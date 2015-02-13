#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

class PointOfInterest:

    def __init__(self, x, y, point_type):
        self.x = x
        self.y = y
        self.point_type = point_type
        self.visible = True
