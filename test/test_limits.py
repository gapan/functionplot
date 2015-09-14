#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

import unittest
from functionplot.FunctionGraph import FunctionGraph as FG

class TestLimits(unittest.TestCase):

    def setUp(self):
        self.fg = FG()

    def test_default_limits(self):
        self.assertEqual(self.fg.get_limits(), ((-1.2, 1.2), (-1.2, 1.2)))

    def test_sin(self):
        self.fg.add_function('sin(x)')
        (x_min, x_max), (y_min, y_max) = self.fg.get_limits()
        self.assertTrue(-3 < y_min < -1.5 )
        self.assertTrue(1.5 < y_max < 3)
        # period is 2*pi and at least 2 periods should be shown
        self.assertTrue(12.56 < x_max - x_min < 200)

    def test_cos(self):
        self.fg.add_function('cos(x)')
        (x_min, x_max), (y_min, y_max) = self.fg.get_limits()
        self.assertTrue(-3 < y_min < -1.5 )
        self.assertTrue(1.5 < y_max < 3)
        # period is 2*pi and at least 2 periods should be shown
        self.assertTrue(12.56 < x_max - x_min < 200)

    def test_tan(self):
        self.fg.add_function('tan(x)')
        (x_min, x_max), (y_min, y_max) = self.fg.get_limits()
        self.assertTrue(-10 < y_min < -2 )
        self.assertTrue(2 < y_max < 10)
        # period is 2*pi and at least 2 periods should be shown
        self.assertTrue(6.2 < x_max - x_min < 60)

    def test_cot(self):
        self.fg.add_function('cot(x)')
        (x_min, x_max), (y_min, y_max) = self.fg.get_limits()
        self.assertTrue(-10 < y_min < -2 )
        self.assertTrue(2 < y_max < 10)
        # period is 2*pi and at least 2 periods should be shown
        self.assertTrue(6.2 < x_max - x_min < 60)

    def test_sec(self):
        self.fg.add_function('sec(x)')
        (x_min, x_max), (y_min, y_max) = self.fg.get_limits()
        self.assertTrue(-20 < y_min < -8 )
        self.assertTrue(8 < y_max < 20)
        # period is 2*pi and at least 2 periods should be shown
        self.assertTrue(12.56 < x_max - x_min < 80)

    def test_csc(self):
        self.fg.add_function('csc(x)')
        (x_min, x_max), (y_min, y_max) = self.fg.get_limits()
        self.assertTrue(-20 < y_min < -8 )
        self.assertTrue(8 < y_max < 20)
        # period is 2*pi and at least 2 periods should be shown
        self.assertTrue(12.56 < x_max - x_min < 80)

    def test_outlier_y(self):
        '''
        This test should find an outlier in the y axis and not take it into
        account when calculating limits
        '''
        self.fg.add_function('x^2')
        self.fg.add_function('-x^2+1')
        self.fg.add_function('x-1')
        self.fg.add_function('-x+1')
        self.fg.add_function('-20x^2+500')
        (x_min, x_max), (y_min, y_max) = self.fg.get_limits()
        self.assertTrue(y_min < 30)

if __name__ == '__main__':
    unittest.main()
