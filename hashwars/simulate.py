from concurrent.futures import ProcessPoolExecutor
from random import shuffle

from .utils import notify

def single_static_binary_simulation(namespace, name, distance, hashrate_ratio, simulator_argv):
    simulator = getattr(namespace, name)
    distance = float(distance)
    hashrate_ratio = float(hashrate_ratio)
    notify("SIMULATION: {}".format(name))
    notify("DISTANCE: {}".format(distance))
    notify("HASHRATE RATIO: {}".format(hashrate_ratio))
    notify("ARGV: {}".format(simulator_argv))
    return simulator((distance, hashrate_ratio, simulator_argv))
    
def many_static_binary_simulations(namespace, name, count, distances, hashrate_ratios, simulator_argv):
    simulator = getattr(namespace, name)
    notify("SIMULATION: {}".format(name))
    notify("DISTANCES: {} - {} ({} total)".format(distances[0], distances[-1], len(distances)))
    notify("HASHRATE RATIOS: {} - {} ({} total)".format(hashrate_ratios[0], hashrate_ratios[-1], len(hashrate_ratios)))
    notify("COUNT: {}".format(count))
    notify("ARGV: {}".format(simulator_argv))

    runs = []
    for distance in distances:
        for hashrate_ratio in hashrate_ratios:
            for run in range(count):
                runs.append((distance, hashrate_ratio, simulator_argv))

    notify("TOTAL RUNS: {}".format(len(runs)))
    notify("Randomizing runs...")
    shuffle(runs)
    notify("Starting simulations...")
    with ProcessPoolExecutor() as executor:
        results_list = list(executor.map(simulator, runs))
        notify("Obtained results...")
        results_matrix = []
        for distance in distances:
            results_row_at_distance = []
            results_at_distance_list = [result for result in results_list if result[0] == distance]
            for hashrate_ratio in hashrate_ratios:
                results_row_at_distance.append([result[2] for result in results_at_distance_list if result[1] == hashrate_ratio])
            results_matrix.append(results_row_at_distance)
        notify("Collated results")
        return (distances, hashrate_ratios, results_matrix)
