import csv
import time
import random
from math import e, ceil
from game import train_simulated_annealing, train_hill_climb, calculateAllFitnesses, successor, playGame, train_hill_climb_tabu
from players import myModels, Defector, Cooperator, GrimTrigger, TitForTat, TwoTitForTat, NiceTitForTat, SuspiciousTitForTat

def head_to_head(player1, player2, payoffs, minRounds=50, maxRounds=200, numMatches=20):
    """Run head-to-head matches between two players.
    For each match, randomly select a number of rounds between minRounds and maxRounds.
    Returns the average score of player1 and player2 over all matches."""
    total_score1 = 0
    total_score2 = 0
    for _ in range(numMatches):
        numRounds = random.randint(minRounds, maxRounds)
        s1, s2 = playGame(payoffs, player1, player2, numRounds)
        total_score1 += s1
        total_score2 += s2
    avg_score1 = total_score1 / numMatches
    avg_score2 = total_score2 / numMatches
    return avg_score1, avg_score2

def head_to_head_all(evolved_player, baselines, payoffs, minRounds=50, maxRounds=200, numMatches=20):
    """Evaluate the evolved model against each baseline model using head-to-head matches.
    Returns the average evolved model score over all baseline matchups."""
    total = 0
    count = 0
    for baseline in baselines:
        avg_evolved, _ = head_to_head(evolved_player, baseline, payoffs, minRounds, maxRounds, numMatches)
        total += avg_evolved
        count += 1
    return round(total / count, 2) if count > 0 else 0

def run_experiment_for_config(method, params, num_trials, payoffs, memSize, baseLineModels, config_id):
    """Run experiments for one specific parameter configuration.
    The results include a unique configuration identifier and the memory size."""
    results = []
    for trial in range(num_trials):
        start_time = time.perf_counter()
        best_model = None

        if method == 'simulated_annealing':
            best_model, fitness = train_simulated_annealing(
                params['numRestarts'],
                params['temperature'],
                successor,
                baseLineModels,
                payoffs,
                memSize
            )
        elif method == 'hill_climb':
            best_model, fitness = train_hill_climb(
                params['numRestarts'],
                params['numIterations'],
                successor,
                memSize
            )
        elif method == 'tabu_search':
            best_model, fitness = train_hill_climb_tabu(
                params['numRestarts'],
                params['numIterations'],
                successor,
                memSize,
                params['tabuSize']
            )

        end_time = time.perf_counter()
        elapsed = end_time - start_time

        # Evaluate tournament score (evolved model added to baseline pool)
        models = baseLineModels + [myModels[memSize](best_model)]
        tournament_scores = calculateAllFitnesses(payoffs, models)
        rounded_tournament_scores = [round(score, 2) for score in tournament_scores]

        # Evaluate head-to-head performance: evolved model vs. each baseline.
        evolved_player = myModels[memSize](best_model)
        head_to_head_score = head_to_head_all(evolved_player, baseLineModels, payoffs, minRounds=50, maxRounds=200, numMatches=20)

        results.append({
            'config_id': config_id,
            'method': method,
            'trial': trial,
            'params': str(params),
            'fitness': round(fitness, 2),
            'tournament_score': str(rounded_tournament_scores),
            'head_to_head_score': head_to_head_score,
            'runtime': round(elapsed, 5),
            'memory': memSize,
            'bit_string': bin(best_model)[2:]  # without "0b" prefix
        })
    return results

def run_experiments(method, param_configs, num_trials, payoffs, memSize, baseLineModels):
    """Run experiments for multiple parameter configurations.
    Returns a list of results."""
    all_results = []
    global config_id
    for params in param_configs:
        results = run_experiment_for_config(method, params, num_trials, payoffs, memSize, baseLineModels, config_id)
        all_results.extend(results)
        config_id += 1
    return all_results

def run_experiments_over_memories(method, param_configs, num_trials, payoffs, memory_sizes, baseLineModels):
    """Run experiments for multiple memory sizes and parameter configurations.
    Returns a list of results."""
    all_results = []
    for mem in memory_sizes:
        results = run_experiments(method, param_configs, num_trials, payoffs, mem, baseLineModels)
        all_results.extend(results)
    return all_results

# Set up payoff parameters as provided
# cooperateReward = (5, 5)
# betrayalReward = (8, 0)
# betrayedReward = (0, 8)
# bothBetray = (2, 2)
# payoffs = [
#     [cooperateReward[0], betrayedReward[0]],
#     [betrayalReward[0], bothBetray[0]]
# ]
payoffs = [[3, 0], [5, 1]]

# Define baseline models
baseLineModels = [
    Defector(),
    Cooperator(),
    GrimTrigger(),
    TitForTat(),
    TwoTitForTat(),
    NiceTitForTat(),
    SuspiciousTitForTat()
]

# Define parameter configurations for simulated annealing.
# For simulated annealing, we vary numRestarts and temperature.
numRestarts_values_SA = [1, 2, 3, 4, 5]
temperature_values = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45]

# Define a list of memory sizes to test
memory_sizes = [21, 85, 149]
config_id = 1
# Instead of using a dict, build a list of parameter configurations for SA.
param_configs_SA = []
for nr in numRestarts_values_SA:
    for temp in temperature_values:
        param_configs_SA.append({'numRestarts': nr, 'temperature': temp})


# Define parameter configurations for hill climbing.
# For hill climbing, we vary numRestarts and numIterations.
numRestarts_values_HC = [1, 2, 3, 4, 5]
numIterations_values = [10, 20, 30, 40, 50]

param_configs_HC = []
for nr in numRestarts_values_HC:
    for iters in numIterations_values:
        param_configs_HC.append({'numRestarts': nr, 'numIterations': iters})

# Run experiments for simulated annealing over multiple memory sizes
results_SA = run_experiments_over_memories('simulated_annealing', param_configs_SA,
                                           num_trials=5,
                                           payoffs=payoffs,
                                           memory_sizes=memory_sizes,
                                           baseLineModels=baseLineModels)

# Run experiments for hill climbing over multiple memory sizes
results_HC = run_experiments_over_memories('hill_climb', param_configs_HC,
                                           num_trials=5,
                                           payoffs=payoffs,
                                           memory_sizes=memory_sizes,
                                           baseLineModels=baseLineModels)

# Combine results from both methods
all_results = results_SA + results_HC

# Save the results to CSV
with open('hill_annealing.csv', mode='w', newline='') as csvfile:
    fieldnames = ['config_id', 'method', 'trial', 'params', 'fitness', 'tournament_score', 'head_to_head_score', 'runtime', 'memory', 'bit_string']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in all_results:
        writer.writerow(row)

print("Experiment complete. Results saved to 'hill_annealing.csv'.")