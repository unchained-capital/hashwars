from argparse import ArgumentParser

import matplotlib.pyplot as plt
from numpy import array, mean, var, convolve, ones

from hashwars import write_plot

from simulations.shared import *

_DEFAULT_WINDOW = 5

def _comma_separated(sequence):
    return map(lambda element: element.strip(), (sequence or "").strip().split(","))

_parser = ArgumentParser(description="Plot of a blockchain launch's history.")
_parser.add_argument("-w", "--window", type=int, default=_DEFAULT_WINDOW, help="smooth this many points", metavar="POINTS")
_parser.add_argument("-l", "--labels", type=_comma_separated, help="smooth this many points", metavar="LABEL1,LABEL2,...", default=[])

def _moving_average(series, window):
    return convolve(series, ones(window), 'valid') / window

def hashrate_distance_slices(results, output_file, argv):
    (
        distances,
        hashrate_ratios,
        minority_weights_ratios
    ) = results

    args = _parser.parse_args(argv)

    minority_weights_ratios_means = mean(minority_weights_ratios, axis=2)
    minority_weights_ratios_vars = var(minority_weights_ratios, axis=2)

    fig, ax = plt.subplots(nrows=1)
    ax.set_title('Blockchain Launch')
    ax.set_xlabel('Majority/Minority Hashrate Ratio')
    ax.set_ylabel('Fraction Weight Mined by Minority')
    if hashrate_ratios[0] < 1 and hashrate_ratios[-1] > 1:
        ax.set_xscale('log')
        ax.axvline(x=1.0, color='gray', linestyle='--', linewidth=0.5)
    #ax.set_ylim(0, 1)

    smoothed_hashrate_ratios = _moving_average(hashrate_ratios, args.window)
    ax.plot(smoothed_hashrate_ratios, 1/(1 + smoothed_hashrate_ratios), linestyle='--', color='gray', linewidth=0.5, label='0s (adjacent)')
    
    for index, distance in enumerate(distances):
        #ax.errorbar(hashrate_ratios, minority_weights_ratios_means[index], yerr=minority_weights_ratios_vars[index], label="{}s".format(distance))
        smoothed_minority_weights_ratios_means = _moving_average(minority_weights_ratios_means[index], args.window)
        label = args.labels[index] if len(args.labels) > index else "{}s".format(distance)
        ax.plot(smoothed_hashrate_ratios, smoothed_minority_weights_ratios_means, label=label)

    plt.legend(loc='lower left', title="Distance")

    write_plot(output_file)
