from .agent import PoissonAgent
from .blockchain import Block, BlockSequence, BlockSequenceTransmission
from .state import current_time, add_agent, log

class Miners(PoissonAgent):
    
    def __init__(self, id, location,  blockchain, initial_hashrate=1.0, difficulty_premium=1.0, active=True):
        PoissonAgent.__init__(self, id, location, active=active)
        self.blockchain = blockchain
        self.hashrate = initial_hashrate
        self.difficulty_premium = difficulty_premium

    def log_advance(self, duration):
        log("AGENT {} ADVANCE w/ {} BLOCKCHAIN {} {}".format(self.id, [transmission.id for transmission in self.transmissions_received.values()], self.blockchain.sequence.height, self.blockchain.sequence.weight))

    def mean_time_between_actions(self):
        return ((self.blockchain.difficulty.value * self.difficulty_premium) / self.hashrate)

    def react(self, transmission):
        if isinstance(transmission, (BlockSequenceTransmission,)):
            self.blockchain.add(transmission.sequence)
        PoissonAgent.react(self, transmission)

    def act(self):
        block = Block(
            "{}:{}".format(self.id, Block.new_id()), 
            self.blockchain.sequence.tip.id,
            (self.blockchain.difficulty.value * self.difficulty_premium))
        if self.blockchain.add(BlockSequence(block)):
            self.blocks_found.append(block)
            log("MINER {} MINED {}".format(self.id, block.id))

    def run_pre_actions(self):
        self.blocks_found = []

    def run_post_actions(self):
        if len(self.blocks_found) == 0: return
        sequence = BlockSequence(*self.blocks_found)
        transmission = BlockSequenceTransmission(
            "{} (transmission)".format(sequence),
            self,
            current_time(),
            sequence)
        add_agent(transmission)
