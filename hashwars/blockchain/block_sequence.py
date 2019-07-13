from hashwars.agent import Transmission

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

    def __str__(self):
        return "".format(self.genesis.id, self.tip.id, self.weight,  self.height)

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

    def uncle_last_blocks(self, number):
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
        return (self.get_block(id) for id in list(reversed(self.heights))[:number])

    @property
    def weight(self, upto_height=None):
        return sum([self.get_block(id).weight for index, id in enumerate(self.heights) if (upto_height is None) or (index < upto_height)])

    def weight_after_height(self, min_height):
        return sum([self.get_block(id).weight for index, id in enumerate(reversed(self.heights)) if (min_height is None) or (index < min_height)])

    @property
    def previous(self):
        return self.genesis.previous
