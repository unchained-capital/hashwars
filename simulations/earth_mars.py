import matplotlib.pyplot as plt
from numpy import array, arange

from latinum import *

class EarthMiners(Miners):
    
    def react(self, time,  transmission):
        if isinstance(transmission, (BlockchainLaunch,)):
            self.active = True
            log("MINER {} ACTIVATING".format(self.id))
        Miners.react(self, time, transmission)

class BlockchainLaunch(Transmission):
    pass

earth_mars_distance_in_light_seconds = (22 *  60) # 22 mins average distance = 1320 s

def single_run(distance, hashrate_ratio):
    reset_simulation()
    set_spatial_boundary(-1, distance + 1)

    genesis_block = Block("genesis-block", None, difficulty=600, height=1)
    mars_blockchain = Blockchain("mars-blockchain", genesis_block)
    mars_miners  = Miners("mars-miners", 0, mars_blockchain, initial_hashrate=1.0)


    muskcoin_launch = BlockchainLaunch("muskcoin-launch", mars_miners, current_time())


    earth_blockchain = Blockchain("earth-blockchain", genesis_block)

    earth_miners = EarthMiners("earth-miners", distance, earth_blockchain, initial_hashrate=hashrate_ratio, difficulty_premium=1.0, active=False)

    add_agent(mars_miners)
    add_agent(earth_miners)
    add_agent(muskcoin_launch)

    times = []
    mars_miners_blocks = []
    mars_miners_mars_blocks = []
    mars_miners_earth_blocks = []
    earth_miners_blocks = []
    earth_miners_mars_blocks = []
    earth_miners_earth_blocks = []
    simulation_length = 12          # hours
    max_time = (3600 * simulation_length)

    while current_time() < max_time:
        advance_time(60)

        times.append(current_time())

        if mars_miners.blockchain.height > 1:
            mars_miners_blocks.append(mars_miners.blockchain.height - 1)
            mars_miners_mars_blocks.append(len([block_id for block_id in mars_miners.blockchain.heights if mars_miners.id in block_id]))
            mars_miners_earth_blocks.append(len([block_id for block_id in mars_miners.blockchain.heights if earth_miners.id in block_id]))
        else:
            mars_miners_blocks.append(0)
            mars_miners_mars_blocks.append(0)
            mars_miners_earth_blocks.append(0)

        if earth_miners.blockchain.height > 1:
            earth_miners_blocks.append(earth_miners.blockchain.height - 1)
            earth_miners_mars_blocks.append(len([block_id for block_id in earth_miners.blockchain.heights if mars_miners.id in block_id]))
            earth_miners_earth_blocks.append(len([block_id for block_id in earth_miners.blockchain.heights if earth_miners.id in block_id]))
        else:
            earth_miners_blocks.append(0)
            earth_miners_mars_blocks.append(0)
            earth_miners_earth_blocks.append(0)

    return (
        distance,
        mars_miners,
        earth_miners,
        times, 
        mars_miners_blocks,
        mars_miners_mars_blocks,
        mars_miners_earth_blocks,
        earth_miners_blocks,
        earth_miners_mars_blocks,
        earth_miners_earth_blocks,
    )

def plot_single_run(
        distance,
        mars_miners,
        earth_miners,
        times, 
        mars_miners_blocks,
        mars_miners_mars_blocks,
        mars_miners_earth_blocks,
        earth_miners_blocks,
        earth_miners_mars_blocks,
        earth_miners_earth_blocks,
        ):

    max_blocks = max(
        max(mars_miners_mars_blocks) + max(mars_miners_earth_blocks),
        max(earth_miners_mars_blocks) + max(earth_miners_earth_blocks))

    fig, (mars_blocks, earth_blocks) = plt.subplots(nrows=2, sharex=True)

    mars_blocks.set_title("On Mars")
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

def plot_many_runs(distances, hashrate_ratios, runs_per_sample):
    results = []
    for distance in distances:
        results_for_distance = []
        for hashrate_ratio in hashrate_ratios:
            results_for_distance_and_hashrate = []
            for run in range(runs_per_sample):
                print("Running distance={} hashrate_ratio={} run={}".format(distance, hashrate_ratio, run))
                (distance,
                mars_miners,
                earth_miners,
                times, 
                mars_miners_blocks,
                mars_miners_mars_blocks,
                mars_miners_earth_blocks,
                earth_miners_blocks,
                earth_miners_mars_blocks,
                earth_miners_earth_blocks) = single_run(distance, hashrate_ratio)

                mars_blocks_ratio = mars_miners_mars_blocks[-1]/(mars_miners_mars_blocks[-1]+mars_miners_earth_blocks[-1])
                results_for_distance_and_hashrate.append(mars_blocks_ratio)
            results_for_distance.append(array(results_for_distance_and_hashrate).mean())
        results.append(results_for_distance)

    results = array(results).transpose()

    fig, ax = plt.subplots(nrows=1)
    mappable = ax.contourf(distances, hashrate_ratios, results, cmap="coolwarm")
    plt.colorbar(mappable)
    plt.show()

plot_many_runs(
    [1, 600, 1200, 1800],
    [1.0, 1.05, 1.1, 1.25, 1.5, 2.0, 3.0, 5.0, 10.0],
    25)

#single_run(600.0, 1.1)
