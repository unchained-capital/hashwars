from random import random

class Duration(object):

    def __init__(self, start, end):
        assert end > start,  "First parameter `start` should be less than second parameter `end`"
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

    def random_time(self):
        return self.start + (self.length * random())
