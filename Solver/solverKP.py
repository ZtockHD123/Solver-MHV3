import numpy as np
import os
import time

from Problem.KP.problem import KP

from Metaheuristics.imports import iterarGWO, iterarSCA, iterarWOA, iterarPSA, iterarGA
from Metaheuristics.imports import iterarPSO, iterarFOX, iterarEOO, iterarRSA, iterarGOA
from Metaheuristics.imports import iterarHBA, iterarTDO, iterarSHO, iterarSBOA, iterarEHO
from Metaheuristics.imports import iterarEBWOA, iterarFLO, iterarHLOAScp, iterarLOA, iterarNO
from Metaheuristics.imports import iterarPOA, IterarPO, iterarWOM, iterarQSO, iterarAOA

from Diversity.imports import diversidadHussain,porcentajesXLPXPT
from Discretization import discretization as b
from Util import util
from BD.sqlite import BD

def solverKP(id, mh, maxIter, pop, instancia, DS, param):
    
    dirResult = './Resultados/'
    instance = KP(instancia)
    
    chaotic_map = None
    
    # tomo el tiempo inicial de la ejecucion
    initialTime = time.time()
    
    initializationTime1 = time.time()
    print("------------------------------------------------------------------------------------------------------")
    print("instancia KP a resolver: "+instancia)
    
    results = open(dirResult+mh+"_"+instancia.split(".")[0]+"_"+str(id)+".csv", "w")
    results.write(
        f'iter,fitness,time,XPL,XPT,DIV\n'
    )
    
    # Genero una población inicial binaria, esto ya que nuestro problema es binario
    population = np.random.randint(low=0, high=2, size = (pop, instance.getItems()))
    
    maxDiversity = diversidadHussain(population)
    XPL , XPT, state = porcentajesXLPXPT(maxDiversity, maxDiversity)
    
    # Genero un vector donde almacenaré los fitness de cada individuo
    fitness = np.zeros(pop)

    # Genero un vetor dedonde tendré mis soluciones rankeadas
    solutionsRanking = np.zeros(pop)
    
    # calculo de factibilidad de cada individuo y calculo del fitness inicial
    for i in range(population.__len__()):
        flag = instance.factibilityTest(population[i])
        if not flag: #solucion infactible
            population[i] = instance.repair(population[i])
            

        fitness[i] = instance.fitness(population[i])
        
    # esta funcion ordena de menor a mayor
    solutionsRanking = np.argsort(fitness) # rankings de los mejores fitnes
    # es de maximizacion
    bestRowAux = solutionsRanking[pop-1]
    
    # DETERMINO MI MEJOR SOLUCION Y LA GUARDO 
    best = population[bestRowAux].copy()
    bestFitness = fitness[bestRowAux]
    
    # PARA MFO
    bestFitnessArray = fitness[solutionsRanking] 
    bestSolutions = population[solutionsRanking]
    
    matrixBin = population.copy()
    
    initializationTime2 = time.time()
    
    # mostramos nuestro fitness iniciales
    print("------------------------------------------------------------------------------------------------------")
    print("fitness incial: "+str(fitness))
    print("best fitness inicial: "+str(bestFitness))
    print("------------------------------------------------------------------------------------------------------")
    if mh == "GA":
        print("COMIENZA A TRABAJAR LA METAHEURISTICA "+mh)
    else: 
        print("COMIENZA A TRABAJAR LA METAHEURISTICA "+mh+ " / Binarizacion: "+ str(DS))
    print("------------------------------------------------------------------------------------------------------")
    print("iteracion: "+
            str(0)+
            ", best: "+str(bestFitness)+
            ", mejor iter: "+str(fitness[solutionsRanking[pop-1]])+
            ", peor iter: "+str(fitness[solutionsRanking[0]])+
            ", optimo: "+str(instance.getOptimum())+
            ", time (s): "+str(round(initializationTime2-initializationTime1,3))+
            ", XPT: "+str(XPT)+
            ", XPL: "+str(XPL)+
            ", DIV: "+str(maxDiversity))
    results.write(
        f'0,{str(bestFitness)},{str(round(initializationTime2-initializationTime1,3))},{str(XPL)},{str(XPT)},{maxDiversity}\n'
    )
    
    bestPop = np.copy(population)

    # Función objetivo para GOA, HBA, TDO y SHO
    def fo(x):
        x = b.aplicarBinarizacion(x.tolist(), DS[0], DS[1], best, matrixBin[i].tolist(), iter, pop, maxIter, i, chaotic_map)
        x = instance.repair(x) # Reparación de soluciones
        return x,instance.fitness(x) # Return de la solución reparada y valor de función objetivo
    
    if mh == 'PO':
        iterarPO = IterarPO(fo, instance.getItems(), pop, maxIter, 0, 1)

    for iter in range(0, maxIter):
        # obtengo mi tiempo inicial
        timerStart = time.time()
        
        if mh == "MFO":
            for i in range(bestSolutions.__len__()):
                bestFitnessArray[i] = instance.fitness(bestSolutions[i])
        
        # perturbo la poblacion con la metaheuristica, pueden usar SCA y GWO
        # en las funciones internas tenemos los otros dos for, for de individuos y for de dimensiones
        # print(population)
        if mh == "SCA":
            population = iterarSCA(maxIter, iter, instance.getItems(), population.tolist(), best.tolist())

        if mh == "GWO":
            population = iterarGWO(maxIter, iter, instance.getItems(), population.tolist(), fitness.tolist(), 'MIN')

        if mh == 'WOA':
            population = iterarWOA(maxIter, iter, instance.getItems(), population.tolist(), best.tolist())

        if mh == 'PSA':
            population = iterarPSA(maxIter, iter, instance.getItems(), population.tolist(), best.tolist())

        if mh == "GA":

            cross = float(param.split(";")[0].split(":")[1])
            muta = float(param.split(";")[1].split(":")[1])

            population = iterarGA(population.tolist(), fitness, cross, muta)

        if mh == 'PSO':
            population = iterarPSO(maxIter, iter, instance.getItems(), population.tolist(), best.tolist(),bestPop.tolist())

        if mh == 'FOX':
            population = iterarFOX(maxIter, iter, instance.getItems(), population.tolist(), best.tolist())

        if mh == 'EOO':
            population = iterarEOO(maxIter, iter, population.tolist(), best.tolist())

        if mh == 'RSA':
            population = iterarRSA(maxIter, iter, instance.getItems(), population.tolist(), best.tolist(),0,1)

        if mh == 'GOA':
            population = iterarGOA(maxIter, iter, instance.getItems(), population, best.tolist(), fitness.tolist(),fo, 'MAX')

        if mh == 'HBA':
            population = iterarHBA(maxIter, iter, instance.getItems(), population.tolist(), best.tolist(), fitness.tolist(),fo, 'MAX')

        if mh == 'TDO':
            population = iterarTDO(maxIter, iter, instance.getItems(), population.tolist(), fitness.tolist(),fo, 'MAX')

        if mh == 'SHO':
            population = iterarSHO(maxIter, iter, instance.getItems(), population.tolist(), best.tolist(),fo, 'MAX')
            
        if mh == "GA":
            
            cross = float(param.split(";")[0].split(":")[1])
            muta = float(param.split(";")[1].split(":")[1])

            population = iterarGA(population.tolist(), fitness, cross, muta)
        if mh == 'HBA':
            population = iterarHBA(maxIter, iter, instance.getItems(), population.tolist(), best.tolist(), fitness.tolist(), fo, 'MIN')
            
        if mh == 'TDO':
            population = iterarTDO(maxIter, iter, instance.getItems(), population.tolist(), fitness.tolist(), fo, 'MIN')
            
        if mh == 'SHO':
            population = iterarSHO(maxIter, iter, instance.getItems(), population.tolist(), best.tolist(), fo, 'MIN')
            
        if mh == 'SBOA':
            population = iterarSBOA(maxIter, iter, instance.getItems(), population.tolist(), fitness.tolist(), best.tolist(), fo)
            
        if mh == 'EHO':
            lb = [0] * instance.getItems()
            ub = [1] * instance.getItems()
            
            population = iterarEHO(maxIter, iter, instance.getItems(), population.tolist(), best.tolist(), lb, ub, fitness.tolist())
            
        if mh == 'EBWOA':
            population = iterarEBWOA(maxIter, iter, instance.getItems(), population.tolist(), best.tolist(), 0, 1)
            
        if mh == 'FLO': 
            population = iterarFLO(maxIter, iter, instance.getItems(), population.tolist(), fitness.tolist(), best.tolist(), fo, 'MIN', 0, 1)
            
        if mh == 'HLOA':
            population = iterarHLOAScp(maxIter, iter, instance.getItems(), population.tolist(), best.tolist(), 0, 1)
            
        if mh == "LOA":
            population, posibles_mejoras = iterarLOA(maxIter, population.tolist(), best.tolist(), 0, 1, iter, instance.getItems())
            
        if mh == 'NO':
            population = iterarNO(maxIter, iter, instance.getItems(), population.tolist(), best.tolist())
            
        if mh == 'POA':
            population = iterarPOA(maxIter, iter, instance.getItems(), population.tolist(), fitness.tolist(), fo, 0, 1, 'MIN')
            
        if mh == 'PO':
            iterarPO.pob(population.tolist(), iter)
            population = iterarPO.optimizer(iter)
            
        if mh == 'WOM':
            lb = [0] * instance.getItems()
            ub = [1] * instance.getItems()
            
            population = iterarWOM(maxIter, iter, instance.getItems(), population.tolist(), fitness.tolist(), lb, ub, fo)
        
        if mh == 'QSO':
            population = iterarQSO(maxIter, iter, instance.getItems(), population.tolist(), best.tolist(), 0, 1)
            
        if mh == 'AOA':
            population = iterarAOA(maxIter, iter, instance.getItems(), population.tolist(), best.tolist())
        
        
        # Binarizo, calculo de factibilidad de cada individuo y calculo del fitness
        for i in range(population.__len__()):

            if mh != "GA":
                population[i] = b.aplicarBinarizacion(population[i].tolist(), DS[0], DS[1], best, matrixBin[i].tolist(), iter, pop, maxIter, i, chaotic_map)

            flag = instance.factibilityTest(population[i])
            # print(aux)
            if not flag: #solucion infactible
                population[i] = instance.repair(population[i])
                
            fitness[i] = instance.fitness(population[i])

            if mh == 'PSO':
                if fitness[i] < instance.fitness(bestPop[i]):
                    bestPop[i] = np.copy(population[i])
                    
            if mh == 'LOA':
                func, fitn = fo(posibles_mejoras[i])
                if fitn < fitness[i]:
                    population[i] = posibles_mejoras[i]


        solutionsRanking = np.argsort(fitness) # rankings de los mejores fitness
        
        #Conservo el best
        if fitness[solutionsRanking[pop-1]] > bestFitness:
            bestFitness = fitness[solutionsRanking[pop-1]]
            best = population[solutionsRanking[pop-1]]
        matrixBin = population.copy()

        div_t = diversidadHussain(population)
        
        if maxDiversity < div_t:
            maxDiversity = div_t
            
        XPL , XPT, state = porcentajesXLPXPT(div_t, maxDiversity)

        timerFinal = time.time()
        # calculo mi tiempo para la iteracion t
        timeEjecuted = timerFinal - timerStart
        
        print("iteracion: "+
            str(iter+1)+
            ", best: "+str(bestFitness)+
            ", mejor iter: "+str(fitness[solutionsRanking[pop-1]])+
            ", peor iter: "+str(fitness[solutionsRanking[0]])+
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
    print("Cantidad de columnas seleccionadas: "+str(sum(best)))
    print("------------------------------------------------------------------------------------------------------")

    finalTime = time.time()
    timeExecution = finalTime - initialTime

    print("Tiempo de ejecucion (s): " + str(timeExecution))

    results.close()
    
    binary = util.convert_into_binary(dirResult + mh + "_" + instancia.split(".")[0] + "_" + str(id) + ".csv")

    fileName = mh + "_" + instancia.split(".")[0]

    bd = BD()
    bd.insertarIteraciones(fileName, binary, id)
    bd.insertarResultados(bestFitness, timeExecution, best, id)
    bd.actualizarExperimento(id, 'terminado')
    
    os.remove(dirResult+mh+"_"+instancia.split(".")[0]+"_"+str(id)+".csv")