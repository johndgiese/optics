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


class OpticalElement(object):

    def propagate(self, ray):
        raise NotImplementedError


class Space(OpticalElement):

    def __init__(self, distance):
        self.distance = distance

    def propagate(self, ray):
        ray.x = ray.x + math.tan(ray.th)*self.distance


class SimpleLens(OpticalElement):

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


class Setup(object):

    def __init__(self, elements):
        self.elements = elements

    def propagate(self, ray):
        for el in self.elements:
            el.propagate(ray)


class RayBundle(object):

    def __iter__(self):
        raise NotImplementedError


class RayDistribution(RayBundle):

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


class Recorder(object):

    def record(self, ray):
        raise NotImplementedError


class PositionHistogram(Recorder):

    def __init__(self, x_bins):
        self.x_bins = np.array(x_bins)
        self.bins = np.zeros(len(x_bins) + 1)

    def record(self, ray):
        x_bin = helpers.digitize(ray.x, self.x_bins)
        self.bins[x_bin] += ray.a


class PositionAngleHistogram(Recorder):

    def __init__(self, x_bins, th_bins=100):
        self.x_bins = np.array(x_bins)
        if type(th_bins) == int:
            self.th_bins = np.linspace(-math.pi/2.0, math.pi/2.0, th_bins)
        else:
            self.th_bins = np.array(th_bins)
        self.bins = np.zeros([len(self.x_bins) + 1, len(self.th_bins) + 1])

    def record(self, ray):
        x_bin = helpers.digitize(ray.x, self.x_bins)
        th_bin = helpers.digitize(ray.th, self.th_bins)
        self.bins[x_bin, th_bin] += ray.a


class Simulation(object):

    def __init__(self, setup, ray_bundle, recorders):
        self.setup = setup
        self.ray_bundle = ray_bundle
        self.recorders = recorders

    def record_all(self, ray):
        for r in self.recorders:
            r.record(ray)

    def run(self):
        for ray in self.ray_bundle:
            self.setup.propagate(ray)
            self.record_all(ray)
                
