import numpy as np

def digitize(x, bins):
    inds = np.digitize([x], bins)    
    return inds[0]

def rotate(x, y, theta):
    x_new = x*np.cos(theta) - y*np.sin(theta)
    y_new = x*np.sin(theta) + y*np.cos(theta)
    return x_new, y_new

def to_ray_coordinates(ray, x, y):
    """
    Convert from standard coordinate system, to coordinate system where
    the ray position defines the origin and the ray-direction defines the
    y-axis.
    """
    return rotate(x - ray.x, y, ray.th)

def to_standard_coordinates(ray, x, y):
    """
    Convert from ray coordinate system where
    the ray position defines the origin and the ray-direction defines the
    y-axis, back to the standard coordinate system.
    """
    return rotate(x + ray.x, y, -ray.th)
