from flask import Flask, request, jsonify
from flask_cors import CORS
import json 
from game import * #mainly train_simulated_annealing and successor
from players import * #all player types

app = Flask(__name__)
CORS(app)

@app.route('/index')
def home():
    return "Hello, world!"

@app.route('/get_model', methods=["POST"])
def get_players():
    j = request.get_json()
    players = j["players"]
    payoffs = j["payoffs"]
    # print(players)
    models = []
    #ik this code is ugly, easiest way to do it though
    for i in range(players['Tit For Tat']):
        models.append(TitForTat())
    for i in range(players['Grim Trigger']):
        models.append(GrimTrigger())
    for i in range(players['Two Tit For Tat']):
        models.append(TwoTitForTat())
    for i in range(players['Nice Tit For Tat']):
        models.append(NiceTitForTat())
    for i in range(players['Always Cooperate']):
        models.append(Cooperator())
    for i in range(players['Always Defect']):
        models.append(Defector())
    for i in range(players['Suspicious Tit For Tat']):
        models.append(SuspiciousTitForTat())
    
    model, perf = train_simulated_annealing(numRestarts=5, temperature=100, successor=successor, models=models, payoffs=payoffs)
    # print(models)
    print(bin(model))
    # print(perf)
    return {"model": bin(model)[2:]}

@app.route('/getmodel')
def get_model():
    data = request.get_json()
    models = []
    print(data)

    return train_simulated_annealing(numRestarts=10, temperature=100, successor=successor, models=models)

    

if __name__ == '__main__':
    app.run(debug=True)
