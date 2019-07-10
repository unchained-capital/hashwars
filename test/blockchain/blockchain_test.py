from test.base import *
from test.factories import new_blockchain, new_genesis_block

class TestNewBlockchain(object):

    def setup(self):
        self.blockchain = new_blockchain()
        self.genesis_block = self.blockchain.genesis_block

    def test_length_is_unity(self):
        assert self.blockchain.height == 1

    def test_weight_is_genesis_block_difficulty(self):
        assert self.blockchain.weight == self.genesis_block.difficulty

    def test_add_block_with_insufficient_difficulty_and_missing_(self):
        old_height = self.blockchain.height
        old_weight = self.blockchain.weight
        old_difficulty = self.blockchain.difficulty
        block = Block('insufficient-difficulty', self.genesis_block.id, self.blockchain.difficulty - 1)
        assert not self.blockchain.add(block)
        assert self.blockchain.height == old_height
        assert self.blockchain.weight == old_weight
        assert self.blockchain.difficulty == old_difficulty
        assert block.height is None

    def test_add_block_with_sufficient_difficulty(self):
        old_height = self.blockchain.height
        old_weight = self.blockchain.weight
        old_difficulty = self.blockchain.difficulty
        block = Block('insufficient-difficulty', self.genesis_block.id, self.blockchain.difficulty - 1)
        assert not self.blockchain.add(block)
        assert self.blockchain.height == old_height
        assert self.blockchain.weight == old_weight
        assert self.blockchain.difficulty == old_difficulty
        assert block.height is None
