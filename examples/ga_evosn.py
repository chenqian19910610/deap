#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

import sys
import random
import logging

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

from deap import algorithms
from deap import base
from deap import creator
from deap import operators
from deap import toolbox

import sortingnetwork as sn

INPUTS = 6

def evalEvoSN(individual, dimension):
    network = sn.SortingNetwork(dimension, individual)
    return network.assess(), network.length, network.depth

def genWire(dimension):
    return (random.randrange(dimension), random.randrange(dimension))
    
def genNetwork(dimension, min_size, max_size):
    size = random.randint(min_size, max_size)
    return [genWire(dimension) for i in xrange(size)]
    
def mutWire(individual, dimension, indpb):
    for index, elem in enumerate(individual):
        if random.random() < indpb:
            individual[index] = genWire(dimension)      

def mutAddWire(individual, dimension):
    index = random.randint(0, len(individual))
    individual.insert(index, genWire(dimension))

def mutDelWire(individual):
    index = random.randrange(len(individual))
    del individual[index]

creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0, -1.0))
creator.create("Individual", list, fitness=creator.FitnessMin)

tools = toolbox.Toolbox()

# Gene initializer
tools.register("network", genNetwork, dimension=INPUTS, min_size=9, max_size=12)

# Structure initializers
tools.register("individual", toolbox.fillIter, creator.Individual, tools.network)
tools.register("population", toolbox.fillRepeat, list, tools.individual)

tools.register("evaluate", evalEvoSN, dimension=INPUTS)
tools.register("mate", operators.cxTwoPoints)
tools.register("mutate", mutWire, dimension=INPUTS, indpb=0.05)
tools.register("addwire", mutAddWire, dimension=INPUTS)
tools.register("delwire", mutDelWire)

tools.register("select", operators.selNSGA2)

def main():
    random.seed(64)

    population = tools.population(n=300)
    hof = operators.ParetoFront()
    
    stats = operators.Statistics(lambda ind: ind.fitness.values)
    stats.register("Avg", operators.mean)
    stats.register("Std", operators.std_dev)
    stats.register("Min", min)
    stats.register("Max", max)

    CXPB, MUTPB, ADDPB, DELPB, NGEN = 0.5, 0.2, 0.01, 0.01, 40
    
    # Evaluate every individuals
    fitnesses = tools.map(tools.evaluate, population)
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit
    
    hof.update(population)
    stats.update(population)
    
    # Begin the evolution
    for g in xrange(NGEN):
        print "-- Generation %i --" % g
        offsprings = [tools.clone(ind) for ind in population]
    
        # Apply crossover and mutation
        for ind1, ind2 in zip(offsprings[::2], offsprings[1::2]):
            if random.random() < CXPB:
                tools.mate(ind1, ind2)
                del ind1.fitness.values
                del ind2.fitness.values
        
        # Note here that we have a different sheme of mutation than in the
        # original algorithm, we use 3 different mutations subsequently.
        for ind in offsprings:
            if random.random() < MUTPB:
                tools.mutate(ind)
                del ind.fitness.values
            if random.random() < ADDPB:
                tools.addwire(ind)
                del ind.fitness.values
            if random.random() < DELPB:
                tools.delwire(ind)
                del ind.fitness.values
                
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offsprings if not ind.fitness.valid]
        fitnesses = tools.map(tools.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        print "  Evaluated %i individuals" % len(invalid_ind)
        
        population = tools.select(population+offsprings, n=len(offsprings))
        hof.update(population)
        stats.update(population)
        print stats
        
        if stats.Min() < (100,):
            break

    best_network = sn.SortingNetwork(INPUTS, hof[0])
    print best_network
    print best_network.draw()
    print "%i errors, length %i, depth %i" % hof[0].fitness.values
    
    return population, stats, hof

if __name__ == "__main__":
    main()
