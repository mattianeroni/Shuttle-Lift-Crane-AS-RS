import matt99
import simpy

import numpy as np

if __name__ == "__main__":

    simTime = 140_000
    initFilling = 0.5
    avgArrival = 120

    env = simpy.Environment()

    sim = matt99.Simulation(env,
                            shuttles = tuple(matt99.Shuttle(env, 1.0, 0.3, (i*30, 0, 0)) for i in range(4)),
                            racks = tuple(matt99.Rack(corridors=30, levels=10, corridor_size=4, level_size=1,
                                                      position=(0, 0, i*18), location_size=(6,2),
                                                      crane=matt99.Crane(env, (1,1,1), (0.3,0.3,0.3), (0,10,i*18)),
                                                      lifts=tuple(matt99.Lift(env, 0.6, 0.3, (j*30, 0, i*18), (j*30, 10, i*18), (j*30, 0, i*18)) for j in range(4))
                                                      )
                                          for i in range(3)),
                            depots = tuple(matt99.Depot((i*30, 0, 0)) for i in range(4)),
                            depots_prob = {0 : 0.25, 1 : 0.25, 2 : 0.25, 3 : 0.25},
                            kinds_prob = {matt99.INPUT : 0.5, matt99.OUTPUT : 0.5},
                            codes_prob = {(101, 6) : 0.5, (102, 3) : 0.2, (103, 5) : 0.1, (104, 3) : 0.05, (105, 6) : 0.05},
                            quantities_prob = {1 : 0.5, 2 : 0.5},
                            uploadTime = 20.0
                        )

    sim.warmup (initFilling)
    env.process(sim(simTime, avgArrival))
    env.run(until=simTime)

    print(len(sim.done), len(sim.wasted))
    #for job in sim.done:
    #    print(job.kind, " - ", job.history["END"] - job.history["START"])
