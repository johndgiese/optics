from base import OpticalElement
import util

class PartionedApertureLens(OpticalElement):

    def __init__(self, f, lens_separation):
        self.f = f
        self.lens_separation = lens_separation

    def propagate(self, ray):
        if ray.x > 0:
            x_effective = ray.x - self.lens_separation
        else:
            x_effective = ray.x + self.lens_separation
        ray.th = ray.th - x_effective/self.f


class DielectricSphere(OpticalElement):

    def __init__(self, radius, center, n_sphere, n_surround=1.0):
        self.radius = radius
        self.center = center
        self.n_sphere = n_sphere
        self.n_surround = n_surround
        self.dz = 2*radius

    def intersect_sphere(self, ray):
        x0 = self.center
        y0 = self.radius
        x1, y1 = util.to_ray_coordinates(ray, x0, y0)
        return abs(x0) < radius

    def enter_sphere(self, ray):
        ray.save()

    def exit_sphere(self, ray):
        ray.save()

    def to_exit_plane(self, ray):
        ray.save()

    def propagate(self, ray):
        z_final = ray.z + self.dz
        if intersect_sphere(self, ray):
            self.enter_sphere(ray)
            self.exit_sphere(ray)
        self.to_exit_plane(ray, z_final)


