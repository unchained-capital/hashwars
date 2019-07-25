from sys import stdout, stderr, stdin
from pickle import dumps, loads
from random import choice, random
from string import ascii_lowercase

from numpy import arange, array, concatenate
import matplotlib.pyplot as plt

from .duration import Duration

def random_string(length=10):
    return ''.join(choice(ascii_lowercase) for i in range(length))

def write_results(results, output_file):
    with (output_file or stdout.buffer) as output:
        output.write(dumps(results))

def read_results(input_file):
    return loads((input_file or stdin.buffer).read())

def write_plot(output_file):
    if output_file:
        plt.savefig(output_file)
    else:
        plt.show()

# 0.1,0.5,0.8,1.0,1.2 => array([0.1, 0.5, 0.8, 1.0, 1.2])
# [1,5,1] => array([1.0, 2.0, 3.0, 4.0])
# [0.1,1,0.3][1,5,1] => array([0.1, 0.4, 0.7, 1.0, 2.0, 3.0, 4.0])
def array_glob(spec):
    if spec.startswith('['):
        subarray_specs = spec[1:-1].split('][')
        values = array([])
        for subarray_spec in subarray_specs:
            start, stop, step = subarray_spec.split(',')
            values = concatenate((values, arange(float(start), float(stop), float(step))))
        return values
    else:
        return array([float(n) for n in spec.split(',')])

def notify(string):
    stderr.write(string)
    stderr.write("\n")
    stderr.flush()
