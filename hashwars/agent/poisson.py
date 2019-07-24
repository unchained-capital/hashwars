from math import exp, factorial
from random import random

from .base import Agent

# https://towardsdatascience.com/the-poisson-distribution-and-poisson-process-explained-4e2cb17d459
class PoissonAgent(Agent):

    MAX_FACTORIAL = 1000 # boot time cost
    FACTORIALS = [factorial(k) for k in range(MAX_FACTORIAL)]
    MAX_ACTIONS = 10

    def __init__(self, id, location, max_actions_per_advance=None, active=True):
        Agent.__init__(self, id, location, active=active)
        self.max_actions_per_advance = (max_actions_per_advance if max_actions_per_advance is not None else self.MAX_ACTIONS)
        assert self.max_actions_per_advance <= self.MAX_FACTORIAL
    
    def actions_for(self, duration):
        actions = []
        if not self.active: return actions
        for action in range(self.number_of_actions_for(duration)):
            actions.append((duration.random_time(), None))
        return actions

    def number_of_actions_for(self, duration):
        # This is the constant 'lambda' for the given `duration`
        l = (1 / self.mean_time_between_actions()) * duration.length
        # We truncate at a maximum value of k
        k_max = self.max_actions_per_advance
        # These are the probabilities p_k for k events to occur in the
        # given `duration`
        probabilities = [exp(-1 * l) * (pow(l, k) / self.FACTORIALS[k]) for k in range(k_max)]
        # Draw a random value in (0,1)
        r = random()
        # Return first k for which the partial sum of p_j {j=0..k} is less than r
        for k, p_k in enumerate(probabilities):
            if r <= p_k:
                return k
            else:
                r -= p_k
        # If we reach this point, just return the max k -- this is an
        # approximation, but we shouldn't reach here frequently anyway
        return k_max

    def mean_time_between_actions(self):
        return 1.0
