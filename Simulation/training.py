import os, csv
from collections import defaultdict

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from Game.environment import Environment

from Agents.q_agent import QAgent
from Agents.mbve_q_agent import MbveQAgent
from Agents.optimal_agent import OptimalAgent
from Agents.random_agent import RandomAgent

from definitions import CSV_DIR, TRAINING_DIR


def save_q_tables_to_csv(q_agent: QAgent, train_id):
    for player_index, q_table in q_agent.q_tables.items():
        filename = f"q_table_id{train_id}_{q_agent.agent_name}.csv"
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


# Trains one q-agent (with or without mbve)
# Number of players and q-agent position is given. Max 5 players. One optimal agent. Rest is random.
# Returns the whole player setup: [agent_class, ...]
def run_simulation_q_learning(num_players=3, q_agent_pos=0, with_mbve=False, train_id=0, rounds_to_simulate=1000000):
    environment = Environment(deck_count=4, players=num_players)

    players = []
    important_indices = []
    optimal_added = False
    first_random_added = False

    for i in range(num_players):
        if q_agent_pos == i:
            important_indices.append(i)
            players.append(MbveQAgent() if with_mbve else QAgent())
            players[q_agent_pos].training_index = q_agent_pos
            continue
        if not optimal_added:
            optimal_added = True
            important_indices.append(i)
            players.append(OptimalAgent())
            continue
        if not first_random_added:
            first_random_added = True
            important_indices.append(i)
        players.append(RandomAgent())

    round_outcomes = []
    return_tracking = {i: [] for i in range(num_players)}
    cumulative_return = {i: 0 for i in range(num_players)}
    win_tracking = {i: [] for i in range(num_players)}
    cumulative_wins = {i: 0 for i in range(num_players)}
    action_log = []

    for round_num in range(1, rounds_to_simulate + 1):
        print(f"\n=== Simulation Round {round_num} ===")
        round_finished = False
        round_action_log = []

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
                            raise Exception(f"Algorithm not yet implemented for {current_agent_label}")

                        if player_index in important_indices:
                            round_action_log.append([round_num, player_index, hand_index, action])

                        round_history_output = environment.input(player_index, hand_index, action=action)

                        if round_history_output:
                            print(">>> Round completed")

                            q_agent_history = [entry for entry in round_history_output if entry[q_agent_pos] == 0]
                            if q_agent_history:
                                print(f"Updating Q-table for Q-agent")
                                players[q_agent_pos].process_round_history_for_q_values(q_agent_history)

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

                                if p_idx in important_indices:
                                    round_outcomes.append([round_num, p_idx, h_idx, outcome, result])

                            round_finished = True
                            break
                    if round_finished:
                        break

        action_log.extend(round_action_log)

    # Save round outcomes
    csv_path = os.path.join(CSV_DIR, f"round_outcomes_id{train_id}_{players[q_agent_pos].agent_name}.csv")
    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Round", "Player", "Hand", "Outcome", "Return"])
        writer.writerows(round_outcomes)

    # Save Q-table
    save_q_tables_to_csv(players[q_agent_pos], train_id)

    # Save action log
    actions_csv = os.path.join(CSV_DIR, f"actions_id{train_id}_{players[q_agent_pos].agent_name}.csv")
    with open(actions_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Round", "Player", "Hand", "Action"])
        writer.writerows(action_log)

    print("Simulation complete. Results saved.")

    return players



# Players is the whole player setup: [agent_class, ...]
def plot_training_results(players, train_id=0, window_size=100):
    q_agent = next((x for x in players if isinstance(x, QAgent)), None)
    
    csv_path = os.path.join(CSV_DIR, f"round_outcomes_id{train_id}_{q_agent.agent_name}.csv")
    df = pd.read_csv(csv_path)
    max_round = df["Round"].max()
    rounds = pd.Series(range(1, max_round + 1), name="Round")

    # Retrieve important indices
    first_random_retrieved = False
    important_indices = []

    for i, player in enumerate(players):
        if isinstance(player, QAgent) or isinstance(player, OptimalAgent):
            important_indices.append(i)
        elif isinstance(player, RandomAgent) and not first_random_retrieved:
            first_random_retrieved = True
            important_indices.append(i)

    # Plot 1: Cumulative Wins
    plt.figure(figsize=(12, 6))
    for player_id in important_indices:
        player = players[player_id]
        df_wins = df[(df["Player"] == player_id) & (df["Outcome"] == "WIN")]
        wins_cumulative = df_wins.groupby("Round").size().cumsum()
        wins_full = wins_cumulative.reindex(rounds).ffill().fillna(0).astype(int)
        plt.plot(rounds, wins_full, label=f"{player.agent_label.upper()} Wins")

    plt.xlabel("Round")
    plt.ylabel("Cumulative Wins")
    plt.title(f"Training - {q_agent.agent_name.upper()}: Cumulative Wins Over Rounds")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(TRAINING_DIR, f"training_cumulative_wins_id{train_id}_{q_agent.agent_name}.png"))
    plt.show()

    # Plot 2: Rolling Win Rate
    plt.figure(figsize=(12, 6))
    for player_id in important_indices:
        player = players[player_id]
        df_player = df[df["Player"] == player_id].copy()
        df_player["IsWin"] = (df_player["Outcome"] == "WIN").astype(int)
        win_series = df_player.groupby("Round")["IsWin"].sum().reindex(rounds, fill_value=0)
        rolling_win_rate = win_series.rolling(window=window_size, min_periods=1).mean()
        plt.plot(rounds, rolling_win_rate, label=f"{player.agent_label.upper()} Win Rate")

    plt.xlabel("Round")
    plt.ylabel(f"Win Rate (rolling window={window_size})")
    plt.title(f"Training - {q_agent.agent_name.upper()}: Rolling Win Rate Over {window_size} Rounds")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(TRAINING_DIR, f"training_win_rate_id{train_id}_{q_agent.agent_name}.png"))
    plt.show()

    # Plot 3: Cumulative Returns
    plt.figure(figsize=(12, 6))
    for player_id in important_indices:
        player = players[player_id]
        df_player = df[df["Player"] == player_id]
        returns = df_player.groupby("Round")["Return"].sum().cumsum()
        returns_full = returns.reindex(rounds).ffill().fillna(0).astype(int)
        plt.plot(rounds, returns_full, label=f"{player.agent_label.upper()} Return", linestyle="--")

    plt.xlabel("Round")
    plt.ylabel("Cumulative Return")
    plt.title(f"Training - {q_agent.agent_name.upper()}: Cumulative Return Over Rounds")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(TRAINING_DIR, f"training_cumulative_returns_id{train_id}_{q_agent.agent_name}.png"))
    plt.show()

    # Plot 4: Rolling Returns
    plt.figure(figsize=(12, 6))
    for player_id in important_indices:
        player = players[player_id]
        df_player = df[df["Player"] == player_id]
        return_series = df_player.groupby("Round")["Return"].sum().reindex(rounds, fill_value=0)
        rolling_returns = return_series.rolling(window=window_size, min_periods=1).mean()
        plt.plot(rounds, rolling_returns, label=f"{player.agent_label.upper()} Rolling Return")

    plt.xlabel("Round")
    plt.ylabel(f"Avg Return (rolling window={window_size})")
    plt.title(f"Training - {q_agent.agent_name.upper()}: Rolling Average Return Over {window_size} Rounds")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(TRAINING_DIR, f"training_rolling_returns_id{train_id}_{q_agent.agent_name}.png"))
    plt.show()


