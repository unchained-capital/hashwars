from argparse import ArgumentParser

import matplotlib.pyplot as plt
from numpy import array, mean, var

from hashwars import write_plot, COLORS, moving_average

_DEFAULT_WIDTH = 12
_DEFAULT_HEIGHT = 8
_DEFAULT_DPI = 100

def _comma_separated(sequence):
    return map(lambda element: element.strip(), (sequence or "").strip().split(","))

_parser = ArgumentParser(description="Plot of a blockchain launch's history.")
_parser.add_argument("-w", "--window", type=int, help="smooth this many points", metavar="POINTS")
_parser.add_argument("-c", "--colors", type=_comma_separated, help="use these colors names", metavar="COLOR1,COLOR2,...", default=[])
_parser.add_argument("-X", "--figure-width", help="figure width in inches", metavar="WIDTH", type=float, default=_DEFAULT_WIDTH)
_parser.add_argument("-Y", "--figure-height", help="figure height in inches", metavar="HEIGHT", type=float, default=_DEFAULT_HEIGHT)
_parser.add_argument("-Z", "--resolution", help="resolution in DPI", metavar="DPI", type=float, default=_DEFAULT_DPI)

def hashrate_distance_slices(results, output_file, argv):
    (
        distances,
        hashrate_ratios,
        minority_weights_ratios
    ) = results

    args = _parser.parse_args(argv)

    hashrate_fractions = list(reversed(1/(1+hashrate_ratios)))
    minority_weights_ratios_means = mean(minority_weights_ratios, axis=2)
    minority_weights_ratios_vars = var(minority_weights_ratios, axis=2)

    fig, ax = plt.subplots(
        nrows=1, 
        figsize=(args.figure_width, args.figure_height),
        dpi=args.resolution)
    ax.set_title('Blockchain Launch')
    ax.set_xlabel('Defender Relative Hashrate')
    ax.set_ylabel('Fraction Weight Mined by Defender')
    ax.set_xlim(hashrate_fractions[0], hashrate_fractions[-1])
    if hashrate_fractions[0] < 0.5 and hashrate_fractions[-1] > 0.5:
        # ax.set_xscale('log')
        ax.axvline(x=0.5, color='gray', linestyle='--', linewidth=0.5)
    ax.set_ylim(0, 1.01)
    ax.axhline(y=0.5, color='gray', linestyle='--', linewidth=0.5)

    smoothed_hashrate_fractions = moving_average(hashrate_fractions, args.window)

    colors = list(args.colors)
    # ax.plot(smoothed_hashrate_fractions, smoothed_hashrate_fractions, linestyle='--', color='gray', linewidth=0.5, label='0s')
    for index, distance in enumerate(distances):
        #ax.errorbar(hashrate_ratios, minority_weights_ratios_means[index], yerr=minority_weights_ratios_vars[index], label="{}s".format(distance))
        smoothed_minority_weights_ratios_means = list(reversed(moving_average(minority_weights_ratios_means[index], args.window)))
        color = (COLORS[colors[index]] if len(colors) > index else None)
        label = "{}s".format(int(distance))
        if len(colors) > index:
            label = '{} ({}) '.format(colors[index].capitalize(), label)
        ax.plot(smoothed_hashrate_fractions, smoothed_minority_weights_ratios_means, color=color, label=label)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.legend(loc='lower right', title="Distance", frameon=False)

    write_plot(fig, output_file)
