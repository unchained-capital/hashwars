from concurrent.futures import ProcessPoolExecutor
from random import shuffle

from .utils import notify, read_results

def plot(namespace, name, input_file, output_file, plotter_argv):
    plotter = getattr(namespace, name)
    return plotter(read_results(input_file), output_file, plotter_argv)
