import simpy
import numpy as np
import collections
import math



class Depot (object):

    def __init__ (self, position, controlInterval = 1000):
        self.position = np.asarray(position)
        self.controlInterval = controlInterval
        self.queue = collections.deque()
        self.queue_report = dict()

    def push (self, job, time):
        self.queue.append(job)
        self.queue_report[time // self.controlInterval] = len(self.queue)

    def pop (self, time):
        self.queue.popleft()
        self.queue_report[time // self.controlInterval] = len(self.queue)



class Machine (simpy.PriorityResource):

    def __init__ (self, env, speed, acceleration, position, direction):
        self.env = env
        self.speed = speed
        self.acceleration = acceleration
        self.transitory_dist = 2 * speed**2 / (2*acceleration)
        self.position = np.asarray(position)
        self.direction = np.asarray(direction)
        self.moving_time = 0.0

        super(Machine, self).__init__(env, capacity=1)


    def move (self, position):
        if (d := (np.abs(self.position - position) * self.direction).sum()) > 0:
            a, v = self.acceleration, self.speed
            time = math.sqrt(d * a) / a if d <= self.transitory_dist else (d - self.transitory_dist) / v + 2 * v / a
            self.moving_time += time
            self.position = position
            yield self.env.timeout(time)


    def prepare (self, position, req):
        yield req
        yield self.env.process(self.move(position))



class Lift (Machine):

    def __init__ (self, env, speed, acceleration, position, up, down):
        self.env = env
        self.up = np.asarray(up)
        self.down = np.asarray(down)
        super(Lift, self).__init__(env, speed, acceleration, position, (0,1,0))



class Shuttle(Machine):

    def __init__(self, env, speed, acceleration, position):
        self.env = env
        super(Shuttle, self).__init__(env, speed, acceleration, position, (0, 0, 1))



class Crane (simpy.PriorityResource):

    def __init__ (self, env, speeds, accelerations, position):
        self.env = env
        self.mx = Machine(env, speeds[0], accelerations[0], position, (1,0,0))
        self.my = Machine(env, speeds[1], accelerations[1], position, (0,1,0))
        self.mz = Machine(env, speeds[2], accelerations[2], position, (0,0,1))
        super(Crane, self).__init__(env, capacity=1)


    def takeIn (self, job, uploadTime):
        position = job.destination
        env = self.env
        yield env.process(self.mx.move(position)) & env.process(self.mz.move(position))
        yield env.process(self.my.move(position))
        yield env.timeout(uploadTime)


    def prepareIn (self, position, req):
        yield req
        yield self.env.process(self.my.move(position))
        yield self.env.process(self.mx.move(position)) & self.env.process(self.mz.move(position))


    def takeOut (self, position, job, uploadTime):
        env = self.env
        pLoc = job.destination
        yield env.process(self.my.move(position))
        yield env.process(self.mx.move(pLoc)) & env.process(self.mz.move(pLoc))
        yield env.process(self.my.move(pLoc))
        yield env.timeout(uploadTime)
        yield env.process(self.my.move(position))
        yield env.process(self.mx.move(position)) & env.process(self.mz.move(position))