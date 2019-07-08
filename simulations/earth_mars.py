from latinum import *

earth_mars_distance_in_light_seconds = (22 *  60) # 22 mins average distance
set_spatial_boundary(-1, earth_mars_distance_in_light_seconds + 1)

genesis_block = Block("genesis-block", None, difficulty=600, height=1)
mars_blockchain = Blockchain("mars-blockchain", genesis_block)
mars_miners  = Miners("mars-miners", 0, mars_blockchain, initial_hashrate=1.0)

class BlockchainLaunch(Transmission):
    pass

muskcoin_launch = BlockchainLaunch("muskcoin-launch",  current_time(), mars_miners.location)


earth_blockchain = Blockchain("earth-blockchain", genesis_block)
class EarthMiners(Miners):
    
    def react(self, transmission):
        if isinstance(transmission, (BlockchainLaunch,)):
            self.active = True
            log("MINER {} ACTIVATING".format(self.id))
        Miners.react(self, transmission)

earth_miners = EarthMiners("earth-miners", earth_mars_distance_in_light_seconds, earth_blockchain, initial_hashrate=10.0, active=False)

add_agent(mars_miners)
add_agent(earth_miners)
add_agent(muskcoin_launch)

while current_time() < 3600:
    advance_time(60)
