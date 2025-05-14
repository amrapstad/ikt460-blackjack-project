import os, csv

import pandas as pd
import matplotlib.pyplot as plt

from Agents.q_agent import QAgent
from Game.environment import Environment

from definitions import CSV_DIR, EVALUATION_DIR


# Players is the whole player setup: [(agent_class, "agent name", ...)]
def run_evaluation(players, eval_id=0, num_games=10000):
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
    csv_path = os.path.join(CSV_DIR, f"evaluation_results_id{eval_id}.csv")
    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Game", "Player", "Hand", "Outcome", "Return"])
        writer.writerows(results)

    print("Evaluation complete. Results saved to 'evaluation_results.csv'")


# Players is the whole player setup: [agent_class, ...]
def plot_evaluation_results(players, eval_id=0, window_size=50):
    csv_path = os.path.join(CSV_DIR, f"evaluation_results_id{eval_id}.csv")
    df_eval = pd.read_csv(csv_path)
    max_game = df_eval["Game"].max()
    games = pd.Series(range(1, max_game + 1), name="Game")

    # Plot 1: Cumulative Wins
    plt.figure(figsize=(12, 6))
    for player_id, player in enumerate(players):
        df_wins = df_eval[(df_eval["Player"] == player_id) & (df_eval["Outcome"] == "WIN")]
        wins_cumulative = df_wins.groupby("Game").size().cumsum()
        wins_full = wins_cumulative.reindex(games).ffill().fillna(0).astype(int)
        plt.plot(games, wins_full, label=f"{player.agent_name.upper()} Wins")

    plt.xlabel("Game")
    plt.ylabel("Cumulative Wins")
    plt.title("Evaluation: Cumulative Wins Over Games")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EVALUATION_DIR, f"evaluation_cumulative_wins_id{eval_id}.png"))
    plt.show()

    # Plot 2: Rolling Win Rate
    plt.figure(figsize=(12, 6))
    for player_id, player in enumerate(players):
        df_player = df_eval[df_eval["Player"] == player_id].copy()
        df_player["IsWin"] = (df_player["Outcome"] == "WIN").astype(int)
        win_series = df_player.groupby("Game")["IsWin"].sum().reindex(games, fill_value=0)
        rolling_win_rate = win_series.rolling(window=window_size, min_periods=1).mean()
        plt.plot(games, rolling_win_rate, label=f"{player.agent_name.upper()} Win Rate")

    plt.xlabel("Game")
    plt.ylabel(f"Win Rate (rolling window={window_size})")
    plt.title(f"Evaluation: Rolling Win Rate Over {window_size} Games")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EVALUATION_DIR, f"evaluation_win_rate_id{eval_id}.png"))
    plt.show()

    # Plot 3: Cumulative Returns
    plt.figure(figsize=(12, 6))
    for player_id, player in enumerate(players):
        df_player = df_eval[df_eval["Player"] == player_id]
        returns = df_player.groupby("Game")["Return"].sum().cumsum()
        returns_full = returns.reindex(games).ffill().fillna(0).astype(int)
        plt.plot(games, returns_full, label=f"{player.agent_name.upper()} Return", linestyle="--")

    plt.xlabel("Game")
    plt.ylabel("Cumulative Return")
    plt.title("Evaluation: Cumulative Return Over Games")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EVALUATION_DIR, f"evaluation_cumulative_returns_id{eval_id}.png"))
    plt.show()

    # Plot 4: Rolling Returns
    plt.figure(figsize=(12, 6))
    for player_id, player in enumerate(players):
        df_player = df_eval[df_eval["Player"] == player_id]
        return_series = df_player.groupby("Game")["Return"].sum().reindex(games, fill_value=0)
        rolling_returns = return_series.rolling(window=window_size, min_periods=1).mean()
        plt.plot(games, rolling_returns, label=f"{player.agent_name.upper()} Rolling Return")

    plt.xlabel("Game")
    plt.ylabel(f"Avg Return (rolling window={window_size})")
    plt.title(f"Evaluation: Rolling Average Return Over {window_size} Games")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(EVALUATION_DIR, f"evaluation_rolling_returns_id{eval_id}.png"))
    plt.show()


# Players is the whole player setup: [agent_class, ...]
def plot_return_distributions(players, eval_id=0, train_id=0):
    # First cut random and optimal agents from players
    players = [player for player in players if isinstance(player, QAgent)]

    # Bin setup
    bin_edges = [-float("inf"), -40, -20, -10, -5, 0, 5, 10, 20, 40, float("inf")]
    bin_labels = ["< -40", "-40", "-20", "-10", "-5", "0", "5", "10", "20", "40+"]

    def prepare_distribution(df, player_index, _agent_name, label):
        df_agent = df[df["Player"] == player_index].copy()
        df_agent["AgentName"] = _agent_name
        df_agent["Bin"] = pd.cut(df_agent["Return"], bins=bin_edges, labels=bin_labels, right=False)
        df_agent["Source"] = label
        return df_agent

    # Load evaluation data once
    eval_path = os.path.join(CSV_DIR, f"evaluation_results_id{eval_id}.csv")
    df_eval_full = pd.read_csv(eval_path)

    for eval_index, player in enumerate(players):
        agent_name = player.agent_name
        training_index = player.training_index
        safe_name = agent_name.lower().replace(" ", "_")

        # Load that agent's training data
        train_csv = os.path.join(CSV_DIR, f"round_outcomes_id{train_id}_{safe_name}.csv")
        if not os.path.exists(train_csv):
            print(f"Training CSV not found for agent '{agent_name}' at: {train_csv}")
            continue
        df_train_full = pd.read_csv(train_csv)

        # Prepare training and evaluation slices
        df_train = prepare_distribution(df_train_full, training_index, agent_name, "Training")
        df_eval = prepare_distribution(df_eval_full, eval_index, agent_name, "Evaluation")

        # Combine both
        df_combined = pd.concat([df_train, df_eval], ignore_index=True)

        # Group and normalize to percentages
        grouped = df_combined.groupby(["Bin", "Source"], observed=False).size().unstack(fill_value=0).reindex(bin_labels)
        grouped_percent = grouped.divide(grouped.sum(axis=0), axis=1) * 100  # Convert to percentages

        ax = grouped_percent.plot(kind="bar", figsize=(12, 6), width=0.7)
        plt.title(f"{agent_name.upper()} Agent - Return Distribution (% - Training vs Evaluation)")
        plt.xlabel("Return Range")
        plt.ylabel("Percentage (%)")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()

        # Annotate bars with percentages
        for container in ax.containers:
            for bar in container:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(f"{height:.1f}%",
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=9)

        # Save and show
        filename = f"return_distribution_id{eval_id}_{safe_name}.png"
        plots_path = os.path.join(EVALUATION_DIR, filename)
        plt.savefig(plots_path)
        plt.show()
