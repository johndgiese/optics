
class PropagationException(Exception):

    def __init__(self, ray):
        Exception.__init__(self)
        self.ray = ray


class AbsorbedRay(PropagationException):
    """
    A ray is absorbed, and no longer propagates.

    For example, a ray is blocked by an aperture.
    """


class EscapedRay(PropagationException):
    """
    A ray escapes an optical component out to the side.

    For example, a ray traveling on the z-axis is reflected at 45 degrees, and
    propagates indefinitely to the side while never reaching the next component
    in the simulation.
    """


class TrappedRay(PropagationException):
    """
    A ray is trapped in an optical component.

    For example, a ray is trapped in a resonator for longer than the simulation
    wants to handle.
    """


class Ray(object):

    def __init__(self, x, th, a=1.0, z=0.0):
        self.x = x
        self.th = th
        self.z = z
        self.a = a
        self.children = []

    def save(self):
        pass

    def __unicode__(self):
        return u'x: {}, z: {}, theta: {}, amplitude: {}'.format(
                self.x, self.z, self.th, self.a )


class Source(object):

    def __init__(self, Ray=Ray):
        self.Ray = Ray

    def __iter__(self):
        return self

    def next(self):
        raise NotImplementedError


class OpticalElement(object):

    def propagate(self, ray):
        raise NotImplementedError

    def dz(self):
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

    @property
    def detectors(self):
        return [obj for obj in self.setup if isinstance(obj, Detector)]

    @property
    def optical_elements(self):
        return [obj for obj in self.setup if isinstance(obj, OpticalElement)]

    def pre_process(self):
        # calculate and attach absolute z-positions to optical elements
        z = 0
        for oe in self.optical_elements:
            oe.z_front = z
            z += oe.dz()
            oe.z_back = z

    def propagate(self, ray):
        try:
            for obj in self.setup:
                if isinstance(obj, Detector):
                    obj.detect(ray)
                if isinstance(obj, OpticalElement):
                    obj.propagate(ray)
        except AbsorbedRay as e:
            self.handle_absorbed_ray(e.ray)
        except EscapedRay as e:
            self.handle_escaped_ray(e.ray)
        except TrappedRay as e:
            self.handle_trapped_ray(e.ray)
        except PropagationException as e:
            pass

        for child_ray in ray.children:
            self.propagate(child_ray)

    def handle_absorbed_ray(ray):
        pass

    def handle_escaped_ray(ray):
        pass

    def handle_trapped_ray(ray):
        pass

    def post_process(self):
        for d in self.detectors:
            d.post_process()

    def report(self):
        report = {}
        for d in self.detectors:
            report[d.name] = d.report()
        return report

    def run(self):
        self.pre_process()
        for ray in self.source:
            self.propagate(ray)
        self.post_process()
        return self.report()
