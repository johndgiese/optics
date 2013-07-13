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
        x = self.center
        z = self.radius
        x_r, z_r = util.to_ray_coordinates(ray, x, z)
        return abs(x_r) < self.radius

    def enter_sphere(self, ray):
        radius = self.radius
        x = self.center
        z = self.radius
        x_r, z_r = util.to_ray_coordinates(ray, x, z)
        sphere_thickness_at_intersect = sqrt(radius**2 - x_r**2)
        xi_r = 0 # by definition
        zi_r = z_r - sphere_thickness_at_intersect
        ray.save()

    def exit_sphere(self, ray):
        ray.save()

    def to_exit_plane(self, ray, z_final):
        distance = z_final - ray.z
        ray.x = ray.x + math.tan(ray.th)*distance
        ray.z += z_final
        ray.save()

    def propagate(self, ray):
        z_final = ray.z + self.dz
        if self.intersect_sphere(ray):
            self.enter_sphere(ray)
            self.exit_sphere(ray)
        self.to_exit_plane(ray, z_final)
