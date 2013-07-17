class Ray(object):

    def __init__(self, x, th, a=1.0, z=0.0):
        self.x = x
        self.th = th
        self.z = z
        self.a = a

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

    def propagate(self, ray):
        for obj in self.setup:
            if isinstance(obj, Detector):
                obj.detect(ray)
            if isinstance(obj, OpticalElement):
                obj.propagate(ray)

    def pre_process(self):
        # calculate and attach absolute z-positions to optical elements
        z = 0
        for oe in self.optical_elements:
            oe.z_front = z
            z += oe.dz()
            oe.z_back = z

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
