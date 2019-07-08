from .agent import PoissonAgent
from .blockchain import Block, BlockSequence, BlockSequenceTransmission
from .state import current_time, add_agent, log

class Miners(PoissonAgent):
    
    def __init__(self, id, location,  blockchain, initial_hashrate=1.0, active=True):
        PoissonAgent.__init__(self, id, location, active=active)
        self.blockchain = blockchain
        self.hashrate = initial_hashrate

    def log_advance(self, duration):
        log("AGENT {} ADVANCE w/ {} BLOCKCHAIN {} {}".format(self.id, [transmission.id for transmission in self.transmissions_received.values()], self.blockchain.sequence.height, self.blockchain.sequence.weight))

    def mean_time_between_actions(self):
        return (self.blockchain.difficulty.value / self.hashrate)

    def react(self, transmission):
        if isinstance(transmission, (BlockSequenceTransmission,)):
            self.blockchain.add(transmission.sequence)
        PoissonAgent.react(self, transmission)

    def act(self):
        block = Block(
            "{}:{}".format(self.id, Block.new_id()), 
            self.blockchain.sequence.tip.id,
            self.blockchain.difficulty.value) # this is conservative; miners may elect to deliver a weightier block?
        self.blockchain.add(BlockSequence(block))
        log("MINER {} MINED {}".format(self.id, block.id))
        transmission = BlockSequenceTransmission(
            "{} (transmission)".format(block.id),
            self.location,
            current_time(),
            BlockSequence(block))
        add_agent(transmission)
        
