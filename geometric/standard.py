import math

import numpy as np

from base import *
import util

class Trace(Ray):

    def __init__(self, *args, **kwargs):
        super(Trace, self).__init__(*args, **kwargs)
        self.locations = [(self.x, self.z)]

    def save(self):
        self.locations.append((self.x, self.z))


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
        if f == 0:
            raise ValueError("Can not have a focal length of zero.")
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
            ray.save()
            raise AbsorbedRay(ray)


    def dz(self):
        return 0.0


class ConcreteSource(Source):

    def __init__(self, x, th, a=None, **kwargs):
        super(ConcreteSource, self).__init__(**kwargs)
        self.x = x
        self.th = th
        if a:
            self.a = a
        else:
            self.a = np.ones(len(x))

        self.num_rays = len(x) # all inputs assumed same length
        self.count = 0

    def next(self):
        if self.count >= self.num_rays:
            raise StopIteration()

        x = self.x[self.count]
        th = self.th[self.count]
        a = self.a[self.count]

        ray = self.Ray(x, th, a=a)

        self.count += 1
        return ray


class SingleRaySource(ConcreteSource):

    def __init__(self, x, th, a=1.0, **kwargs):
        super(SingleRaySource, self).__init__([x], [th], [a], **kwargs)
    

class AngleSpanSource(Source):
    
    def __init__(self, num_rays, **kwargs):
        super(AngleSpanSource, self).__init__(**kwargs)
        self.num_rays = num_rays
        self.x = kwargs.pop('x', 0)
        self.th_span = kwargs.pop('th_span', math.pi/2)

        self.dth = self.th_span/(self.num_rays - 1)
        self.count = 0

    def next(self):
        if self.count >= self.num_rays:
            raise StopIteration()

        x = self.x
        th = self.count*self.dth - self.th_span/2.0
        ray = self.Ray(x, th)

        self.count += 1
        return ray


class PositionSpanSource(Source):
    
    def __init__(self, num_rays, x_start, x_stop, **kwargs):
        super(PositionSpanSource, self).__init__(**kwargs)
        self.num_rays = num_rays
        self.th = kwargs.pop('th', 0)
        self.x_start = float(x_start)
        self.x_stop = float(x_stop)

        self.dx = abs(self.x_stop - self.x_start)/(self.num_rays - 1)
        self.count = 0

    def next(self):
        if self.count >= self.num_rays:
            raise StopIteration()

        x = self.count*self.dx + self.x_start
        th = self.th
        ray = self.Ray(x, th)

        self.count += 1
        return ray 


class RandomSource(Source):

    def __init__(self, num_rays, distribution, **kwargs):
        super(RandomSource, self).__init__(**kwargs)
        self.num_rays = num_rays
        self.distribution = distribution
        self.count = 0

    def next(self):
        if self.count >= self.num_rays:
            raise StopIteration()

        x, th = self.distribution()
        ray = self.Ray(x, th)

        self.count += 1
        return ray


class RayDetector(Detector):

    def __init__(self, name):
        self.name = name
        self.rays = []

    def detect(self, ray):
        self.rays.append(ray)

    def report(self):
        report = {}
        report['rays'] = self.rays
        return report


class PositionDetector(Detector):

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


class PositionAngleDetector(Detector):

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
