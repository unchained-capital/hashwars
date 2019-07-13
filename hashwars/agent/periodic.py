from math import floor

from .base import Agent

class PeriodicAgent(Agent):

    def __init__(self, id, location, start_at, period=1, active=True):
        Agent.__init__(self, id, location, active=active)
        self.start_at = start_at
        self.period = period

    # FIXME -- this is broken...
    def actions_for(self, duration):
        actions  = []
        if not self.active: return actions
        #
        # (...)...[===|...
        #
        if self.start_at > duration.end: return actions
        #
        # (...[===|===|-)-|===...
        #
        if self.start_at > duration.start:
            return floor((duration.end - self.start_at) / self.period)
        #
        # [==|==|==|-(-|==|==|-)-|==|==...
        #
        else:
            num_actions_before_start = floor((duration.start - self.start_at) / self.period)
            last_action_at =  self.start_at + (num_actions_before_start * self.period)
            return floor((duration.end - last_action_at) / self.period)