def plot_q_value_convergence(q_agent: QAgent, train_id=0, window_size=50):
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
    plt.title(f"Q-Value Convergence with Rolling Average - {q_agent.agent_name.upper()}")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Fixed path
    path = os.path.join(TRAINING_DIR, f"q_value_convergence_id{train_id}_{q_agent.agent_name}.png")
    plt.savefig(path)
    plt.show()

def plot_state_value_max_and_avg_heatmaps(q_agent: QAgent, train_id=0):
    q_values = defaultdict(list)

    for (state, action), q in q_agent.q_tables[0].items():
        player_hand = state[0][0] if state[0] else 0
        dealer_card = state[1]
        q_values[(player_hand, dealer_card)].append(q)

    # Compute both max and average Q-values
    max_q_values = {(k[0], k[1]): max(v) for k, v in q_values.items()}
    avg_q_values = {(k[0], k[1]): sum(v) / len(v) for k, v in q_values.items()}

    # Create dataframes
    max_data = pd.DataFrame([{'Player': k[0], 'Dealer': k[1], 'Q': v} for k, v in max_q_values.items()])
    avg_data = pd.DataFrame([{'Player': k[0], 'Dealer': k[1], 'Q': v} for k, v in avg_q_values.items()])

    max_heatmap_data = max_data.pivot(index='Player', columns='Dealer', values='Q')
    avg_heatmap_data = avg_data.pivot(index='Player', columns='Dealer', values='Q')

    # Plot both heatmaps side by side
    fig, axes = plt.subplots(1, 2, figsize=(18, 8), sharey=True)

    sns.heatmap(max_heatmap_data, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5, ax=axes[0])
    axes[0].set_title(f"Max Q-Value Heatmap - {q_agent.agent_name.upper()}")
    axes[0].set_xlabel("Dealer Showing")
    axes[0].set_ylabel("Player Hand Value")

    sns.heatmap(avg_heatmap_data, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5, ax=axes[1])
    axes[1].set_title(f"Avg Q-Value Heatmap - {q_agent.agent_name.upper()}")
    axes[1].set_xlabel("Dealer Showing")
    axes[1].set_ylabel("")

    plt.tight_layout()
    # Fixed path
    path = os.path.join(TRAINING_DIR, f"state_value_heatmap_id{train_id}_{q_agent.agent_name}.png")
    plt.savefig(path)
    plt.show()

