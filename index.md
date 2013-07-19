---
title: Simulation
---

# Overview

This library provides an extensible python framework for developing optical
simulations using the geometric model of light propagation.  Basic optical
components such as lenses and apertures are included and custom components can
be added simply.

A typical simulation has three types of components
1. Source -- determines the initial position and direction of optical rays entering the system
2. Optical Components -- objects that determine how a ray changes as it propagates through the system (e.g. a lens or free space)
3. Detectors -- objects that record some aspect of a ray as it passes through

Here is an example:

{% highlight python %}
    from optics.geometric import *
        
    source = PositionSpanSource(-1, 1)
    f = 0.5
    setup = [
        ParaxialSpace(f),
        ParaxialLens(f),
        ParaxialSpace(2*f),
        ParaxialLens(f),
        ParaxialSpace(f),
        PositionDetector('camera', -2, 2, 100)
    ]

    simulation = Simulation(source, setup)
    report = simulation.run()
    print(report['camera'])

{% endhighlight %}

Note that you can have multiple detectors interspersed throughout your optical
setup; for example, if you wanted to know the spatial/angular distribution of
rays at the fourier plane you could have modified the setup as follows:

{% highlight python %}
    setup = [
        ParaxialSpace(f),
        ParaxialLens(f),
        ParaxialSpace(f),
        PositionAngleDetector('fourier', -2, 2, 100, 100)
        ParaxialSpace(f),
        ParaxialLens(f),
        ParaxialSpace(f),
        PositionDetector('camera', -2, 2, 100)
    ]
{% endhighlight %}

It is probably clear from the examples, that the library is focused on making
it easy to simulate optical setups, and is not a general purpose ray tracer.
The library makes the following basic assumptions about your setup

* A setup is a linear sequence of optical components, each occupying a portion
  of the z-axis with a well-defined width
* Rays propagate predomantly along the z-axis
