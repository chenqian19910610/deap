#    This file is part of EAP.
#
#    EAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    EAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with EAP. If not, see <http://www.gnu.org/licenses/>.

from deap import base
from deap import operators
from deap import creator
from deap import toolbox
from deap import benchmarks


import random
import array

# Problem dimension
NDIM = 10

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", array.array, typecode='d', fitness=creator.FitnessMin)

tools = toolbox.Toolbox()
tools.register("attr_float", random.uniform, -3, 3)
tools.register("individual", toolbox.fillRepeat, creator.Individual, tools.attr_float, NDIM)
tools.register("population", toolbox.fillRepeat, list, tools.individual)
tools.register("select", operators.selRandom, n=3)
tools.register("evaluate", benchmarks.sphere)

def main():
    # Differential evolution parameters
    CR = 0.25
    F = 1  
    MU = 300
    NGEN = 200    
    
    pop = tools.population(n=MU);
    hof = operators.HallOfFame(1)
    stats = operators.Statistics(lambda ind: ind.fitness.values)
    stats.register("Avg", operators.mean)
    stats.register("Std", operators.std_dev)
    stats.register("Min", min)
    stats.register("Max", max)
    
    # Evaluate the individuals
    fitnesses = tools.map(tools.evaluate, pop)
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    
    for g in range(NGEN):
        for k, agent in enumerate(pop):
            a,b,c = tools.select(pop)
            y = tools.clone(agent)
            index = random.randrange(NDIM)
            for i, value in enumerate(agent):
                if i == index or random.random() < CR:
                    y[i] = a[i] + F*(b[i]-c[i])
            y.fitness.values = tools.evaluate(y)
            if y.fitness > agent.fitness:
                pop[k] = y
        hof.update(pop)
        stats.update(pop)
        
        print "-- Generation %i --" % g
        print stats
            
    print "Best individual is ", hof[0], hof[0].fitness.values[0]
            
if __name__ == "__main__":
    main()
