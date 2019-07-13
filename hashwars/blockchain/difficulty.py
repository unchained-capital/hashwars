from hashwars.state import log

class Difficulty():

    def __init__(self, blockchain, readjustment_period=2016, block_time=600.0, initial_value=600.0, max_change_factor=4):
        self.blockchain = blockchain
        self.readjustment_period = readjustment_period
        self.block_time = block_time
        self.value = initial_value
        self.max_change_factor = max_change_factor
        self.inverse_max_change_factor = (1/max_change_factor)

