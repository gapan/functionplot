#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

import unittest
from functionplot.FunctionGraph import FunctionGraph as FG

class TestLimits(unittest.TestCase):

    def setUp(self):
        self.fg = FG()

    def test_default_limits(self):
        self.assertEqual(self.fg.get_limits(), ((-1.2, 1.2), (-1.2, 1.2)))

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
