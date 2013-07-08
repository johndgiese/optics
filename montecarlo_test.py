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
        source = montecarlo.RandomSource(num_photons, x_dist, th_dist)
         
        max_photon_spread = math.tan(th_span/2.0)
        bin_edges = linspace(-2*max_photon_spread, 2*max_photon_spread, 100)
        recorder = montecarlo.PositionHistogram(bin_edges)
        recorders = [recorder]

        self.max_photon_spread = max_photon_spread
        self.num_photons = num_photons
        self.simulation = montecarlo.Simulation(source, setup, recorders)

    def test_simple(self):
        simulation = self.simulation
        simulation.run()

        bins = simulation.recorders[0].bins
        num_bins = len(bins)

        self.assertEqual(sum(bins), self.num_photons)

        photons_below = sum(bins[:(num_bins/4 - 1)])
        photons_above = sum(bins[-(num_bins/4 - 1):])
        photons_outside_spread = photons_below + photons_above

        self.assertEqual(photons_outside_spread, 0.0)


class Imaging(unittest.TestCase):
    """
    Test a simple paraxial 4-f imaging setup.
    """

    def setUp(self):
        d = 1
        setup = montecarlo.Setup([
            montecarlo.ParaxialSpace(d),
            montecarlo.ParaxialLens(d),
            montecarlo.ParaxialSpace(2*d),
            montecarlo.ParaxialLens(d),
            montecarlo.ParaxialSpace(d),
        ])

        th_span = math.pi*0.5
        num_photons = 1e4
        th_dist = lambda: rand()*th_span - th_span/2.0
        x_dist = lambda: 0
        source = montecarlo.RandomSource(num_photons, x_dist, th_dist)
         
        pos_bin_edges = linspace(-0.3, 0.3, 101)
        recorder = montecarlo.PositionAngleHistogram(pos_bin_edges)
        recorders = [recorder]

        self.num_photons = num_photons
        self.simulation = montecarlo.Simulation(source, setup, recorders)

    def test_imaging(self):
        simulation = self.simulation
        simulation.run()

        bins = simulation.recorders[0].bins
        num_bins = len(bins)

        central_bin = round(num_bins/2.0)
        photons_in_central_bin = sum(bins[central_bin, :])
        self.assertEqual(photons_in_central_bin, self.num_photons)
        

if __name__ == '__main__':
    unittest.main()
