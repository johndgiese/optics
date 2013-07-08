"""Library for creating simple 2D Ray-Optics Monte-Carlo simulations."""

import math
import numpy as np

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


class BinPosition(Recorder):

    def __init__(self, bin_edges):
        self.pos_bin_edges = np.array(bin_edges)
        self.bins = np.zeros(self.num_pos_bins)

    @property
    def num_pos_bins(self):
        return len(self.pos_bin_edges) + 1

    def record(self, ray):
        pos_bin = self.num_pos_bins - 1
        for i, edge in enumerate(self.pos_bin_edges):
            if ray.x < edge:
                pos_bin = i
                break
        self.bins[pos_bin] += ray.a


class BinPositionAngle(Recorder):

    def __init__(self, pos_bin_edges, ang_bin_edges=100):
        self.pos_bin_edges = pos_bin_edges
        if type(ang_bin_edges) == int:
            ang_bin_edges = np.linspace(-math.pi/2.0, math.pi/2.0, ang_bin_edges)
        self.ang_bin_edges = ang_bin_edges

        self.bins = np.zeros([self.num_pos_bins, self.num_ang_bins])

    @property
    def num_pos_bins(self):
        return len(self.pos_bin_edges) + 1

    @property
    def num_ang_bins(self):
        return len(self.ang_bin_edges) + 1

    def record(self, ray):
        # TODO: optimize
        pos_bin = self.num_pos_bins - 1
        for i, edge in enumerate(self.pos_bin_edges):
            if ray.x < edge:
                pos_bin = i
                break
        ang_bin = self.num_pos_bins - 1
        for i, edge in enumerate(self.ang_bin_edges):
            if ray.th < edge:
                ang_bin = i
                break
        self.bins[pos_bin, ang_bin] += ray.a


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
                
