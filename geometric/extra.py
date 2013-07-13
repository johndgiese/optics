from math import sqrt, cos, sin, tan, acos, asin, atan, pi

from base import OpticalElement
from util import ray_coordinates, standard_coordinates

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


class Bead(OpticalElement):

    def __init__(self, radius, center, n_sphere, n_surround=1.0):
        self.radius = radius
        self.center = center
        self.n_sphere = n_sphere
        self.n_surround = n_surround
        self.dz = 2*radius

    def intersect_sphere(self, ray):
        x_sphere = self.center
        z_sphere = self.radius
        x_sphere_r, z_sphere_r = ray_coordinates(ray, x_sphere, z_sphere)
        return abs(x_sphere_r) < self.radius

    def enter_sphere(self, ray):
        radius = self.radius
        
        # calculate sphere center in ray-coordinates
        x_sphere = self.center
        z_sphere = self.radius
        x_sphere_r, z_sphere_r = ray_coordinates(ray, x_sphere, z_sphere)

        # use equation-of-a-circle to determine intersect point
        sphere_thickness_at_intersect = sqrt(radius**2 - x_sphere_r**2)
        x_intersect_r = 0
        z_intersect_r = z_sphere_r - sphere_thickness_at_intersect

        # use first derivative of the equation-of-a-circle and snell's law to
        # calculate the ray bending at the surface
        theta1_r = atan(x_sphere_r/sqrt(radius**2 - x_sphere_r**2))
        theta2_r = asin(self.n_surround/self.n_sphere*sin(theta1_r))

        # convert back to standard coordinates
        x_intersect, z_intersect = standard_coordinates(ray, x_intersect_r, z_intersect_r)
        theta2 = ray.th + theta2_r

        ray.x = x_intersect
        ray.z += z_intersect
        ray.th = theta2
        ray.save()

    def exit_sphere(self, ray):
        ray.save()

    def to_exit_plane(self, ray, z_final):
        distance = z_final - ray.z
        ray.x = ray.x + tan(ray.th)*distance
        ray.z = z_final
        ray.save()

    def propagate(self, ray):
        z_final = ray.z + self.dz
        if self.intersect_sphere(ray):
            self.enter_sphere(ray)
            self.exit_sphere(ray)
        self.to_exit_plane(ray, z_final)
