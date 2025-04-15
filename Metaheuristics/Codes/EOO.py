import numpy as np

# Eurasian Oystercatcher Optimizer (EOO)
# https://doi.org/10.1515/jisys-2022-0017

def iterarEOO(maxIter, it, population, bestSolution):
    population = np.array(population, dtype=np.float64)
    bestSolution = np.array(bestSolution, dtype=np.float64)

    n, _ = population.shape
    it = maxIter - it + 1

    L = np.random.uniform(3, 5, size = n)  # L diferente para cada individuo
    T = (((L - 5) / (5 - 3)) * 10) - 5

    E = np.full(n, (1 / (n - 1)) - 0.5)  # Valor por defecto
    
    if it > 1:
        E = np.full(n, ((it - 1) / (n - 1)) - 0.5)

    C = (((L - 3) / (5 - 3)) * 2) + 0.6
    r = np.random.uniform(0, 1, size=n)  # Un r para cada individuo

    # Expande dimensiones para permitir el broadcasting
    L = L[:, None]
    T = T[:, None]
    E = E[:, None]
    r = r[:, None]

    # Cálculo de Y y actualización de la población
    Y = T + E + L * r * (bestSolution - population)  # Ahora el broadcasting es compatible
    
    population *= C[:, None]  # Ajusta la población multiplicando por C
    population += Y  # Suma Y a la población

    return population
