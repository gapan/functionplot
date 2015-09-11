
About
=====

**Functionplot** is an application that plots mathematical functions of
one variable, that is, functions of the form *y=f(x)*.

What sets this apart from other similar function plotting applications,
is that the user doesn't have to zoom in/out or move the graph around to
find its optimal placement. This is calculated according to the *points
of interest* of the functions that are entered. These include:

* Axes intercepts
* Local extrema
* Inflection points
* Discontinuities
* Horizontal asymptotes
* Points where the slope of the function is 45 or -45 degrees
* Function intersections, if multiple functions are entered at the same time

In addition, the plotting algorithm that is used is really good. It can cope
with functions that are very hard to plot and with which most other
plotting applications fail miserably. The graphs that are produced are
of very high quality.


Dependencies
============

In order to run **functionplot**, you will need to have installed:
* Python 2.7
* matplotlib >= 1.3.1
* sympy >= 0.7.6
* numpy >= 1.9.1
* GTK+2 2.24.x
* PyGTK >= 2.24.0
* pygobject >= 2.28.x

Older versions of these libraries may also work, but haven't been
tested.
