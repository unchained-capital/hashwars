from matplotlib import rcParams
import matplotlib.pyplot as plt
from numpy import sqrt, convolve, ones

from .utils import notify, read_results

COLORS = {
    'background': '#12121d',
    'white':      '#FFFFFF',
    'text':       '#efefef',
    'earth':      '#00a600',
    'mars':       '#d94221',
    'jupiter':    '#db850d',
    'saturn':     '#f5e536',
    'uranus':     '#d0edf0',
    'neptune':    '#4b74ed',
    'pluto':      '#540d03',
}

rcParams['figure.facecolor'] = COLORS['background']

rcParams['axes.facecolor'] = COLORS['background']
rcParams['axes.labelcolor'] = COLORS['text']

rcParams['text.color'] = COLORS['text']

rcParams['xtick.color'] = COLORS['text']
rcParams['ytick.color'] = COLORS['text']


def plot(namespace, name, input_file, output_file, plotter_argv):
    plotter = getattr(namespace, name)
    return plotter(read_results(input_file), output_file, plotter_argv)


def write_plot(fig, output_file):
    if output_file:
        plt.savefig(output_file, facecolor=fig.get_facecolor())
    else:
        plt.show()

def moving_average(series, window=None):
    if window is None:
        window = int(sqrt(len(series)))
    if window < 2:
        window = 2
    return convolve(series, ones(window), 'valid') / window

def format_percent(value, index=None, places=0):
    return '{{:,.{}%}}'.format(places).format(value)
