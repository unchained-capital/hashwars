from sys import argv, stderr, stdout
from pickle import dumps

from simulations.earth_mars.shared import *

def single_run(simulation_length, distance, hashrate_ratio):
    simulation_length = int(simulation_length)
    distance = float(distance)
    hashrate_ratio = float(hashrate_ratio)
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

if __name__ == '__main__':
    if len(argv) < 4:
        stderr.write("usage: single_run.py HOURS DISTANCE HASHRATE_RATIO [OUTPUT_PATH]\n")
        exit(1)
    hours, distance, hashrate_ratio = argv[1:4]
    results = single_run(int(hours), float(distance), float(hashrate_ratio))
    output = dumps(results)

    if len(argv) > 4:
        with open(argv[4], 'wb') as f:
            f.write(output)
    else:
        stdout.buffer.write(output)
