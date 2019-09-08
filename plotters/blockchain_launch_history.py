from argparse import ArgumentParser

import matplotlib.pyplot as plt
from numpy import array

from hashwars import write_plot, COLORS, format_percent

_DEFAULT_WIDTH = 12
_DEFAULT_HEIGHT = 8
_DEFAULT_DPI = 100

_parser = ArgumentParser(description="Plot of a blockchain launch's history.")
_parser.add_argument("-X", "--figure-width", help="figure width in inches", metavar="WIDTH", type=float, default=_DEFAULT_WIDTH)
_parser.add_argument("-Y", "--figure-height", help="figure height in inches", metavar="HEIGHT", type=float, default=_DEFAULT_HEIGHT)
_parser.add_argument("-Z", "--resolution", help="resolution in DPI", metavar="DPI", type=float, default=_DEFAULT_DPI)

def blockchain_launch_history(results, output_file, argv):
    (
        distance,
        hashrate_ratio,
        times,
        minority_miners_minority_weight,
        minority_miners_majority_weight,
        majority_miners_minority_weight,
        majority_miners_majority_weight,
    ) = results
    args = _parser.parse_args(argv)

    max_weight = max(
        max(minority_miners_minority_weight) + max(minority_miners_majority_weight),
        max(majority_miners_minority_weight) + max(majority_miners_majority_weight))

    fig, (minority_weight, majority_weight) = plt.subplots(
        nrows=2, 
        sharex=True,
        figsize=(args.figure_width, args.figure_height),
        dpi=args.resolution)

    minority_weight.set_title("Minority (Distance: {}, Final {})".format(distance, format_percent(minority_miners_minority_weight[-1]/(minority_miners_minority_weight[-1] + minority_miners_majority_weight[-1]), places=2)))
    minority_weights_stackplot = minority_weight.stackplot(times, minority_miners_minority_weight, minority_miners_majority_weight, labels=['Mined by Minority', 'Mined by Majority'], colors=[COLORS['mars'], COLORS['earth']], baseline='zero')
    minority_weight.set_ylim(0, max_weight)
    minority_weight.set_xlim(0, times[-1])
    minority_weight.set_ylabel('Weight')
    minority_weight.axvline(x=distance, color='gray', linestyle='--', linewidth=0.5)
    minority_weight.axvline(x=(2 * distance), color='gray', linestyle='--', linewidth=0.5)

    minority_ratio = minority_weight.twinx()
    minority_fraction_line = minority_ratio.plot(times, array(minority_miners_minority_weight)/(array(minority_miners_minority_weight)+array(minority_miners_majority_weight)), color=COLORS['white'], label="Fraction Mined by Minority")
    minority_ratio.set_ylabel('Minority Fraction')
    minority_ratio.set_ylim(0, 1.01)
    minority_ratio.set_yticklabels([format_percent(y) for y in minority_ratio.get_yticks()])

    minority_traces = minority_weights_stackplot + minority_fraction_line
    minority_labels = [trace.get_label() for trace in minority_traces]
    minority_weight.legend(minority_traces, minority_labels, loc='upper center')

    majority_weight.set_title("On Majority ({}x hashrate ratio)".format(hashrate_ratio))
    majority_weights_stackplot = majority_weight.stackplot(times, majority_miners_minority_weight, majority_miners_majority_weight, labels=['Mined by Minority', 'Mined by Majority'], colors=[COLORS['mars'], COLORS['earth']])
    majority_weight.set_ylim(0, max_weight)
    minority_weight.set_xlim(0, times[-1])
    majority_weight.set_ylabel('Weight')
    majority_weight.axvline(x=distance, color=COLORS['white'], linestyle='--', linewidth=0.5)
    majority_weight.axvline(x=(2 * distance), color=COLORS['white'], linestyle='--', linewidth=0.5)
    # majority_weight.set_xticks(
    #     [hour * 3600 for hour in range(simulation_length)],
    #     [str(hour) for hour in range(simulation_length)],
    # )
    majority_weight.set_xlabel("Seconds")
    
    majority_ratio = majority_weight.twinx()
    majority_fraction_line = majority_ratio.plot(times, array(majority_miners_majority_weight)/(array(majority_miners_minority_weight)+array(majority_miners_majority_weight)), color=COLORS['white'], label="Fraction Mined by Majority")
    majority_ratio.set_ylabel('Majority Fraction')
    majority_ratio.set_ylim(0, 1.01)
    majority_ratio.set_yticklabels([format_percent(y) for y in majority_ratio.get_yticks()])

    majority_traces = majority_weights_stackplot + majority_fraction_line
    majority_labels = [trace.get_label() for trace in majority_traces]
    majority_weight.legend(majority_traces, majority_labels, loc='upper center')

    write_plot(fig, output_file)
