import csv
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

from Game.environment import Environment
from Game.dealer import Dealer
from Game.card import Card, Suit
from Agent.q_learning import Q_Learning
from Agent.random_agent import RandomAgent 



def print_environment_state_true():
    print("")
    print("### Players ###")
    for player_index, player in enumerate(environment.game_manager.players):  # Track player index
        print(f'- Player {player_index+1}')
        for hand_index, hand in enumerate(player.hands):
            print(f'    - Hand #{hand_index+1}')
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
        print(f'- Player {player_index+1}')
        for hand_index, hand in enumerate(player.hands):
            print(f'    - Hand #{hand_index+1}')
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

def save_q_tables_to_csv(q_learning_agent):
    for player_index, q_table in q_learning_agent.q_tables.items():
        filename = f"q_table_player_{player_index + 1}.csv"
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Player Hand", "Dealer Card", "Action", "Q-Value"])

            for (state, action), q_value in q_table.items():
                player_hand_repr, dealer_info = state
                dealer_value, dealer_suit = dealer_info
                player_hand_str = '; '.join(f"{val} of {suit}" for val, suit in player_hand_repr)
                dealer_card_str = f"{dealer_value} of {dealer_suit}"
                writer.writerow([player_hand_str, dealer_card_str, action, round(q_value, 4)])

def run_simulation():
    environment = Environment(deck_count=4)
    q_learning_agent = Q_Learning()
    random_agent = RandomAgent()

    rounds_to_simulate = 300000

    round_outcomes = []
    return_tracking = {0: [], 1: []}
    cumulative_return = {0: 0, 1: 0}
    win_tracking = {0: [], 1: []}
    cumulative_wins = {0: 0, 1: 0}

    for round_num in range(1, rounds_to_simulate + 1):
        print(f"\n=== Simulation Round {round_num} ===")

        round_finished = False

        while not round_finished:
            for player_index, player in enumerate(environment.game_manager.players):
                for hand_index, hand in enumerate(player.hands):
                    if hand.is_standing:
                        continue

                    if player_index == 0:
                        action = q_learning_agent.choose_action(
                            player_index, hand, environment.game_manager.dealer.face_up_card
                        )
                    else:
                        action = random_agent.choose_action(
                            hand, environment.game_manager.dealer.face_up_card
                        )

                    round_history_output = environment.input(player_index, hand_index, action=action)

                    if round_history_output:
                        print(">>> Round completed ✅")

                        # Process Q-learning updates ONLY for Player 0
                        player_0_history = [entry for entry in round_history_output if entry[0] == 0]
                        if player_0_history:
                            print(f"🧠 Updating Q-table for Player 0")
                            q_learning_agent.process_round_history_for_q_values(player_0_history)
                            # q_learning_agent.print_q_tables()  # Uncomment for spammy debugging

                        # Track outcomes
                        for p_idx, h_idx, hand_history, outcome, _ in round_history_output:
                            if not hand_history:
                                continue
                            stake = hand_history[-1][1]
                            if outcome == "WIN":
                                result = stake
                                cumulative_wins[p_idx] += 1
                            elif outcome == "LOSE":
                                result = -stake
                            else:
                                result = 0

                            cumulative_return[p_idx] += result
                            win_tracking[p_idx].append((round_num, cumulative_wins[p_idx]))
                            return_tracking[p_idx].append((round_num, cumulative_return[p_idx]))
                            round_outcomes.append([round_num, p_idx, h_idx, outcome, result])

                        round_finished = True
                        break  # Break inner loop once round ends
                if round_finished:
                    break

    # Save round outcomes
    with open("round_outcomes.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Round", "Player", "Hand", "Outcome", "Return"])
        writer.writerows(round_outcomes)

    print("Simulation complete. Results saved.")
    return q_learning_agent



if __name__ == "__main__":

    q_learning_agent = run_simulation()
    save_q_tables_to_csv(q_learning_agent)

    # Load results
    df = pd.read_csv("round_outcomes.csv")

    # Set up base rounds for alignment
    rounds = pd.Series(range(1, df["Round"].max() + 1), name="Round")

    # Plot 1: Cumulative Wins
    plt.figure(figsize=(12, 6))
    for player_id, label in zip([0, 1], ["Q-Learning", "Random"]):
        df_wins = df[(df["Player"] == player_id) & (df["Outcome"] == "WIN")]
        wins_cumulative = df_wins.groupby("Round").size().cumsum()
        wins_full = wins_cumulative.reindex(rounds).ffill().fillna(0).astype(int)
        plt.plot(rounds, wins_full, label=f"{label} Wins")

    plt.xlabel("Round")
    plt.ylabel("Cumulative Wins")
    plt.title("Cumulative Wins Over Rounds")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("cumulative_wins_comparison.png")
    plt.show()

    # Plot 2: Cumulative Returns
    plt.figure(figsize=(12, 6))
    for player_id, label in zip([0, 1], ["Q-Learning", "Random"]):
        df_player = df[df["Player"] == player_id]
        returns = df_player.groupby("Round")["Return"].sum().cumsum()
        returns_full = returns.reindex(rounds).ffill().fillna(0).astype(int)
        plt.plot(rounds, returns_full, label=f"{label} Return", linestyle="--")

    plt.xlabel("Round")
    plt.ylabel("Cumulative Return")
    plt.title("Cumulative Return Over Rounds")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("cumulative_returns_comparison.png")
    plt.show()



