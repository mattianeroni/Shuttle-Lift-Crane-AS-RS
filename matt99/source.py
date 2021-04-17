import random
import numpy as np

from matt99 import kind



def source (simtime, avgArrival, depots, kinds, codes, quantities):
    t = 0.0
    while t < simtime:
        t += random.expovariate(1 / avgArrival)
        code, length = select(codes)
        yield Job(t, select(depots), select(kinds), code, length, select(quantities))


def single_job (depots, codes, quantities):
    code, length = select(codes)
    return Job(0, select(depots), kind.INPUT, code, length, select(quantities))


def select (options):
    return random.choices(tuple(options.keys()), tuple(options.values()), k=1)[0]



class Job (object):

    def __init__(self, arrival, depot, kind, code, length, quantity):
        self.arrival = arrival
        self.depot = depot
        self.kind = kind
        self.code = code
        self.quantity = quantity
        self.length = length
        self.bundle = np.full((length, quantity), code)

        self.destination = None
        self.history = dict()

