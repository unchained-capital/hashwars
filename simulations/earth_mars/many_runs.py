from sys import argv, stderr, stdout
from pickle import dumps
from numpy import arange, array

from simulations.earth_mars.single_run import single_run

# 0.1,0.4,0.5,0.8,1.0,2.0,3.0,4.0
#
# [0.1,4.0,0.1]
def _parse_array(s):
    if s.startswith('['):
        start, stop, step = s[1:-1].split(',')
        return arange(float(start), float(stop), float(step))
    else:
        return array([float(n) for n in s.split(',')])

def many_runs(hours, runs_per_sample, distances, hashrate_ratios):
    mars_blocks_ratios = []
    for distance in distances:
        mars_blocks_ratios_for_distance = []
        for hashrate_ratio in hashrate_ratios:
            mars_blocks_ratios_for_distance_and_hashrate = []
            for run in range(runs_per_sample):
                print("Running distance={} hashrate_ratio={} run={}".format(distance, hashrate_ratio, run))
                (distance,
                mars_miners,
                earth_miners,
                times, 
                mars_miners_blocks,
                mars_miners_mars_blocks,
                mars_miners_earth_blocks,
                earth_miners_blocks,
                earth_miners_mars_blocks,
                earth_miners_earth_blocks) = single_run(hours, distance, hashrate_ratio)

                mars_blocks_ratio = mars_miners_mars_blocks[-1]/(mars_miners_mars_blocks[-1]+mars_miners_earth_blocks[-1])
                mars_blocks_ratios_for_distance_and_hashrate.append(mars_blocks_ratio)
            mars_blocks_ratios_for_distance.append(array(mars_blocks_ratios_for_distance_and_hashrate).mean())
        mars_blocks_ratios.append(mars_blocks_ratios_for_distance)

    mars_blocks_ratios = array(mars_blocks_ratios).transpose()
    return (distances, hashrate_ratios, mars_blocks_ratios)


if __name__ == '__main__':
    if len(argv) < 5:
        stderr.write("usage: many_runs.py HOURS RUNS_PER_SAMPLE DISTANCES HASHRATE_RATIOS [OUTPUT_PATH]\n")
        exit(1)
    hours, runs_per_sample, distances, hashrate_ratios = argv[1:5]
    results = many_runs(int(hours), int(runs_per_sample), _parse_array(distances), _parse_array(hashrate_ratios))
    output = dumps(results)

    if len(argv) > 5:
        with open(argv[5], 'wb') as f:
            f.write(output)
    else:
        stdout.buffer.write(output)
