import pylab

from base import Ray

def plot_traces(traces):
    for t in traces:
        num_locations = len(t.locations)
        x = pylab.empty(num_locations)
        z = pylab.empty(num_locations)
        for i, loc in enumerate(t.locations):
            x[i], z[i] = loc
        pylab.plot(z, x)
