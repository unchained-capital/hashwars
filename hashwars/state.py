from os import environ
from sys import stderr

from .utils import Duration

_TIME = 0.0

_SPACE = [0, 1]

_AGENTS = {}

_LOG = []

_LOG_ID = None

def log(string):
    _LOG.append((_TIME, string))
    if environ.get('DEBUG'):
        _print_log_line(_TIME, string)

def set_log_id(string):
    global _LOG_ID
    _LOG_ID = string

def print_log():
    for time, string in _LOG:
        _print_log_line(time, string)

def _print_log_line(time, string):
    stderr.write("{}{}\t{}\n".format(
        "{}: ".format(_LOG_ID) if _LOG_ID is not None else "",
        time,
        string))

def current_time():
    return _TIME

def advance_time(amount):
    assert amount > 0
    global _TIME
    duration_end = _TIME + amount
    duration = Duration(_TIME, duration_end)
    log("TIME => {} AGENTS {}".format(duration_end, len(_AGENTS)))
    agents = [get_agent(agent_id) for agent_id in list(all_agent_ids())]
    for agent in reversed(sorted(agents, key=lambda agent: agent.priority)):
        agent.advance(duration)
    _TIME = duration_end

def get_spatial_boundary():
    return _SPACE

def set_spatial_boundary(x, y):
    assert y > x
    _SPACE[0] = x
    _SPACE[1] = y

def add_agent(agent):
    log("AGENT {} ADDED @ {}".format(agent.id, agent.location))
    _AGENTS[agent.id] = agent

def all_agent_ids():
    return _AGENTS.keys()

def get_agent(id):
    return _AGENTS[id]

def remove_agent(id):
    log("AGENT {} DELETED".format(id))
    del _AGENTS[id]

def agents_located_in(a, b):
    assert b > a
    return (agent for agent in _AGENTS.values() if agent.location >= a and agent.location <= b)

def reset_time():
    global _TIME
    _TIME = 0

def reset_log():
    global _LOG, _LOG_ID
    _LOG.clear()
    _LOG_ID = None

def reset_agents():
    global _AGENTS
    _AGENTS = {}

def reset_simulation():
    reset_agents()
    reset_time()
    reset_log()
