import matplotlib.pyplot as plt
from numpy import array

from latinum import *


earth_mars_distance_in_light_seconds = (22 *  60) # 22 mins average distance

distance = 10 * earth_mars_distance_in_light_seconds
set_spatial_boundary(-1, distance + 1)

genesis_block = Block("genesis-block", None, difficulty=600, height=1)
mars_blockchain = Blockchain("mars-blockchain", genesis_block)
mars_miners  = Miners("mars-miners", 0, mars_blockchain, initial_hashrate=1.0)

class BlockchainLaunch(Transmission):
    pass

muskcoin_launch = BlockchainLaunch("muskcoin-launch", mars_miners, current_time())


earth_blockchain = Blockchain("earth-blockchain", genesis_block)
class EarthMiners(Miners):
    
    def react(self, transmission):
        if isinstance(transmission, (BlockchainLaunch,)):
            self.active = True
            log("MINER {} ACTIVATING".format(self.id))
        Miners.react(self, transmission)

earth_miners = EarthMiners("earth-miners", distance, earth_blockchain, initial_hashrate=10.0, difficulty_premium=1.0, active=False)

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
simulation_length = 36          # hours
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
        

fig, (ax1_blocks, ax2_blocks) = plt.subplots(nrows=2, sharex=True)

ax1_blocks.set_title("On Mars")
ax1_blocks.stackplot(times, mars_miners_mars_blocks, mars_miners_earth_blocks, labels=['Mined on Mars', 'Mined on Earth'], colors=['red', 'green'])
ax1_blocks.legend(loc='upper left')
ax1_blocks.set_ylabel('Counts')
ax1_blocks.axvline(x=distance, color='gray', linestyle='--', linewidth=0.5)
ax1_blocks.axvline(x=(2 * distance), color='gray', linestyle='--', linewidth=0.5)
ax1_ratio = ax1_blocks.twinx()
ax1_ratio.plot(times, array(mars_miners_mars_blocks)/(array(mars_miners_mars_blocks)+array(mars_miners_earth_blocks)), color='black')
ax1_ratio.set_ylabel('Ratio')
ax1_ratio.set_ylim(0, 1)

ax2_blocks.set_title("On Earth ({}x hashrate, {}x premium)".format(earth_miners.hashrate/mars_miners.hashrate, earth_miners.difficulty_premium))
ax2_blocks.stackplot(times, earth_miners_mars_blocks, earth_miners_earth_blocks, labels=['Mined on Mars', 'Mined on Earth'], colors=['red', 'green'])
ax2_blocks.legend(loc='upper left')
ax2_blocks.set_ylabel('Counts')
ax2_blocks.axvline(x=distance, color='gray', linestyle='--', linewidth=0.5)
ax2_blocks.axvline(x=(2 * distance), color='gray', linestyle='--', linewidth=0.5)
# ax2_blocks.set_xticks(
#     [hour * 3600 for hour in range(simulation_length)],
#     [str(hour) for hour in range(simulation_length)],
# )
ax2_blocks.set_xlabel("Seconds")

ax2_ratio = ax2_blocks.twinx()
ax2_ratio.plot(times, array(earth_miners_earth_blocks)/(array(earth_miners_mars_blocks)+array(earth_miners_earth_blocks)), color='black')
ax2_ratio.set_ylabel('Ratio')
ax2_ratio.set_ylim(0, 1)

plt.show()
