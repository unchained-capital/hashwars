from typing import Optional

from numpy import mean

from latinum.state import log
from latinum.agent import Agent, Transmission

from .block import Block
from .difficulty import Difficulty

class Blockchain():

    def __init__(self, 
                 id:str, 
                 genesis_block:Block, 
                 block_time: Optional[float] = 600.0, 
                 difficulty_readjustment_period: Optional[int] = 2016, 
                 initial_difficulty: Optional[float] = 600.0, 
                 max_difficulty_change_factor: Optional[int] = 4):

        assert genesis_block.height == 1
        assert genesis_block.previous is None

        assert block_time > 0
        assert difficulty_readjustment_period > 0
        assert initial_difficulty > 0
        assert max_difficulty_change_factor > 0

        self.id = id
        self.genesis_block = genesis_block
        self.block_time = block_time

        self.blocks  = {}
        self.blocks[self.genesis_block.id] = self.genesis_block
        self.heights = [self.genesis_block.id]
        self.height = len(self.heights)
        self.weight = self.genesis_block.difficulty

        self.difficulty_readjustment_period = difficulty_readjustment_period
        self.difficulty = initial_difficulty
        self.max_difficulty_change_factor = max_difficulty_change_factor
        self.inverse_max_difficulty_change_factor = (1/self.max_difficulty_change_factor)

        self.chain_params = (
            self.genesis_block.id,
            self.block_time,
            self.difficulty_readjustment_period,
            self.max_difficulty_change_factor,
        )

    def __str__(self):
        return "{{{} | {} -- {} : {} {}}}".format(self.id, self.genesis_block.id, self.tip.id, self.weight, self.height)

    @property
    def tip(self) -> Block:
        return self.blocks[self.heights[-1]]

    def merge(self, other: 'Blockchain') -> bool:
        log("BLOCKCHAIN {} MERGING {}".format(self, other))

        assert other.chain_params == self.chain_params

        if other.weight < self.weight:
            log("BLOCKCHAIN {} REJECT {} AS LIGHTER CHAIN".format(self, other))
            return False

        self.blocks = other.blocks
        self.heights = other.heights
        self.height = other.height
        self.weight = other.weight
        self.difficulty = other.difficulty
        return True
        
    def add(self, block: Block) -> bool:
        log("BLOCKCHAIN {} ADDING {}".format(self, block))
        if block.difficulty < self.difficulty:
            log("BLOCKCHAIN {} REJECT {} TOO LIGHT {} < {}".format(self, block, block.difficulty, self.difficulty))
            return False
        if block.previous.id != self.tip.id:
            if block.previous.id in self.blocks:
                log("BLOCKCHAIN {} REJECT {} STALE".format(self, block))
            else:
                log("BLOCKCHAIN {} REJECT {} UNKNOWN TIP {}".format(self, block, block.previous.id))
            return False
        self.blocks[block.id] = block
        self.heights.append(block.id)
        self.height += 1
        self.weight += block.difficulty
        if self.height % self.difficulty_readjustment_period == 0:
            self.readjust_difficulty()
        return True

    def readjust_difficulty(self):
        #
        # By construction,
        # 
        #      old_difficulty                           new_difficulty
        #   -------------------  = observed hashrate = -----------------
        #   observed block time                        target block time
        #
        # so new_difficulty = (target block time * old_difficulty) / (observed block time)
        # 
        log("BLOCKCHAIN {} DIFF READJ AT BLOCK {}".format(self, self.height))
        blocks = [self.blocks[block_id] for block_id in list(reversed(self.heights))[:self.difficulty_readjustment_period]]
        block_gaps = [(blocks[index+1].time - block.time) for index, block in enumerate(blocks[:-1])]
        observed_block_time = mean(block_gaps)
        old_difficulty = self.difficulty
        new_difficulty = (self.block_time * old_difficulty) / observed_block_time
        difficulty_change_ratio = new_difficulty / old_difficulty
        if difficulty_change_ratio > self.max_difficulty_change_factor:
            difficulty_change_ratio = self.max_difficulty_change_factor
        elif difficulty_change_ratio < self.inverse_max_difficulty_change_factor:
            difficulty_change_ratio = self.inverse_max_difficulty_change_factor
        self.difficulty = old_difficulty * difficulty_change_ratio
        log("BLOCKCHAIN {} DIFF. ADJ. {} => {}".format(self, old_difficulty, self.difficulty))
    

class BlockchainTransmission(Transmission):
    
    def __init__(self, 
                 id:str,  
                 source_agent:Agent, 
                 transmission_time:float,
                 blockchain:Blockchain,
                 speed: Optional[float] = 1.0):
        Transmission.__init__(self, id, source_agent, transmission_time, speed=speed)
        self.blockchain = blockchain
