import unittest
import math
import pdb

from pylab import *

from base import *
from standard import *
from extra import *
from visualization import plot_traces

class SpaceProp(unittest.TestCase):
    """
    Test photons leaving from a small angular spread on the origin, and
    propagating a certain distance.
    """

    def setUp(self):
        th_span = math.pi*0.1
        num_photons = 1e4
        th_dist = lambda: rand()*th_span - th_span/2.0
        x_dist = lambda: 0
        source = RandomSource(num_photons, x_dist, th_dist)
         
        max_photon_spread = math.tan(th_span/2.0)
        bin_edges = linspace(-2*max_photon_spread, 2*max_photon_spread, 100)
        
        d = 1
        setup = [
            Space(d),
            PositionHistogram('camera', bin_edges),
        ]

        self.max_photon_spread = max_photon_spread
        self.num_photons = num_photons
        self.simulation = Simulation(source, setup)

    def test_simple(self):
        simulation = self.simulation
        report = simulation.run()

        data = report['camera']['data']
        num_bins = len(data)

        self.assertEqual(sum(data), self.num_photons)

        photons_below = sum(data[:(num_bins/4 - 1)])
        photons_above = sum(data[-(num_bins/4 - 1):])
        photons_outside_spread = photons_below + photons_above

        self.assertEqual(photons_outside_spread, 0.0)


class Imaging(unittest.TestCase):
    """Test a simple paraxial 4-f imaging setup."""

    def setUp(self):

        th_span = math.pi*0.5
        num_photons = 1e4
        th_dist = lambda: rand()*th_span - th_span/2.0
        x_dist = lambda: 0
        source = RandomSource(num_photons, x_dist, th_dist)
         
        x_bins = linspace(-0.3, 0.3, 101)
        d = 1

        setup = [
            ParaxialSpace(d),
            ParaxialLens(d),
            ParaxialSpace(2*d),
            ParaxialLens(d),
            ParaxialSpace(d),
            PositionAngleHistogram('camera', x_bins)
        ]

        self.num_photons = num_photons
        self.simulation = Simulation(source, setup)

    def test_imaging(self):
        simulation = self.simulation
        report = simulation.run()

        data = report['camera']['data']
        num_bins = data.shape[0]

        central_bin = round(num_bins/2.0)
        photons_in_central_bin = sum(data[central_bin, :])
        self.assertEqual(photons_in_central_bin, self.num_photons)

    def test_tracing(self):
        simulation = self.simulation

        # modify the base setup a bit for this test
        simulation.source = AngleSpan(5, Ray=Trace)
        simulation.setup.append(AllRays('rays'))

        report = simulation.run()
        plot_traces(report['rays']['rays'])
        show()


class DielectricBead(unittest.TestCase):

    def setUp(self):
        th_dist = lambda: rand()*pi - math.pi/2
        x_dist = lambda: rand() - 0.5
        num_photons = 10
        source = RandomSource(num_photons, x_dist, th_dist, Ray=Trace)

        setup = [
            DielectricSphere(1, 0.2, 1.3),
            Space(1),
            AllRays('rays'),
        ]
        
        self.num_photons = num_photons
        self.simulation = Simulation(source, setup)

    def test_tracing(self):
        simulation = self.simulation
        report = simulation.run()

        plot_traces(report['rays']['rays'])
        show()


if __name__ == '__main__':
    unittest.main()
