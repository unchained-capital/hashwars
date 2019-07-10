from .base import Agent

from latinum.state import log, get_spatial_boundary, agents_located_in, remove_agent

class Transmission(Agent):

    def __init__(self, id, source_agent, transmission_time, speed=1.0):
        Agent.__init__(self, id, source_agent.location)
        self.source_agent = source_agent
        self.source = self.location
        self.transmission_time = transmission_time
        self.speed = speed
        self.extent = [self.source, self.source]
        self.priority = 1

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
            if agent == self.source_agent: continue
            travel_time = agent.distance_to(self.source) / self.speed
            reception_time = self.transmission_time + travel_time
            agent.receive(self, reception_time)

        self.extent = new_extent
        if self.extent[0] < boundary[0] and self.extent[1] > boundary[1]:
            remove_agent(self.id)

    def receive(self, transmission, time):
        pass
