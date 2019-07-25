# Hash Wars

Have you ever wondered what would happen if Earth and Mars got into a
hash war over bitcoin in the far future?

Of course you have!  Now you don't need to wonder because you can
simulate.

Hash Wars is a tactical simulator for hashrate battles between miners
at relativistically large distances from each other.  It can be used
to model miners on Earth and Mars competing with hashrate over the
gulf which divides them (among many other possible scenarios).

There exist [other blockchain
simulators](https://github.com/citp/mining_simulator), some [even in
Python](https://github.com/kennethgoodman/mining-simulator), but they
are not intended for esoteric purposes such as ours.

## Quickstart

```
$ git clone https://github.com/unchained-capital/hashwars
$ cd hashwars
$ make
$ source environment.sh
# Simulate and view a miner on mars (720 light seconds)
# with 25% the hashrate of Earth
$ single-static-binary-simulation miner_launch 720 4 | plot blockchain_launch_history
```

## Simulator Core

Hash Wars is very simple:

* Time is modeled as a real number (`float`) but the simulation advances by discrete amounts of time.
* Space is one-dimensional.
* Miners are located at different locations with differing amounts of hashrate and their own local copies of a blockchain
* Miners produce blocks in accordance with their hashrate, the blockchain's difficulty, and (naive) Poisson statistics
* Blocks found by miners propagate through the simulation at a finite speed (of light)
* Each miner's blockchain obeys the consensus rules around heaviest chain, uncling, difficulty rebalancing, &c.

See the code in [`hashwars`](hashwars).

## Simulations

These primitives allow building simulations which capture the
essentials of futuristic hash combat.

```python
#
# Example simulation between two static, binary agents
#
# Put in simulations/earth_vs_mars.py
#

from hashwars import *

simulation_length = (12 * 60 * 60) # 12 hours
earth_position = 0
mars_position  = 720 # in light seconds

def earth_vs_mars(params):
    """Simulates Earth and Mars mining the same blockchain

    For simplicity, the simulation lasts only 12 hours and assumes
    miners on both Earth & Mars are single coordinated entities with a
    fixed hashrate at a fixed position, 720 light seconds apart.

    The simulation also assumes both start with an identical copy of a
    new, fresh blockchain: a genesis block.
    """

    # params is supplied by simulation runner
    (
	distance,            # distance between two agents
	hashrate_ratio,      # hashrate ratio between two agents
	argv                 # other options
    ) = params
    
    # Resets time to 0 and clears all agents
    reset_simulation()
    
    # Define the spatial extent of the simulation
    set_spatial_boundary(-1, mars_position + 1)

    # Setup the blockchains & miners
    genesis_block = Block("genesis", None, height=1, time=current_time())
    mars_blockchain = Blockchain("mars", genesis_block)
    earth_blockchain = Blockchain("earth", genesis_block)
    mars_miners  = Miners("mars-miners", 0, mars_blockchain, initial_hashrate=1.0)
    earth_miners = MajorityMiners("earth-miners", distance, earth_blockchain, initial_hashrate=hashrate_ratio)

    # Add miners to the simulation
    add_agent(minority_miners)
    add_agent(majority_miners)

    # Our results
    times = []
    weight_mined_on_mars = []
    weight_mined_on_earth = []

    # Run the simulation
    while current_time() < simulation_length:

        advance_time(60) # move simulation forward 60 seconds

        times.append(current_time())

        if mars_miners.blockchain.height > 1:
            weight_mined_on_mars.append(sum([block.weight for block in mars_miners.blockchain.blocks.values() if mars_miners.id in block.id]))
            weight_mined_on_earth.append(sum([block.weight for block in mars_miners.blockchain.blocks.values() if earth_miners.id in block.id]))
        else:
            weight_mined_on_mars.append(0)
            weight_mined_on_earth.append(0)

    # Can return anything that can be pickled
    return (distance, hashrate_ratio, times, weight_mined_on_mars, weight_mined_on_earth)
```

Once this simulation is in the `simulations` directory, you can run it

```
# Run once at a distance of 720 light seconds
# and a Earth/Mars hashrate ratio of 4
$ single-static-binary-simulation earth_vs_mars 720 4 --output /tmp/earth_vs_mars.dat
```

## Plotters

Plotters output data from simulations.  They accept the return values
of simulations as their first argument.

```python
#
# Example of a plotter
#
# Put in plotters/weight_mined_on_mars_over_time.py
# 

import matplotlib.pyplot as plt

from hashwars import write_plot

def weight_mined_on_mars_over_time(results, output_file, argv):
    (
        distance,
        hashrate_ratio,
        times,
        weight_mined_on_mars,
        weight_mined_on_earth,
    ) = results
    fig, ax = plt.subplots(nrows=1)
    ax.stackplot(times, weight_mined_on_mars, weight_mined_on_earth, labels=['Mars', 'Earth'], colors=['red', 'green'], baseline='zero')
    ax.legend()
    ax.set_ylabel('Weight')
    ax.set_xlabel('Seconds')
    write_plot(output_file)
```

Once this plotter is in the `plotters` directory, and assuming you ran
the `earth_vs_mars` simulator example above, you can run it

```
$ plot weight_mined_on_mars_over_time --input /tmp/earth_vs_mars.dat
```

## TODO

* Optimize...too much copying of data structures ATM
* Add support for agents moving at relativistic velocitiees with respect to each other
* Support 2 dimensional space
