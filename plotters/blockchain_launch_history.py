from argparse import ArgumentParser

import matplotlib.pyplot as plt
from numpy import array

from hashwars import write_plot

_parser = ArgumentParser(description="Plot of a blockchain launch's history.")

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

    fig, (minority_weight, majority_weight) = plt.subplots(nrows=2, sharex=True)

    minority_weight.set_title("Minority (Distance: {}, Final {:0.4f})".format(distance, minority_miners_minority_weight[-1]/(minority_miners_minority_weight[-1] + minority_miners_majority_weight[-1])))
    minority_weight.stackplot(times, minority_miners_minority_weight, minority_miners_majority_weight, labels=['Mined on Minority', 'Mined on Majority'], colors=['red', 'green'], baseline='zero')
    minority_weight.legend(loc='upper left')
    minority_weight.set_ylim(0, max_weight)
    minority_weight.set_ylabel('Weight')
    minority_weight.axvline(x=distance, color='gray', linestyle='--', linewidth=0.5)
    minority_weight.axvline(x=(2 * distance), color='gray', linestyle='--', linewidth=0.5)
    minority_ratio = minority_weight.twinx()
    minority_ratio.plot(times, array(minority_miners_minority_weight)/(array(minority_miners_minority_weight)+array(minority_miners_majority_weight)), color='black')
    minority_ratio.set_ylabel('Ratio')
    minority_ratio.set_ylim(0, 1)

    majority_weight.set_title("On Majority ({}x hashrate ratio)".format(hashrate_ratio))
    majority_weight.stackplot(times, majority_miners_minority_weight, majority_miners_majority_weight, labels=['Mined on Minority', 'Mined on Majority'], colors=['red', 'green'])
    majority_weight.legend(loc='upper left')
    majority_weight.set_ylim(0, max_weight)
    majority_weight.set_ylabel('Weight')
    majority_weight.axvline(x=distance, color='gray', linestyle='--', linewidth=0.5)
    majority_weight.axvline(x=(2 * distance), color='gray', linestyle='--', linewidth=0.5)
    # majority_weight.set_xticks(
    #     [hour * 3600 for hour in range(simulation_length)],
    #     [str(hour) for hour in range(simulation_length)],
    # )
    majority_weight.set_xlabel("Seconds")

    majority_ratio = majority_weight.twinx()
    majority_ratio.plot(times, array(majority_miners_majority_weight)/(array(majority_miners_minority_weight)+array(majority_miners_majority_weight)), color='black')
    majority_ratio.set_ylabel('Ratio')
    majority_ratio.set_ylim(0, 1)

    write_plot(output_file)
