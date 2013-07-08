import unittest
import math

from pylab import *

import montecarlo
reload(montecarlo)

class SpaceProp(unittest.TestCase):
    """
    Test photons leaving from a small angular spread on the origin, and
    propagating a certain distance.
    """

    def setUp(self):
        d = 1
        elements = [montecarlo.Space(d)]
        setup = montecarlo.Setup(elements)

        th_span = math.pi*0.1
        num_photons = 1e4
        th_dist = lambda: rand()*th_span - th_span/2.0
        x_dist = lambda: 0
        ray_bundle = montecarlo.RayDistribution(num_photons, x_dist, th_dist)
         
        max_photon_spread = math.tan(th_span/2.0)
        bin_edges = linspace(-2*max_photon_spread, 2*max_photon_spread, 100)
        recorder = montecarlo.PositionHistogram(bin_edges)
        recorders = [recorder]

        self.max_photon_spread = max_photon_spread
        self.num_photons = num_photons
        self.simulation = montecarlo.Simulation(setup, ray_bundle, recorders)

    def test_simple(self):
        simulation = self.simulation
        simulation.run()

        bins = simulation.recorders[0].bins
        num_bins = len(bins)

        self.assertEqual(sum(bins), self.num_photons)

        energy_below = sum(bins[:(num_bins/4 - 1)])
        energy_above = sum(bins[-(num_bins/4 - 1):])
        energy_outside_spread = energy_below + energy_above

        self.assertEqual(energy_outside_spread, 0.0)


class Imaging(unittest.TestCase):
    def setUp(self):
        d = 1
        elements = [
            montecarlo.Space(d),
            montecarlo.SimpleLens(d),
            montecarlo.Space(2*d),
            montecarlo.SimpleLens(d),
            montecarlo.Space(d),
        ]
        setup = montecarlo.Setup(elements)

        th_span = math.pi*0.5
        num_photons = 1e4
        th_dist = lambda: rand()*th_span - th_span/2.0
        x_dist = lambda: 0
        ray_bundle = montecarlo.RayDistribution(num_photons, x_dist, th_dist)
         
        pos_bin_edges = linspace(-0.3, 0.3, 100)
        recorder = montecarlo.PositionAngleHistogram(pos_bin_edges)
        recorders = [recorder]

        self.num_photons = num_photons
        self.simulation = montecarlo.Simulation(setup, ray_bundle, recorders)

    def test_imaging(self):
        simulation = self.simulation
        simulation.run()

        bins = simulation.recorders[0].bins
        num_bins = len(bins)

        imshow(bins)
        show()
        

if __name__ == '__main__':
    unittest.main()
