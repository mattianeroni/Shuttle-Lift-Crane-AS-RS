import random
import collections
import numpy as np

from matt99 import priority, source, kind


# Events registed for jobs
START = "START"
END = "END"


class Simulation (object):

    def __init__ (self, env, *, shuttles, racks, depots, depots_prob, kinds_prob, codes_prob, quantities_prob, uploadTime=20.0):
        self.env = env
        self.shuttles = shuttles
        self.racks = racks
        self.depots = depots
        self.depots_prob = depots_prob
        self.kinds_prob = kinds_prob
        self.codes_prob = codes_prob
        self.quantities_prob = quantities_prob
        self.uploadTime = uploadTime

        self.done = collections.deque()
        self.wasted = collections.deque()


    def warmup (self, percentage = .5):
        capacity = sum(loc.length * loc.deep for rack in self.racks for loc in rack.locations)
        filling = 0
        while filling / capacity < percentage:
            rack = random.choice(list(self.racks))
            loc = random.choice(list(rack.locations))
            job = source.single_job(self.depots_prob[kind.INPUT], self.codes_prob, self.quantities_prob)
            if loc.place(job):
                filling += job.length * job.quantity


    def __call__ (self, simtime, avgArrival):
        env = self.env
        jobs = source.source(simtime, avgArrival, self.depots_prob, self.kinds_prob, self.codes_prob, self.quantities_prob)
        for job in jobs:
            yield env.timeout(max(0, job.arrival - env.now))
            env.process (self.execute(job))


    def getRack (self, job, position):
        if job.kind == kind.INPUT:
            for rack in sorted(list(self.racks), key=lambda r: len(r.crane.queue) + len(r.crane.users)):
                for loc in rack.place(job, position):
                    return rack, loc
        elif job.kind == kind.OUTPUT:
            for rack in sorted(list(self.racks), key=lambda r: len(r.crane.queue) + len(r.crane.users)):
                for loc in rack.take(job, position):
                    return rack, loc

        return None, None


    def execute (self, job):
        env = self.env
        shuttle = self.shuttles[job.depot]
        depot = self.depots[job.depot]
        rack, location = self.getRack(job, self.racks[0].lifts[job.depot].up)
        job.history[START] = int(env.now)

        if location is None:
            self.wasted.append(job)
        else:
            depot.push (job, env.now)
            lift = rack.lifts[job.depot]
            crane = rack.crane
            location.frozen = True
            if job.kind == kind.INPUT:
                yield (reqs := shuttle.request(priority=priority.NORMAL, preempt=False))
                yield env.process(shuttle.move(depot.position))
                reql = lift.request(priority=priority.NORMAL, preempt=False)
                lift_preparation = env.process(lift.prepare(lift.down, reql))
                yield env.timeout(self.uploadTime)
                depot.pop(env.now)
                yield env.process(shuttle.move(lift.down))
                yield lift_preparation
                reqc = crane.request(priority=priority.NORMAL, preempt=False)
                crane_preparation = env.process(crane.prepareIn(lift.up, reqc))
                yield env.timeout(self.uploadTime)
                shuttle.release(reqs)
                yield env.process(lift.move(lift.up))
                yield crane_preparation
                yield env.timeout(self.uploadTime)
                lift.release(reql)
                yield env.process(crane.takeIn(job, self.uploadTime))
                crane.release(reqc)
                location.frozen = False

            elif job.kind == kind.OUTPUT:
                yield (reqc := crane.request(priority=priority.NORMAL, preempt=False))
                reql = lift.request(priority=priority.NORMAL, preempt=False)
                lift_preparation = env.process(lift.prepare(lift.up, reql))
                yield env.process(crane.takeOut(lift.up, job, self.uploadTime))
                location.frozen = False
                yield lift_preparation
                reqs = shuttle.request(priority=priority.NORMAL, preempt=False)
                shuttle_prepare = env.process(shuttle.prepare(lift.down, reqs))
                yield env.timeout(self.uploadTime)
                crane.release(reqc)
                yield env.process(lift.move(lift.down))
                yield shuttle_prepare
                yield env.timeout(self.uploadTime)
                lift.release(reql)
                yield env.process(shuttle.move(depot.position))
                yield env.timeout(self.uploadTime)
                depot.pop(env.now)
                shuttle.release(reqs)

            self.done.append(job)
            job.history[END] = int(env.now)
