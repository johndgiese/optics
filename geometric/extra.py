from math import sqrt, cos, sin, tan, acos, asin, atan, pi

from base import OpticalElement
from util import ray_coordinates, standard_coordinates, quadrant_atan

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

    def dz(self):
        return 0.0


class Bead(OpticalElement):

    def __init__(self, radius, x, n_bead, n_surround=1.0):
        self.radius = radius
        self.x = x
        self.n_bead = n_bead
        self.n_surround = n_surround

    def intersect(self, ray):
        x_bead = self.x
        z_bead = self.radius
        x_bead_r, z_bead_r = ray_coordinates(ray, x_bead, z_bead)
        return abs(x_bead_r) < self.radius

    def enter(self, ray):
        radius = self.radius
        
        # calculate bead center in ray-coordinates
        x_bead = self.x
        z_bead = self.radius
        x_bead_r, z_bead_r = ray_coordinates(ray, x_bead, z_bead)

        # use equation-of-a-circle to determine intersect point
        bead_thickness_at_intersect = sqrt(radius**2 - x_bead_r**2)
        x_intersect_r = 0
        z_intersect_r = z_bead_r - bead_thickness_at_intersect

        # use first derivative of the equation-of-a-circle and snell's law to
        # calculate the ray bending at the surface
        theta1_r = atan(x_bead_r/sqrt(radius**2 - x_bead_r**2))
        theta2_r = asin(self.n_surround/self.n_bead*sin(theta1_r))

        # convert back to standard coordinates
        x_intersect, z_intersect = standard_coordinates(ray, x_intersect_r, z_intersect_r)
        theta2 = ray.th + theta2_r

        ray.x = x_intersect
        ray.z += z_intersect
        ray.th = theta2
        ray.save()

    def exit(self, ray):
        # Use the cosine law with the triangle formed by the
        # raypath-inside-the- bead, the ray-entrance-to-center, and the
        # ray-exit-to-center.  The cosine law gives the length of the raypath
        # inside the bead, which can be used to find the exit location.
        dx = self.x - ray.x
        dz = self.z_front + self.radius - ray.z
        xaxis_bead_angle = quadrant_atan(dx, dz)
        xaxis_ray_angle = pi/2.0 - ray.th
        bead_ray_angle = abs(xaxis_ray_angle - xaxis_bead_angle)
        pathlength_in_bead = 2*self.radius*cos(bead_ray_angle)

        import pprint
        xaxis_bead_angle_deg = round(xaxis_bead_angle*180/pi, 2)
        xaxis_ray_angle_deg = round(xaxis_ray_angle*180/pi, 2)
        print(xaxis_bead_angle_deg, xaxis_ray_angle_deg, xaxis_ray_angle_deg -  xaxis_bead_angle_deg)
        #pprint.pprint(locals())

        ray.x += pathlength_in_bead*cos(xaxis_ray_angle)
        ray.z += pathlength_in_bead*sin(xaxis_ray_angle)

        # calculate the exit angle
        # TODO
        ray.th = 0

        ray.save()

    def to_exit_plane(self, ray, z_final):
        distance = z_final - ray.z
        ray.x = ray.x + tan(ray.th)*distance
        ray.z = z_final
        ray.save()

    def propagate(self, ray):
        z_final = ray.z + self.dz()
        if self.intersect(ray):
            self.enter(ray)
            self.exit(ray)
        self.to_exit_plane(ray, z_final)

    def dz(self):
        return self.radius*2
