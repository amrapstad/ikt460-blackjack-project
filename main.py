from Simulation.training import *
from Simulation.evaluation import *

from Agents.random_agent import RandomAgent
from Agents.optimal_agent import OptimalAgent

if __name__ == "__main__":
    # --- Q-agent training ---
    current_pos = 0
    current_rounds = 100000 # Number of rounds in training

    q_learning_result = run_simulation_q_learning(num_players=3, q_agent_pos=current_pos, rounds_to_simulate=current_rounds) # This trains a regular Q-agent
    q_learning_agent = q_learning_result[current_pos] # q_learning_result[q_agent_pos]

    # Training results
    plot_training_results(q_learning_result)
    plot_action_distribution(q_learning_result)
    plot_state_value_heatmaps(q_learning_agent)
    plot_q_value_convergence(q_learning_agent, window_size=100)


    # --- MBVE Q-agent training ---
    mbve_learning_result = run_simulation_q_learning(num_players=3, q_agent_pos=current_pos, with_mbve=True, rounds_to_simulate=current_rounds) # This trains a MBVE Q-agent
    mbve_learning_agent = mbve_learning_result[current_pos]

    # Training results
    plot_training_results(mbve_learning_result)
    plot_action_distribution(mbve_learning_result)
    plot_state_value_heatmaps(mbve_learning_agent)
    plot_q_value_convergence(mbve_learning_agent, window_size=100)


    # --- Varied position and player number ---
    num_games_eval = 10000 # Number of rounds in evaluation

    # Setup 1: 2 players (Q-agent vs. MBVE-agent)
    eval_setup1 = [q_learning_agent, mbve_learning_agent]
    setup_num = 0
    run_evaluation(eval_setup1, eval_id=setup_num, num_games=num_games_eval)
    plot_evaluation_results(eval_setup1, eval_id=setup_num, window_size=100)
    plot_return_distributions(eval_setup1, eval_id=setup_num, train_id=0)

    # Setup 2: 5 players (Q-agent - Optimal - Random - Random - MBVE-agent)
    eval_setup2 = [q_learning_agent, RandomAgent(), OptimalAgent(), RandomAgent(1), mbve_learning_agent]
    setup_num = 1
    run_evaluation(eval_setup2, eval_id=setup_num, num_games=num_games_eval)
    plot_evaluation_results(eval_setup2, eval_id=setup_num, window_size=100)
    plot_return_distributions(eval_setup2, eval_id=setup_num, train_id=0)

    print("The end")
