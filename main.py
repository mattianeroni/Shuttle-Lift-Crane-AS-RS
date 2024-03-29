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
import algorithm

from asrs.source import source, Code 
from asrs.kind import INPUT, OUTPUT


import functools 


if __name__ == "__main__":

    simTime = 140_000
    initFilling = 0.5
    avgArrival = 120
    maxJobs = float("inf")
    Br_mu, Br_std = 0.7, 0.05 
    Bb_mu, Bb_std = 0.9, 0.05

    depot_prob = { INPUT : {0 : 0.25,  2 : 0.25}, OUTPUT : {1 : 0.25, 3 : 0.25} }
    kind_prob = {INPUT : 0.5, OUTPUT : 0.5}
    code_prob = {Code(6, 1000) : 0.5, Code(3, 500) : 0.2, Code(5, 600) : 0.1, Code(3, 1000) : 0.05, Code(6, 500) : 0.05}
    quantity_prob = {INPUT : {1 : 0.5, 2 : 0.5}, OUTPUT : {1 : 0.5, 2 : 0.5}}
    quality_prob = {INPUT : {1 : 0.33, 2 : 0.33, 3 : 0.34}, OUTPUT : {1 : 0.33, 2 : 0.33, 3 : 0.34}}

    jobs = tuple(source(
        simTime=simTime, 
        maxJobs=maxJobs,
        avgArrival=avgArrival, 
        depot_prob=depot_prob, 
        code_prob=code_prob,
        quantity_prob=quantity_prob,
        quality_prob=quality_prob,
        kind_prob=kind_prob,
    ))

    makespan = algorithm.heuristic(
        jobs=jobs, 
        Br_generator=functools.partial(algorithm.utils.normaldist, mu=Br_mu, sigma=Br_std), 
        Bb_generator=functools.partial(algorithm.utils.normaldist, mu=Bb_mu, sigma=Bb_std), 
        code_prob=code_prob, 
        depot_prob=depot_prob, 
        quantity_prob=quantity_prob, 
        quality_prob=quality_prob, 
        initFilling=initFilling
    )


    print("The makespan is: ", int(makespan))