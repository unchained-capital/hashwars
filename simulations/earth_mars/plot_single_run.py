from sys import argv, stderr, stdout, stdin
from pickle import loads

import matplotlib.pyplot as plt
from numpy import array

from simulations.earth_mars.single_run import *

def plot_single_run(
        distance,
        mars_miners,
        earth_miners,
        times, 
        mars_miners_mars_blocks,
        mars_miners_earth_blocks,
        earth_miners_mars_blocks,
        earth_miners_earth_blocks,
        ):

    max_blocks = max(
        max(mars_miners_mars_blocks) + max(mars_miners_earth_blocks),
        max(earth_miners_mars_blocks) + max(earth_miners_earth_blocks))

    fig, (mars_blocks, earth_blocks) = plt.subplots(nrows=2, sharex=True)

    mars_blocks.set_title("On Mars (Distance: {}, Final {:0.4f})".format(distance, mars_miners_mars_blocks[-1]/(mars_miners_mars_blocks[-1] + mars_miners_earth_blocks[-1])))
    mars_blocks.stackplot(times, mars_miners_mars_blocks, mars_miners_earth_blocks, labels=['Mined on Mars', 'Mined on Earth'], colors=['red', 'green'], baseline='zero')
    mars_blocks.legend(loc='upper left')
    mars_blocks.set_ylim(0, max_blocks)
    mars_blocks.set_ylabel('Counts')
    mars_blocks.axvline(x=distance, color='gray', linestyle='--', linewidth=0.5)
    mars_blocks.axvline(x=(2 * distance), color='gray', linestyle='--', linewidth=0.5)
    mars_ratio = mars_blocks.twinx()
    mars_ratio.plot(times, array(mars_miners_mars_blocks)/(array(mars_miners_mars_blocks)+array(mars_miners_earth_blocks)), color='black')
    mars_ratio.set_ylabel('Ratio')
    mars_ratio.set_ylim(0, 1)

    earth_blocks.set_title("On Earth ({}x hashrate, {}x premium)".format(earth_miners.hashrate/mars_miners.hashrate, earth_miners.difficulty_premium))
    earth_blocks.stackplot(times, earth_miners_mars_blocks, earth_miners_earth_blocks, labels=['Mined on Mars', 'Mined on Earth'], colors=['red', 'green'])
    earth_blocks.legend(loc='upper left')
    earth_blocks.set_ylim(0, max_blocks)
    earth_blocks.set_ylabel('Counts')
    earth_blocks.axvline(x=distance, color='gray', linestyle='--', linewidth=0.5)
    earth_blocks.axvline(x=(2 * distance), color='gray', linestyle='--', linewidth=0.5)
    # earth_blocks.set_xticks(
    #     [hour * 3600 for hour in range(simulation_length)],
    #     [str(hour) for hour in range(simulation_length)],
    # )
    earth_blocks.set_xlabel("Seconds")

    earth_ratio = earth_blocks.twinx()
    earth_ratio.plot(times, array(earth_miners_earth_blocks)/(array(earth_miners_mars_blocks)+array(earth_miners_earth_blocks)), color='black')
    earth_ratio.set_ylabel('Ratio')
    earth_ratio.set_ylim(0, 1)

    plt.show()

if __name__ ==  '__main__':
    if len(argv) == 2:
        input_stream = open(argv[1], 'rb')
    else:
        input_stream = stdin.buffer
    results = loads(input_stream.read())
    plot_single_run(*results)
