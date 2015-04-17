#!/usr/bin/env python
# vim:et:sta:sts=4:sw=4:ts=8:tw=79:

# setup.py Install script for simpleconfig.py
# Copyright (C) 2011 George Vlahavas
# E-mail: vlahavas ~ at ~ gmail ~ dot ~ com

# This software is licensed under the terms of the GPLv3 license.

from setuptools import setup, find_packages
 
setup (
    name = "FunctionPlot",
    version = "0.1",
    description="FunctionPlot is an application for plotting math functions",
    long_description="""\
FunctionPlot is an application for plotting 1-variable mathematical
functions on a 2D graph. For every mathematical function it plots, it
calculates respective points of interest and uses those to determine the
optimal position and zoom scale for the graph.""",
    author="George Vlahavas",
    author_email="vlahavas ~ at ~ gmail ~ dot ~ com",
    url="https://github.com/gapan/",
    package_data = {'': ['functionplot.glade', '*.png']},
    data_files = [ ('share/applications', ['desktop/functionplot.desktop']) ],
    packages = find_packages(exclude="test"),
 
    entry_points = {
        'console_scripts': ['functionplot = functionplot.functionplot:main']
                    },
 
    download_url = "https://github.com/gapan/functionplot",
    zip_safe = False
)
