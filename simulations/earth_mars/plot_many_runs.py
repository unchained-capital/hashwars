from sys import argv, stderr, stdout, stdin
from pickle import loads

import matplotlib.pyplot as plt
from numpy import array

from simulations.earth_mars.single_run import *

def plot_many_runs(distances, hashrate_ratios, mars_blocks_ratios):
    fig, ax = plt.subplots(nrows=1)
    mappable = ax.contourf(distances, hashrate_ratios, mars_blocks_ratios, cmap="coolwarm")
    plt.colorbar(mappable)
    plt.show()

if __name__ ==  '__main__':
    if len(argv) == 2:
        input_stream = open(argv[1], 'rb')
    else:
        input_stream = stdin.buffer
    results = loads(input_stream.read())
    plot_many_runs(*results)
