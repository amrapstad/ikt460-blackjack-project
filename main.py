from Simulation.training import *
from Simulation.evaluation import *

from Agents.random_agent import RandomAgent
from Agents.optimal_agent import OptimalAgent

def print_environment_state_true(environment):
    print("")
    print("### Players ###")
    for player_index, player in enumerate(environment.game_manager.players):  # Track player index
        print(f'- Player {player_index + 1}')
        for hand_index, hand in enumerate(player.hands):
            print(f'    - Hand #{hand_index + 1}')
            print(f'        STANDING: {hand.is_standing}')
            for card in hand.hand_cards:
                print(f'        {card.suit}, Value: {card.value}')
            print(f'        Possible values: {hand.get_possible_values()}')
            print(f'        Hand stake: {hand.stake}')
    print('### Dealer ###')
    for card in environment.game_manager.dealer.dealer_cards:
        print(f'    {card.suit}, Value: {card.value}')
    print(f'    Possible values: {environment.game_manager.dealer.get_possible_values()}')
    print("### Overviews ###")
    print(f'Total available cards: {len(environment.game_manager.available_cards)}\n')


def print_environment_state_player_view(environment):
    print("")
    print("### Players ###")
    for player_index, player in enumerate(environment.game_manager.players):  # Track player index
        print(f'- Player {player_index + 1}')
        for hand_index, hand in enumerate(player.hands):
            print(f'    - Hand #{hand_index + 1}')
            print(f'        STANDING: {hand.is_standing}')
            for card in hand.hand_cards:
                print(f'        {card.suit}, Value: {card.value}')
            print(f'        Possible values: {hand.get_possible_values()}')
            print(f'        Hand stake: {hand.stake}')
    print('### Dealer ###')
    card = environment.game_manager.dealer.face_up_card
    print(f'    {card.suit}, Value: {card.value}')
    print("### Overviews ###")
    print(f'Total available cards: {len(environment.game_manager.available_cards)}')


if __name__ == "__main__":
    """
    Example:
        players = [q_learning_agent, OptimalAgent(), RandomAgent()]
        Q-agent: players[0]
    """

    # Q-agent training
    current_pos = 0
    q_learning_result = run_simulation_q_learning(num_players=4, q_agent_pos=current_pos, rounds_to_simulate=1000)
    q_learning_agent = q_learning_result[current_pos] # q_learning_result[q_agent_pos]

    # MBVE Q-agent training
    # TODO: Train a q-agent with mbve

    # Training results
    plot_training_results(q_learning_result)
    plot_state_value_heatmap(q_learning_agent)
    plot_q_value_convergence(q_learning_agent, window_size=100)

    # Evaluation
    eval_players = [q_learning_agent, OptimalAgent(), RandomAgent()]
    run_evaluation(eval_players, num_games=1000)
    plot_evaluation_results(eval_players)

    # Win/Loss Distribution of Stakes
    plot_return_distributions(eval_players)
    plot_action_distribution(eval_players)

    print("The end")
