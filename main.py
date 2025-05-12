import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

from Game.environment import Environment
from Game.dealer import Dealer
from Game.card import Card, Suit
from Agent.q_learning import Q_Learning
from Agent.random_agent import RandomAgent
from Agent.optimal_agent import OptimalAgent

from definitions import CSV_DIR, PLOTS_DIR

def print_environment_state_true(environment):
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
        filepath = os.path.join(CSV_DIR, filename)
        with open(filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Player Hand", "Dealer Card", "Action", "Q-Value"])

            for (state, action), q_value in q_table.items():
                player_hand_repr, dealer_info = state
                dealer_value = dealer_info
                player_hand_str = ', '.join(str(val) for val in player_hand_repr)
                dealer_card_str = f"{dealer_value}"
                writer.writerow([player_hand_str, dealer_card_str, action, round(q_value, 4)])


# Setup:
# q_learning_pos: 0-4 (left to right)
# This only trains one q-learning agent
# Takes in number of players and q-agent position
# 2 to 4 dummy agents
# Requires at least one random and one optimal agent
def run_simulation_q_learning(num_players=3, q_agent_pos=0, rounds_to_simulate=1000000):
    environment = Environment(deck_count=4, players=num_players)

    players = []
    optimal_added = False

    for i in range(num_players):
        if q_agent_pos == i:
            players.append((Q_Learning(), "q-learning"))
            continue
        if not optimal_added:
            optimal_added = True
            players.append((OptimalAgent(), "optimal"))
            continue
        players.append((RandomAgent(), "random"))

    round_outcomes = []

    return_tracking = { }
    for i in range(num_players):
        return_tracking[i] = []

    cumulative_return = { }
    for i in range(num_players):
        cumulative_return[i] = 0

    win_tracking = { }
    for i in range(num_players):
        win_tracking[i] = []

    cumulative_wins = { }
    for i in range(num_players):
        cumulative_wins[i] = 0

    action_log = []

    for round_num in range(1, rounds_to_simulate + 1):
        print(f"\n=== Simulation Round {round_num} ===")
        round_finished = False

        while not round_finished:
            for player_index, player in enumerate(environment.game_manager.players):
                for hand_index, hand in enumerate(player.hands):
                    if hand.is_standing:
                        continue

                    if players[player_index][1] == "q-learning":
                        action = players[player_index][0].choose_action(
                            player_index, hand, environment.game_manager.dealer.face_up_card
                        )
                    elif players[player_index][1] == "optimal":
                        action = players[player_index][0].choose_action(
                            hand, environment.game_manager.dealer.face_up_card
                        )
                    elif players[player_index][1] == "random":
                        action = players[player_index][0].choose_action(
                            hand, environment.game_manager.dealer.face_up_card
                        )

                    round_history_output = environment.input(player_index, hand_index, action=action)
                    action_log.append([round_num, player_index, hand_index, action])

                    if round_history_output:
                        print(">>> Round completed")

                        # Q-table updates
                        q_agent_history = [entry for entry in round_history_output if entry[q_agent_pos] == 0]
                        if q_agent_history:
                            print(f"Updating Q-table for Q-agent")
                            players[q_agent_pos][0].process_round_history_for_q_values(q_agent_history)

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
    csv_path = os.path.join(CSV_DIR, "round_outcomes.csv")
    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Round", "Player", "Hand", "Outcome", "Return"])
        writer.writerows(round_outcomes)

    # Save the Q-table at the end of simulation
    save_q_tables_to_csv(players[q_agent_pos][0])

    # Save action log to CSV
    actions_csv = os.path.join(CSV_DIR, "actions.csv")
    with open(actions_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Round", "Player", "Hand", "Action"])
        writer.writerows(action_log)

    print("Simulation complete. Results saved.")
    return players[q_agent_pos][0]


def run_evaluation(q_learning_agent, num_games):
    print(f"\n🔍 Running evaluation over {num_games} games...")
    environment = Environment(deck_count=4, players=3)
    random_agent = RandomAgent()
    optimal_agent = OptimalAgent()

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
                    elif player_index == 1:
                        action = random_agent.choose_action(
                            hand, environment.game_manager.dealer.face_up_card
                        )
                    elif player_index == 2:
                        action = optimal_agent.choose_action(
                            hand, environment.game_manager.dealer.face_up_card
                        )

                    round_history_output = environment.input(player_index, hand_index, action=action)

                    if round_history_output:
                        print(">>> Evaluation Round completed")
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
    csv_path = os.path.join(CSV_DIR, "evaluation_results.csv")
    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Game", "Player", "Hand", "Outcome", "Return"])
        writer.writerows(results)

    print("Evaluation complete. Results saved to 'evaluation_results.csv'")

def plot_evaluation_results():
    csv_path = os.path.join(CSV_DIR, "evaluation_results.csv")
    df_eval = pd.read_csv(csv_path)

    rounds = pd.Series(range(1, df_eval["Game"].max() + 1), name="Game")

    # Plot 1: Cumulative Wins over games (Evaluation)
    plt.figure(figsize=(12, 6))
    for player_id, label in zip([0, 1, 2], ["Q-Learning", "Random", "Optimal"]):
        df_wins = df_eval[(df_eval["Player"] == player_id) & (df_eval["Outcome"] == "WIN")]
        wins_cumulative = df_wins.groupby("Game").size().cumsum()
        wins_full = wins_cumulative.reindex(rounds).ffill().fillna(0).astype(int)
        plt.plot(rounds, wins_full, label=f"{label} Wins")

    plt.xlabel("Rounds")
    plt.ylabel("Cumulative Wins")
    plt.title("Evaluation: Cumulative Wins Over Rounds")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plots_path = os.path.join(PLOTS_DIR, "evaluation_cumulative_wins.png")
    plt.savefig(plots_path)
    plt.show()

    # Plot 3: Cumulative Returns (Evaluation)
    plt.figure(figsize=(12, 6))
    for player_id, label in zip([0, 1, 2], ["Q-Learning", "Random", "Optimal"]):
        df_player = df_eval[df_eval["Player"] == player_id]
        returns = df_player.groupby("Game")["Return"].sum().cumsum()
        returns_full = returns.reindex(rounds).ffill().fillna(0).astype(int)
        plt.plot(rounds, returns_full, label=f"{label} Return", linestyle="--")

    plt.xlabel("Rounds")
    plt.ylabel("Cumulative Return")
    plt.title("Evaluation: Cumulative Return Over Rounds")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plots_path = os.path.join(PLOTS_DIR, "evaluation_cumulative_returns.png")
    plt.savefig(plots_path)
    plt.show()


def plot_training_results():
    csv_path = os.path.join(CSV_DIR, "round_outcomes.csv")
    df = pd.read_csv(csv_path)
    rounds = pd.Series(range(1, df["Round"].max() + 1), name="Round")

    # Plot 1: Cumulative Wins (Training)
    plt.figure(figsize=(12, 6))
    for player_id, label in zip([0, 1, 2], ["Q-Learning", "Random", "Optimal"]):
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
    plots_path = os.path.join(PLOTS_DIR, "training_cumulative_wins.png")
    plt.savefig(plots_path)
    plt.show()

    # Plot 2: Cumulative Returns (Training)
    plt.figure(figsize=(12, 6))
    for player_id, label in zip([0, 1, 2], ["Q-Learning", "Random", "Optimal"]):
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
    plots_path = os.path.join(PLOTS_DIR, "training_cumulative_returns.png")
    plt.savefig(plots_path)
    plt.show()

def plot_return_distributions():
    # Define bin edges and labels
    bin_edges = [-float("inf"), -40, -20, -10, -5, 0, 5, 10, 20, 40, float("inf")]
    bin_labels = ["< -40", "-40", "-20", "-10", "-5", "0", "5", "10", "20", "40+"]

    def prepare_distribution(df, label):
        df["Bin"] = pd.cut(df["Return"], bins=bin_edges, labels=bin_labels, right=False)
        df["Source"] = label
        return df

    # Load and label the data
    csv_path = os.path.join(CSV_DIR, "round_outcomes.csv")
    df_train = pd.read_csv(csv_path)
    df_train = prepare_distribution(df_train, "Training")

    csv_path = os.path.join(CSV_DIR, "evaluation_results.csv")
    df_eval = pd.read_csv(csv_path)
    df_eval = prepare_distribution(df_eval, "Evaluation")

    # Combine both
    df_all = pd.concat([df_train, df_eval], ignore_index=True)

    player_labels = ["Q-Learning", "Random", "Optimal"]

    for player_id in [0, 1, 2]:
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
        plots_path = os.path.join(PLOTS_DIR, filename)
        plt.savefig(plots_path)
        plt.show()


def plot_q_value_convergence(q_learning_agent):
    convergence_data = q_learning_agent.q_value_changes
    plt.figure(figsize=(12, 6))
    plt.plot(convergence_data, label='Avg Q-Value Change')
    plt.xlabel('Q-Update Iteration')
    plt.ylabel('Average ΔQ')
    plt.title('Q-Value Convergence Over Time')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    path = os.path.join(PLOTS_DIR, 'q_value_convergence.png')
    plt.savefig(path)
    plt.show()

def plot_action_distribution():
    csv_path = os.path.join(CSV_DIR, "actions.csv")
    df = pd.read_csv(csv_path)

    action_labels = {0: "Stand", 1: "Hit", 2: "Double", 3: "Split", 4: "Insurance"}
    df["ActionLabel"] = df["Action"].map(action_labels)

    plt.figure(figsize=(12, 6))
    for player_id, label in zip([0, 1, 2], ["Q-Learning", "Random", "Optimal"]):
        df_player = df[df["Player"] == player_id]
        action_counts = df_player["ActionLabel"].value_counts(normalize=True).sort_index()
        plt.bar([f"{label} - {a}" for a in action_counts.index], action_counts.values, label=label)

    plt.ylabel("Proportion of Actions")
    plt.title("Action Distribution per Agent")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    plots_path = os.path.join(PLOTS_DIR, "action_distribution.png")
    plt.savefig(plots_path)
    plt.show()


def plot_state_value_heatmap(q_learning_agent):
    # Assuming state = ((player_value,), dealer_card), we reduce to 2D
    q_values = defaultdict(list)
    
    for (state, action), q in q_learning_agent.q_tables[0].items():
        player_hand = state[0][0] if state[0] else 0
        dealer_card = state[1]
        q_values[(player_hand, dealer_card)].append(q)

    avg_q_values = {(k[0], k[1]): sum(v)/len(v) for k, v in q_values.items()}

    data = pd.DataFrame([{'Player': k[0], 'Dealer': k[1], 'Q': v} for k, v in avg_q_values.items()])
    heatmap_data = data.pivot(index='Player', columns='Dealer', values='Q')

    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
    plt.title("State-Value Heatmap (Avg Q-Value)")
    plt.xlabel("Dealer Showing")
    plt.ylabel("Player Hand Value")
    plt.tight_layout()
    path = os.path.join(PLOTS_DIR, 'state_value_heatmap.png')
    plt.savefig(path)
    plt.show()

if __name__ == "__main__":
    # Training
    q_learning_agent = Q_Learning()  # Index = 0
    random_agent = RandomAgent()  # Index = 1
    optimal_agent = OptimalAgent()  # Index = 2

    agents = [q_learning_agent, random_agent, optimal_agent]

    q_learning_agent = run_simulation_q_learning(num_players=3, q_agent_pos=0, rounds_to_simulate=1000)
    plot_training_results()

    # Evaluation
    # run_evaluation(q_learning_agent, num_games=10000)
    run_evaluation(q_learning_agent, num_games=10000)
    plot_evaluation_results()

    # Win/Loss Distribution of Stakes
    plot_return_distributions()
    
    plot_q_value_convergence(q_learning_agent)
    plot_action_distribution()
    plot_state_value_heatmap(q_learning_agent)

    print("The end")
