import random
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