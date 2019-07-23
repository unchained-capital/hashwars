from sys import argv, stderr, stdout, stdin
from pickle import loads

import matplotlib.pyplot as plt
from numpy import array, mean, var

from simulations.earth_mars.single_run import *

def plot_many_runs(distances, hashrate_ratios, mars_blocks_ratios):
    fig, (ax_means, ax_vars) = plt.subplots(nrows=2, sharex=True)
    mars_blocks_ratios_means = mean(mars_blocks_ratios, axis=2)
    mars_blocks_ratios_vars = var(mars_blocks_ratios, axis=2)

    sample_distances = []
    sample_hashrate_ratios = []
    for distance in distances:
        for hashrate_ratio in hashrate_ratios:
            sample_distances.append(distance)
            sample_hashrate_ratios.append(hashrate_ratio)

    fig.suptitle('Fraction Blocks Mined on Mars')

    ax_means.set_title("Mean")
    ax_means.set_ylabel('Earth/Mars Hashrate')
    means_mappable = ax_means.contourf(distances, hashrate_ratios, mars_blocks_ratios_means.transpose(), cmap="coolwarm")
    plt.colorbar(means_mappable, ax=ax_means)
    ax_means.scatter(sample_distances, sample_hashrate_ratios, s=5, color='black', linewidths=0.01, alpha=0.25)

    ax_vars.set_title("Variance")
    ax_vars.set_ylabel('Earth/Mars Hashrate')
    ax_vars.set_xlabel("Seconds")
    vars_mappable = ax_vars.contourf(distances, hashrate_ratios, mars_blocks_ratios_vars.transpose(), cmap="Greys")
    plt.colorbar(vars_mappable, ax=ax_vars)
    ax_vars.scatter(sample_distances, sample_hashrate_ratios, s=5, color='black', linewidths=0.01, alpha=0.25)

    plt.show()

if __name__ ==  '__main__':
    if len(argv) == 2:
        input_stream = open(argv[1], 'rb')
    else:
        input_stream = stdin.buffer
    results = loads(input_stream.read())
    plot_many_runs(*results)
