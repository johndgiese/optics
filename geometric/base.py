class Ray(object):

    def __init__(self, x, th, z=0, a=1):
        self.x = x
        self.th = th
        self.z = z
        self.a = a

    def save(self):
        pass


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

    def propagate(self, ray):
        for obj in self.setup:
            if isinstance(obj, Detector):
                obj.detect(ray)
            if isinstance(obj, OpticalElement):
                obj.propagate(ray)

    def post_process(self):
        for d in self.detectors:
            d.post_process()

    def report(self):
        report = {}
        for d in self.detectors:
            report[d.name] = d.report()
        return report

    def run(self):
        for ray in self.source:
            self.propagate(ray)
        self.post_process()
        return self.report()
