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
import numpy as np
from typing import Tuple, Sequence, Generator

from .location import Location
from .source import Job 
from .machine import Crane, Lift 


class Rack (object):

    """ An instance of this class represents a storage rack """
    
    def __init__(self, *, ncorridors: int, nlevels: int, corridor_size: int, level_size: int, 
                position: Tuple[int, int, int], 
                nshelves: int, shelves_deep: int, shelves_size: int, 
                crane: Crane, lifts: Sequence[Lift]):
        self.crane = crane
        self.lifts = lifts
        self.position = np.asarray(position)
        self.locations = tuple(Location(self, [x*corridor_size, y*level_size, position[2]], nshelves, shelves_deep, shelves_size)
                                      for y in range(nlevels)
                                    for x in range(ncorridors)
                                 for _ in range(2))


    def place (self, job: Job, position : Tuple[int, int, int] = (0,0,0)) -> Generator[Location, None, None]:
        pos = np.asarray(position)
        locations = sorted(self.locations, key=lambda loc: (pos - loc.position).sum())
        for loc in locations:
            if not loc.frozen and loc.place(job):
                yield loc


    def take (self, job: Job, position : Tuple[int, int, int] = (0,0,0)) -> Generator[Location, None, None]:
        pos = np.asarray(position)
        locations = sorted(self.locations, key=lambda loc: (pos - loc.position).sum())
        for loc in locations:
            if not loc.frozen and loc.take(job):
                yield loc