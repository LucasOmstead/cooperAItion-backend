'''
So, how should I represent the game?

Game state is easiest to represent with a 2d array:
a[0] = all moves of 1st player
a[1] = all moves of 2nd player
-1 = no move yet, 0 = cooperate, 1 = defect

TODO:
-implement genetic algorithm
-implement hill-climbing algorithm
-tabu search (use LRU cache for hill-climbing)

'''

import random
import time
from math import e
from players import Player, Defector, Cooperator, GrimTrigger, RandomChooser, TitForTat, TwoTitForTat, NiceTitForTat, SuspiciousTitForTat, ModelPlayer
#In general, past_moves[0] = your own moves, past_moves[1] = opponent's moves
#region LRUCache
class Node:
    def __init__(self, key: int, value: int):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.keyToNode = {}
        self.head = Node(-1, -1)
        self.tail = Node(-1, -1)
        self.join(self.head, self.tail)

    def get(self, key: int) -> int:
        if key not in self.keyToNode:
            return -1
        node = self.keyToNode[key]
        self.remove(node)
        self.moveToHead(node)
        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self.keyToNode:
            node = self.keyToNode[key]
            node.value = value
            self.remove(node)
            self.moveToHead(node)
            return

        if len(self.keyToNode) == self.capacity:
            lastNode = self.tail.prev
            del self.keyToNode[lastNode.key]
            self.remove(lastNode)

        self.moveToHead(Node(key, value))
        self.keyToNode[key] = self.head.next

    def join(self, node1: Node, node2: Node):
        node1.next = node2
        node2.prev = node1

    def moveToHead(self, node: Node):
        self.join(node, self.head.next)
        self.join(self.head, node)

    def remove(self, node: Node):
        self.join(node.prev, node.next)




cooperateReward = (5, 5)
betrayalReward = (8, 0)
betrayedReward = (0, 8)
bothBetray = (2, 2)
#payoffmatrix[player1choice][player2choice] = reward for player1, player2

payoffs = [[cooperateReward[0], betrayedReward[0]], 
             [betrayalReward[0], bothBetray[0]]]

        
def playGame(payoffs, player1: Player, player2: Player, numRounds: int):
    score1 = 0
    score2 = 0
    past_moves = [[-1 for i in range(numRounds)], [-1 for i in range(numRounds)]]
    for i in range(numRounds):
        action1 = player1.get_action(past_moves, i)
        action2 = player2.get_action(past_moves[::-1], i)
        past_moves[0][i] = action1
        past_moves[1][i] = action2 
        score1 += payoffs[action1][action2]
        score2 += payoffs[action2][action1]
    # print(player1, player2)
    return (score1, score2)

def calculateAllFitnesses(payoffs, models):
    #each player in the pool plays 1 game against each other
    scores = [0 for i in range(len(models))]
    
    for i in range(len(models)):
        for j in range(len(models)):
            score1, score2 = playGame(payoffs, models[i], models[j], 10)
            scores[i] += score1 
            scores[j] += score2 
    return scores

def calculateFitness(payoffs, models, modelPlayer):
    #each player in the pool plays 1 game against each other
    
    
    
    score = 0
    for i in range(len(models)):
        score1, score2 = playGame(payoffs, models[i], modelPlayer, 10)
        score += score2 
    score += playGame(payoffs, modelPlayer, modelPlayer, 10)[0]*2 
    return score



#First we'll use hill-climbing; should be easier to implement
def train_hill_climb(numRestarts: int, numIterations: int):
    #we'll be storing a vector of past 3 game states, and if the other guy has defected AT ALL (even previous to those three states)
    #128 total states once you've made it to >= 3 rounds
    #and then 2^4 states
    #and then 2^2 states
    #and then only 1 state at first
    #so first 128 bits are just the regular states, next 16 = i == 2, next 4 = i == 1, next 1 = i == 0
    #128 + 16 + 4 + 1 = 149 total bits 
    
    #this is just a training set, we can swap it out with other models
    models = [Defector(), Cooperator(), GrimTrigger(), RandomChooser(), TitForTat(), TwoTitForTat(), NiceTitForTat(), SuspiciousTitForTat()]
    # models = [Cooperator(), Cooperator(), Cooperator()]

    bestModels = []
    for _ in range(numRestarts): #number of random restarts. After 10 iterations we just return the best model so far
        curModel = random.getrandbits(149)
        
        #print(_)
        for i in range(numIterations):
            successors = [(curModel, calculateFitness(payoffs, models, ModelPlayer(curModel)))]
            
            for i in range(149): #at most we'll hill climb 300 iterations
                # print(i)
                # print(curModel)
                for j in range(random.randint(1, 10)): #always make at least 1 move, make more as temperature is lower so that you explore more combinations
                    model = curModel ^ (1 << random.randint(0, 148)) #flip 1 bit. This'll generate each successor
                
                # print(model)
                modelPlayer = ModelPlayer(model)

                fitness = calculateFitness(payoffs=payoffs, models=models, modelPlayer=modelPlayer)
                successors.append((model, fitness))
                
            # print(successors)
            
            successors.sort(reverse=True, key=lambda x: x[1])
            nextModels = [successors[i][0] for i in range(149)]
            nextWeights = [(successors[i][1]-successors[-1][1])**2 for i in range(149)]
        


            curModel = random.choices(nextModels, nextWeights)[0]
            # print(curModel)
            
             
            
        # print(bestModels)
        bestModels.append((curModel, calculateFitness(payoffs, models, ModelPlayer(curModel))))
    bestModels.sort(reverse=True, key=lambda x: x[1])
    return bestModels[0]

