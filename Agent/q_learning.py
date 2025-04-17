class Q_Learning:
    def __init__(self):
        self.q_tables = {}

    def process_round_history_for_q_values(self, round_history_output, learning_rate=0.1, discount_factor=0.9):
        for player_index, hand_index, hand_history, outcome, dealer_face_up_card in round_history_output:
            dealer_info = (dealer_face_up_card.value, dealer_face_up_card.suit.name)

            # Initialize q_table for this player if it doesn't exist
            if player_index not in self.q_tables:
                self.q_tables[player_index] = {}

            q_table = self.q_tables[player_index]

            for i, (cards, stake, action) in enumerate(hand_history):
                player_hand_repr = tuple(sorted((card.value, card.suit.name) for card in cards))
                state = (player_hand_repr, dealer_info)
                action_key = action

                # Reward logic
                if outcome == "WIN":
                    reward = stake
                elif outcome == "LOSE":
                    reward = -stake
                else:
                    reward = 0
                if action == 3:
                    reward *= 2

                if (state, action_key) not in q_table:
                    q_table[(state, action_key)] = 0.0

                if i + 1 < len(hand_history):
                    next_cards, _, _ = hand_history[i + 1]
                    next_hand_repr = tuple(sorted((card.value, card.suit.name) for card in next_cards))
                    next_state = (next_hand_repr, dealer_info)
                    future_qs = [q_table.get((next_state, a), 0.0) for a in [0, 1, 2, 3, 4]]
                    max_future_q = max(future_qs)
                else:
                    max_future_q = 0.0

                old_q = q_table[(state, action_key)]
                new_q = old_q + learning_rate * (reward + discount_factor * max_future_q - old_q)
                q_table[(state, action_key)] = new_q


    def print_q_tables(self):
        if not self.q_tables:
            print("No Q-tables available.")
            return

        action_names = {0: "STAND", 1: "HIT", 2: "DOUBLE", 3: "SPLIT", 4: "INSURANCE"}

        for player_index, q_table in self.q_tables.items():
            print(f"\n# Q-Table for Player #{player_index + 1} #\n")
            for (state, action), q_value in q_table.items():
                player_hand_repr, dealer_info = state
                dealer_value, dealer_suit = dealer_info
                action_label = action_names.get(action, f"UNKNOWN({action})")

                player_hand_str = ', '.join(f"{val} of {suit}" for val, suit in player_hand_repr)
                dealer_card_str = f"{dealer_value} of {dealer_suit}"

                print(f"State -> Player Hand: [{player_hand_str}], Dealer: {dealer_card_str}")
                print(f"  Action: {action_label} ({action})")
                print(f"  Q-Value: {q_value:.4f}\n")


