from random import choice
from string import ascii_lowercase

def random_string(length=10):
    return ''.join(choice(ascii_lowercase) for i in range(length))

class Duration(object):

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return "[{} => {}]".format(self.start, self.end)

    @property
    def length(self):
        return (self.end - self.start)

    def contains(self, time):
        if time < self.start: return False
        if time > self.end: return False
        return True
