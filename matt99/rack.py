import numpy as np
import collections


class Location (object):

    def __init__(self, position, spaces, size):
        self.position = np.asarray(position)
        self.length, self.deep = spaces
        self.size = size
        self.space = np.zeros(spaces)
        self.codes = collections.defaultdict(lambda: 0)
        self.frozen = False


    def __getitem__ (self, index):
        return self.space[index]


    def __setitem__(self, index, value):
        self.space[index] = values


    def keepCode (self, code):
        return True if self.codes[code] > 0 else False


    def place (self, job):
        bundle, code = job.bundle, job.code
        space = self.space
        length, deep = bundle.shape

        if np.where(space == 0, 1, 0).sum() < length * deep:
            return False

        if deep == 2:
            for i in range(length, self.length + 1):
                if (space[i-length:i, :] * bundle).sum() == 0:
                    space[i-length:i, :] = bundle
                    self.codes[code] += 1
                    job.destination = self.position + np.asarray([0,0,(length/2 + i-length) * self.size])
                    return True
        elif deep == 1:
            for i in range(length, self.length + 1):
                if (space[i-length:i, 1:] * bundle).sum() == 0:
                    if (space[i-length:i, :1] * bundle).sum() == 0:
                        space[i - length:i, :1] = bundle
                    else:
                        space[i-length:i, 1:] = bundle

                    self.codes[code] += 1
                    job.destination = self.position + np.asarray([0,0,(length/2 + i-length) * self.size])
                    return True

        return False


    def take (self, job):
        if self.codes[job.code] == 0:
            return False

        bundle, code = job.bundle, job.code
        length, deep = bundle.shape
        space = self.space

        if deep == 2:
            for i in range(length, self.length + 1):
                if np.array_equal(space[i - length:i, :], bundle):
                    space[i - length:i, :] = np.zeros(bundle.shape)
                    self.codes[code] -= 1
                    job.destination = self.position + np.asarray([0,0,(length/2 + i-length) * self.size])
                    return True
        elif deep == 1:
            for i in range(length, self.length + 1):
                if np.array_equal(space[i - length:i, 1:], bundle):
                    space[i - length:i, 1:] = np.zeros(bundle.shape)
                    self.codes[code] -= 1
                    job.destination = self.position + np.asarray([0,0,(length/2 + i-length) * self.size])
                    return True

                if space[i - length:i, 1].sum() == 0 and np.array_equal(space[i - length:i, :1], bundle):
                    space[i - length:i, :1] = np.zeros(bundle.shape)
                    self.codes[code] -= 1
                    job.destination = self.position + np.asarray([0,0,(length/2 + i-length) * self.size])
                    return True

        return False




class Rack (object):

    def __init__(self, *, corridors, levels, corridor_size, level_size, position, location_spaces, location_size, crane, lifts):
        self.crane = crane
        self.lifts = lifts
        self.position = np.asarray(position)
        self.locations = tuple(Location([x*corridor_size, y*level_size, position[2]], location_spaces, location_size)
                                      for y in range(levels)
                                    for x in range(corridors)
                                 for _ in range(2))


    def place (self, job, position=(0,0,0)):
        pos = np.asarray(position)
        locations = sorted(self.locations, key=lambda loc: (pos - loc.position).sum())
        for loc in locations:
            if not loc.frozen and loc.place(job):
                yield loc


    def take (self, job, position=(0,0,0)):
        pos = np.asarray(position)
        locations = sorted(self.locations, key=lambda loc: (pos - loc.position).sum())
        for loc in locations:
            if not loc.frozen and loc.take(job):
                yield loc