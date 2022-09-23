"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
This file is part of the collaboration between University of Parma, Universitat 
Oberta de Catalunya, and Matter Srl.

The object of the collaboration is (i) the development of a discrete event simulation 
for the Matt99 system (i.e., a Shuttle-Lift-Crane based Automated Storage/Retrieval 
System sold by the company), (ii) the development of a web application so that the 
simulation can be used by everybody (even who is not able of programming), (iii) the 
development aand validation of a biased-randomised discrete event heuristic 
able to improve the system performance.


Written by: Mattia Neroni, Ph.D, Eng. (May 2020)
Author's contact: mattianeroni@yahoo.it
Author's website: https://mattianeroni.github.io

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
import random
import numpy as np

from typing import Optional

from asrs import kind



def source (simTime, maxJobs, avgArrival, depot_prob, code_prob, quantity_prob, quality_prob, kind_prob, ):
    """
    Generator of jobs. 

    :param simTime: The simulation time.
    :param maxJobs: The maximum number of operations to generate.
    :param avgArrival: The interarrival between operations.
    :param depot_prob: The possible depots and the respective probabilities.
    :param code_prob: The managed products and their probability to be required.
    :param quantity_prob: The number of bundles required and their probbility.
    :param quality_prob: The probability for each quality level.
    :param kind_prob: The probabilities to have an input or an output oepration.
    """
    t, counter = 0.0, 0
    while t < simTime and counter < maxJobs:
        t += random.expovariate(1 / avgArrival)
        code = __select(code_prob)
        k = __select(kind_prob)
        depot = __select(depot_prob[k])
        qty = __select(quantity_prob[k])
        quality = __select(quality_prob[k])
        counter += 1
        yield Job(t, depot, k, code, code.length, code.weight * qty, quality, qty)


def single_job (depot_prob, code_prob, quantity_prob, quality_prob, kind_prob):
    """ 
    Generate a new job.
    
    :param depot_prob: The possible depots and the respective probabilities.
    :param code_prob: The managed products and their probability to be required.
    :param quantity_prob: The number of bundles required and their probability.
    :param quality_prob: The probability for each quality level.
    :param kind_prob: The probabilities to have an input or an output oepration.
    """
    k = __select(kind_prob)
    code = __select(code_prob)
    qty = __select(quantity_prob[k])
    quality = __select(quality_prob[k])
    return Job(0, __select(depot_prob), k, code, code.length, code.weight * qty, quality, qty)


def __select (options : dict):
    """ Function to select an elements between several possible options """
    return random.choices(tuple(options.keys()), tuple(options.values()), k=1)[0]



class Code (object):
    """
    An instance of this class represents a type of produt stored inside the warehouse.
    """
    def __init__(self, length : int, weight : int):
        self.length = length 
        self.weight = weight
    

class Bundle (object):
    """ An instance of this class represents one of the bundles handled by the system """
    def __init__(self, code: Code, weight: int, quality: int, start: Optional[int] = None):
        self.code = code 
        self.weight = weight 
        self.quality = quality
        self.start = start 
        self.deep = None
        self.loc = None
        self.taken = False # Used just by algorithm


    @property
    def length(self):
        return self.code.length

    @property 
    def end (self):
        return self.start + self.code.length - 1

    def __repr__(self):
        return f"Bundle(start={self.start}, length={self.length}, deep={self.deep})"



class Job (object):
    """
    Operation to be made by the warehouse.
    """
    def __init__(self, arrival: float, depot: int, _kind: str, code: Code, 
                length: int, weight: int, quality: int, quantity: int):
        """
        :param arrival: The arrival time of operation.
        :param depot: The depot interested by the operation.
        :param _kind: Input or output. 
        :param length: The length of moved bundles (in shelves).
        :param weight: The OVERALL moved weight (in case of two bundles it's the total weight).
        :param quality: The quality level associated to the interested bundles.
        :param quantity: The number of moved bundles (one or two).

        :attr bundle: A matricial representation of bundles.
        :attr history: A collection of events that interest the job.
        :attr destination: The position interested by the operation.
        """
        self.arrival = arrival
        self.depot = depot
        self.kind = _kind
        self.code = code
        self.length = length
        self.weight = weight 
        self.quality = quality
        self.quantity = quantity
        #self.bundle = np.full((length, quantity), code)

        self.bundles = tuple( Bundle(code, weight // quantity, quality) for _ in range(quantity)) if _kind == kind.INPUT else tuple()

        self.destination = None
        self.history = dict()

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        result.destination = None 
        result.history = {} 
        return result


