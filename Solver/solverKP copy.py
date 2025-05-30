import numpy as np
import os
import time

from Problem.KP.problem import KP
from Metaheuristics.imports import IterarPO
from Diversity.imports import diversidadHussain,porcentajesXLPXPT
from Discretization import discretization as b # Still needed for binarization within the loop if not handled by MH
from Util import util
from BD.sqlite import BD

# Import functions from the new population_kp.py
from Solver.population.population_KP import (
    initialize_population,
    evaluate_population,
    binarize_and_evaluate,
    update_best_solution,
    iterate_population_kp
)

def solverKP(id, mh, maxIter, pop, instancia, DS, param):
    
    dirResult = './Resultados/'
    instance = KP(instancia)
    
    # chaotic_map is not used in the new binarize_and_evaluate for KP, so can be removed or kept if planned for future use
    chaotic_map = None 
    
    # Get initial execution time
    initialTime = time.time()
    
    initializationTime1 = time.time()
    print("------------------------------------------------------------------------------------------------------")
    print("instancia KP a resolver: "+instancia)
    
    results = open(dirResult+mh+"_"+instancia.split(".")[0]+"_"+str(id)+".csv", "w")
    results.write(
        f'iter,fitness,time,XPL,XPT,DIV\n'
    )
    
    # Initialize the population using the new function
    population, vel, pBestScore, pBest = initialize_population(mh, pop, instance)
    
    maxDiversity = diversidadHussain(population)
    XPL, XPT, state = porcentajesXLPXPT(maxDiversity, maxDiversity)
    
    # Initialize fitness array
    fitness = np.zeros(pop)

    # Evaluate the initial population using the new function
    fitness, best, bestFitness, pBest, pBestScore = evaluate_population(
        mh, population, fitness, instance, pBest, pBestScore)
    
    matrixBin = population.copy() # matrixBin still needed for binarization
    
    i = population.__len__() - 1

    initializationTime2 = time.time()

    posibles_mejoras = None
    
    # Log initial state
    print("------------------------------------------------------------------------------------------------------")
    print("fitness inicial: "+ str(fitness))
    print("best fitness inicial: "+ str(bestFitness))
    print("------------------------------------------------------------------------------------------------------")
    if mh == "GA":
        print("COMIENZA A TRABAJAR LA METAHEURISTICA "+mh)
    else: 
        print("COMIENZA A TRABAJAR LA METAHEURISTICA "+mh+ " / Binarizacion: "+ str(DS))
    print("------------------------------------------------------------------------------------------------------")
    print("iteracion: "+
            str(0)+
            ", best: "+str(bestFitness)+
            ", mejor iter: "+str(fitness[np.argsort(fitness)[pop-1]])+ # Adapted to get best from initial fitness array
            ", peor iter: "+str(fitness[np.argsort(fitness)[0]])+ # Adapted to get worst from initial fitness array
            ", optimo: "+str(instance.getOptimum())+
            ", time (s): "+str(round(initializationTime2-initializationTime1,3))+
            ", XPT: "+str(XPT)+
            ", XPL: "+str(XPL)+
            ", DIV: "+str(maxDiversity))
    results.write(
        f'0,{str(bestFitness)},{str(round(initializationTime2-initializationTime1,3))},{str(XPL)},{str(XPT)},{maxDiversity}\n'
    )
    
    def fo(x):
        x = b.aplicarBinarizacion(x, DS, best, matrixBin[i]) # 'i' is still an issue here outside the loop
        x = instance.repair(x)
        return x, instance.fitness(x)

    if mh == 'PO':
        iterarPO = IterarPO(fo, instance.getItems(), pop, maxIter, 0, 1)

    for iter in range(0, maxIter):
        # Get iteration start time
        timerStart = time.time()
        
        if mh == 'PO':
            # 'population' no fue modificada por iterate_population_scp en este caso
            iterarPO.pob(population, iter)
            population = iterarPO.optimizer(iter)
            if not isinstance(population, np.ndarray):
                population = np.array(population)

        # All metaheuristic iteration logic is now centralized in iterate_population_kp
        # 'bestSolutions' and 'bestFitnessArray' are currently only used by MFO,
        # so they are passed conditionally or handled within iterate_population_kp if MFO is supported.
        population, vel, _ = iterate_population_kp(
            mh=mh,
            population=population,
            iter=iter,
            maxIter=maxIter,
            instance=instance,
            fitness=fitness,
            best=best,
            vel=vel,
            pBest=pBest, # Will be None unless PSO is integrated to use it
            fo=fo,       # Pass the objective function
            param=param,
        )
        
        population, fitness, pBest = binarize_and_evaluate(
            mh, population, fitness, DS, best, matrixBin, instance, pBest, pBestScore, posibles_mejoras, fo)

        # Update the best solution using the new function
        best, bestFitness = update_best_solution(population, fitness, best, bestFitness)
        
        # Update matrixBin for the next iteration's binarization if needed
        matrixBin = population.copy()

        # Calculate diversity
        div_t = diversidadHussain(population)
        
        if maxDiversity < div_t:
            maxDiversity = div_t
            
        XPL , XPT, state = porcentajesXLPXPT(div_t, maxDiversity)

        timerFinal = time.time()
        # Calculate time for the current iteration
        timeEjecuted = timerFinal - timerStart
        
        print("iteracion: "+
            str(iter+1)+
            ", best: "+str(bestFitness)+
            ", mejor iter: "+str(fitness[np.argsort(fitness)[pop-1]])+
            ", peor iter: "+str(fitness[np.argsort(fitness)[0]])+
            ", optimo: "+str(instance.getOptimum())+
            ", time (s): "+str(round(timeEjecuted,3))+
            ", XPT: "+str(XPT)+
            ", XPL: "+str(XPL)+
            ", DIV: "+str(div_t))
        
        results.write(
            f'{iter+1},{str(bestFitness)},{str(round(timeEjecuted,3))},{str(XPL)},{str(XPT)},{str(div_t)}\n'
        )
    print("------------------------------------------------------------------------------------------------------")
    print("best fitness: "+str(bestFitness))
    print("Cantidad de columnas seleccionadas: "+str(sum(best))) # For KP, this would be "Number of items selected"
    print("------------------------------------------------------------------------------------------------------")
    finalTime = time.time()
    timeExecution = finalTime - initialTime
    print("Tiempo de ejecucion (s): "+str(timeExecution))
    results.close()
    
    binary = util.convert_into_binary(dirResult+mh+"_"+instancia.split(".")[0]+"_"+str(id)+".csv")

    fileName = mh+"_"+instancia.split(".")[0]

    bd = BD()
    bd.insertarIteraciones(fileName, binary, id)
    bd.insertarResultados(bestFitness, timeExecution, best, id)
    bd.actualizarExperimento(id, 'terminado')
    
    os.remove(dirResult+mh+"_"+instancia.split(".")[0]+"_"+str(id)+".csv")