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
import collections
import operator 

from typing import Tuple, Dict, List, Sequence 

from .source import Job, Bundle, Code


class Space (object):
    """ An instance of this class represents a space in a storage location """
    def __init__(self, start, length):
        self.start = start 
        self.length = length

    @property 
    def end (self):
        return self.start + self.length - 1

    def __repr__(self):
        return f"Space(start={self.start}, length={self.length})"


class Location (object):
    """ 
    An instance of this class represents a storage 
    location inside the warehouse. 
    """
    def __init__(self, rack, position: Tuple[int,int,int], length: int, deep: int, shelves_size: int):
        self.rack = rack
        self.position = np.asarray(position)
        self.length, self.deep = length, deep
        self.shelves_size = shelves_size
        #self.space = np.zeros(spaces)
        self.codes: Dict[Code, int] = collections.defaultdict(lambda: 0)
        #self.bundles: Dict[int, List[Bundle]] = collections.defaultdict(list)
        self.items: Dict[int, List[Space]] = { i: [Space(0, length)] for i in range(deep) }
        self.frozen = False


    def keepCode (self, code: Code) -> bool:
        """ Method to check if a certain product is stored in the location """
        return self.codes[code] > 0 


    def place (self, job: Job) -> bool:
        """ Method used to place the bundles moved by the Job into the Location """
        n, length, code = job.quantity, job.length, job.code 
        items = self.items

        # The job brings two bundles...
        if n == 2 and self.deep == 2:
            # if there's no space in at least one of the sheves
            # the placement is not possible
            if sum(1 for i in items[0] if type(i) == Space) == 0 or sum(1 for i in items[1] if type(i) == Space) == 0:
                return False

            # try the couples of space in first and second depth...
            for s1 in items[0]:
                
                # if s1 is a bundle and not a space...
                if type(s1) != Space or s1.length < length:
                    continue 

                for s2 in items[1]:

                    # if s2 is a bundle and not a space...
                    if type(s2) != Space or s2.length < length:
                        continue 

                    # if spaces do not overlap...
                    if s2.start > s1.end or s1.start > s2.end:
                        continue

                    # compute the space length
                    _start = max(s1.start, s2.start) 
                    _end = min(s1.end, s2.end)
                    _space = _end - _start + 1

                    # if the space is enough to place the bundles...
                    if _space >= length:
                        # place job bundles 
                        job.bundles[0].start = _start 
                        job.bundles[1].start = _start 
                        job.bundles[0].deep = 0 
                        job.bundles[1].deep = 1 
                        job.bundles[0].loc = self 
                        job.bundles[1].loc = self
                        items[0].append(job.bundles[0])
                        items[1].append(job.bundles[1])
                        
                        # update spaces
                        for i, space in enumerate((s1, s2)):

                            bundle = job.bundles[i]
                            
                            if space.start == _start and space.length == length:
                                # the space has exactly the same size of bundles 
                                items[i].remove(space) 
                            
                            elif space.start == _start:
                                # the space starts where the bundle is placed and 
                                # it therefore must be shortened
                                space.start = _start + length
                                space.length -= length
                                if space.length == 0: 
                                    items[i].remove(space)

                            elif space.end == _end:
                                # the space ends where the bundle ends 
                                space.length -= length 
                                if space.length == 0:
                                    items[i].remove(space)
                            
                            else: 
                                # the space is bigger than the bundle
                                space_end = space.end
                                space.length = _start - space.start
                                if space.length == 0:
                                    items[i].remove(space)
                                newspace = Space(_start + length, space_end - _end)
                                if newspace.length >= 1:
                                    items[i].append(newspace)

                        # sort items by starting position 
                        items[0].sort(key=operator.attrgetter("start"))
                        items[1].sort(key=operator.attrgetter("start"))

                        # update codes dict and job destination 
                        self.codes[code] += 2
                        job.destination = self.position + np.asarray([0, 0, (length/2 + _start) * self.shelves_size])
                        
                        # return that the bundles have been placed
                        return True

        elif n == 1 and self.deep == 1:
            space = next( (space for space in items[0] if type(space) == Space and space.length >= length), None)
            if space is not None:
                # place bundle
                _start = space.start 
                job.bundles[0].start = _start
                job.bundles[0].deep = 0
                job.bundles[0].loc = self 
                items[0].append(job.bundles[0])

                # update space 
                space.start = _start + length 
                space.length -= length 
                if space.length == 0:
                    items[0].remove(space)

                # sort items by starting position 
                items[0].sort(key=operator.attrgetter("start"))

                # update codes dict and job destination 
                self.codes[code] += 1
                job.destination = self.position + np.asarray([0, 0, (length/2 + _start) * self.shelves_size])
                return True
                

        elif n == 1 and self.deep == 2:
            # if there's no space in first depth the bundle cannot be placed
            if sum(1 for i in items[0] if type(i) == Space) == 0:
                return False

            # try the couples of space in first and second depth...
            for s1 in items[0]:
                
                # if s1 is a bundle and not a space...
                if type(s1) != Space or s1.length < length:
                    continue 

                # Placement is possible. But let's check before the second depth.
                for s2 in items[1]:

                    # if s2 is a bundle and not a space...
                    if type(s2) != Space or s2.length < length:
                        continue 

                    # if spaces do not overlap...
                    if s2.start > s1.end or s1.start > s2.end:
                        continue

                    # compute the space length
                    _start = max(s1.start, s2.start) 
                    _end = min(s1.end, s2.end)
                    _space = _end - _start + 1

                    # if the space is enough to place the bundles...
                    if _space >= length:
                        # Placement in second depth...
                        # place job bundle
                        job.bundles[0].start = _start 
                        job.bundles[0].deep = 1
                        job.bundles[0].loc = self 
                        items[1].append(job.bundles[0])
                        
                        # update space
                        if s2.start == _start and s2.length == length:
                            items[1].remove(s2) 
                            
                        elif s2.start == _start:
                            s2.start = _start + length
                            s2.length -= length
                            if s2.length == 0: 
                                items[1].remove(s2)

                        elif s2.end == _end:
                            s2.length -= length 
                            if s2.length == 0:
                                items[1].remove(s2)
                            
                        else: 
                            # the space is bigger than the bundle
                            s2 = space.end
                            s2.length = _start - s2.start
                            if s2.length == 0:
                                items[1].remove(s2)
                            newspace = Space(_start + length, space_end - _end)
                            if newspace.length >= 1:
                                items[1].append(newspace)

                        # sort items by starting position 
                        items[1].sort(key=operator.attrgetter("start"))

                        # update codes dict and job destination 
                        self.codes[code] += 1
                        job.destination = self.position + np.asarray([0, 0, (length/2 + _start) * self.shelves_size])
                        
                        # return that the bundles have been placed
                        return True
                
                # Bundle placed in first depth...
                # update bundle
                _start = s1.start 
                job.bundles[0].start = _start
                job.bundles[0].deep = 0
                job.bundles[0].loc = self 
                items[0].append(job.bundles[0])
                # update space
                s1.start += length 
                s1.length -= length 
                if s1.length <= 1:
                    items[0].remove(s1)
                
                items[0].sort(key=operator.attrgetter("start"))
                self.codes[code] += 1
                job.destination = self.position + np.asarray([0, 0, (length/2 + _start) * self.shelves_size])
                return True

        return False 



    def take (self, job: Job) -> None:
        """ Method used to take the bundles required by the Job from the Location """
        n, code, length = job.quantity, job.code, job.length 
        items = self.items 

        for bundle in job.bundles:
            location = items[bundle.deep] 
            idx = location.index(bundle)

            before = location[idx - 1] if idx > 0 else None 
            after = location[idx + 1] if idx < len(location) - 1 else None 

            if type(before) == Space:
                if type(after) == Space:
                    before.length += length + after.length
                    location.remove(after)
                else:
                    before.length += length 

            elif type(after) == Space:
                after.start = bundle.start
                after.length += length
                
            items[bundle.deep].remove(bundle)
        
        items[0].sort(key=operator.attrgetter("start"))
        items[1].sort(key=operator.attrgetter("start"))
        self.codes[job.code] -= n
        job.destination = self.position + np.asarray([0, 0, (length/2 + job.bundles[0].start) * self.shelves_size])
        return True