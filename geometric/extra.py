from base import OpticalElement

class PawLens(OpticalElement):

    def __init__(self, f, lens_separation):
        self.f = f
        self.lens_separation = lens_separation

    def propagate(self, ray):
        if ray.x > 0:
            x_effective = ray.x - self.lens_separation
        else:
            x_effective = ray.x + self.lens_separation
        ray.th = ray.th - x_effective/self.f
