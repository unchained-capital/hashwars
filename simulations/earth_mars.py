from latinum import *
import matplotlib.pyplot as plt

earth_mars_distance_in_light_seconds = (22 *  60) # 22 mins average distance
#earth_mars_distance_in_light_seconds = 1
set_spatial_boundary(-1, earth_mars_distance_in_light_seconds + 1)

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

earth_miners = EarthMiners("earth-miners", earth_mars_distance_in_light_seconds, earth_blockchain, initial_hashrate=10.0, difficulty_premium=5.0, active=False)

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
max_time = (3600 * 24)

while current_time() < max_time:
    advance_time(60)
    
    times.append(current_time())

    if len(mars_miners.blockchain.sequence) > 1:
        mars_miners_blocks.append(len(mars_miners.blockchain.sequence) - 1)
        mars_miners_mars_blocks.append(len([block_id for block_id in mars_miners.blockchain.sequence.heights if mars_miners.id in block_id]))
        mars_miners_earth_blocks.append(len([block_id for block_id in mars_miners.blockchain.sequence.heights if earth_miners.id in block_id]))
    else:
        mars_miners_blocks.append(0)
        mars_miners_mars_blocks.append(0)
        mars_miners_earth_blocks.append(0)

    if len(earth_miners.blockchain.sequence) > 1:
        earth_miners_blocks.append(len(earth_miners.blockchain.sequence) - 1)
        earth_miners_mars_blocks.append(len([block_id for block_id in earth_miners.blockchain.sequence.heights if mars_miners.id in block_id]))
        earth_miners_earth_blocks.append(len([block_id for block_id in earth_miners.blockchain.sequence.heights if earth_miners.id in block_id]))
    else:
        earth_miners_blocks.append(0)
        earth_miners_mars_blocks.append(0)
        earth_miners_earth_blocks.append(0)
        

fig, (ax1, ax2) = plt.subplots(nrows=2)
ax1.set_title("On Mars")
ax1.stackplot(times, mars_miners_mars_blocks, mars_miners_earth_blocks, labels=['Blocks from Mars', 'Blocks from Earth'])
ax1.legend(loc='upper left')
ax2.set_title("On Earth")
ax2.stackplot(times, earth_miners_mars_blocks, earth_miners_earth_blocks, labels=['Blocks from Mars', 'Blocks from Earth'])
ax2.legend(loc='upper left')
plt.show()
