from os import environ
from sys import argv, stderr, stdout, stdin
from pickle import loads

import matplotlib.pyplot as plt
from numpy import array, mean, var, convolve, ones

from simulations.earth_mars.single_run import *

def _moving_average(series, window):
    return convolve(series, ones(window), 'valid') / window

def plot_lines(distances, hashrate_ratios, mars_blocks_ratios):
    mars_blocks_ratios_means = mean(mars_blocks_ratios, axis=2)
    mars_blocks_ratios_vars = var(mars_blocks_ratios, axis=2)

    fig, ax = plt.subplots(nrows=1)
    ax.set_title('Colony Blockchain Launch')
    ax.set_xlabel('Empire/Colony Hashrate Ratio')
    ax.set_ylabel('Fraction Blocks Mined by Colony')
    ax.set_xscale('log')
    #ax.set_ylim(0, 1)

    smoothing_window = 20
    smoothed_hashrate_ratios = _moving_average(hashrate_ratios, smoothing_window)
    ax.plot(smoothed_hashrate_ratios, 1/(1 + smoothed_hashrate_ratios), linestyle='--', color='gray', linewidth=0.5, label='0s')
    ax.axvline(x=1.0, color='gray', linestyle='--', linewidth=0.5)
    for index, distance in enumerate(distances):
        #ax.errorbar(hashrate_ratios, mars_blocks_ratios_means[index], yerr=mars_blocks_ratios_vars[index], label="{}s".format(distance))
        smoothed_mars_blocks_ratios_means = _moving_average(mars_blocks_ratios_means[index], smoothing_window)
        ax.plot(smoothed_hashrate_ratios, smoothed_mars_blocks_ratios_means, label="{}s".format(distance))

    plt.legend(loc='lower left', title="Distance to Colony")
    plt.show()

    
if __name__ ==  '__main__':
    if len(argv) > 1:
        input_stream = open(argv[1], 'rb')
    else:
        input_stream = stdin.buffer
    results = loads(input_stream.read())
    plot_lines(*results)
