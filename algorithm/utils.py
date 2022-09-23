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
import random 
import math 
import itertools 
import operator

from asrs.source import Job, Bundle
from asrs.kind import INPUT, OUTPUT
from asrs import Rack
from asrs.location import Location

from typing import Sequence, List, Any, Union, Generator, Tuple, Iterable, Set

from .exceptions import UnfeasibleSolution

Array = Any




def normaldist (mu: float, sigma: float, n: int = 1) -> Union[Array, int]:
    return np.random.normal(mu, sigma, n)


def bra (options: List, beta: float) -> Generator[Any, None, None]:
    L, _options = len(options), list(options)
    for _ in range(L):
        idx = int(math.log(random.random(), 1.0 - beta)) % len(_options)
        yield _options.pop(idx)


def postpone(id: int, job: Job, jobs: List[Job]) -> int:
    
    if job.kind == INPUT:
        # Get the position of the next job that is freeing a space 
        # big enough to host the entering bundles that have been postponed
        position = next( (i for i, j in enumerate(jobs[id+1:], start=id+1) if (
                                                                        j.kind == OUTPUT and  
                                                                        j.length >= job.length and 
                                                                        j.quantity >= job.quantity    
                                                                    ) ) , None)
        # If no position is found the solution is marked as unfeasible.
        if position is None:
            raise UnfeasibleSolution()
        # Otherwise, the job is postponed after the output that freed the space.
        return position + 1
    
    elif job.kind == OUTPUT:
        # Get teh position of the next entering job that stores the required product
        position = next( (i for i, j in enumerate(jobs[id+1:], start=id+1) if j.kind == INPUT and  j.code == job.code ) , None)
        # If no position is found the solution is marked as unfeasible.
        if position is None:
            raise UnfeasibleSolution()
        # Otherwise, the job is postponed.
        return position + 1



def process_input (job: Job, racks: Iterable[Rack], Br: float) -> Tuple[Rack, Location]:
    for rack in bra(sorted(racks, key=lambda rack: ( len(rack.crane.users), len(rack.crane.queue)  )), beta=Br):
        locs = [i for i in rack.locations if not i.frozen]
        random.shuffle(locs)
        for loc in locs:
            if loc.place(job):
                loc.frozen = True 
                return rack, loc 
    return None, None


def _can_retrieve(bundle: Bundle, taken_bundles: Set[Bundle]):
    if bundle.deep == 0:
        return True 
    
    loc = bundle.loc  
    # Check obstruction
    for i in loc.items[0]:
        if (type(i) == Bundle and 
            i not in taken_bundles and 
            ( (i.start <= bundle.start and i.end >= bundle.start) or  (i.start <= bundle.end and i.end >= bundle.end)  )
        ):
            return False 
    return True



def _aggregate(job: Job, bundles: Set[Bundle]) -> List[Job]:
    b = set(bundles)
    jobs = [] 
    for i, j in itertools.combinations(b, 2):
        if not i.taken and not j.taken and i.loc == j.loc and i.start == j.start:
            i.taken = True 
            j.taken = True 
            newjob = Job(job.arrival, job.depot, job.kind, job.code, job.length, i.weight + j.weight, (i.quality + j.quality) / 2, 2 )
            newjob.bundles = tuple(sorted([i, j], key=operator.attrgetter("deep")))
            jobs.append(newjob)
    
    for i in bundles:
        i.loc.frozen = True
        if not i.taken:
            newjob = Job(job.arrival, job.depot, job.kind, job.code, job.length, i.weight, i.quality, 1 )
            newjob.bundles = (i, )
            jobs.append(newjob)

    return jobs 



def process_output (job: Job, racks: Iterable[Rack], Br: float, Bb: float, weight_error: float) -> List[Job]:
    total_weight = 0 
    total_quality = 0 
    bundles_count = 0
    taken_bundles = set()
    for rack in bra(sorted(racks, key=lambda rack: (len(rack.crane.users), len(rack.crane.queue))), beta=Br):
        
        bundles = tuple( bundle
            for loc in rack.locations if not loc.frozen 
            for bundle in loc.items[0] + loc.items[1] if type(bundle) == Bundle and bundle.code == job.code
        )

        for bundle in bra(sorted(bundles, key= lambda i: (- i.quality, i.weight)), beta=Bb):
            if _can_retrieve(bundle, taken_bundles):
                taken_bundles.add(bundle)
                bundle.taken = False
                total_weight += bundle.weight 
                total_quality += bundle.quality 
                bundles_count += 1
            

            if total_weight >= job.weight - job.weight * weight_error:

                if total_weight > job.weight + job.weight * weight_error or total_quality / bundles_count < job.quality:
                    return None

                #print(job.weight, total_weight, job.quality, total_quality / bundles_count)
                resulting_jobs = _aggregate(job, taken_bundles)
                return resulting_jobs

    return None