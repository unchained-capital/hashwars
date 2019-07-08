from .agent import Transmission
from .utils import random_string

class Block():
    
    def __init__(self, id, previous, difficulty, height=None):
        self.id = id
        self.previous = previous
        self.difficulty = difficulty
        self.height = height

    @classmethod
    def new_id(self):
        return random_string(8)

    @property
    def weight(self):
        return self.difficulty

    def copy(self):
        # Don't include height
        return Block(id=self.id, previous=self.previous, difficulty=self.difficulty)

class BlockSequence():

    class InvalidSequence(ValueError):
        pass

    class InvalidExtension(ValueError):
        pass

    class InvalidBlock(ValueError):
        pass

    class InvalidUncling(ValueError):
        pass

    def __init__(self, *blocks):
        if len(blocks) == 0:
            raise self.InvalidSequence("At least one block must be in a sequence")

        self.genesis = blocks[0]
        self.blocks = {}
        self.blocks[self.genesis.id] = self.genesis
        self.heights = [self.genesis.id]

        self._add_blocks(*blocks[1:])

    def _add_blocks(self, *blocks):
        for block in blocks:
            self._add_block(block)

    def _add_block(self, block):
        current_tip = self.tip
        if block.previous != current_tip.id:
            raise self.InvalidExtension("Each block's id ({}) must match the next block's previous id ({})".format(current_tip.id, block.previous))

        current_height = self.height
        block.height = current_height + 1

        self.blocks[block.id] = block
        self.heights.append(block.id)

    def _assert_valid_height(self, height):
        if height > self.height:
            raise self.InvalidBlockSlice("Must be less than {}.".format(self.height))

    def add(self, sequence):
        for block_id in sequence.heights:
            self._add_block(sequence.blocks[block_id])

    def uncle_lastblocks(self, number):
        for block in self.get_last_blocks(number):
            self._uncle_block(block)

    def _uncle_block(self, block):
        current_tip = self.tip
        if current_tip.id != block.id:
            raise self.InvalidUncling("Can only uncle the tip of the sequence")
        block.height = None
        del self.blocks[block.id]
        self.heights.pop()

    def has_block(self, id):
        return id in self.blocks

    def get_block(self, id):
        try:
            return self.blocks[id]
        except KeyError:
            raise self.InvalidBlock("No such block: {}".format(id))

    @property
    def tip(self):
        return self.get_block(self.heights[-1])

    def __len__(self):
        return len(self.heights)

    @property
    def height(self):
        return len(self)

    def get_last_blocks(self, number):
        self._assert_valid_height(number)
        return (self.get_block(id) for id in reversed(self.heights)[:number])

    @property
    def id(self):
        height = len(self)
        if height == 1:
            return '{} [empty]'.format(self.genesis.id)
        elif height == 2:
            return '{} -> {}'.format(self.genesis.id, self.tip.id)
        elif height == 3:
            return '{} -- {} --> {} '.format(self.genesis.id, self.get_block(self.heights[1]).id, self.tip.id)
        else:
            return '{} -- [{} blocks] --> {} '.format(self.genesis.id, len(self) - 2, self.tip.id)

    @property
    def weight(self, upto_height=None):
        return sum([self.get_block(id).weight for index, id in enumerate(self.heights) if (upto_height is None) or (index < upto_height)])

    def weight_after_height(self, min_height):
        return sum([self.get_block(id).weight for index, id in enumerate(reversed(self.heights)) if (min_height is None) or (index < min_height)])

    @property
    def previous(self):
        return self.genesis.previous
        
class Blockchain():

    def __init__(self, id, genesis_block, block_time=600.0, difficulty_readjustment_period=2016, initial_difficulty=600.0, max_difficulty_change_factor=4):
        self.id = id
        self.sequence = BlockSequence(genesis_block)
        self.block_time = block_time
        self.difficulty = Difficulty(self, block_time=block_time, readjustment_period=difficulty_readjustment_period, initial_value=initial_difficulty, max_change_factor=max_difficulty_change_factor)

    def add(self, sequence):
        if not self.sequence.has_block(sequence.previous): return False
        previous_block = self.sequence.get_block(sequence.previous)
        assert previous_block is not None
        if previous_block.id != self.sequence.tip.id:
            if sequence.weight > self.sequence.weight_after_height(previous_block.height):
                uncled_blocks = self.sequence.height - previous_block.height
                self.sequence.uncle_last_blocks(uncled_blocks)
            else:
                return
        self.sequence.add(sequence)

class BlockSequenceTransmission(Transmission):
    
    def __init__(self, id,  source, transmission_time, sequence, speed=1.0):
        Transmission.__init__(self, id, source, transmission_time, speed=speed)
        self.sequence = sequence


class Difficulty():

    def __init__(self, blockchain, readjustment_period=2016, block_time=600.0, initial_value=600.0, max_change_factor=4):
        self.blockchain = blockchain
        self.readjustment_period = readjustment_period
        self.block_time = block_time
        self.value = initial_value
        self.max_change_factor = max_change_factor
        self.inverse_max_change_factor = (1/max_change_factor)

    def readjust(self):
        #
        # By construction,
        # 
        #      old_difficulty                           new_difficulty
        #   -------------------  = observed hashrate = -----------------
        #   observed block time                        target block time
        #
        # so new_difficulty = (target block time * old_difficulty) / (observed block time)
        # 
        blocks = self.blockchain.get_last_blocks(self.readjustment_period)
        block_gaps = [(blocks[index+1].time - block.time) for index, block in enumerate(blocks[:-1])]
        observed_block_time = mean(block_gaps)
        old_difficulty = self.value
        new_difficulty = (self.block_time * old_difficulty) / observed_block_time
        difficulty_change_ratio = new_difficulty / old_difficulty
        if difficulty_change_ratio > self.max_change_factor:
            difficulty_change_ratio = self.max_change_factor
        elif difficulty_change_ratio < self.inverse_max_change_factor:
            difficulty_change_ratio = self.inverse_max_change_factor
        self.value = old_difficulty * difficulty_change_ratio
