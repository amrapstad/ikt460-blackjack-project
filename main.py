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
                dealer_value = dealer_info
                player_hand_str = ', '.join(str(val) for val in player_hand_repr)
                dealer_card_str = f"{dealer_value}"
                writer.writerow([player_hand_str, dealer_card_str, action, round(q_value, 4)])

def run_simulation(rounds_to_simulate=1000000):
    environment = Environment(deck_count=4)
    q_learning_agent = Q_Learning()
    random_agent = RandomAgent()



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

                        # Q-table updates
                        player_0_history = [entry for entry in round_history_output if entry[0] == 0]
                        if player_0_history:
                            print(f"🧠 Updating Q-table for Player 0")
                            q_learning_agent.process_round_history_for_q_values(player_0_history)

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
                        break
                if round_finished:
                    break

    # Save round outcomes
    with open("round_outcomes.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Round", "Player", "Hand", "Outcome", "Return"])
        writer.writerows(round_outcomes)

    # ✅ Save the Q-table at the end of simulation
    save_q_tables_to_csv(q_learning_agent)

    print("Simulation complete. Results saved.")
    return q_learning_agent


def run_evaluation(q_learning_agent, num_games):
    print(f"\n🔍 Running evaluation over {num_games} games...")
    environment = Environment(deck_count=4)
    random_agent = RandomAgent()

    results = []

    for game_num in range(1, num_games + 1):
        print(f"\n--- Evaluation Game {game_num} ---")
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
                        print(">>> Evaluation Round completed ✅")
                        # Record the result but do NOT update Q-values
                        for p_idx, h_idx, hand_history, outcome, _ in round_history_output:
                            if not hand_history:
                                continue
                            stake = hand_history[-1][1]
                            if outcome == "WIN":
                                result = stake
                            elif outcome == "LOSE":
                                result = -stake
                            else:
                                result = 0
                            results.append([game_num, p_idx, h_idx, outcome, result])

                        round_finished = True
                        break
                if round_finished:
                    break

    # Save evaluation results
    with open("evaluation_results.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Game", "Player", "Hand", "Outcome", "Return"])
        writer.writerows(results)

    print("✅ Evaluation complete. Results saved to 'evaluation_results.csv'")

def plot_evaluation_results():
    df_eval = pd.read_csv("evaluation_results.csv")

    rounds = pd.Series(range(1, df_eval["Game"].max() + 1), name="Game")

    # Plot 1: Cumulative Wins (Evaluation)
    plt.figure(figsize=(12, 6))
    for player_id, label in zip([0, 1], ["Q-Learning", "Random"]):
        df_wins = df_eval[(df_eval["Player"] == player_id) & (df_eval["Outcome"] == "WIN")]
        wins_cumulative = df_wins.groupby("Game").size().cumsum()
        wins_full = wins_cumulative.reindex(rounds).ffill().fillna(0).astype(int)
        plt.plot(rounds, wins_full, label=f"{label} Wins")

    plt.xlabel("Game")
    plt.ylabel("Cumulative Wins")
    plt.title("Evaluation: Cumulative Wins Over Games")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("evaluation_cumulative_wins.png")
    plt.show()

    # Plot 2: Cumulative Returns (Evaluation)
    plt.figure(figsize=(12, 6))
    for player_id, label in zip([0, 1], ["Q-Learning", "Random"]):
        df_player = df_eval[df_eval["Player"] == player_id]
        returns = df_player.groupby("Game")["Return"].sum().cumsum()
        returns_full = returns.reindex(rounds).ffill().fillna(0).astype(int)
        plt.plot(rounds, returns_full, label=f"{label} Return", linestyle="--")

    plt.xlabel("Game")
    plt.ylabel("Cumulative Return")
    plt.title("Evaluation: Cumulative Return Over Games")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("evaluation_cumulative_returns.png")
    plt.show()


def plot_training_results(csv_path="round_outcomes.csv"):
    df = pd.read_csv(csv_path)
    rounds = pd.Series(range(1, df["Round"].max() + 1), name="Round")

    # Plot 1: Cumulative Wins (Training)
    plt.figure(figsize=(12, 6))
    for player_id, label in zip([0, 1], ["Q-Learning", "Random"]):
        df_wins = df[(df["Player"] == player_id) & (df["Outcome"] == "WIN")]
        wins_cumulative = df_wins.groupby("Round").size().cumsum()
        wins_full = wins_cumulative.reindex(rounds).ffill().fillna(0).astype(int)
        plt.plot(rounds, wins_full, label=f"{label} Wins")

    plt.xlabel("Round")
    plt.ylabel("Cumulative Wins")
    plt.title("Training: Cumulative Wins Over Rounds")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("training_cumulative_wins.png")
    plt.show()

    # Plot 2: Cumulative Returns (Training)
    plt.figure(figsize=(12, 6))
    for player_id, label in zip([0, 1], ["Q-Learning", "Random"]):
        df_player = df[df["Player"] == player_id]
        returns = df_player.groupby("Round")["Return"].sum().cumsum()
        returns_full = returns.reindex(rounds).ffill().fillna(0).astype(int)
        plt.plot(rounds, returns_full, label=f"{label} Return", linestyle="--")

    plt.xlabel("Round")
    plt.ylabel("Cumulative Return")
    plt.title("Training: Cumulative Return Over Rounds")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("training_cumulative_returns.png")
    plt.show()

def plot_return_distributions(train_path="round_outcomes.csv", eval_path="evaluation_results.csv"):
    # Define bin edges and labels
    bin_edges = [-float("inf"), -40, -20, -10, -5, 0, 5, 10, 20, 40, float("inf")]
    bin_labels = ["< -40", "-40", "-20", "-10", "-5", "0", "5", "10", "20", "40+"]

    def prepare_distribution(df, label):
        df["Bin"] = pd.cut(df["Return"], bins=bin_edges, labels=bin_labels, right=False)
        df["Source"] = label
        return df

    # Load and label the data
    df_train = pd.read_csv(train_path)
    df_train = prepare_distribution(df_train, "Training")

    df_eval = pd.read_csv(eval_path)
    df_eval = prepare_distribution(df_eval, "Evaluation")

    # Combine both
    df_all = pd.concat([df_train, df_eval], ignore_index=True)

    player_labels = ["Q-Learning", "Random"]

    for player_id in [0, 1]:
        df_player = df_all[df_all["Player"] == player_id]

        # Group by Bin and Source (training/eval)
        grouped = df_player.groupby(["Bin", "Source"], observed=False).size().unstack(fill_value=0).reindex(bin_labels)

        # Plot
        ax = grouped.plot(kind="bar", figsize=(12, 6), width=0.7)
        plt.title(f"{player_labels[player_id]} Return Distribution (Training vs Evaluation)")
        plt.xlabel("Return Range")
        plt.ylabel("Count")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()

        # Add value labels above each bar
        for container in ax.containers:
            for bar in container:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f"{int(height)}",
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=9)

        # Save and show
        filename = f"return_distribution_{player_labels[player_id].lower().replace(' ', '_')}.png"
        plt.savefig(filename)
        plt.show()



if __name__ == "__main__":
    # Training
    q_learning_agent = run_simulation(rounds_to_simulate=1000000)
    plot_training_results()

    # Evaluation
    run_evaluation(q_learning_agent, num_games=10000)
    plot_evaluation_results()

    # Win/Loss Distribution of Stakes
    plot_return_distributions()



