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
import copy 

from .utils import bra, normaldist
from .exceptions import UnfeasibleSolution


def heuristic (jobs, Br_generator, Bb_generator,
        code_prob, depot_prob,
        quantity_prob, quality_prob, 
        initFilling):
    """
    This method represents a single execution of the algorithm.
    """

    env = simpy.Environment()

    Br = Br_generator()
    Bb = Bb_generator()

    sim = asrs.Simulation(
        env,
        config = asrs.simulation.Config( Bb = Bb,Br = Br), 
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

    try:
        env.process(sim(jobs))
        env.run()
        return env.now 
    except UnfeasibleSolution:
        return float("inf")


def multistart (jobs, maxiter, Br_generator, Bb_generator,
        code_prob, depot_prob,
        quantity_prob, quality_prob, 
        initFilling):

    best_makespan = heuristic(copy.deepcopy(jobs), Br_generator, Bb_generator, code_prob, depot_prob, quantity_prob, quality_prob, initFilling)
    
    for _ in range(maxiter):
        makespan = heuristic(copy.deepcopy(jobs), Br_generator, Bb_generator, code_prob, depot_prob, quantity_prob, quality_prob, initFilling)
        best_makespan = min(makespan, best_makespan)

    return best_makespan


