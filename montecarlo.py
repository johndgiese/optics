"""Library for creating simple 2D Ray-Optics Monte-Carlo simulations."""

import math
import numpy as np

import helpers
reload(helpers)

class Ray(object):

    def __init__(self, x, th, a=1):
        self.x = x
        self.th = th
        self.a = a


class Source(object):

    def __iter__(self):
        raise NotImplementedError


class OpticalElement(object):

    def propagate(self, ray):
        raise NotImplementedError


class Detector(object):

    def __init__(self, name, *args, **kwargs):
        self.name = name

    def detect(self, ray):
        raise NotImplementedError

    def post_process(self):
        pass

    def report(self):
        raise NotImplementedError


class Simulation(object):

    def __init__(self, source, setup):
        self.source = source
        self.setup = setup
        self.detectors = [obj for obj in setup if isinstance(obj, Detector)]

    def propagate(self, ray):
        for obj in self.setup:
            if isinstance(obj, Detector):
                obj.detect(ray)
            elif isinstance(obj, OpticalElement):
                obj.propagate(ray)

    def post_process(self):
        for d in self.detectors:
            d.post_process()

    def report(self):
        report = {}
        for d in self.detectors:
            report[d.name] = d.report()
        return report

    def run(self):
        for ray in self.source:
            self.propagate(ray)
        self.post_process()
        return self.report()


class Space(OpticalElement):

    def __init__(self, distance):
        self.distance = distance

    def propagate(self, ray):
        ray.x = ray.x + math.tan(ray.th)*self.distance


class ParaxialSpace(OpticalElement):

    def __init__(self, distance):
        self.distance = distance

    def propagate(self, ray):
        ray.x = ray.x + ray.th*self.distance


class ParaxialLens(OpticalElement):

    def __init__(self, f):
        self.f = f

    def propagate(self, ray):
        ray.th = ray.th - ray.x/self.f


class Aperture(OpticalElement):

    def __init__(self, *args):
        if len(args) == 1:
            radius = args[0]
            self.left = -radius
            self.right = radius
        else:
            self.left = args[0]
            self.right = args[1]

    def propagate(self, ray):
        if ray.x < self.left or ray.x > self.right:
            ray.a = 0


class RandomSource(Source):

    def __init__(self, num_rays, x_dist, th_dist, a_dist=None):
        self.num_rays = num_rays
        self.x_dist = x_dist
        self.th_dist = th_dist
        if a_dist:
            self.a_dist = a_dist
        else:
            self.a_dist = lambda: 1

        self.count = 0

    def next(self):
        if self.count >= self.num_rays:
            raise StopIteration()

        self.count += 1

        x = self.x_dist()
        th = self.th_dist()
        a = self.a_dist()
        return Ray(x, th, a)

    def __iter__(self):
        return self


class PositionHistogram(Detector):

    def __init__(self, name, x_bins):
        self.name = name
        self.x_bins = np.array(x_bins)
        self.data = np.zeros(len(self.x_bins) + 1)

    def detect(self, ray):
        x_bin = helpers.digitize(ray.x, self.x_bins)
        self.data[x_bin] += ray.a

    def report(self):
        report = {}
        report['x_bins'] = self.x_bins
        report['data'] = self.data
        return report


class PositionAngleHistogram(Detector):

    def __init__(self, name, x_bins, th_bins=100):
        self.name = name
        self.x_bins = np.array(x_bins)
        if type(th_bins) == int:
            self.th_bins = np.linspace(-math.pi/2.0, math.pi/2.0, th_bins)
        else:
            self.th_bins = np.array(th_bins)
        self.data= np.zeros([len(self.x_bins) + 1, len(self.th_bins) + 1])

    def detect(self, ray):
        x_bin = helpers.digitize(ray.x, self.x_bins)
        th_bin = helpers.digitize(ray.th, self.th_bins)
        self.data[x_bin, th_bin] += ray.a

    def report(self):
        report = {}
        report['x_bins'] = self.x_bins
        report['th_bins'] = self.th_bins
        report['data'] = self.data
        return report
