from sys import argv, stderr, stdout
from pickle import dumps
from concurrent.futures import ProcessPoolExecutor
from random import shuffle

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

def _single_run(params):
    distance, hashrate_ratio = params
    stderr.write("Running distance={} hashrate_ratio={}\n".format(distance, hashrate_ratio))
    stderr.flush()
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
    return (distance, hashrate_ratio, mars_blocks_ratio)

def many_runs(hours, runs_per_sample, distances, hashrate_ratios):
    stderr.write("HOURS: {}\n".format(hours))
    stderr.write("RUNS PER POINT: {}\n".format(runs_per_sample))
    stderr.write("DISTANCES: {} - {} ({} total)\n".format(distances[0], distances[-1], len(distances)))
    stderr.write("HASHRATE RATIOS: {} - {} ({} total)\n".format(hashrate_ratios[0], hashrate_ratios[-1], len(hashrate_ratios)))
    runs = []
    for distance in distances:
        for hashrate_ratio in hashrate_ratios:
            for run in range(runs_per_sample):
                runs.append((distance, hashrate_ratio))
    stderr.write("TOTAL RUNS: {}\n".format(len(runs)))
    stderr.flush()
    shuffle(runs)
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(_single_run, runs))
        mars_blocks_ratios = []
        for distance in distances:
            mars_blocks_ratios_at_distance = []
            results_at_distance = [result for result in results if result[0] == distance]
            for hashrate_ratio in hashrate_ratios:
                mars_blocks_ratios_at_distance_and_hashrate_ratio = []
                results_at_distance_and_hashrate_ratio = [result for result in results_at_distance if result[1] == hashrate_ratio]
                mars_blocks_ratio_at_distance_and_hashrate_ratio = array([result[2] for result in results_at_distance_and_hashrate_ratio]).mean()
                mars_blocks_ratios_at_distance.append(mars_blocks_ratio_at_distance_and_hashrate_ratio)
            mars_blocks_ratios.append(mars_blocks_ratios_at_distance)
        return (distances, hashrate_ratios, array(mars_blocks_ratios).transpose())

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
