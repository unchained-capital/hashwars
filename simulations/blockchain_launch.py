from argparse import ArgumentParser

from hashwars import random_string, notify, set_log_id
from .shared import *

_DEFAULT_HOURS = 6
_DEFAULT_STEP = 60

_parser = ArgumentParser(description="The launch of a blockchain.")
_parser.add_argument("--hours", help="Number of hours to simulate", type=int, default=_DEFAULT_HOURS)
_parser.add_argument("--step", help="Step length in seconds", type=int, default=_DEFAULT_STEP)

def blockchain_launch(params):
    distance, hashrate_ratio, argv = params
    distance = float(distance)
    hashrate_ratio = float(hashrate_ratio)
    args = _parser.parse_args(argv)
    
    run_id = random_string()
    reset_simulation()
    set_log_id(run_id)
    set_spatial_boundary(-1, distance + 1)

    genesis_block = Block("genesis", None, difficulty=600, height=1)
    minority_blockchain = Blockchain("minority", genesis_block)
    minority_miners  = Miners("minority-miners", 0, minority_blockchain, initial_hashrate=1.0)

    genesis_block_mined = BlockchainLaunch("genesis-mined", minority_miners, current_time())

    majority_blockchain = Blockchain("majority", genesis_block)

    majority_miners = MajorityMiners("majority-miners", distance, majority_blockchain, initial_hashrate=hashrate_ratio, difficulty_premium=1.0, active=False)

    add_agent(minority_miners)
    add_agent(majority_miners)
    add_agent(genesis_block_mined)

    times = []
    minority_miners_minority_weight = []
    minority_miners_majority_weight = []
    majority_miners_minority_weight = []
    majority_miners_majority_weight = []
    max_time = (3600 * args.hours)

    while current_time() < max_time:
        advance_time(args.step)

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

    return (
        distance,
        hashrate_ratio,
        times, 
        minority_miners_minority_weight,
        minority_miners_majority_weight,
        majority_miners_minority_weight,
        majority_miners_majority_weight,
    )

def blockchain_launch_minority_weight_ratio(params):
    (distance,
     hashrate_ratio,
     times, 
     minority_miners_minority_weight,
     minority_miners_majority_weight,
     majority_miners_minority_weight,
     majority_miners_majority_weight
    ) = blockchain_launch(params)
    return (distance, hashrate_ratio, minority_miners_minority_weight[-1] / (minority_miners_minority_weight[-1] + minority_miners_majority_weight[-1]))
