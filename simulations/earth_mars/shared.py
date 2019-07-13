from latinum import *

class EarthMiners(Miners):
    
    def react(self, time,  transmission):
        if isinstance(transmission, (BlockchainLaunch,)):
            self.active = True
            log("MINER {} ACTIVATING".format(self.id))
        Miners.react(self, time, transmission)

class BlockchainLaunch(Transmission):
    pass
