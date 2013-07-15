__all__ = ['Trace', 'Space', 'ParaxialSpace', 'ParaxialLens', 'Aperture',
    'AngleSpan', 'RandomSource', 'AllRays', 'PositionHistogram',
    'PositionAngleHistogram']

import math

import numpy as np

from base import *
import util

class Trace(Ray):

    def __init__(self, *args, **kwargs):
        super(Trace, self).__init__(*args, **kwargs)
        self.locations = [(self.x, self.z)]

    def save(self):
        current = (self.x, self.z)
        previous = self.locations[-1]

        if previous != current:
            self.locations.append(current)


class Space(OpticalElement):

    def __init__(self, distance):
        self.distance = distance

    def propagate(self, ray):
        ray.z += self.distance
        ray.x = ray.x + math.tan(ray.th)*self.distance
        ray.save()

    def dz(self):
        return self.distance


class ParaxialSpace(OpticalElement):

    def __init__(self, distance):
        self.distance = distance

    def propagate(self, ray):
        ray.z += self.distance
        ray.x = ray.x + ray.th*self.distance
        ray.save()

    def dz(self):
        return self.distance


class ParaxialLens(OpticalElement):

    def __init__(self, f):
        self.f = f

    def propagate(self, ray):
        ray.th = ray.th - ray.x/self.f
        ray.save()

    def dz(self):
        return 0.0


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
            ray.save()

    def dz(self):
        return 0.0


class AngleSpan(Source):
    
    def __init__(self, num_rays, **kwargs):
        super(AngleSpan, self).__init__(**kwargs)
        self.num_rays = num_rays
        self.x = kwargs.pop('x', 0)
        self.th_span = kwargs.pop('th_span', math.pi/2)

        self.dth = self.th_span/(self.num_rays - 1)
        self.count = 0

    def next(self):
        if self.count >= self.num_rays:
            raise StopIteration()
        self.count += 1

        x = self.x
        th = (self.count - 1)*self.dth - self.th_span/2.0
        return self.Ray(x, th)


class RandomSource(Source):

    def __init__(self, num_rays, distribution, **kwargs):
        super(RandomSource, self).__init__(**kwargs)
        self.num_rays = num_rays
        self.distribution = distribution
        self.count = 0

    def next(self):
        if self.count >= self.num_rays:
            raise StopIteration()
        self.count += 1
        x, th = self.distribution()
        return self.Ray(x, th, 0.0, 1.0)


class AllRays(Detector):

    def __init__(self, name):
        self.name = name
        self.rays = []

    def detect(self, ray):
        self.rays.append(ray)

    def report(self):
        report = {}
        report['rays'] = self.rays
        return report


class PositionHistogram(Detector):

    def __init__(self, name, x_bins):
        self.name = name
        self.x_bins = np.array(x_bins)
        self.data = np.zeros(len(self.x_bins) + 1)

    def detect(self, ray):
        x_bin = util.digitize(ray.x, self.x_bins)
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
        x_bin = util.digitize(ray.x, self.x_bins)
        th_bin = util.digitize(ray.th, self.th_bins)
        self.data[x_bin, th_bin] += ray.a

    def report(self):
        report = {}
        report['x_bins'] = self.x_bins
        report['th_bins'] = self.th_bins
        report['data'] = self.data
        return report