def train_hill_climb_tabu(numRestarts: int, numIterations: int):
    
    #we'll be storing a vector of past 3 game states, and if the other guy has defected AT ALL (even previous to those three states)
    #128 total states once you've made it to >= 3 rounds
    #and then 2^4 states
    #and then 2^2 states
    #and then only 1 state at first
    #so first 128 bits are just the regular states, next 16 = i == 2, next 4 = i == 1, next 1 = i == 0
    #128 + 16 + 4 + 1 = 149 total bits 
    
    #this is just a training set, we can swap it out with other models
    models = [Defector(), Cooperator(), GrimTrigger(), RandomChooser(), TitForTat(), TwoTitForTat(), NiceTitForTat(), SuspiciousTitForTat()]
    # models = [Cooperator(), Cooperator(), Cooperator()]

    bestModels = []
    
    
    visitedStates = LRUCache(10000)
    for _ in range(numRestarts): #number of random restarts. After 10 iterations we just return the best model so far
        curModel = random.getrandbits(149)
        visitedStates.put(curModel, curModel)
        
        # print(_)
        for i in range(numIterations):

            successors = [(curModel, calculateFitness(payoffs, models, ModelPlayer(curModel)))]
            
            for i in range(149): #at most we'll hill climb 300 iterations
                # print(i)
                # print(curModel)
                
                for j in range(random.randint(1, 10)): #always make at least 1 move, make more as temperature is lower so that you explore more combinations
                    model = curModel ^ (1 << random.randint(0, 148)) #flip 1 bit. This'll generate each successor
                while model in visitedStates.keyToNode:
                    for j in range(random.randint(1, 10)): #always make at least 1 move, make more as temperature is lower so that you explore more combinations
                        model = model ^ (1 << random.randint(0, 148))
                    
                # print(visitedStates.keyToNode)
                visitedStates.put(model, model)
                # print(model)
                modelPlayer = ModelPlayer(model)

                fitness = calculateFitness(payoffs=payoffs, models=models, modelPlayer=modelPlayer)
                successors.append((model, fitness))
                
            # print(successors)
            
            successors.sort(reverse=True, key=lambda x: x[1])
            nextModels = [successors[i][0] for i in range(149)]
            nextWeights = [(successors[i][1]-successors[-1][1])**2 for i in range(149)]
        


            curModel = random.choices(nextModels, nextWeights)[0]
            # print(curModel)
            
             
            
        # print(bestModels)
        bestModels.append((curModel, calculateFitness(payoffs, models, ModelPlayer(curModel))))
    bestModels.sort(reverse=True, key=lambda x: x[1])
    
    return bestModels[0]

def train_simulated_annealing(numRestarts, temperature):
    #generate a successor state. If better take it, otherwise don't
    curModel = random.getrandbits(149)
    models = [Defector(), Cooperator(), GrimTrigger(), TitForTat(), TwoTitForTat(), NiceTitForTat(), SuspiciousTitForTat()]
    bestGlobal = curModel 
    bestGlobalFitness = calculateFitness(payoffs, models, ModelPlayer(curModel))
    for _ in range(numRestarts):
        
            
        curModel = random.getrandbits(149)
        t = temperature
        while t > .1:
            # if random.randint(1, 1000) == 1:
            #     print(t)
            #     print(calculateFitness(payoffs, models, ModelPlayer(curModel)))
                
            nextModel = curModel 
            for i in range(random.randint(1, 10)):
                nextModel = nextModel ^ (1 << random.randint(1, 148))
            curModelFitness = calculateFitness(payoffs, models, ModelPlayer(curModel))
            nextModelFitness = calculateFitness(payoffs, models, ModelPlayer(nextModel))
            if nextModelFitness > bestGlobalFitness:
                bestGlobal = nextModel 
                bestGlobalFitness = nextModelFitness
                ''' #this is for when you have a Random player
                fitnesses = [] #to get rid of outliers from Random model
                for i in range(10):
                    fitnesses.append(calculateFitness(payoffs, models, ModelPlayer(nextModel)))
                if sum(fitnesses)//10 > bestGlobalFitness:
                    bestGlobal = curModel
                    bestGlobalFitness = sum(fitnesses)//10
                '''
            if nextModelFitness >= curModelFitness:
                curModel = nextModel 
            else:
                probChoose = e**(nextModelFitness-curModelFitness)
                curModel = random.choices([curModel, nextModel], [1-probChoose, probChoose])[0]
            t *= .99
    return (bestGlobal, calculateFitness(payoffs, models, ModelPlayer(bestGlobal)))

print("Annealing model:")
annealing_model = train_simulated_annealing(100, 100)
models = [Defector(), Cooperator(), GrimTrigger(), TitForTat(), TwoTitForTat(), NiceTitForTat(), SuspiciousTitForTat(), ModelPlayer(annealing_model[0])]
print(annealing_model)
print("Annealing model fitnesses:")
print(calculateAllFitnesses(payoffs, models))

 
    
print("Tabu search model: ")
trained_bin_model, performance = train_hill_climb_tabu(10, 250)
trained_bin_model = bin(trained_bin_model)
print(trained_bin_model, performance)
print("Tabu search model fitnesses:")
models = [Defector(), Cooperator(), GrimTrigger(), TitForTat(), TwoTitForTat(), NiceTitForTat(), SuspiciousTitForTat(), ModelPlayer(int(trained_bin_model[2:], 2))]
print(calculateAllFitnesses(payoffs, models))
# print((trained_bin_model>>148)&1, (trained_bin_model>>144)&1, (trained_bin_model>>128)&1) #prints what happens with no defections - usually 0 0 0            





            

    


