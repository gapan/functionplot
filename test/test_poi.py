#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

import unittest
from functionplot.FunctionGraph import FunctionGraph as FG

class PoiTest(unittest.TestCase):

    def setUp(self):
        self.fg = FG()

    def assertPoi(self, poi_test, poi_correct):
        '''
        assertPoi checks two lists of PointOfInterest against each other
        '''
        self.assertEqual(len(poi_test), len(poi_correct))
        for p in poi_test:
            self.assertIn(p, poi_correct)

    def assertPoiAtLeast(self, poi_test, poi_correct):
        '''
        assertPoiAtLeast checks if at least all the points in the correct list
        are part of the test list. Helps with functions that have infinite
        POIs
        '''
        self.assertTrue(len(poi_test) >= len(poi_correct))
        for p in poi_correct:
            self.assertIn(p, poi_test)

    def assertPoiAtLeastApprox(self, poi_test, poi_correct,
                               round_x=2, round_y=2):
        '''
        assertPoiAtLeastApprox checks if at least all the points in the correct
        list are part of the test list, after the points in the test list have
        been rounded to the specified accuracy
        '''
        poi_test = tuple(((round(p[0], round_x), round(p[1], round_y), p[2])
                      for p in poi_test))
        self.assertPoiAtLeast(poi_test, poi_correct)

    def assertPoiApprox(self, poi_test, poi_correct, round_x=2, round_y=2):
        '''
        assertPoiApprox rounds the poi coordinates to the given values and
        compares them to the given (correct) values
        '''
        poi_test = tuple(((round(p[0], round_x), round(p[1], round_y), p[2])
                      for p in poi_test))
        self.assertPoi(poi_test, poi_correct)

    def get_poi(self, fg):
        functions = [f for f in fg.functions]
        poi = [(p.x, p.y, p.point_type) for p in f.poi for f in functions]
        return poi

    def test_x(self):
        self.fg.add_function('x')
        poi = self.get_poi(self.fg)
        self.assertPoi(poi, [(0, 0, 2), (0, 0, 3)])

    def test_x_square(self):
        self.fg.add_function('x^2')
        poi = self.get_poi(self.fg)
        correct = [(0, 0, 2), (0, 0, 4), (0.5, 0.25, 8), (-0.5, 0.25, 8),
                   (0, 0, 3)]
        self.assertPoi(poi, correct)

    def test_x_cubed(self):
        self.fg.add_function('x^2')
        poi = self.get_poi(self.fg)
        correct = [(0, 0, 2), (0, 0, 4), (0.5, 0.25, 8), (-0.5, 0.25, 8),
                   (0, 0, 3)]
        self.assertPoi(poi, correct)

    def test_poly(self):
        self.fg.add_function('x^4-3x^2+5x-3')
        poi = self.get_poi(self.fg)
        correct = [(1, 0, 2), (-2.37, 0, 2), (-1.52, -12.19, 4),
                   (-0.71, -7.79, 5), (0.71, -0.71, 5),
                   (-1.48, -12.17, 8), (-1.57, -12.17, 8), (0, -3, 3)]
        self.assertPoiApprox(poi, correct)

    def test_abs(self):
        self.fg.add_function('abs(x+2)-4')
        poi = self.get_poi(self.fg)
        correct = [(-6, 0, 2), (2, 0, 2), (-2, -4, 4), (0, -2, 3)]
        self.assertPoiApprox(poi, correct)

    def test_rational1(self):
        self.fg.add_function('1/(x+2)')
        poi = self.get_poi(self.fg)
        correct = [(-2, 0, 6), (0, 0, 7), (-3, -1, 8), (-1, 1, 8), (0, 0.5, 3)]
        self.assertPoi(poi, correct)

    def test_rational2(self):
        self.fg.add_function('4/(x^2+1)')
        poi = self.get_poi(self.fg)
        correct = [(0, 4, 4), (-0.5774, 3, 5), (0.5774, 3, 5),
                   (0, 0, 7), (-1.6085, 1.1151, 8), (-0.1292, 3.9343, 8),
                   (0.1292, 3.9343, 8), (1.6085, 1.1151, 8), (0, 4, 3)]
        self.assertPoiApprox(poi, correct, round_x=4, round_y=4)

    def test_power1(self):
        self.fg.add_function('2^(x+1)')
        poi = self.get_poi(self.fg)
        correct = [(0, 0, 7), (-0.47, 1.44, 8), (0, 2, 3)]
        self.assertPoiApprox(poi, correct)

    def test_power2(self):
        self.fg.add_function('x^x')
        poi = self.get_poi(self.fg)
        correct = [(0.3679, 0.6922, 4), (0.106, 0.7883, 8),
                   (1.0021, 1.0021, 8), (0, 1, 3)]
        self.assertPoiApprox(poi, correct, round_x=4, round_y=4)

    def test_cos(self):
        self.fg.add_function('cos(x)')
        poi = self.get_poi(self.fg)
        correct = [(1.57, 0, 2), (4.71, 0, 2), (0, 1, 4), (3.14, -1, 4),
                   (1.57, 0, 5), (4.71, 0, 5), (-1.57, 0, 8),
                   (4.71, 0, 8), (1.57, 0, 8), (0, 1, 3)]
        self.assertPoiAtLeastApprox(poi, correct)

    def test_intersections(self):
        self.fg.add_function('2x+5')
        self.fg.add_function('-(x-1)^3-2')
        self.fg.add_function('(x-2)^2-6')
        poi = self.get_poi(self.fg)
        correct = [(-2.5, 0, 2), (0, 5.0, 3), (-0.26, 0, 2),
                   (1, -2, 4), (1, -2, 5), (0.42, -1.81, 8),
                   (1.58, -2.19, 8), (0, -1, 3), (4.45, 0, 2), (-0.45, 0, 2),
                   (2, -6, 4), (2.5, -5.75, 8), (1.5, -5.75, 8), (0, -2, 3),
                   (-0.76, 3.48, 1), (-1, 3, 1), (7, 19, 1), (2.55, -5.7, 1)]
        self.assertPoiApprox(poi, correct)
