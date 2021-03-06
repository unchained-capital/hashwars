from argparse import ArgumentParser

from hashwars import *

_DEFAULT_MIN_TIME = 21600       # in seconds (6 hours)
_DEFAULT_TIME_DISTANCE_RATIO = 50

_DEFAULT_STEPS = 500            # count
_DEFAULT_STEP_VARIANCE = 0.1    # fraction of step size

_DEFAULT_PREMIUM = 1.0

_parser = ArgumentParser(description="The launch of a blockchain.")
_parser.add_argument("-t", "--min_time", help="Minimum simulation length (in seconds)", type=float, default=_DEFAULT_MIN_TIME)
_parser.add_argument("-R", "--time_distance_ratio", help="Set simulation length to this multiple of distance", type=float, default=_DEFAULT_TIME_DISTANCE_RATIO)
_parser.add_argument("--steps", help="Number of steps", type=int, default=_DEFAULT_STEPS)
_parser.add_argument("--premium", help="Hash premium", type=float, default=_DEFAULT_PREMIUM)

class MajorityMiners(Miners):
    
    def react(self, time,  transmission):
        if (not self.active) and isinstance(transmission, (BlockchainLaunch,)):
            self.active = True
            log("MINER {} ACTIVATING".format(self.id))
        Miners.react(self, time, transmission)

class BlockchainLaunch(Transmission):
    pass

def blockchain_launch(params):
    return _launch(params, 'blockchain')

def miner_launch(params):
    return _launch(params, 'miner')

def _launch(params, mode):
    distance, hashrate_ratio, argv = params
    distance = float(distance)
    hashrate_ratio = float(hashrate_ratio)
    args = _parser.parse_args(argv)
    
    run_id = random_string()
    reset_simulation()
    set_log_id(run_id)
    set_spatial_boundary(-1, distance + 1)

    genesis_block = Block("genesis", None, difficulty=600, height=1, time=current_time())
    minority_blockchain = Blockchain("minority", genesis_block)
    majority_blockchain = Blockchain("majority", genesis_block)
    minority_miners  = Miners("minority-miners", 0, minority_blockchain, initial_hashrate=1.0)
    majority_miners = MajorityMiners("majority-miners", distance, majority_blockchain, initial_hashrate=hashrate_ratio, difficulty_premium=args.premium, active=(mode == 'miner'))

    add_agent(minority_miners)
    add_agent(majority_miners)

    if mode == 'blockchain':
        genesis_block_mined = BlockchainLaunch("genesis-mined", minority_miners, current_time())
        add_agent(genesis_block_mined)
    
    times = []
    minority_miners_minority_weight = []
    minority_miners_majority_weight = []
    majority_miners_minority_weight = []
    majority_miners_majority_weight = []

    max_time = (distance * args.time_distance_ratio)
    if max_time < args.min_time: max_time = args.min_time

    step = max_time / args.steps
    steps_taken = 0
    while current_time() < max_time:
        advance_time(_jitter(step))
        steps_taken += 1

        times.append(current_time())

        if minority_miners.blockchain.height > 1:
            minority_miners_minority_weight.append(sum([block.weight for block in minority_miners.blockchain.blocks.values() if minority_miners.id in block.id]))
            minority_miners_majority_weight.append(sum([block.weight for block in minority_miners.blockchain.blocks.values() if majority_miners.id in block.id]))
        else:
            minority_miners_minority_weight.append(0)
            minority_miners_majority_weight.append(0)

        if majority_miners.blockchain.height > 1:
            majority_miners_minority_weight.append(sum([block.weight for block in majority_miners.blockchain.blocks.values() if minority_miners.id in block.id]))
            majority_miners_majority_weight.append(sum([block.weight for block in majority_miners.blockchain.blocks.values() if majority_miners.id in block.id]))
        else:
            majority_miners_minority_weight.append(0)
            majority_miners_majority_weight.append(0)

    notify("FINISHED {}: T={:0.4f} S={:0.4f} N={} | D={:0.4f} | HR={:0.4f} | Minority={:0.4f}".format(
        run_id,
        max_time,
        step,
        steps_taken,
        distance,
        hashrate_ratio,
        minority_miners_minority_weight[-1] / (minority_miners_minority_weight[-1] + minority_miners_majority_weight[-1])
    ))
    return (
        distance,
        hashrate_ratio,
        times, 
        minority_miners_minority_weight,
        minority_miners_majority_weight,
        majority_miners_minority_weight,
        majority_miners_majority_weight,
    )

def _jitter(step):
    return (step * (1 - _DEFAULT_STEP_VARIANCE/2)) + (step * _DEFAULT_STEP_VARIANCE * random())

def blockchain_launch_minority_weight_fraction(params):
    return _minority_weight_fraction(blockchain_launch(params))

def miner_launch_minority_weight_fraction(params):
    return _minority_weight_fraction(miner_launch(params))

def _minority_weight_fraction(results):
    (distance,
     hashrate_ratio,
     times, 
     minority_miners_minority_weight,
     minority_miners_majority_weight,
     majority_miners_minority_weight,
     majority_miners_majority_weight
    ) = results
    minority_weight_fraction = minority_miners_minority_weight[-1] / (minority_miners_minority_weight[-1] + minority_miners_majority_weight[-1])
    return (distance, hashrate_ratio, minority_weight_fraction)
