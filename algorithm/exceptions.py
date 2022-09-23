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

class UnfeasibleSolution(Exception):
    def __init__(self):
        self.message = "Unfeasible solution found."