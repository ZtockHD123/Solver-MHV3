import random 
import numpy as np

class KP:
    def __init__(self, instance):
        self.__items = 0
        self.__capacity = 0
        self.__weights = []
        self.__profits = []
        self.__tradeOff = []
        self.__optimum = 0
        self.readIntances(instance)
        
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
        
    def readIntances(self, instance):
        
        file = open('./Problem/KP/Instances/'+instance, 'r')
        
        self.setOptimum(self.obtenerOptimoKP(instance))
        
        linea = file.readline()

        items = int(linea.split(" ")[0])
        capacity = float(linea.replace("\n","").split(" ")[1])
        
        weights = []
        profits = []
        i = 1
        while i <= items:
            linea = file.readline()
            profits.append(float(linea.split(" ")[0]))
            weights.append(float(linea.replace("\n","").split(" ")[1]))
            
            i+=1
        self.setItems(items)
        self.setCapacity(capacity)
        self.setWeights(np.array(weights))
        self.setProfits(np.array(profits))
        self.setTradeOff(self.getProfits()/self.getWeights())
        
    def fitness(self, solution):
        return np.dot(solution, self.getProfits())
    
    def factibilityTest(self, solution):
        validacion = np.dot(solution, self.getWeights())
        if validacion > self.getCapacity():
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
    
    
    def obtenerOptimoKP(self, archivoInstancia):
        orden = {
            'f1_l-d_kp_10_269'          :[0,295],
            'f2_l-d_kp_20_878'          :[1,1024],
            'f3_l-d_kp_4_20'            :[2,35],
            'f4_l-d_kp_4_11'            :[3,23],
            'f5_l-d_kp_15_375'          :[4,481.0694],
            'f6_l-d_kp_10_60'           :[5,52],
            'f7_l-d_kp_7_50'            :[6,107],
            'f8_l-d_kp_23_10000'        :[7,9767],
            'f9_l-d_kp_5_80'            :[8,130],
            'f10_l-d_kp_20_879'         :[9,1025],
            'knapPI_1_100_1000_1'       :[10,9147],
            'knapPI_1_200_1000_1'       :[11,11238],
            'knapPI_1_500_1000_1'       :[12,28857],
            'knapPI_1_1000_1000_1'      :[13,54503],
            'knapPI_1_2000_1000_1'      :[14,110625],
            'knapPI_1_5000_1000_1'      :[15,276457],
            'knapPI_1_10000_1000_1'     :[16,563647],
            'knapPI_2_100_1000_1'       :[17,1514],
            'knapPI_2_200_1000_1'       :[18,1634],
            'knapPI_2_500_1000_1'       :[19,4566],
            'knapPI_2_1000_1000_1'      :[20,9052],
            'knapPI_2_2000_1000_1'      :[21,18051],
            'knapPI_2_5000_1000_1'      :[22,44356],
            'knapPI_2_10000_1000_1'     :[23,90204],
            'knapPI_3_100_1000_1'       :[24,2397],
            'knapPI_3_200_1000_1'       :[25,2697],
            'knapPI_3_500_1000_1'       :[27,7117],
            'knapPI_3_1000_1000_1'      :[28,14390],
            'knapPI_3_2000_1000_1'      :[29,28919],
            'knapPI_3_5000_1000_1'      :[30,72505],
            'knapPI_3_10000_1000_1'     :[31,146919]
            
        }

        for nomInstancia in orden:
            if nomInstancia in archivoInstancia:
                #print(f"instancia {nomInstancia}")
                return orden[nomInstancia][1]

        return None
    
def obtenerOptimoKP(archivoInstancia):
    orden = {
        'f1_l-d_kp_10_269'          :[0,295],
        'f2_l-d_kp_20_878'          :[1,1024],
        'f3_l-d_kp_4_20'            :[2,35],
        'f4_l-d_kp_4_11'            :[3,23],
        'f5_l-d_kp_15_375'          :[4,481.0694],
        'f6_l-d_kp_10_60'           :[5,52],
        'f7_l-d_kp_7_50'            :[6,107],
        'f8_l-d_kp_23_10000'        :[7,9767],
        'f9_l-d_kp_5_80'            :[8,130],
        'f10_l-d_kp_20_879'         :[9,1025],
        'knapPI_1_100_1000_1'       :[10,9147],
        'knapPI_1_200_1000_1'       :[11,11238],
        'knapPI_1_500_1000_1'       :[12,28857],
        'knapPI_1_1000_1000_1'      :[13,54503],
        'knapPI_1_2000_1000_1'      :[14,110625],
        'knapPI_1_5000_1000_1'      :[15,276457],
        'knapPI_1_10000_1000_1'     :[16,563647],
        'knapPI_2_100_1000_1'       :[17,1514],
        'knapPI_2_200_1000_1'       :[18,1634],
        'knapPI_2_500_1000_1'       :[19,4566],
        'knapPI_2_1000_1000_1'      :[20,9052],
        'knapPI_2_2000_1000_1'      :[21,18051],
        'knapPI_2_5000_1000_1'      :[22,44356],
        'knapPI_2_10000_1000_1'     :[23,90204],
        'knapPI_3_100_1000_1'       :[24,2397],
        'knapPI_3_200_1000_1'       :[25,2697],
        'knapPI_3_500_1000_1'       :[27,7117],
        'knapPI_3_1000_1000_1'      :[28,14390],
        'knapPI_3_2000_1000_1'      :[29,28919],
        'knapPI_3_5000_1000_1'      :[30,72505],
        'knapPI_3_10000_1000_1'     :[31,146919]
        
    }

    for nomInstancia in orden:
        if nomInstancia in archivoInstancia:
            #print(f"instancia {nomInstancia}")
            return orden[nomInstancia][1]

    return None
            