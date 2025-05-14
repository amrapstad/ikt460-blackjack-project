import os, csv

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict

from Agents.q_agent import QAgent
from Game.environment import Environment

from definitions import CSV_DIR, PLOTS_DIR, EVALUATION_DIR, DISTRIBUTIONS_DIR, Q_VALUE_DIR


# Players is the whole player setup: [(agent_class, "agent name", ...)]
def run_evaluation(players, num_games=10000):
    print(f"\n🔍 Running evaluation over {num_games} games...")

    player_count = len(players)
    environment = Environment(deck_count=4, players=player_count)

    results = []

    for game_num in range(1, num_games + 1):
        print(f"\n--- Evaluation Game {game_num} ---")
        round_finished = False

        while not round_finished:
            for player_index, player in enumerate(environment.game_manager.players):
                all_hands_done = False
                while not all_hands_done:
                    all_hands_done = True
                    for hand_index, hand in enumerate(player.hands):
                        if hand.is_standing:
                            continue
                        all_hands_done = False

                        current_agent_label = players[player_index].agent_label

                        if current_agent_label in ("q-learning", "mbve-q-learning"):
                            action = players[player_index].choose_action(
                                player_index, hand, environment.game_manager.dealer.face_up_card
                            )
                        elif current_agent_label in ("optimal", "random"):
                            action = players[player_index].choose_action(
                                hand, environment.game_manager.dealer.face_up_card
                            )
                        else:
                            raise Exception(f"Algorithm not yet implemented for {players[player_index].agent_label}")

                        round_history_output = environment.input(player_index, hand_index, action=action)

                        if round_history_output:
                            print(">>> Evaluation Round completed")
                            for p_idx, h_idx, hand_history, outcome, _ in round_history_output:
                                if not hand_history:
                                    continue
                                stake = hand_history[-1][1]
                                result = stake if outcome == "WIN" else -stake if outcome == "LOSE" else 0
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



# Players is the whole player setup: [agent_class, ...]
def plot_evaluation_results(players, window_size=50):
    csv_path = os.path.join(CSV_DIR, "evaluation_results.csv")
    df_eval = pd.read_csv(csv_path)
    max_game = df_eval["Game"].max()
    games = pd.Series(range(1, max_game + 1), name="Game")

    # Plot 1: Cumulative Wins
    plt.figure(figsize=(12, 6))
    for player_id, player in enumerate(players):
        df_wins = df_eval[(df_eval["Player"] == player_id) & (df_eval["Outcome"] == "WIN")]
        wins_cumulative = df_wins.groupby("Game").size().cumsum()
        wins_full = wins_cumulative.reindex(games).ffill().fillna(0).astype(int)
        plt.plot(games, wins_full, label=f"{player.agent_label.upper()} Wins")

    plt.xlabel("Game")
    plt.ylabel("Cumulative Wins")
    plt.title("Evaluation: Cumulative Wins Over Games")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EVALUATION_DIR, "evaluation_cumulative_wins.png"))
    plt.show()

    # Plot 2: Rolling Win Rate
    plt.figure(figsize=(12, 6))
    for player_id, player in enumerate(players):
        df_player = df_eval[df_eval["Player"] == player_id].copy()
        df_player["IsWin"] = (df_player["Outcome"] == "WIN").astype(int)
        win_series = df_player.groupby("Game")["IsWin"].sum().reindex(games, fill_value=0)
        rolling_win_rate = win_series.rolling(window=window_size, min_periods=1).mean()
        plt.plot(games, rolling_win_rate, label=f"{player.agent_label.upper()} Win Rate")

    plt.xlabel("Game")
    plt.ylabel(f"Win Rate (rolling window={window_size})")
    plt.title(f"Evaluation: Rolling Win Rate Over {window_size} Games")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EVALUATION_DIR, f"evaluation_win_rate_{window_size}.png"))
    plt.show()

    # Plot 3: Cumulative Returns
    plt.figure(figsize=(12, 6))
    for player_id, player in enumerate(players):
        df_player = df_eval[df_eval["Player"] == player_id]
        returns = df_player.groupby("Game")["Return"].sum().cumsum()
        returns_full = returns.reindex(games).ffill().fillna(0).astype(int)
        plt.plot(games, returns_full, label=f"{player.agent_label.upper()} Return", linestyle="--")

    plt.xlabel("Game")
    plt.ylabel("Cumulative Return")
    plt.title("Evaluation: Cumulative Return Over Games")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EVALUATION_DIR, "evaluation_cumulative_returns.png"))
    plt.show()

    # Plot 4: Rolling Returns
    plt.figure(figsize=(12, 6))
    for player_id, player in enumerate(players):
        df_player = df_eval[df_eval["Player"] == player_id]
        return_series = df_player.groupby("Game")["Return"].sum().reindex(games, fill_value=0)
        rolling_returns = return_series.rolling(window=window_size, min_periods=1).mean()
        plt.plot(games, rolling_returns, label=f"{player.agent_label.upper()} Rolling Return")

    plt.xlabel("Game")
    plt.ylabel(f"Avg Return (rolling window={window_size})")
    plt.title(f"Evaluation: Rolling Average Return Over {window_size} Games")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EVALUATION_DIR, f"evaluation_rolling_returns_{window_size}.png"))
    plt.show()


