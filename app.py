from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json 
from game import * #mainly train_simulated_annealing and successor
from players import * #all player types

app = Flask(__name__)

# Configure CORS to only allow your frontend domain
CORS(app, origins=["http://localhost", "http://localhost:80"])

# Configure rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per hour", "10 per minute"],
    storage_uri="memory://"
)

@app.route('/index')
def home():
    return "Hello, world!"

@app.route('/get_model', methods=["POST"])
@limiter.limit("2 per minute")  # Only 2 model generations per minute per IP
def get_players():
    j = request.get_json()
    players = j["players"]
    payoffs = j["payoffs"]
    # print(players)
    models = []
    #Ugly code but it's ok
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
    
    model, perf = train_simulated_annealing(numRestarts=5, temperature=100, successor=successor, models=models, payoffs=payoffs, memSize=149)
    # print(models)
    print(bin(model))
    # print(perf)
    return {"model": bin(model)[2:]}

@app.route('/getmodel')
def get_model():
    # This endpoint appears to be unused/broken - disable it
    return {"error": "This endpoint is deprecated"}, 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
