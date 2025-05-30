import numpy as np

from Discretization import discretization as b
from Metaheuristics.imports import metaheuristics, MH_ARG_MAP # Assuming MH_ARG_MAP also applies to KP or will be adapted


def initialize_population(mh, pop, instance):

    vel, pBestScore, pBest = None, None, None
    
    if mh == 'PSO':
        vel = np.zeros((pop, instance.getItems()))
        pBestScore = np.full(pop, float("inf"))  # Más directo
        pBest = np.zeros((pop, instance.getItems()))
    
    # Genero una población inicial binaria, esto ya que nuestro problema es binario
    population = np.random.randint(low = 0, high = 2, size = (pop, instance.getItems()))
    
    return population, vel, pBestScore, pBest

def evaluate_population(mh, population, fitness, instance, pBest, pBestScore):
    """
    Evaluates the initial population for KP, checking feasibility and calculating fitness.
    """
    # Calculate feasibility and initial fitness for each individual
    for i in range(population.__len__()):
        flag = instance.factibilityTest(population[i])
        if not flag:  # infeasible solution
            population[i] = instance.repair(population[i])

        fitness[i] = instance.fitness(population[i])

        if mh == 'PSO':
            if pBestScore[i] > fitness[i]:
                pBestScore[i] = fitness[i]
                pBest[i, :] = population[i, :].copy()

    # For maximization problems (like KP), sort in descending order
    solutionsRanking = np.argsort(fitness)[::-1]  # rankings of the best fitnesses (descending)
    
    # Determine and store the best solution
    bestRowAux = solutionsRanking[0] # The first element after reverse sorting is the best
    best = population[bestRowAux].copy()
    bestFitness = fitness[bestRowAux]
    
    return fitness, best, bestFitness, pBest, pBestScore


def iterate_population_kp(mh, population, iter, maxIter, instance, fitness, best, 
                           vel=None, pBest=None, fo=None, param=None):
    """
    Iterates over the population for KP using the specified metaheuristic ('mh'),
    constructing arguments dynamically based on MH_ARG_MAP.
    Handles special cases like GA.
    """

    # --- Manejo especial para PO ---
    if mh == 'PO':
        return np.array(population), vel, None
    
    # --- Manejo especial para GA ---
    if mh == 'GA':
        if param is None:
            raise ValueError("Parameters 'cross' and 'muta' not provided for GA.")
        
        partes = param.split(";")
        cross = float(partes[0].split(":")[1])
        muta = float(partes[1].split(":")[1])

        # Assuming iterarGA is the function from Metaheuristics/imports
        new_population = metaheuristics['GA'](population.tolist(), fitness, cross, muta)
        if not isinstance(new_population, np.ndarray):
            new_population = np.array(new_population)
        return new_population, vel, None # No 'posibles_mejoras' for GA

    if mh not in metaheuristics:
        raise ValueError(f"Metaheuristic '{mh}' not found in 'metaheuristics' (Metaheuristics/imports.py).")
    if mh not in MH_ARG_MAP:
        raise ValueError(f"MH_ARG_MAP for '{mh}' not defined (Metaheuristics/imports.py).")

    dim = instance.getItems()
    lb0_val = 0
    ub0_val = 1
    lb_arr = np.zeros(dim)
    ub_arr = np.ones(dim)
    
    context = {
        'maxIter': maxIter,
        'iter': iter,
        'dim': dim,
        'population': population,
        'fitness': fitness,
        'best': best,
        'vel': vel,       # Will be None for most MHs except PSO
        'pBest': pBest,   # Will be None for most MHs except PSO
        'ub': ub_arr,           # Array de 1s
        'lb': lb_arr,           # Array de 0s
        'ub0': ub0_val,         # Escalar 1
        'lb0': lb0_val,         # Escalar 0
        'fo': fo,
        'objective_type': 'MAX' # KP is a maximization problem
    }
    # 2. Get the names of the required arguments for this MH
    required_args_names = MH_ARG_MAP[mh]

    # 3. Build 'kwargs' dictionary with only the necessary arguments
    kwargs = {}
    for arg_name in required_args_names:
        if arg_name not in context:
            raise KeyError(f"Internal Error: Argument '{arg_name}' required by {mh} (according to MH_ARG_MAP) not found in 'context'.")
        kwargs[arg_name] = context[arg_name]

    mh_function = metaheuristics[mh]
    try:
        result = mh_function(**kwargs)
    except TypeError as e:
        raise TypeError(f"Type error when calling the function for {mh}. Check MH_ARG_MAP['{mh}'] and the function definition.") from e

    new_population = None
    new_vel = vel # vel will remain None for most MHs
    posibles_mejoras = None

    if mh == 'LOA':
        if isinstance(result, tuple) and len(result) == 2:
            new_population, posibles_mejoras = result
        else:
             raise TypeError(f"Retorno inesperado de LOA (SCP). Se esperaba (population, posibles_mejoras), se obtuvo {type(result)}")

    elif isinstance(result, tuple) and len(result) == 2:
        new_population, new_vel = result 

    elif isinstance(result, (np.ndarray, list)):
        new_population = result

    else:
        raise TypeError(f"Unexpected return type from {mh} (KP): {type(result)}. Expected ndarray, list, or tuple.")

    if not isinstance(new_population, np.ndarray):
        new_population = np.array(new_population)

    return new_population, new_vel, posibles_mejoras


def binarize_and_evaluate(mh, population, fitness, DS, best, matrixBin, instance, pBest, pBestScore, posibles_mejoras, fo):
    """
    Binarizes (if not GA), checks feasibility, and calculates fitness for each individual in KP.
    """
    for i in range(population.__len__()):
        # The original solverKP had a commented-out binarization line.
        # If binarization is generally applied, uncomment and ensure DS is correctly handled.
        # For now, based on solverKP's active code, binarization might be handled inside MH functions,
        # or it's implicitly assumed the population is already in a binarized state or continuous
        # values are being worked with directly by the MH and then implicitly converted.
        # If a explicit binarization step is needed AFTER the MH update and BEFORE fitness evaluation:
        if mh != "GA":
           population[i] = b.aplicarBinarizacion(population[i], DS, best, matrixBin[i])
        
        flag = instance.factibilityTest(population[i])

        if not flag:  # infeasible solution
            population[i] = instance.repair(population[i])

        fitness[i] = instance.fitness(population[i])

        if mh == 'PSO':
            if fitness[i] < pBestScore[i]:
                pBest[i] = np.copy(population[i])
                
        '''if mh == 'LOA':
            _, fitn = fo(posibles_mejoras[i])
            
            if fitn < fitness[i]:
                population[i] = posibles_mejoras[i]'''

    return population, fitness, pBest


def update_best_solution(population, fitness, best, bestFitness):
    # Generate a vector of ranked solutions (for maximization, sort descending)
    solutionsRanking = np.argsort(fitness)[::-1]  # rankings of the best fitnesses

    # Preserve the best (maximization: higher fitness is better)
    if fitness[solutionsRanking[0]] > bestFitness:
        bestFitness = fitness[solutionsRanking[0]]
        best = population[solutionsRanking[0]]

    return best, bestFitness