
class PropagationException(Exception):
    """
    The base exception class for situations when rays stop propagating.
    """

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
    """
    A class representing a single optical ray.

    This Ray class keeps track of its x-position, z-position, angle, and
    amplitude.  The angle (in radians) is relative to the positive z-axis.

    Instances of this class also keep a list of references to "child rays",
    rays that were created directly from this ray.  For example reflections
    would be considered child rays.

    Ray objects must expose a single method, "save".  This method is called by
    optical elements every time the properties of the ray are changed.  By
    default the save method doesn't do anything, but is exposed to define the
    minimal interface a Ray class must implement.  An example of when the save
    method is necessary is when one wants to trace the path of a ray through a
    system; in order for a ray to remember its history, it must 

    In general, one may be interested in modeling polarization, phase, and
    or other quantities, so more complex ray objects are possible.  This class
    defines the simplest Ray class; other ray models must implement at least
    the quantities represented by this class.
    """

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
    """
    An abstract base class for optical sources.

    Optical sources are iterators that return rays.  The only required argument
    is the Ray class that is used to create rays.
    """

    def __init__(self, **kwargs):
        self.Ray = kwargs.pop('Ray', Ray)

    def __iter__(self):
        return self

    def next(self):
        raise NotImplementedError


class OpticalElement(object):
    """
    An abstract class representing an optical element.

    Common optical elements are lenses, free space, prisms, apertures, etc.

    All optical elements must occupy a fixed segment of the z-axis.  Optical
    elements must implement a method, "dz", which returns its width in meters.
    Note that the width of of an element can be zero (e.g. for a thin lens).
    
    Optical elements must implement a "propagate" method, which takes a
    single ray and propagates the ray through itself.  For example, a "free
    space" optical element would adjust the ray's z-position and x-position.
    
    Note that the ray's save method should be invoked every time the ray's
    properties are adjusted, thus for a lens, the ray's save method will be
    invoked once, but for a volume diffuser where the ray bounces several times
    before passing through the system, the save method may be invoked many
    hundreds of times.
    
    Note that because optical elements are required to fill a fixed segment of
    the z-axis, some useful optical elements aren't possible.  For example, it
    is impossible to have a "Bead" optical element and then place two instances
    of the Bead element side-by-side on the x-axis.  It would be possible to
    create a Bead element and place them side by side along the z-axis, or even
    to create an optical element that has several beads that it keeps track of
    internally.
    """

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

    def handle_absorbed_ray(self, ray):
        pass

    def handle_escaped_ray(self, ray):
        pass

    def handle_trapped_ray(self, ray):
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