def plot_state_value_heatmaps(q_agent: QAgent, train_id=0):
    q_values = defaultdict(list)

    for (state, action), q in q_agent.q_tables[0].items():
        player_hand = state[0][0] if state[0] else 0
        dealer_card = state[1]
        q_values[(player_hand, dealer_card)].append(q)

    # Compute both max and average Q-values
    max_q_values = {(k[0], k[1]): max(v) for k, v in q_values.items()}
    avg_q_values = {(k[0], k[1]): sum(v) / len(v) for k, v in q_values.items()}

    # Create dataframes
    max_data = pd.DataFrame([{'Player': k[0], 'Dealer': k[1], 'Q': v} for k, v in max_q_values.items()])
    avg_data = pd.DataFrame([{'Player': k[0], 'Dealer': k[1], 'Q': v} for k, v in avg_q_values.items()])

    max_heatmap_data = max_data.pivot(index='Player', columns='Dealer', values='Q')
    avg_heatmap_data = avg_data.pivot(index='Player', columns='Dealer', values='Q')

    # Plot Max Q-Value heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(max_heatmap_data, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
    plt.title(f"State-Value Heatmap (Max Q-Value) - {q_agent.agent_name.upper()}")
    plt.xlabel("Dealer Showing")
    plt.ylabel("Player Hand Value")
    plt.tight_layout()
    # Fixed path
    path = os.path.join(TRAINING_DIR, f"state_value_heatmap_max_id{train_id}_{q_agent.agent_name}.png")
    plt.savefig(path)
    plt.show()

    # Plot Avg Q-Value heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(avg_heatmap_data, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
    plt.title(f"State-Value Heatmap (Avg Q-Value) - {q_agent.agent_name.upper()}")
    plt.xlabel("Dealer Showing")
    plt.ylabel("Player Hand Value")
    plt.tight_layout()

    path = os.path.join(TRAINING_DIR, f"state_value_heatmap_id{train_id}_{q_agent.agent_name}.png")
    plt.savefig(path)
    plt.show()


# Players is the whole player setup: [agent_class, ...]
def plot_action_distribution(players, train_id=0):
    q_agent = next((x for x in players if isinstance(x, QAgent)), None)

    csv_path = os.path.join(CSV_DIR, f"actions_id{train_id}_{q_agent.agent_name}.csv")
    df = pd.read_csv(csv_path)

    action_labels = {0: "Stand", 1: "Hit", 2: "Double", 3: "Split", 4: "Insurance"}
    df["ActionLabel"] = df["Action"].map(action_labels)

    plt.figure(figsize=(12, 6))
    for player_id, player in enumerate(players):
        df_player = df[df["Player"] == player_id]
        action_counts = df_player["ActionLabel"].value_counts(normalize=True).sort_index()
        plt.bar([f"{player.agent_name.upper()} - {a}" for a in action_counts.index], action_counts.values, label=player.agent_name)

    plt.ylabel("Proportion of Actions")
    plt.title(f"Action Distribution per Agent - {q_agent.agent_name.upper()}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    plots_path = os.path.join(TRAINING_DIR, f"action_distribution_id{train_id}_{q_agent.agent_name}.png")
    plt.savefig(plots_path)
    plt.show()
