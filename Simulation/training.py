import os, csv

from Game.environment import Environment

from Agents.q_agent import QAgent
from Agents.optimal_agent import OptimalAgent
from Agents.random_agent import RandomAgent

from definitions import CSV_DIR, PLOTS_DIR


def save_q_tables_to_csv(q_learning_agent: QAgent):
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


# Trains one q-agent. Number of players and q-agent position is given. Max 5 players. One optimal agent. Rest is random.
# Returns the whole player setup: [(agent_class, "agent name"), ...]
def run_simulation_q_learning(num_players=3, q_agent_pos=0, rounds_to_simulate=1000000):
    environment = Environment(deck_count=4, players=num_players)

    players = []
    optimal_added = False

    for i in range(num_players):
        if q_agent_pos == i:
            players.append((QAgent(), "q-learning"))
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

    return players

def plot_training_results(players, window_size=50):
    import os
    import pandas as pd
    import matplotlib.pyplot as plt

    csv_path = os.path.join(CSV_DIR, "round_outcomes.csv")
    df = pd.read_csv(csv_path)
    max_round = df["Round"].max()
    rounds = pd.Series(range(1, max_round + 1), name="Round")

    # Plot 1: Rolling Win Rate
    plt.figure(figsize=(12, 6))
    for player_id, player in enumerate(players):
        df_player = df[df["Player"] == player_id].copy()
        df_player["IsWin"] = (df_player["Outcome"] == "WIN").astype(int)
        win_series = df_player.groupby("Round")["IsWin"].sum().reindex(rounds, fill_value=0)
        rolling_win_rate = win_series.rolling(window=window_size, min_periods=1).mean()
        plt.plot(rounds, rolling_win_rate, label=f"{player[1]} Win Rate")

    plt.xlabel("Round")
    plt.ylabel(f"Win Rate (rolling window={window_size})")
    plt.title(f"Training: Rolling Win Rate Over {window_size} Rounds")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, f"training_win_rate_{window_size}.png"))
    plt.show()

    # Plot 2: Cumulative Wins
    plt.figure(figsize=(12, 6))
    for player_id, player in enumerate(players):
        df_wins = df[(df["Player"] == player_id) & (df["Outcome"] == "WIN")]
        wins_cumulative = df_wins.groupby("Round").size().cumsum()
        wins_full = wins_cumulative.reindex(rounds).ffill().fillna(0).astype(int)
        plt.plot(rounds, wins_full, label=f"{player[1]} Wins")

    plt.xlabel("Round")
    plt.ylabel("Cumulative Wins")
    plt.title("Training: Cumulative Wins Over Rounds")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "training_cumulative_wins.png"))
    plt.show()

    # Plot 3: Cumulative Returns
    plt.figure(figsize=(12, 6))
    for player_id, player in enumerate(players):
        df_player = df[df["Player"] == player_id]
        returns = df_player.groupby("Round")["Return"].sum().cumsum()
        returns_full = returns.reindex(rounds).ffill().fillna(0).astype(int)
        plt.plot(rounds, returns_full, label=f"{player[1]} Return", linestyle="--")

    plt.xlabel("Round")
    plt.ylabel("Cumulative Return")
    plt.title("Training: Cumulative Return Over Rounds")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "training_cumulative_returns.png"))
    plt.show()

    # Plot 4: Rolling Returns
    plt.figure(figsize=(12, 6))
    for player_id, player in enumerate(players):
        df_player = df[df["Player"] == player_id]
        return_series = df_player.groupby("Round")["Return"].sum().reindex(rounds, fill_value=0)
        rolling_returns = return_series.rolling(window=window_size, min_periods=1).mean()
        plt.plot(rounds, rolling_returns, label=f"{player[1]} Rolling Return")

    plt.xlabel("Round")
    plt.ylabel(f"Avg Return (rolling window={window_size})")
    plt.title(f"Training: Rolling Average Return Over {window_size} Rounds")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, f"training_rolling_returns_{window_size}.png"))
    plt.show()
