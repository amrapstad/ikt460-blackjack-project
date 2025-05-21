from Simulation.training import *
from Simulation.evaluation import *

from Agents.random_agent import RandomAgent
from Agents.optimal_agent import OptimalAgent

if __name__ == "__main__":
    # --- Q-agent training ---
    current_pos = 0
    current_rounds = 500000 # Number of rounds in training

    q_learning_result = run_simulation_q_learning(num_players=3, q_agent_pos=current_pos, rounds_to_simulate=current_rounds) # This trains a regular Q-agent
    q_learning_agent = q_learning_result[current_pos] # q_learning_result[q_agent_pos]

    # Training results
    plot_training_results(q_learning_result)
    plot_action_distribution(q_learning_result)
    plot_state_value_heatmaps(q_learning_agent)
    plot_q_value_convergence(q_learning_agent, window_size=int(current_rounds*0.01))
    # -----------------------


    # --- MBVE Q-agent training ---
    mbve_learning_result = run_simulation_q_learning(num_players=3, q_agent_pos=current_pos, with_mbve=True, rounds_to_simulate=current_rounds) # This trains a MBVE Q-agent
    mbve_learning_agent = mbve_learning_result[current_pos]

    # Training results
    plot_training_results(mbve_learning_result)
    plot_action_distribution(mbve_learning_result)
    plot_state_value_heatmaps(mbve_learning_agent)
    plot_q_value_convergence(mbve_learning_agent, window_size=int(current_rounds*0.01))
    # -----------------------


    # --- Varied position and player number ---
    num_games_eval = 50000 # Number of rounds in evaluation

    """
    # 2 players (Q-agent vs. MBVE-agent)
    eval_setup1 = [q_learning_agent, mbve_learning_agent]
    setup_num = 0
    run_evaluation(eval_setup1, eval_id=setup_num, num_games=num_games_eval)
    plot_evaluation_results(eval_setup1, eval_id=setup_num, window_size=500)
    plot_return_distributions(eval_setup1, eval_id=setup_num, train_id=0)
    """

    # 7 players (Q-agent first)
    eval_setup2 = [q_learning_agent,
                   OptimalAgent(),
                   RandomAgent(0), RandomAgent(1), RandomAgent(2), RandomAgent(3),
                   mbve_learning_agent]
    setup_num = 1
    run_evaluation(eval_setup2, eval_id=setup_num, num_games=num_games_eval)
    plot_evaluation_results(eval_setup2, eval_id=setup_num, window_size=500)
    plot_return_distributions(eval_setup2, eval_id=setup_num, train_id=0)

    # Wait for user input before proceeding
    input("Press key to proceed...")

    # 7 players (MBVE-agent first)
    eval_setup3 = [mbve_learning_agent,
                   OptimalAgent(),
                   RandomAgent(0), RandomAgent(1), RandomAgent(2), RandomAgent(3),
                   q_learning_agent]
    setup_num = 2
    run_evaluation(eval_setup3, eval_id=setup_num, num_games=num_games_eval)
    plot_evaluation_results(eval_setup3, eval_id=setup_num, window_size=int(num_games_eval*0.01))
    plot_return_distributions(eval_setup3, eval_id=setup_num, train_id=0)