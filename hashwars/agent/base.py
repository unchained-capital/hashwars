from itertools import chain

from hashwars.state import log

class Agent(object):

    def __init__(self, id, location, active=True):
        self.id = id
        self.location = location
        self.transmissions_received = {}
        self.active = active
        self.priority = 0

    def __str__(self):
        return self.id

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
                self.react(action[0], action[1])
            else:
                self.act(action[0])

    def actions_for(self, duration):
        return []

    def distance_to(self, location):
        return abs(self.location - location)

    def receive(self, time, transmission):
        log("AGENT {} RECEIVE {}".format(self.id, transmission.id))
        self.transmissions_received[time] = transmission

    def act(self, time):
        pass

    def react(self, time, transmission):
        self.transmissions_received = {time:t for time,t in self.transmissions_received.items() if t != transmission}
