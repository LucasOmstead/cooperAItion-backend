'''
So, how should I represent the game?

Game state is easiest to represent with a 2d array:
a[0] = all moves of 1st player
a[1] = all moves of 2nd player
-1 = no move yet, 0 = cooperate, 1 = defect

TODO:
-implement genetic algorithm
-implement hill-climbing algorithm
-tabu search (use LRU cache for hill-climbing
)






'''

import random
import time
#In general, past_moves[0] = your own moves, past_moves[1] = opponent's moves
class Player:
    def __init__(self):
        self.score = 0
    
    def get_action(self, past_moves, i):
        return 0 

class Defector(Player):
    def get_action(self, past_moves, i):
        return 1 

class Cooperator(Player):
    def get_action(self, past_moves, i):
        return 0
    
class GrimTrigger(Player):
    def get_action(self, past_moves, i):
        return 1 if 1 in past_moves[1] else 0

class RandomChooser(Player):
    def get_action(self, past_moves, i):
        return random.choice((0, 1))

class TitForTat(Player):
    def get_action(self, past_moves, i):
        if i == 0:
            return 0
        return past_moves[1][i-1]

class TwoTitForTat(Player):
    def get_action(self, past_moves, i):
        if i < 2:
            return 0
        return 1 if past_moves[1][i-1] == 1 and past_moves[1][i-2] == 1 else 0 

class NiceTitForTat(Player):
    def get_action(self, past_moves, i):
        if i == 0 or past_moves[1].count(1) / i < .2:
            return 0 
        return 1
    
class SuspiciousTitForTat(Player):
    def get_action(self, past_moves, i):
        if i == 0:
            return 1
        return past_moves[1][i-1]

class ModelPlayer(Player):
    def __init__(self, model):
        self.model = model
    def get_model_move(self, past_moves, i):
        if i < 3:
            if i == 0:
                return (self.model >> 148) & 1
            if i  == 1:
                encoding = (past_moves[0][0]<<1) + (past_moves[1][0])
                return ((self.model >> 144) >> encoding) & 1
            if i == 2:
                encoding = (past_moves[0][i-1]<<3) + (past_moves[0][i-2]<<2) + (past_moves[1][i-1]<<1) + (past_moves[1][i-2])
                return ((self.model >> 128) >> encoding) & 1
        else: #i >= 3
            encoding = (int(1 in past_moves[1])<<6) + (past_moves[0][i-1]<<5) + (past_moves[0][i-2]<<4) + (past_moves[0][i-3]<<3) \
                        + (past_moves[1][i-1]<<2) + (past_moves[1][i-2]<<1) + past_moves[1][i-3]
            return (self.model >> encoding) & 1    
        
    def get_action(self, past_moves, i):
        return self.get_model_move(past_moves, i)

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
def train_hill_climb():
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
    for _ in range(10): #number of random restarts. After 10 iterations we just return the best model so far
        curModel = random.getrandbits(149)
        temperature = 100
        print(_)
        # print(bestModels)
        # t = time.time()
        
            
        # print(_)
        # print(calculateFitness(payoffs, models, ModelPlayer(curModel)))
        for _ in range(1000):
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
        # print(nextWeights)
        # print(successors[0][1])
        # print(curModel != successors[0][0])


            curModel = random.choices(nextModels, nextWeights)[0]
            # print(curModel)
            
             
            
        # print(bestModels)
        bestModels.append((curModel, calculateFitness(payoffs, models, ModelPlayer(curModel))))
    bestModels.sort(reverse=True, key=lambda x: x[1])
    return bestModels[0]

trained_bin_model, performance = train_hill_climb()
print((trained_bin_model>>148)&1, (trained_bin_model>>144)&1, (trained_bin_model>>128)&1)
trained_bin_model = bin(trained_bin_model)
print(trained_bin_model, performance)

models = [Defector(), Cooperator(), GrimTrigger(), RandomChooser(), TitForTat(), TwoTitForTat(), NiceTitForTat(), SuspiciousTitForTat(), ModelPlayer(int(trained_bin_model[2:], 2))]



for i in range(len(models)):
    print(calculateFitness(payoffs, models[:i] + models[i+1:], models[i]))

print(calculateAllFitnesses(payoffs, models))
            





            


# models = [Defector(), Cooperator(), GrimTrigger(), RandomChooser(), TitForTat(), TwoTitForTat(), NiceTitForTat(), SuspiciousTitForTat(), ModelPlayer()]
# print(playGame(payoffs, SuspiciousTitForTat(), Defector(), 10))
# t = time.time()
# calculateFitness(payoffs, models)
# print(time.time()-t)
            

    


