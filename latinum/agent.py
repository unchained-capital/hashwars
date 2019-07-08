from itertools import chain
from math import floor
from numpy.random import poisson

from .state import log, get_spatial_boundary, agents_located_in, remove_agent

class Agent(object):

    def __init__(self, id, location, active=True):
        self.id = id
        self.location = location
        self.transmissions_received = {}
        self.active = active

    def log_advance(self, duration):
        log("AGENT {} ADVANCE w/ {}".format(self.id, [transmission.id for transmission in self.transmissions_received.values()]))

    def advance(self, duration):
        self.log_advance(duration)
        for action in sorted(
                chain(
                    self.actions_for(duration),
                    list(self.transmissions_received.items())),
                key=lambda action: action[0]):
            if action[1] is not None:
                self.react(action[1])
            else:
                self.act()

    def actions_for(self, duration):
        return []

    def distance_to(self, location):
        return abs(self.location - location)

    def receive(self, transmission, time):
        log("AGENT {} RECEIVE {}".format(self.id, transmission.id))
        self.transmissions_received[time] = transmission

    def act(self):
        pass

    def react(self, transmission):
        self.transmissions_received = {time:t for time,t in self.transmissions_received.items() if t != transmission}

class DelayedAgent(Agent):

    def __init__(self, id, location, act_at, active=True):
        Agent.__init__(self, id, location, active=active)
        self.act_at = act_at

    def actions_for(self, duration):
        actions = []
        if not self.active: return actions
        if duration.contains(self.act_at):
            actions.append([(self.act_at, None)])
        return actions


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

class PoissonAgent(Agent):

    def __init__(self, id, location, batch_size=200, active=True):
        Agent.__init__(self, id, location, active=active)
        self.batch_size=batch_size

    # https://docs.scipy.org/doc/numpy/reference/generated/numpy.random.poisson.html
    def actions_for(self, duration):
        actions = []
        if not self.active: return actions
        time = duration.start
        while time < duration.end:
            time_between_actions_sampling = poisson(self.mean_time_between_actions(), self.batch_size)
            index = 0
            while index < self.batch_size and time < duration.end:
                time_to_action = time_between_actions_sampling[index]
                time += time_to_action
                if time >= duration.end: break
                actions.append((time, None))
                index += 1
        return actions

    def mean_time_between_actions(self):
        return 1.0


class Transmission(Agent):

    def __init__(self, id, source, transmission_time, speed=1.0):
        Agent.__init__(self, id, source)
        self.source = self.location
        self.transmission_time = transmission_time
        self.speed = speed
        self.extent = [source, source]

    def advance(self, duration):
        distance_traveled = self.speed * duration.length
        new_extent = [self.extent[0] - distance_traveled, self.extent[1] + distance_traveled]
        #log("TRANS {} PROPAGATES [{} => {}]".format(self.id, self.extent, new_extent))
        agents_reached = set()
        boundary = get_spatial_boundary()
        if self.extent[0] >= boundary[0]:
            agents_reached.update(agents_located_in(new_extent[0], self.extent[0]))
        if self.extent[1] <= boundary[1]:
            agents_reached.update(agents_located_in(self.extent[1], new_extent[1]))
        
        for agent in sorted(agents_reached, key=lambda agent: agent.distance_to(self.source)):
            if agent == self: continue
            travel_time = agent.distance_to(self.source) / self.speed
            reception_time = self.transmission_time + travel_time
            agent.receive(self, reception_time)

        self.extent = new_extent
        if self.extent[0] < boundary[0] and self.extent[1] > boundary[1]:
            remove_agent(self.id)

    def receive(self, transmission, time):
        pass
