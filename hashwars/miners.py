from .agent import PoissonAgent
from .blockchain import Block, BlockchainTransmission
from .state import add_agent, log

class Miners(PoissonAgent):
    
    def __init__(self, id, location,  blockchain, initial_hashrate=1.0, difficulty_premium=1.0, active=True):
        PoissonAgent.__init__(self, id, location, active=active)
        self.blockchain = blockchain
        self.hashrate = initial_hashrate
        self.difficulty_premium = difficulty_premium

    def log_advance(self, duration):
        log("AGENT {} ADVANCE w/ {} BLOCKCHAIN {} {}".format(self.id, [transmission.id for transmission in self.transmissions_received.values()], self.blockchain.height, self.blockchain.weight))

    def mean_time_between_actions(self):
        return ((self.blockchain.difficulty * self.difficulty_premium) / self.hashrate)

    def act(self, time):
        block = Block(
            id="{}:{}".format(self.id, Block.new_id()), 
            previous=self.blockchain.tip,
            difficulty=(self.blockchain.difficulty * self.difficulty_premium),
            time=time,
        )
        if self.blockchain.add(block):
            log("MINER {} MINED {}".format(self.id, block.id))
            transmission = BlockchainTransmission(
                "{} (transmission)".format(self.blockchain),
                self,
                time,
                self.blockchain.copy())
            add_agent(transmission)

    def react(self, time,  transmission):
        if isinstance(transmission, (BlockchainTransmission,)):
            self.blockchain.merge(transmission.blockchain)
        PoissonAgent.react(self, time, transmission)
