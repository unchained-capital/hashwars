from random import choice, random
from string import ascii_lowercase

from .duration import Duration

def random_string(length=10):
    return ''.join(choice(ascii_lowercase) for i in range(length))
