from argparse import ArgumentParser

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from numpy import mean, std, where, full, array

from hashwars import write_plot, array_glob

_DEFAULT_LEVELS = 10
_DEFAULT_WIDTH = 8
_DEFAULT_HEIGHT = 6
_DEFAULT_DPI = 100

_parser = ArgumentParser(description="Plot of the hashrate/distance landscape.")
_parser.add_argument("-s", "--samples", action='store_true', help="show points sampled")
_parser.add_argument("-d", "--min-distance", help="ignore points closer than this distance", metavar="DISTANCE", type=float)
_parser.add_argument("-D", "--max-distance", help="ignore points further than this distance", metavar="DISTANCE", type=float)
_parser.add_argument("-r", "--min-ratio", help="ignore points with less than this ratio", metavar="RATIO", type=float)
_parser.add_argument("-R", "--max-ratio", help="ignore points with more than this ratio", metavar="RATIO", type=float)
_parser.add_argument("-m", "--means-only", help="don't plot standard deviations", action='store_true')
_parser.add_argument("-l", "--levels", help="use this count or these explicit levels", metavar="COUNT|ARRAY", type=array_glob, default=[_DEFAULT_LEVELS])
_parser.add_argument("-X", "--figure-width", help="figure width in inches", metavar="WIDTH", type=float, default=_DEFAULT_WIDTH)
_parser.add_argument("-Y", "--figure-height", help="figure height in inches", metavar="HEIGHT", type=float, default=_DEFAULT_HEIGHT)
_parser.add_argument("-Z", "--resolution", help="resolution in DPI", metavar="DPI", type=float, default=_DEFAULT_DPI)

def _format_percent(value, index):
    return '{:,.0%}'.format(value)

def hashrate_distance_landscape(results, output_file, argv):
    (
        distances,
        hashrate_ratios,
        minority_weights_ratios
    ) = results

    args = _parser.parse_args(argv)

    distances, hashrate_ratios, minority_weights_ratios = _ignore_data(distances, hashrate_ratios, minority_weights_ratios, args)
        
    minority_weights_ratios_means = mean(minority_weights_ratios, axis=2)
    minority_weights_ratios_stds = std(minority_weights_ratios, axis=2)

    fig, axes = plt.subplots(
        figsize=(args.figure_width, args.figure_height),
        dpi=args.resolution,
        nrows=(1 if args.means_only else 2), 
        sharex=True)

    if args.samples:
        sample_distances = []
        sample_hashrate_ratios = []
        for distance in distances:
            for hashrate_ratio in hashrate_ratios:
                sample_distances.append(distance)
                sample_hashrate_ratios.append(hashrate_ratio)

    levels = (args.levels if len(args.levels) > 1 else int(args.levels[0]))

    ax_means = (axes if args.means_only else axes[0])
    title = 'Fraction blockchain weight mined by minority'
    ylabel = 'Minority Hashrate Fraction'
    xlabel = 'Minority Distance (light seconds)'
    if args.means_only:
        ax_means.set_title(title)
    else:
        fig.suptitle(title)
        ax_means.set_title("Mean")

    ax_means.set_ylabel(ylabel)
    means_landscape = ax_means.contourf(
        distances, 
        1/hashrate_ratios, 
        minority_weights_ratios_means.transpose(), 
        levels,
        cmap="coolwarm")
    means_colorbar = plt.colorbar(means_landscape, ax=ax_means, format=ticker.FuncFormatter(_format_percent))
    if args.samples:
        ax_means.scatter(sample_distances, sample_hashrate_ratios, s=5, color='black', linewidths=0.01, alpha=0.25)
    ax_means.set_yticklabels(['{:,.0%}'.format(y) for y in ax_means.get_yticks()])
    if args.means_only:
        ax_means.set_xlabel(xlabel)

    if not args.means_only:
        ax_stds = axes[1]
        ax_stds.set_title("Standard Deviation")
        ax_stds.set_ylabel(ylabel)
        ax_stds.set_xlabel(xlabel)
        stds_landscape = ax_stds.contourf(
            distances, 
            1/hashrate_ratios, 
            minority_weights_ratios_stds.transpose(), 
            levels,
            cmap="Greys")
        stds_colorbar = plt.colorbar(stds_landscape, ax=ax_stds)
        if args.samples:
            ax_stds.scatter(sample_distances, sample_hashrate_ratios, s=5, color='black', linewidths=0.01, alpha=0.25)
        ax_stds.set_yticklabels(['{:,.0%}'.format(y) for y in ax_stds.get_yticks()])

    write_plot(output_file)

def _ignore_data(distances, hashrate_ratios, minority_weights_ratios, args):
    distances_filter = full(len(distances), True)
    hashrate_ratios_filter = full(len(hashrate_ratios), True)

    if args.min_distance:
        distances_filter = where(distances >= args.min_distance, distances_filter, False)
    if args.max_distance:
        distances_filter = where(distances <= args.max_distance, distances_filter, False)
    if args.min_ratio:
        hashrate_ratios_filter = where(hashrate_ratios >= args.min_ratio, hashrate_ratios_filter, False)
    if args.max_ratio:
        hashrate_ratios_filter = where(hashrate_ratios <= args.max_ratio, hashrate_ratios_filter, False)

    distances = distances[distances_filter]
    hashrate_ratios = hashrate_ratios[hashrate_ratios_filter]
    minority_weights_ratios = array(minority_weights_ratios)
    minority_weights_ratios = minority_weights_ratios[distances_filter]
    minority_weights_ratios = minority_weights_ratios.transpose(1, 0, 2)[hashrate_ratios_filter].transpose(1, 0, 2)

    return (distances, hashrate_ratios, minority_weights_ratios)
