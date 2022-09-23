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
import collections
import numpy as np

from asrs import priority, source, kind
import algorithm


# Events registed for jobs
START = "START"
END = "END"



class Config:
    """ The configuration of the simulation """
    def __init__(self, Br, Bb):
        self.Br = Br 
        self.Bb = Bb
        self.weight_error = 0.2


class Simulation (object):
    """ An instance of this class represents the simulation of the system """

    def __init__ (self, env, config, *, shuttles, racks, depots, uploadTime=20.0):
        self.env = env
        self.config = config 
        self.shuttles = shuttles
        self.racks = racks
        self.depots = depots
        self.uploadTime = uploadTime

        self.done = collections.deque()
        self.wasted = collections.deque()


    def warmup (self, code_prob, depot_prob, quantity_prob, quality_prob, percentage = 0.5):
        capacity = sum(loc.length * loc.deep for rack in self.racks for loc in rack.locations)
        filling = 0
        while filling / capacity < percentage:
            rack = random.choice(list(self.racks))
            loc = random.choice(list(rack.locations))
            job = source.single_job(depot_prob[kind.INPUT], code_prob, quantity_prob, quality_prob, kind_prob={kind.INPUT: 1.0})
            if loc.place(job):
                filling += job.length * job.quantity


    def __call__ (self, jobs):
        env, Br, Bb = self.env, self.config.Br, self.config.Bb
        for i, job in enumerate(jobs):
            
            yield env.timeout(max(0, job.arrival - env.now))
            
            if job.kind == kind.INPUT:
                rack, loc = algorithm.process_input(job, self.racks, Br)
                
                if loc is None:
                    algorithm.postpone(i, job, jobs)
                else:
                    env.process (self.execute(job, rack, loc))


            elif job.kind == kind.OUTPUT:
                resulting_jobs = algorithm.process_output(job, self.racks, Br, Bb, self.config.weight_error) 
            
                if resulting_jobs is None:
                    algorithm.postpone(i, job, jobs)
                else:
                    for j in resulting_jobs:
                        loc = j.bundles[0].loc
                        _res = loc.take(j)
                        assert _res == True
                        env.process (self.execute(j, loc.rack, loc))
                        yield env.timeout(0)


    def execute (self, job, rack, location):
        env = self.env
        shuttle = self.shuttles[job.depot]
        depot = self.depots[job.depot]
        #rack, location = self.getRack(job, self.racks[0].lifts[job.depot].up)
        job.history[START] = int(env.now)

        #if location is None:
        #    self.wasted.append(job)
        #else:
        depot.push (job, env.now)
        lift = rack.lifts[job.depot]
        crane = rack.crane
        #location.frozen = True
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
