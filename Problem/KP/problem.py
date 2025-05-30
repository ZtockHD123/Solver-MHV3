import random
import numpy as np

# Global dictionary for KP optimal values, similar to 'orden' in SCP
orden_kp = {
    'kn_f1_l-d_kp_10_269': [0, 295],
    'kn_f2_l-d_kp_20_878': [1, 1024],
    'kn_f3_l-d_kp_4_20': [2, 35],
    'kn_f4_l-d_kp_4_11': [3, 23],
    'kn_f5_l-d_kp_15_375': [4, 481.0694],
    'kn_f6_l-d_kp_10_60': [5, 52],
    'kn_f7_l-d_kp_7_50': [6, 107],
    'kn_f8_l-d_kp_23_10000': [7, 9767],
    'kn_f9_l-d_kp_5_80': [8, 130],
    'kn_f10_l-d_kp_20_879': [9, 1025],
    'knapPI_1_100_1000_1': [10, 9147],
    'knapPI_1_200_1000_1': [11, 11238],
    'knapPI_1_500_1000_1': [12, 28857],
    'knapPI_1_1000_1000_1': [13, 54503],
    'knapPI_1_2000_1000_1': [14, 110625],
    'knapPI_1_5000_1000_1': [15, 276457],
    'knapPI_1_10000_1000_1': [16, 563647],
    'knapPI_2_100_1000_1': [17, 1514],
    'knapPI_2_200_1000_1': [18, 1634],
    'knapPI_2_500_1000_1': [19, 4566],
    'knapPI_2_1000_1000_1': [20, 9052],
    'knapPI_2_2000_1000_1': [21, 18051],
    'knapPI_2_5000_1000_1': [22, 44356],
    'knapPI_2_10000_1000_1': [23, 90204],
    'knapPI_3_100_1000_1': [24, 2397],
    'knapPI_3_200_1000_1': [25, 2697],
    # Note: Instance 'knapPI_3_500_1000_1' had index 27, assuming it should be 26 if contiguous
    'knapPI_3_500_1000_1': [26, 7117], # Adjusted index for consistency if needed
    'knapPI_3_1000_1000_1': [27, 14390], # Adjusted index
    'knapPI_3_2000_1000_1': [28, 28919], # Adjusted index
    'knapPI_3_5000_1000_1': [29, 72505], # Adjusted index
    'knapPI_3_10000_1000_1': [30, 146919] # Adjusted index
}

class KP:
    def __init__(self, instance_basename):
        self.__items = 0
        self.__capacity = 0
        self.__weights = []
        self.__profits = []
        self.__tradeOff = []
        self.__optimum = 0
        self.read_instance(instance_basename)

    def getItems(self):
        return self.__items

    def setItems(self, items):
        self.__items = items

    def getCapacity(self):
        return self.__capacity

    def setCapacity(self, capacity):
        self.__capacity = capacity

    def getWeights(self):
        return self.__weights

    def setWeights(self, weights):
        self.__weights = weights

    def getProfits(self):
        return self.__profits

    def setProfits(self, profits):
        self.__profits = profits

    def getTradeOff(self):
        return self.__tradeOff

    def setTradeOff(self, tradeoff):
        self.__tradeOff = tradeoff

    def getOptimum(self):
        return self.__optimum

    def setOptimum(self, optimum):
        self.__optimum = optimum

    def _get_optimum_value(self, instance_basename):
        if instance_basename in orden_kp:
            return orden_kp[instance_basename][1]
        print(f"Warning: Optimum for instance '{instance_basename}' not found in orden_kp.")
        return None # Or raise an error, or return a default

    def read_instance(self, instance_basename):
        self.setOptimum(self._get_optimum_value(instance_basename))

        filename = f"{instance_basename}"

        file_path = f'./Problem/KP/Instances/{filename}'

        try:
            with open(file_path, 'r') as file:
                linea = file.readline()
                if not linea:
                    raise ValueError(f"Instance file '{file_path}' is empty or first line is missing.")

                parts = linea.split(" ")
                if len(parts) < 2:
                    raise ValueError(f"Instance file '{file_path}' first line format error. Expected items and capacity.")

                items = int(parts[0])
                capacity = float(parts[1].replace("\n",""))

                weights_list = []
                profits_list = []
                i = 1
                while i <= items:
                    linea = file.readline()
                    if not linea:
                        raise ValueError(f"Instance file '{file_path}' ended prematurely. Expected {items} items.")
                    
                    parts = linea.split(" ")
                    if len(parts) < 2:
                        raise ValueError(f"Instance file '{file_path}' item line format error for item {i}.")
                        
                    profits_list.append(float(parts[0]))
                    weights_list.append(float(parts[1].replace("\n","")))
                    i += 1

            self.setItems(items)
            self.setCapacity(capacity)
            self.setWeights(np.array(weights_list))
            self.setProfits(np.array(profits_list))
            
            # Ensure weights are not zero before division
            if np.any(self.getWeights() == 0):
                 # Handle cases where weight can be zero, e.g. by assigning a large number for tradeoff
                # or by specific problem domain rules. For now, printing a warning.
                print(f"Warning: Instance '{instance_basename}' contains items with zero weight.")
                # A common practice is to assign a very high profit/weight ratio or handle as a special case
                # For simplicity, we'll create the tradeoff array but it might contain inf or nan
                # which should be handled in the repair logic if zero-weight items are picked.
                # A more robust solution would be to filter these items or use a masked array.
                # For now, we proceed, but this could lead to DivisionByZeroError if not handled later.
                with np.errstate(divide='ignore', invalid='ignore'): # Suppress division by zero warnings here
                    tradeoff_values = self.getProfits() / self.getWeights()
                    tradeoff_values[np.isinf(tradeoff_values)] = np.finfo(np.float64).max # Replace inf with a large number
                    tradeoff_values[np.isnan(tradeoff_values)] = 0 # Replace nan (0/0) with 0 or other appropriate value
                    self.setTradeOff(tradeoff_values)

            else:
                self.setTradeOff(self.getProfits() / self.getWeights())

        except FileNotFoundError:
            print(f"Error: Instance file '{file_path}' not found.")
            # Optionally, re-raise the error or handle it as appropriate
            raise
        except ValueError as e:
            print(f"Error reading instance file '{file_path}': {e}")
            # Optionally, re-raise or handle
            raise


    def fitness(self, solution):
        return np.dot(solution, self.getProfits())

    def factibilityTest(self, solution):
        validation = np.dot(solution, self.getWeights())
        if validation > self.getCapacity():
            return False
        else:
            return True

    def repair(self, solution):
        # ordenamos los tradeoff de menor a mayor
        orden = np.argsort(self.getTradeOff())
        factible = self.factibilityTest(solution)
        i = 0
        # elimino elementos
        while not factible:
            if solution[orden[i]] == 1:
                solution[orden[i]] = 0
                factible = self.factibilityTest(solution)
        
            i+=1
        # agrego elementos
        i = 1
        pos = -1
        while factible:
            if solution[orden[self.getItems() - i]] == 0:
                solution[orden[self.getItems() - i]] = 1
                pos = orden[self.getItems() - i]
                factible = self.factibilityTest(solution)
            i+=1
        solution[pos] = 0
        return solution
    
def obtenerOptimoKP(archivoInstancia):
    instancia = archivoInstancia.split('/')[-1].replace('.txt', '')
    
    clave_instancia = f"{instancia}"
    
    return orden_kp.get(clave_instancia, [None])[1]