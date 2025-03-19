# genetic_simulations.py
import csv
import time
import random
from math import ceil
from game import calculateFitness, local_beam_search, playGame, calculateAllFitnesses, successor, train_basic_genetic, train_basic_genetic_mutation
from players import myModels, Defector, Cooperator, GrimTrigger, TitForTat, TwoTitForTat, NiceTitForTat, SuspiciousTitForTat

def head_to_head(player1, player2, payoffs, numRounds):
    """Run head-to-head matches between two players.
    For each match, randomly select a number of rounds between minRounds and maxRounds.
    Returns the average score of player1 and player2 over all matches."""
    s1, s2 = playGame(payoffs, player1, player2, numRounds)
    return s1, s2

def head_to_head_all(evolved_player, baselines, payoffs):
    """Evaluate the evolved model against each baseline model using head-to-head matches.
    Returns the average evolved model score over all baseline matchups."""
    total = 0
    count = 0
    for baseline in baselines:
        avg_evolved, _ = head_to_head(evolved_player, baseline, payoffs, numRounds=20)
        total += avg_evolved
        count += 1
    return round(total / count, 2) if count > 0 else 0

def run_genetic_experiment(method, params, num_trials, payoffs, memSize, baseLineModels, config_id):
    """Modified experiment runner for genetic algorithms"""
    results = []
    for trial in range(num_trials):
        start_time = time.perf_counter()
        
        if method == 'genetic':
            best_model = train_basic_genetic(
                params['pop_size'],
                params['numIterations'],  # Now matches function parameter name
                params['percentForCrossover'],
                baseLineModels,
                payoffs,
                memSize
            )
        elif method == 'genetic_mutation':
            best_model = train_basic_genetic_mutation(
                params['pop_size'],
                params['numIterations'],  # Now matches function parameter name
                params['percentForCrossover'],
                params['mutationPercent'],  # Corrected key name
                params['mutationCount'], 
                baseLineModels,
                payoffs,
                memSize
            )
        elif method == 'local_beam':
            best_model = local_beam_search(
                params['numIterations'],
                params['k'],
                successor,
                baseLineModels,
                payoffs,
                memSize
            )

        fitness = best_model[1]  # Extract fitness from tuple
        best_model = best_model[0]

        end_time = time.perf_counter()
        elapsed = end_time - start_time

        # Evaluation metrics
        models = baseLineModels + [myModels[memSize](best_model)]

        evolved_player = myModels[memSize](best_model)
        h2h_score = head_to_head_all(evolved_player, baseLineModels, payoffs)

        results.append({
            'config_id': config_id,
            'method': method,
            'trial': trial,
            'params': str(params),
            'fitness': round(fitness, 2),
            'head_to_head_score': h2h_score,
            'runtime': round(elapsed, 5),
            'memory': memSize,
            'bit_string': bin(best_model)[2:]
        })
    return results

def run_genetic_suite(payoffs, memory_sizes, baseLineModels):
    """Configure and run genetic algorithm experiments"""
    # Genetic Algorithm without mutation
    genetic_configs = []
    for pop in [10, 20, 40, 80]:
        for iters in [10, 20, 40, 80, 160]:
            genetic_configs.append({
                'pop_size': pop,
                'numIterations': iters,
                'percentForCrossover': 1.0
            })

    # Genetic Algorithm with mutation
    mutation_configs = []
    for pop in  [10, 20, 40, 80]:
        for iters in [10, 20, 40, 80, 160]:
            mutation_configs.append({
                'pop_size': pop,
                'numIterations': iters,
                'percentForCrossover': 1.0,
                'mutationPercent': 0.05,
                'mutationCount': 2
            })

    local_beam_configs = []
    for iters in [10, 20, 40, 80, 160, 320]:
        for k in [1, 2, 4, 8, 16, 32]:
            local_beam_configs.append({
                'k': k,
                'numIterations': iters,
            })

    all_results = []
    config_id = 1
    print("ASCDASD")
    # Run experiments across memory sizes
    for mem in memory_sizes:
        # Basic genetic algorithm
        for params in genetic_configs:
            results = run_genetic_experiment('genetic', params, 5, 
                                           payoffs, mem, baseLineModels, config_id)
            all_results.extend(results)
            config_id += 1
    print("THS")
    for mem in memory_sizes:     
        # Genetic algorithm with mutation
        for params in mutation_configs:
            results = run_genetic_experiment('genetic_mutation', params, 5,
                                            payoffs, mem, baseLineModels, config_id)
            all_results.extend(results)
            config_id += 1
    print("ABCSD")
    for mem in memory_sizes:
        for params in local_beam_configs:
            results = run_genetic_experiment('local_beam', params, 5,
                                            payoffs, mem, baseLineModels, config_id)
            all_results.extend(results)
            config_id += 1
            
    return all_results

# Configure payoff matrix and baselines
payoffs = [[3, 0], [5, 1]]
baseLineModels = [
    Defector(), Cooperator(), GrimTrigger(), TitForTat(),
    TwoTitForTat(), NiceTitForTat(), SuspiciousTitForTat()
]

# Run experiments
results = run_genetic_suite(payoffs, [21, 85, 149], baseLineModels)

# Save results
with open('genetic_results.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print("Genetic experiments complete. Results saved to genetic_results.csv")