# Players is the whole player setup: [agent_class, ...]
def plot_return_distributions(players):
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

    for player_id, player in enumerate(players):
        df_player = df_all[df_all["Player"] == player_id]

        # Group by Bin and Source (training/eval)
        grouped = df_player.groupby(["Bin", "Source"], observed=False).size().unstack(fill_value=0).reindex(bin_labels)

        # Plot
        ax = grouped.plot(kind="bar", figsize=(12, 6), width=0.7)
        plt.title(f"{player.agent_label.upper()} agent - Distributions (Training vs Evaluation)")
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
        filename = f"return_distribution_{player.agent_label.lower().replace(' ', '_')}.png"
        plots_path = os.path.join(DISTRIBUTIONS_DIR, filename)
        plt.savefig(plots_path)
        plt.show()


# Players is the whole player setup: [agent_class, ...]
def plot_action_distribution(players):
    csv_path = os.path.join(CSV_DIR, "actions.csv")
    df = pd.read_csv(csv_path)

    action_labels = {0: "Stand", 1: "Hit", 2: "Double", 3: "Split", 4: "Insurance"}
    df["ActionLabel"] = df["Action"].map(action_labels)

    plt.figure(figsize=(12, 6))
    for player_id, player in enumerate(players):
        df_player = df[df["Player"] == player_id]
        action_counts = df_player["ActionLabel"].value_counts(normalize=True).sort_index()
        plt.bar([f"{player.agent_label.upper()} - {a}" for a in action_counts.index], action_counts.values, label=player.agent_label)

    plt.ylabel("Proportion of Actions")
    plt.title("Action Distribution per Agents")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    plots_path = os.path.join(DISTRIBUTIONS_DIR, "action_distribution.png")
    plt.savefig(plots_path)
    plt.show()


def plot_q_value_convergence(q_agent: QAgent, window_size=50):
    deltas = q_agent.q_value_changes_per_round
    rounds = list(range(1, len(deltas) + 1))

    if not deltas:
        print("No Q-value change data available.")
        return

    delta_series = pd.Series(deltas)
    rolling_avg = delta_series.rolling(window=window_size, min_periods=1).mean()

    plt.figure(figsize=(12, 6))
    plt.plot(rounds, deltas, label='Raw Avg ΔQ per Round', alpha=0.5)
    plt.plot(rounds, rolling_avg, label=f'Rolling Avg ΔQ (window={window_size})', linewidth=2)
    plt.xlabel("Round")
    plt.ylabel("Average Q-Value Change")
    plt.title("Q-Value Convergence with Rolling Average")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    
    # Fixed path
    path = os.path.join(Q_VALUE_DIR, f"q_value_convergence_{q_agent.agent_label}.png")
    plt.savefig(path)
    plt.show()




def plot_state_value_heatmap(q_agent: QAgent):
    # Assuming state = ((player_value,), dealer_card), we reduce to 2D
    q_values = defaultdict(list)

    for (state, action), q in q_agent.q_tables[0].items():
        player_hand = state[0][0] if state[0] else 0
        dealer_card = state[1]
        q_values[(player_hand, dealer_card)].append(q)

    avg_q_values = {(k[0], k[1]): sum(v) / len(v) for k, v in q_values.items()}

    data = pd.DataFrame([{'Player': k[0], 'Dealer': k[1], 'Q': v} for k, v in avg_q_values.items()])
    heatmap_data = data.pivot(index='Player', columns='Dealer', values='Q')

    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
    plt.title("State-Value Heatmap (Avg Q-Value)")
    plt.xlabel("Dealer Showing")
    plt.ylabel("Player Hand Value")
    plt.tight_layout()
    path = os.path.join(Q_VALUE_DIR, f"state_value_heatmap_{q_agent.agent_label}.png")
    plt.savefig(path)
    plt.show()
