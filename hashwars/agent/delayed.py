from .base import Agent

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
