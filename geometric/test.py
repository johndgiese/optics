import unittest
import math
import pdb

from pylab import *

from base import *
from standard import *
from extra import *
from visualization import plot_traces


PLOTTING = False

class SpaceProp(unittest.TestCase):
    """
    Test photons leaving from a small angular spread on the origin, and
    propagating a certain distance.
    """

    def setUp(self):
        th_span = math.pi*0.1
        num_rays = 1e4

        def distribution():
            x = 0
            th = rand()*th_span - th_span/2.0
            return x, th
        source = RandomSource(num_rays, distribution)
         
        max_photon_spread = math.tan(th_span/2.0)
        bin_edges = linspace(-2*max_photon_spread, 2*max_photon_spread, 100)
        
        d = 1
        setup = [
            Space(d),
            PositionDetector('camera', bin_edges),
        ]

        self.max_photon_spread = max_photon_spread
        self.num_rays = num_rays
        self.simulation = Simulation(source, setup)

    def test_simple(self):
        simulation = self.simulation
        report = simulation.run()

        data = report['camera']['data']
        num_bins = len(data)

        self.assertEqual(sum(data), self.num_rays)

        photons_below = sum(data[:(num_bins/4 - 1)])
        photons_above = sum(data[-(num_bins/4 - 1):])
        photons_outside_spread = photons_below + photons_above

        self.assertEqual(photons_outside_spread, 0.0)


class Imaging(unittest.TestCase):
    """Test a simple paraxial 4-f imaging setup."""

    def setUp(self):

        th_span = math.pi*0.5
        num_rays = 1e4
        def distribution():
            x = 0.0
            th = rand()*th_span - th_span/2.0
            return x, th

        source = RandomSource(num_rays, distribution)
         
        x_bins = linspace(-0.3, 0.3, 101)
        d = 1

        setup = [
            ParaxialSpace(d),
            ParaxialLens(d),
            ParaxialSpace(2*d),
            ParaxialLens(d),
            ParaxialSpace(d),
            PositionAngleDetector('camera', x_bins)
        ]

        self.num_rays = num_rays
        self.simulation = Simulation(source, setup)

    def test_imaging(self):
        simulation = self.simulation
        report = simulation.run()

        data = report['camera']['data']
        num_bins = data.shape[0]

        central_bin = round(num_bins/2.0)
        photons_in_central_bin = sum(data[central_bin, :])
        self.assertEqual(photons_in_central_bin, self.num_rays)

    @unittest.skipIf(not PLOTTING, 'not plotting')
    def test_tracing(self):
        simulation = self.simulation

        # modify the base setup a bit for this test
        simulation.source = AngleSpanSource(5, Ray=Trace)
        simulation.setup.append(RayDetector('rays'))

        report = simulation.run()
        plot_traces(report['rays']['rays'])
        show()


@unittest.skip("Not done implimenting")
class BeadTest(unittest.TestCase):

    def setUp(self):
        num_rays = 5

        #th_span = pi*0.8
        #def distribution():
            #x = rand()*2 - 1
            #th = rand()*th_span - th_span/2.0
            #return x, th
        #source = RandomSource(num_rays, distribution, Ray=Trace)
        source = PositionSpanSource(num_rays, -0.9, 0.9, Ray=Trace)

        radius = 1.0
        pre_space = 0.1
        post_space = 0.1


        bead = Bead(radius, 0, 1.3)

        setup = [
            Space(pre_space),
            bead,
            Space(post_space),
            RayDetector('rays'),
        ]
        
        self.num_rays = num_rays
        self.bead = bead
        self.pre_space = pre_space
        self.post_space = post_space
        self.simulation = Simulation(source, setup)

    def plot_bead(self):
        bead = self.bead
        fig = figure()
        ax = gca()
        bead_center = (bead.radius + self.pre_space, bead.x)
        circle = Circle(bead_center, bead.radius, color='b', alpha=0.2)
        gca().add_patch(circle)

    def test_known_ray(self):
        simulation = self.simulation
        bead = self.bead

        offset = bead.radius/2.0
        source = SingleRaySource(offset, 0, Ray=Trace)
        simulation.source = source
        a = bead.radius

        x_i = offset
        z_i = self.pre_space + a - np.sqrt(a**2 - offset**2)

        th_i = atan(x_i/a)
        th_r = atan(bead.n_surround/bead.n_bead*sin(th_i))
        pathlength_in_bead = 2*a*cos(th_r)

        beta = th_i - th_r
        x_e = x_i - pathlength_in_bead*sin(beta)
        z_e = z_i + pathlength_in_bead*cos(beta)

        x_theoretical = array([
            offset, # starting place
            offset, # hit first plane of the bead object
            x_i,    # interset bead
            x_e,    # exit bead
                    # should add the last one here once I calculate it
        ])

        z_theoretical = array([
            0,
            self.pre_space,
            z_i,
            z_e,
        ])

        report = simulation.run()

        locations = report['rays']['rays'][0].locations

        if PLOTTING:
            self.plot_bead()
            plot_traces(report['rays']['rays'])
            plot(z_theoretical, x_theoretical, 'r')
            show()

        self.assertEqual(locations[0], (x_theoretical[0], z_theoretical[0]))
        self.assertEqual(locations[1], (x_theoretical[1], z_theoretical[1]))
        self.assertEqual(locations[2], (x_theoretical[2], z_theoretical[2]))
        self.assertEqual(locations[3], (x_theoretical[3], z_theoretical[3]))


    @unittest.skipIf(not PLOTTING, 'not plotting')
    def test_tracing(self):
        simulation = self.simulation
        bead = self.bead
        report = simulation.run()

        self.plot_bead()
        plot_traces(report['rays']['rays'])
        axis('equal')
        show()

class ApertureTest(unittest.TestCase):

    def setUp(self):
        self.centered_aperture = Aperture(1)
        self.offset_aperture = Aperture(1, 2)

    def test_absorption(self):
        ray = Ray(x=0, th=0)

        self.assertRaises(AbsorbedRay, self.offset_aperture.propagate, ray)


if __name__ == '__main__':
    unittest.main()
