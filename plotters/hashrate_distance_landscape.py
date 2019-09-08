from argparse import ArgumentParser

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from numpy import mean, std, where, full, array

from hashwars import write_plot, array_glob, COLORS, moving_average, format_percent

_DEFAULT_LEVELS = 10
_DEFAULT_WIDTH = 12
_DEFAULT_HEIGHT = 8
_DEFAULT_DPI = 100

_parser = ArgumentParser(description="Plot of the hashrate/distance landscape.")
_parser.add_argument("-s", "--samples", action='store_true', help="show points sampled")
_parser.add_argument("-d", "--min-distance", help="ignore points closer than this distance", metavar="DISTANCE", type=float)
_parser.add_argument("-D", "--max-distance", help="ignore points further than this distance", metavar="DISTANCE", type=float)
_parser.add_argument("-f", "--min-hashrate-fraction", help="ignore points with less than this hashrat fraction", metavar="RATIO", type=float)
_parser.add_argument("-F", "--max-hashrate-fraction", help="ignore points with more than this hashrate fraction", metavar="RATIO", type=float)
_parser.add_argument("-m", "--means-only", help="don't plot standard deviations", action='store_true')
_parser.add_argument("-l", "--levels", help="use this count or these explicit levels", metavar="COUNT|ARRAY", type=array_glob, default=[_DEFAULT_LEVELS])
_parser.add_argument("-X", "--figure-width", help="figure width in inches", metavar="WIDTH", type=float, default=_DEFAULT_WIDTH)
_parser.add_argument("-Y", "--figure-height", help="figure height in inches", metavar="HEIGHT", type=float, default=_DEFAULT_HEIGHT)
_parser.add_argument("-Z", "--resolution", help="resolution in DPI", metavar="DPI", type=float, default=_DEFAULT_DPI)
_parser.add_argument("-W", "--weights", help="block weights to trace", type=array_glob, default=[], metavar="ARRAY")

