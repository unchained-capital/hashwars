from argparse import ArgumentParser

import matplotlib.pyplot as plt
from numpy import array, mean, var

from hashwars import write_plot

_parser = ArgumentParser(description="Plot of the hashrate/distance landscape.")
_parser.add_argument("-s", "--samples", action='store_true', help="show points sampled")

def hashrate_distance_landscape(results, output_file, argv):
    (
        distances,
        hashrate_ratios,
        minority_weights_ratios
    ) = results

    args = _parser.parse_args(argv)

    minority_weights_ratios_means = mean(minority_weights_ratios, axis=2)
    minority_weights_ratios_vars = var(minority_weights_ratios, axis=2)

    fig, (ax_means, ax_vars) = plt.subplots(nrows=2, sharex=True)
    fig.suptitle('Fraction Weight Mined on Minority')

    if args.samples:
        sample_distances = []
        sample_hashrate_ratios = []
        for distance in distances:
            for hashrate_ratio in hashrate_ratios:
                sample_distances.append(distance)
                sample_hashrate_ratios.append(hashrate_ratio)

    ax_means.set_title("Mean")
    ax_means.set_ylabel('Majority/Minority Hashrate')
    means_mappable = ax_means.contourf(distances, hashrate_ratios, minority_weights_ratios_means.transpose(), cmap="coolwarm")
    plt.colorbar(means_mappable, ax=ax_means)
    if args.samples:
        ax_means.scatter(sample_distances, sample_hashrate_ratios, s=5, color='black', linewidths=0.01, alpha=0.25)

    ax_vars.set_title("Variance")
    ax_vars.set_ylabel('Majority/Minority Hashrate')
    ax_vars.set_xlabel("Seconds")
    vars_mappable = ax_vars.contourf(distances, hashrate_ratios, minority_weights_ratios_vars.transpose(), cmap="Greys")
    plt.colorbar(vars_mappable, ax=ax_vars)
    if args.samples:
        ax_vars.scatter(sample_distances, sample_hashrate_ratios, s=5, color='black', linewidths=0.01, alpha=0.25)

    write_plot(output_file)
