from itertools import chain

from latinum.state import log

class Agent(object):

    def __init__(self, id, location, active=True):
        self.id = id
        self.location = location
        self.transmissions_received = {}
        self.active = active
        self.priority = 0

    def log_advance(self, duration):
        log("AGENT {} ADVANCE w/ {}".format(self.id, [transmission.id for transmission in self.transmissions_received.values()]))

    def advance(self, duration):
        self.log_advance(duration)
        self.run_pre_actions()
        for action in sorted(
                chain(
                    self.actions_for(duration),
                    list(self.transmissions_received.items())),
                key=lambda action: action[0]):
            if action[1] is not None:
                self.react(action[1])
            else:
                self.act()
        self.run_post_actions()

    def actions_for(self, duration):
        return []

    def distance_to(self, location):
        return abs(self.location - location)

    def receive(self, transmission, time):
        log("AGENT {} RECEIVE {}".format(self.id, transmission.id))
        self.transmissions_received[time] = transmission

    def act(self):
        pass

    def run_pre_actions(self):
        pass

    def run_post_actions(self):
        pass

    def react(self, transmission):
        self.transmissions_received = {time:t for time,t in self.transmissions_received.items() if t != transmission}

