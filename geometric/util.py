import numpy as np

def digitize(x, bins):
    inds = np.digitize([x], bins)    
    return inds[0]

