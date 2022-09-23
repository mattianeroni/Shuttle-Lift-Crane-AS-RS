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
import simpy 
import asrs
from asrs.kind import INPUT, OUTPUT
from asrs.source import source, Code


if __name__ == "__main__":

    simTime = 140_000
    initFilling = 0.5
    avgArrival = 120
    maxJobs = float("inf")

    depot_prob = { INPUT : {0 : 0.25,  2 : 0.25}, OUTPUT : {1 : 0.25, 3 : 0.25} }
    kind_prob = {INPUT : 0.5, OUTPUT : 0.5}
    code_prob = {Code(6, 1000) : 0.5, Code(3, 500) : 0.2, Code(5, 600) : 0.1, Code(3, 1000) : 0.05, Code(6, 500) : 0.05}
    quantity_prob = {INPUT : {1 : 0.5, 2 : 0.5}, OUTPUT : {1 : 0.5, 2 : 0.5}}
    quality_prob = {INPUT : {1 : 0.33, 2 : 0.33, 3 : 0.34}, OUTPUT : {1 : 0.33, 2 : 0.33, 3 : 0.34}}

    jobs = source(
        simTime=simTime, 
        maxJobs=maxJobs,
        avgArrival=avgArrival, 
        depot_prob=depot_prob, 
        code_prob=code_prob,
        quantity_prob=quantity_prob,
        quality_prob=quality_prob,
        kind_prob=kind_prob,
    )

    env = simpy.Environment()

    sim = asrs.Simulation(
        env,
        shuttles = tuple(asrs.Shuttle(env, 2.0, 0.5, (i*30, 0, 0)) for i in range(4)),
        racks = tuple(asrs.Rack(ncorridors=30, nlevels=10, corridor_size=4, level_size=1,
            position=(0, 0, i*12), nshelves=6, shelves_deep=2, shelves_size=2, 
            crane=asrs.Crane(env, (1.3,1.3,1.3), (0.3,0.3,0.3), (0,10,i*12)),
            lifts=tuple(asrs.Lift(env, 0.6, 0.3, (j*30, 0, i*12), (j*30, 10, i*12), (j*30, 0, i*12)) for j in range(4))
        )
        for i in range(3)),
        depots = tuple(asrs.Depot((i*30, 0, 0)) for i in range(4)),
        uploadTime = 20.0
    )

    sim.warmup (
        percentage=initFilling,
        code_prob=code_prob,
        depot_prob=depot_prob,
        quantity_prob=quantity_prob,
        quality_prob=quality_prob,
    )

    env.process(sim(jobs))
    env.run()


    for job in sim.done:
        print(job.kind, job.arrival, " - ", job.history["END"] - job.history["START"])