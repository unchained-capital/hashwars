from hashwars import *

FIXTURES = {
    'genesis_block_id': 'fixture-genesis_block',
    'blockchain_id': 'fixture-blockchain',
    'block_time': 600,
    'difficulty_readjustment_period': 2016,
    'initial_difficulty': 600,
    'max_difficulty_change_factor': 4,
}

def new_genesis_block(id=None, initial_difficulty=None):
    return Block(
        (id if id is not None else FIXTURES['genesis_block_id']),
        None,                   # parent is none by definition
        (initial_difficulty if initial_difficulty is not None else FIXTURES['initial_difficulty']),
        height=1)               # height is 1 by definition

def new_blockchain(id=None, 
                   genesis_block=None, 
                   block_time=None, 
                   difficulty_readjustment_period=None, 
                   initial_difficulty=None, 
                   max_difficulty_change_factor=None):
    return Blockchain(
            (id if id is not None else FIXTURES['blockchain_id']),
            (genesis_block if genesis_block is not None else new_genesis_block()),
            block_time=(block_time if block_time is not None else FIXTURES['block_time']), 
            difficulty_readjustment_period=(difficulty_readjustment_period if difficulty_readjustment_period is not None else FIXTURES['difficulty_readjustment_period']), 
            initial_difficulty=(initial_difficulty if initial_difficulty is not None else FIXTURES['initial_difficulty']), 
            max_difficulty_change_factor=(max_difficulty_change_factor if max_difficulty_change_factor is not None else FIXTURES['max_difficulty_change_factor']))
