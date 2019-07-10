from .agent import PoissonAgent
from .blockchain import Block, BlockchainTransmission
from .state import current_time, add_agent, log

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

    def react(self, transmission):
        if isinstance(transmission, (BlockchainTransmission,)):
            self.blockchain.merge(transmission.blockchain)
        PoissonAgent.react(self, transmission)

    def act(self):
        block = Block(
            id="{}:{}".format(self.id, Block.new_id()), 
            previous=self.blockchain.tip,
            difficulty=(self.blockchain.difficulty * self.difficulty_premium),
            time=current_time(),
        )
        if self.blockchain.add(block):
            self.blocks_found.append(block)
            log("MINER {} MINED {}".format(self.id, block.id))

    def run_pre_actions(self):
        self.blocks_found = []

    def run_post_actions(self):
        if len(self.blocks_found) == 0: return
        transmission = BlockchainTransmission(
            "{} (transmission)".format(self.blockchain),
            self,
            current_time(),
            self.blockchain)
        add_agent(transmission)