def hashrate_distance_landscape(results, output_file, argv):
    (
        distances,
        hashrate_ratios,
        minority_weights_fractions
    ) = results

    args = _parser.parse_args(argv)

    distances, hashrate_ratios, minority_weights_fractions = _ignore_data(distances, hashrate_ratios, minority_weights_fractions, args)

    hashrate_fractions = 1/(1+hashrate_ratios)
        
    minority_weights_fractions_means = mean(minority_weights_fractions, axis=2)
    minority_weights_fractions_stds = std(minority_weights_fractions, axis=2)

    fig, axes = plt.subplots(
        figsize=(args.figure_width, args.figure_height),
        dpi=args.resolution,
        nrows=(1 if args.means_only else 2), 
        sharex=True)

    if args.samples:
        sample_distances = []
        sample_hashrate_fractions = []
        for distance in distances:
            for hashrate_fraction in hashrate_fractions:
                sample_distances.append(distance)
                sample_hashrate_fractions.append(hashrate_fraction)

    levels = (args.levels if len(args.levels) > 1 else int(args.levels[0]))

    ax_means = (axes if args.means_only else axes[0])
    title = 'Block weight mined by pool'
    ylabel = 'Pool Hashrate'
    xlabel = 'Pool Distance (light seconds)'
    if args.means_only:
        ax_means.set_title(title)
    else:
        fig.suptitle(title)
        ax_means.set_title("Mean")

    ax_means.set_ylabel(ylabel)
    means_landscape = ax_means.contourf(
        distances, 
        hashrate_fractions,
        minority_weights_fractions_means.transpose(), 
        levels,
        cmap="coolwarm",
        vmin=0,
        # vmax=1,
    )
    means_colorbar = plt.colorbar(means_landscape, ax=ax_means, format=ticker.FuncFormatter(format_percent))
    if args.samples:
        ax_means.scatter(sample_distances, sample_hashrate_fractions, s=5, color=COLORS['background'], linewidths=0.01, alpha=0.25)
    ax_means.set_yticklabels(['{:,.0%}'.format(y) for y in ax_means.get_yticks()])
    if args.means_only:
        ax_means.set_xlabel(xlabel)

    smoothed_distances = moving_average(distances)
    for target_weight_fraction in args.weights:
        hashrate_fractions_to_reach_weight = []
        for distance_index, distance in enumerate(distances):
            hashrate_fraction_to_reach_weight = None
            for hashrate_fraction_index, minority_weight_fraction in enumerate(minority_weights_fractions_means[distance_index]):
                hashrate_fraction = hashrate_fractions[hashrate_fraction_index]
                if minority_weight_fraction <= target_weight_fraction:
                    hashrate_fraction_to_reach_weight = hashrate_fraction
                    break
            if hashrate_fraction_to_reach_weight is None:
                hashrate_fraction_to_reach_weight = hashrate_fractions[-1]
            hashrate_fractions_to_reach_weight.append(hashrate_fraction_to_reach_weight)
        smoothed_hashrate_fractions_to_reach_weight = moving_average(hashrate_fractions_to_reach_weight)
        ax_means.plot(smoothed_distances, smoothed_hashrate_fractions_to_reach_weight, color=COLORS['background'], linewidth=1)
        ax_means.text(
            x=(smoothed_distances[-1] * 1.01), 
            y=(smoothed_hashrate_fractions_to_reach_weight[-1] * 1), 
            s=format_percent(target_weight_fraction), 
            color=COLORS['background'],
        )

    ax_means.set_xlim(distances[0], distances[-1])
    ax_means.set_ylim(hashrate_fractions[-1], hashrate_fractions[0])
        
    if not args.means_only:
        ax_stds = axes[1]
        ax_stds.set_title("Standard Deviation")
        ax_stds.set_ylabel(ylabel)
        ax_stds.set_xlabel(xlabel)
        stds_landscape = ax_stds.contourf(
            distances, 
            hashrate_fractions,
            minority_weights_fractions_stds.transpose(), 
            levels,
            cmap="Greys",
            vmin=0)
        stds_colorbar = plt.colorbar(stds_landscape, ax=ax_stds)
        if args.samples:
            ax_stds.scatter(sample_distances, sample_hashrate_fractions, s=5, color=COLORS['background'], linewidths=0.01, alpha=0.25)
        ax_stds.set_yticklabels(['{:,.0%}'.format(y) for y in ax_stds.get_yticks()])

        ax_stds.set_ylim(hashrate_fractions[-1], hashrate_fractions[0])

    write_plot(fig, output_file)

def _ignore_data(distances, hashrate_ratios, minority_weights_fractions, args):
    distances_filter = full(len(distances), True)
    hashrate_ratios_filter = full(len(hashrate_ratios), True)

    if args.min_distance:
        distances_filter = where(distances >= args.min_distance, distances_filter, False)
    if args.max_distance:
        distances_filter = where(distances <= args.max_distance, distances_filter, False)
    if args.min_hashrate_fraction:
        max_hashrate_ratio = (1/args.min_hashrate_fraction) - 1
        hashrate_ratios_filter = where(hashrate_ratios <= max_hashrate_ratio, hashrate_ratios_filter, False)
    if args.max_hashrate_fraction:
        min_hashrate_ratio = (1/args.max_hashrate_fraction) - 1
        hashrate_ratios_filter = where(hashrate_ratios >= min_hashrate_ratio, hashrate_ratios_filter, False)

    distances = distances[distances_filter]
    hashrate_ratios = hashrate_ratios[hashrate_ratios_filter]
    minority_weights_fractions = array(minority_weights_fractions)
    minority_weights_fractions = minority_weights_fractions[distances_filter]
    minority_weights_fractions = minority_weights_fractions.transpose(1, 0, 2)[hashrate_ratios_filter].transpose(1, 0, 2)

    return (distances, hashrate_ratios, minority_weights_fractions)
