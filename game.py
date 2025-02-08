'''
So, how should I represent the game?

Game state is easiest to represent with a 2d array:
a[0] = all moves of 1st player
a[1] = all moves of 2nd player
-1 = no move yet, 0 = cooperate, 1 = defect

Neural network takes in that vector (length 20 since we're doing 10 iterations each)
and produces a probability of choosing cooperate 


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
    def get_action(self, past_moves, i):
        #Implement model logic
        return 0 

cooperateReward = (5, 5)
betrayalReward = (8, 0)
betrayedReward = (0, 8)
bothBetray = (2, 2)
#payoffmatrix[player1choice][player2choice] = reward for player1, player2

payoffs = [[cooperateReward[0], betrayedReward[0]], 
             [betrayalReward[0], bothBetray[0]]]


print(payoffs)

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

def calculateFitness(payoffs, models):
    #each player in the pool plays 1 game against each other
    models = [Defector(), Cooperator(), GrimTrigger(), RandomChooser(), TitForTat(), TwoTitForTat(), NiceTitForTat(), SuspiciousTitForTat(), ModelPlayer()]

    scores = [0 for i in range(len(models))]

    for i in range(len(models)):
        for j in range(len(models)):
            score1, score2 = playGame(payoffs, models[i], models[j], 10)
            scores[i] += score1 
            scores[j] += score2 
    return scores

#First we'll use hill-climbing; should be easier to implement
def train_hill_climb():
    #we'll be storing a vector of past 3 game states, and if the other guy has defected AT ALL
    #128 total states once you've made it past 3 rounds
    #before then, there's 2^6 states
    #and then 2^4 states
    #and then 2^2 states
    #and then only 1 state at first
    #so first 128 bits are just the regular states, then next 8 are first 3 states, then next 4 are after 2 moves, then next is after 1 move
    # curModel = random.getrandbits(213)
    # def getMove(past_moves, i):
    #     if i < 3:
    #         if i == 0:
    #             return (curModel >> 212) & 1
    #         if i  == 1:
    #             encoding = past_moves[0][0]<<1 + past_moves[1][0]
    #             return ((curModel >> 208) >> encoding) & 1
    #         if i == 2:
    #             encoding = past_moves[0][0]

            


models = [Defector(), Cooperator(), GrimTrigger(), RandomChooser(), TitForTat(), TwoTitForTat(), NiceTitForTat(), SuspiciousTitForTat(), ModelPlayer()]
print(playGame(payoffs, SuspiciousTitForTat(), Defector(), 10))
t = time.time()
calculateFitness(payoffs, models)
print(time.time()-t)
            

    


